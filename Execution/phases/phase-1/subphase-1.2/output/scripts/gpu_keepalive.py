#!/usr/bin/env python
"""
Standalone GPU keepalive. Runs a tiny matmul every 5 min to register GPU
activity on the SLURM node, preventing YCRC's 1-hr-idle auto-cancel.

Designed to be attached to an existing SLURM job via:
  srun --jobid=<JID> --overlap python gpu_keepalive.py

Exit with SIGTERM / SIGINT when no longer needed (or let it exit with the
parent SLURM job).
"""
from __future__ import annotations

import os
import signal
import sys
import time


def log(msg: str) -> None:
    print(f"[keepalive {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main() -> int:
    try:
        import torch
    except Exception as e:
        log(f"torch import failed: {e}; exiting")
        return 1

    if not torch.cuda.is_available():
        log("no CUDA device; exiting")
        return 1

    dev = torch.device('cuda:0')
    log(f"attached to {torch.cuda.get_device_name(0)} (PID {os.getpid()}); cadence=300 s")

    x = torch.randn(64, 64, device=dev)
    running = True

    def _stop(signum, frame):
        nonlocal running
        log(f"received signal {signum}; stopping")
        running = False

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    pings = 0
    while running:
        try:
            y = torch.matmul(x, x).sum().item()
            torch.cuda.synchronize()
            pings += 1
            if pings % 12 == 0:  # every hour
                log(f"ping {pings} ok (hourly heartbeat)")
        except Exception as e:
            log(f"matmul error: {e}; continuing")
        # Sleep in 10-s chunks so signals land promptly.
        for _ in range(30):
            if not running:
                break
            time.sleep(10)

    log(f"exit clean; {pings} pings total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
