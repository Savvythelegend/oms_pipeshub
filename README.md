# OMS Assignment – Mehfooj | June 2025

## Features

* Basic queuing of incoming orders
* Modify or cancel orders before they're sent
* Rate limit (X orders per second)
* Processes orders only during a configured time window
* Tracks latency between sending and receiving order responses (simulated)

## How to Run

Make sure Python 3.8 or higher is installed.

```bash
python oms_main.py
```

## Files

* `oms_core.py` – core logic
* `models.py` – types and order structure
* `config.py` – session time and throttle settings
* `oms_main.py` – basic test script to check flow

---
