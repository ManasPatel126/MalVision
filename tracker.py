"""
tracker.py — Real-Time Training Progress Tracker & Web Dashboard

Provides live, real-time monitoring of the Malware CNN training pipeline:
    1. Parses active training logs in real time (loss, accuracy, batch, epoch, ETA).
    2. Serves a high-performance, dark-themed real-time Web Dashboard at http://localhost:8050.
    3. Provides a live updating terminal dashboard if run with --cli.
    4. Automatically launches the browser on startup (can be disabled with --no-browser).

Usage:
    python tracker.py            # Starts live Web Dashboard on http://localhost:8050
    python tracker.py --cli      # Runs in live terminal mode
    python tracker.py --port 8080 # Custom port
"""

import os
import re
import sys
import time
import glob
import json
import webbrowser
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

# Default log search path
DEFAULT_LOG_DIR = r"C:\Users\MANAS\.gemini\antigravity\brain\572eb316-4108-4802-b8b9-227a34806e4b\.system_generated\tasks"
FALLBACK_LOG = os.path.join("outputs", "training.log")


def find_latest_log() -> str:
    """Locate the most recent training task log (excluding scheduler timers)."""
    logs = glob.glob(os.path.join(DEFAULT_LOG_DIR, "task-*.log"))
    if logs:
        logs.sort(key=os.path.getmtime, reverse=True)
        for log in logs:
            try:
                with open(log, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(8192)
                    # Exclude schedule timers
                    if "schedule" in content.lower() or "timer:" in content.lower():
                        continue
                    if "STEP 4: Training the model" in content or "Building data pipeline" in content or "main.py" in content:
                        return log
            except Exception:
                continue
        return logs[0]
    return FALLBACK_LOG


def parse_training_log(log_path: str) -> dict:
    """
    Parse the training log file and extract real-time metrics.
    """
    data = {
        "status": "Initializing",
        "current_epoch": 0,
        "total_epochs": 5,
        "current_batch": 0,
        "total_batches": 205,
        "batch_percent": 0.0,
        "overall_percent": 0.0,
        "current_loss": None,
        "current_acc": None,
        "best_val_loss": None,
        "elapsed_seconds": 0.0,
        "eta_seconds": None,
        "epoch_history": [],
        "loss_history": [],
        "acc_history": [],
        "recent_logs": [],
        "test_accuracy": None,
        "model_name": "ResNet-18 (1-ch Grayscale)",
        "num_classes": 26,
        "total_samples": 9339,
    }

    if not os.path.isfile(log_path):
        data["status"] = "Waiting for training to start..."
        return data

    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        data["status"] = f"Log read error: {e}"
        return data

    data["recent_logs"] = [l.strip() for l in lines[-12:] if l.strip()]

    # Extract configuration
    for line in lines:
        if "Discovered" in line and "images across" in line:
            m = re.search(r"Discovered\s+(\d+)\s+images\s+across\s+(\d+)\s+families", line)
            if m:
                data["total_samples"] = int(m.group(1))
                data["num_classes"] = int(m.group(2))
        elif "Building pretrained ResNet-18" in line:
            data["model_name"] = "Pretrained ResNet-18 (Grayscale)"
        elif "Building custom MalwareCNN" in line:
            data["model_name"] = "Custom MalwareCNN"

    # Epoch table parser:
    # "     1 |     1.7737 |    34.25% |     1.9510 |    16.67% |  14.6s"
    epoch_pattern = re.compile(
        r"^\s*(\d+)\s*\|\s*([\d\.]+)\s*\|\s*([\d\.]+)%\s*\|\s*([\d\.]+)\s*\|\s*([\d\.]+)%\s*\|\s*([\d\.]+)s"
    )
    # Batch progress parser:
    # "    Batch  50/205 | Loss: 0.4262 | Batch Acc: 77.0%"
    batch_pattern = re.compile(
        r"Batch\s+(\d+)\s*/\s*(\d+)\s*\|\s*Loss:\s*([\d\.]+)\s*\|\s*Batch Acc:\s*([\d\.]+)%"
    )
    # Best model save
    best_pattern = re.compile(r"Saved best model \(val_loss=([\d\.]+)\)")

    start_time = None
    last_batch_time = None
    completed_epochs = 0

    for line in lines:
        bm = batch_pattern.search(line)
        if bm:
            cur_b = int(bm.group(1))
            tot_b = int(bm.group(2))
            data["current_batch"] = cur_b
            data["total_batches"] = tot_b
            data["current_loss"] = float(bm.group(3))
            data["current_acc"] = float(bm.group(4))
            data["batch_percent"] = round((cur_b / tot_b) * 100, 1)
            data["status"] = "Training in Progress"

        em = epoch_pattern.search(line)
        if em:
            ep_num = int(em.group(1))
            t_loss = float(em.group(2))
            t_acc = float(em.group(3))
            v_loss = float(em.group(4))
            v_acc = float(em.group(5))
            e_time = float(em.group(6))

            completed_epochs = max(completed_epochs, ep_num)
            data["epoch_history"].append({
                "epoch": ep_num,
                "train_loss": t_loss,
                "train_acc": t_acc,
                "val_loss": v_loss,
                "val_acc": v_acc,
                "time_sec": e_time,
            })
            data["loss_history"].append(t_loss)
            data["acc_history"].append(t_acc)
            data["current_epoch"] = ep_num

        sm = best_pattern.search(line)
        if sm:
            data["best_val_loss"] = float(sm.group(1))

        if "STEP 5: Evaluating on the test set" in line:
            data["status"] = "Evaluating on Test Set"

        tm = re.search(r"Test Accuracy:\s*([\d\.]+)", line)
        if tm:
            data["test_accuracy"] = float(tm.group(1))

        if "PIPELINE COMPLETE" in line:
            data["status"] = "Completed"
            data["overall_percent"] = 100.0

    # Calculate overall progress
    if data["status"] != "Completed":
        # Epochs count
        total_eps = data["total_epochs"]
        current_ep = max(0, completed_epochs)
        if data["current_batch"] > 0 and data["total_batches"] > 0:
            fractional_epoch = completed_epochs + (data["current_batch"] / data["total_batches"])
        else:
            fractional_epoch = completed_epochs
        data["current_epoch"] = min(total_eps, completed_epochs + 1)
        data["overall_percent"] = min(99.0, round((fractional_epoch / total_eps) * 100, 1))

    return data


# ──────────────────────────────────────────────────────────────────────────────
# Embedded Web Dashboard (HTML + Vanilla JS + Modern Responsive UI)
# ──────────────────────────────────────────────────────────────────────────────

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Malware CNN — Real-Time Training Tracker</title>
  <style>
    :root {
      --bg: #0d1117;
      --card-bg: #161b22;
      --border: #30363d;
      --text: #c9d1d9;
      --text-bright: #f0f6fc;
      --text-muted: #8b949e;
      --accent-blue: #58a6ff;
      --accent-green: #3fb950;
      --accent-purple: #bc8cff;
      --accent-amber: #d29922;
      --accent-red: #f85149;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    body { background: var(--bg); color: var(--text); padding: 24px; min-height: 100vh; }
    .container { max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }
    
    /* Header */
    .header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 16px; border-bottom: 1px solid var(--border); }
    .title-group h1 { font-size: 24px; color: var(--text-bright); display: flex; align-items: center; gap: 12px; }
    .title-group p { font-size: 14px; color: var(--text-muted); margin-top: 4px; }
    .badge { padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .badge-running { background: rgba(88, 166, 255, 0.15); color: var(--accent-blue); border: 1px solid rgba(88, 166, 255, 0.4); animation: pulse 2s infinite; }
    .badge-done { background: rgba(63, 185, 80, 0.15); color: var(--accent-green); border: 1px solid rgba(63, 185, 80, 0.4); }
    @keyframes pulse { 0% { opacity: 0.7; } 50% { opacity: 1; } 100% { opacity: 0.7; } }

    /* Top Cards Grid */
    .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
    .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 18px; display: flex; flex-direction: column; justify-content: space-between; }
    .card-label { font-size: 13px; color: var(--text-muted); text-transform: uppercase; font-weight: 500; letter-spacing: 0.5px; }
    .card-value { font-size: 28px; font-weight: 700; color: var(--text-bright); margin: 8px 0; }
    .card-sub { font-size: 12px; color: var(--text-muted); }

    /* Progress Section */
    .progress-section { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 20px; }
    .progress-header { display: flex; justify-content: space-between; font-size: 14px; font-weight: 600; color: var(--text-bright); margin-bottom: 8px; }
    .progress-bar-container { width: 100%; height: 12px; background: #21262d; border-radius: 6px; overflow: hidden; position: relative; }
    .progress-bar { height: 100%; width: 0%; border-radius: 6px; transition: width 0.4s ease; }
    .bar-blue { background: linear-gradient(90deg, #1f6feb, #58a6ff); }
    .bar-purple { background: linear-gradient(90deg, #8957e5, #bc8cff); }
    .bar-green { background: linear-gradient(90deg, #238636, #3fb950); }

    /* Chart & History */
    .charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    @media (max-width: 800px) { .charts-grid { grid-template-columns: 1fr; } }
    .chart-container { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 20px; min-height: 240px; display: flex; flex-direction: column; }
    .chart-title { font-size: 15px; font-weight: 600; color: var(--text-bright); margin-bottom: 12px; }
    .chart-canvas-wrapper { flex: 1; position: relative; width: 100%; height: 160px; }
    svg.chart-svg { width: 100%; height: 100%; }

    /* Log Box */
    .log-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 18px; }
    .log-box { background: #090d13; border: 1px solid #21262d; border-radius: 6px; padding: 12px; font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 12px; line-height: 1.6; color: #7ee787; max-height: 160px; overflow-y: auto; white-space: pre-wrap; }

    /* History Table */
    table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 10px; }
    th { text-align: left; padding: 8px 12px; color: var(--text-muted); border-bottom: 1px solid var(--border); font-weight: 500; }
    td { padding: 8px 12px; border-bottom: 1px solid #21262d; color: var(--text); }
    tr:last-child td { border-bottom: none; }
  </style>
</head>
<body>
  <div class="container">
    <!-- Header -->
    <div class="header">
      <div class="title-group">
        <h1>
          <span>🛡️ Malware CNN Live Tracker</span>
          <span id="statusBadge" class="badge badge-running">Training</span>
        </h1>
        <p id="subheading">Dataset: Malimg (9,339 images, 26 families) • Backbone: ResNet-18 (Grayscale)</p>
      </div>
      <div style="text-align: right;">
        <div style="font-size: 12px; color: var(--text-muted);">Auto-refreshing every 1s</div>
        <div id="lastUpdated" style="font-size: 11px; color: var(--accent-blue); margin-top: 4px;">Connecting...</div>
      </div>
    </div>

    <!-- Metrics Cards -->
    <div class="metrics-grid">
      <div class="card">
        <div class="card-label">Current Epoch</div>
        <div id="metricEpoch" class="card-value">- / -</div>
        <div id="metricBatchSub" class="card-sub">Batch: 0 / 205</div>
      </div>
      <div class="card">
        <div class="card-label">Training Loss</div>
        <div id="metricLoss" class="card-value" style="color: var(--accent-amber);">--</div>
        <div id="metricLossSub" class="card-sub">Latest batch cross-entropy</div>
      </div>
      <div class="card">
        <div class="card-label">Batch Accuracy</div>
        <div id="metricAcc" class="card-value" style="color: var(--accent-green);">--%</div>
        <div id="metricAccSub" class="card-sub">Live running batch acc</div>
      </div>
      <div class="card">
        <div class="card-label">Best Val Loss</div>
        <div id="metricBestVal" class="card-value" style="color: var(--accent-purple);">--</div>
        <div id="metricBestValSub" class="card-sub">Checkpoint criteria</div>
      </div>
    </div>

    <!-- Overall Progress -->
    <div class="progress-section">
      <div class="progress-header">
        <span>Overall Training Progress</span>
        <span id="overallPercentLabel">0.0%</span>
      </div>
      <div class="progress-bar-container" style="margin-bottom: 16px;">
        <div id="overallBar" class="progress-bar bar-blue"></div>
      </div>

      <div class="progress-header">
        <span>Current Epoch Progress</span>
        <span id="batchPercentLabel">Batch 0 / 205 (0.0%)</span>
      </div>
      <div class="progress-bar-container">
        <div id="batchBar" class="progress-bar bar-purple"></div>
      </div>
    </div>

    <!-- Epoch History Table -->
    <div class="card">
      <div class="card-label">Epoch Completed History</div>
      <table id="historyTable">
        <thead>
          <tr>
            <th>Epoch</th>
            <th>Train Loss</th>
            <th>Train Acc</th>
            <th>Val Loss</th>
            <th>Val Acc</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody id="historyTbody">
          <tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 16px;">Training first epoch in progress...</td></tr>
        </tbody>
      </table>
    </div>

    <!-- Live Console Tail -->
    <div class="log-card">
      <div class="card-label" style="margin-bottom: 8px;">Live Process Log (Tail)</div>
      <div id="logBox" class="log-box">Waiting for logs...</div>
    </div>
  </div>

  <script>
    async function updateDashboard() {
      try {
        const res = await fetch('/api/status');
        if (!res.ok) return;
        const data = await res.json();

        // Status badge
        const badge = document.getElementById('statusBadge');
        badge.innerText = data.status;
        if (data.status.toLowerCase().includes('complete')) {
          badge.className = 'badge badge-done';
        } else {
          badge.className = 'badge badge-running';
        }

        // Metrics
        document.getElementById('metricEpoch').innerText = `${data.current_epoch} / ${data.total_epochs}`;
        document.getElementById('metricBatchSub').innerText = `Batch: ${data.current_batch} / ${data.total_batches}`;

        if (data.current_loss !== null) {
          document.getElementById('metricLoss').innerText = data.current_loss.toFixed(4);
        }
        if (data.current_acc !== null) {
          document.getElementById('metricAcc').innerText = `${data.current_acc.toFixed(1)}%`;
        }
        if (data.best_val_loss !== null) {
          document.getElementById('metricBestVal').innerText = data.best_val_loss.toFixed(4);
        }

        // Progress bars
        const overallPct = data.overall_percent || 0;
        document.getElementById('overallBar').style.width = `${overallPct}%`;
        document.getElementById('overallPercentLabel').innerText = `${overallPct}%`;

        const batchPct = data.batch_percent || 0;
        document.getElementById('batchBar').style.width = `${batchPct}%`;
        document.getElementById('batchPercentLabel').innerText = `Batch ${data.current_batch} / ${data.total_batches} (${batchPct}%)`;

        // History Table
        if (data.epoch_history && data.epoch_history.length > 0) {
          const tbody = document.getElementById('historyTbody');
          tbody.innerHTML = data.epoch_history.map(row => `
            <tr>
              <td><strong>#${row.epoch}</strong></td>
              <td>${row.train_loss.toFixed(4)}</td>
              <td>${row.train_acc.toFixed(2)}%</td>
              <td><span style="color: var(--accent-purple);">${row.val_loss.toFixed(4)}</span></td>
              <td><span style="color: var(--accent-green);">${row.val_acc.toFixed(2)}%</span></td>
              <td>${row.time_sec.toFixed(1)}s</td>
            </tr>
          `).join('');
        }

        // Logs
        if (data.recent_logs && data.recent_logs.length > 0) {
          const logBox = document.getElementById('logBox');
          logBox.innerText = data.recent_logs.join('\\n');
          logBox.scrollTop = logBox.scrollHeight;
        }

        document.getElementById('lastUpdated').innerText = `Updated at ${new Date().toLocaleTimeString()}`;
      } catch (err) {
        document.getElementById('lastUpdated').innerText = 'Reconnecting...';
      }
    }

    setInterval(updateDashboard, 1000);
    updateDashboard();
  </script>
</body>
</html>
"""


# ──────────────────────────────────────────────────────────────────────────────
# HTTP Server Request Handler
# ──────────────────────────────────────────────────────────────────────────────

class TrackerHandler(BaseHTTPRequestHandler):
    log_file_path = None

    def do_GET(self):
        if self.path == "/api/status":
            data = parse_training_log(TrackerHandler.log_file_path or find_latest_log())
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode("utf-8"))

    def log_message(self, format, *args):
        # Silence default HTTP access logs to keep terminal clean
        return


def run_server(port: int = 8050, log_path: str = None, open_browser: bool = True):
    TrackerHandler.log_file_path = log_path or find_latest_log()
    server = HTTPServer(("0.0.0.0", port), TrackerHandler)
    url = f"http://localhost:{port}"

    print("=" * 70)
    print("  MALWARE CNN REAL-TIME TRAINING TRACKER")
    print("=" * 70)
    print(f"  [SERVER] Live Web Dashboard running at: {url}")
    print(f"  [SOURCE] Reading logs from: {TrackerHandler.log_file_path}")
    print("  [INFO] Press Ctrl+C in terminal to stop tracker.")
    print("=" * 70)

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    server.serve_forever()


def run_cli_monitor(log_path: str = None):
    """Rich animated in-place console monitor."""
    log_file = log_path or find_latest_log()
    print(f"[INFO] Monitoring log: {log_file} (Press Ctrl+C to stop)\n")

    try:
        while True:
            data = parse_training_log(log_file)
            status = data["status"]
            ep = data["current_epoch"]
            tot_ep = data["total_epochs"]
            cb = data["current_batch"]
            tb = data["total_batches"]
            loss = f"{data['current_loss']:.4f}" if data['current_loss'] is not None else "--"
            acc = f"{data['current_acc']:.1f}%" if data['current_acc'] is not None else "--%"
            overall = data["overall_percent"]
            batch_pct = data["batch_percent"]

            # 20-char progress bars
            bar_len = 25
            filled_overall = int((overall / 100) * bar_len)
            overall_bar = "█" * filled_overall + "░" * (bar_len - filled_overall)

            filled_batch = int((batch_pct / 100) * bar_len) if tb > 0 else 0
            batch_bar = "█" * filled_batch + "░" * (bar_len - filled_batch)

            # Clear screen ANSI or print in-place
            output = (
                f"\r[{status:18s}] "
                f"Epoch: {ep}/{tot_ep} [{overall_bar}] {overall:5.1f}% | "
                f"Batch: {cb:3d}/{tb} [{batch_bar}] {batch_pct:5.1f}% | "
                f"Loss: {loss} | Acc: {acc}"
            )
            sys.stdout.write(output)
            sys.stdout.flush()

            if status == "Completed":
                print("\n[INFO] Training complete!")
                break

            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Monitor stopped.")


def main():
    parser = argparse.ArgumentParser(description="Real-Time Training Progress Tracker")
    parser.add_argument("--cli", action="store_true", help="Run in terminal CLI mode instead of web dashboard.")
    parser.add_argument("--port", type=int, default=8050, help="Web dashboard port (default: 8050).")
    parser.add_argument("--log", type=str, default=None, help="Explicit path to the training log file.")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open browser.")
    args = parser.parse_args()

    if args.cli:
        run_cli_monitor(args.log)
    else:
        run_server(port=args.port, log_path=args.log, open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
