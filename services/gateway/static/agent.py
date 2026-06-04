#!/usr/bin/env python3
"""
DevStack Metrics Agent
Streams CPU, RAM and disk usage to your DevStack dashboard every 5 seconds.

Usage:
    pip3 install psutil          # macOS / Linux
    python3 -m pip install psutil  # if pip3 not found

    python3 agent.py --url https://your-dashboard-url --key YOUR_API_KEY --node YOUR_NODE_ID

Optional:
    --interval  Seconds between posts (default: 5)
"""
import argparse
import json
import logging
import sys
import time
import urllib.error
import urllib.request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def check_psutil():
    try:
        import psutil
        return psutil
    except ImportError:
        log.error("psutil is not installed. Run: pip install psutil")
        sys.exit(1)


def collect(psutil):
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    return cpu, ram, disk


def post_metrics(url, key, node_id, cpu, ram, disk):
    payload = json.dumps({
        "node_id": node_id,
        "cpu_pct": cpu,
        "ram_pct": ram,
        "disk_pct": disk,
    }).encode()

    req = urllib.request.Request(
        f"{url.rstrip('/')}/api/v1/metrics",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 201:
                log.info("CPU=%.1f%%  RAM=%.1f%%  DISK=%.1f%%", cpu, ram, disk)
            else:
                log.warning("Unexpected status %s", resp.status)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            log.error("Invalid or revoked API key. Check --key.")
            sys.exit(1)
        else:
            log.warning("HTTP error %s: %s", e.code, e.reason)
    except urllib.error.URLError as e:
        log.warning("Connection error: %s — will retry", e.reason)
    except Exception as e:
        log.warning("Unexpected error: %s — will retry", e)


def main():
    parser = argparse.ArgumentParser(description="DevStack Metrics Agent")
    parser.add_argument("--url", required=True, help="Dashboard base URL")
    parser.add_argument("--key", required=True, help="API key")
    parser.add_argument("--node", required=True, help="Node ID (UUID)")
    parser.add_argument("--interval", type=float, default=5.0, help="Seconds between posts")
    args = parser.parse_args()

    psutil = check_psutil()

    log.info("Agent starting — posting to %s every %.0fs", args.url, args.interval)
    log.info("Node ID: %s", args.node)

    first_success = True
    while True:
        cpu, ram, disk = collect(psutil)
        post_metrics(args.url, args.key, args.node, cpu, ram, disk)
        if first_success:
            print("\n  ✓ Data is live! Open the Live Metrics tab in your dashboard to see your charts.\n")
            first_success = False
        time.sleep(max(0, args.interval - 1))  # cpu_percent already sleeps 1s


if __name__ == "__main__":
    main()
