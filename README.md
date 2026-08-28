# ros2-perception-sim

A ROS 2 (Jazzy) project focused on sensor perception, fusion, closed-loop control, and simulation — built with an emphasis on testing: fault injection, requirements traceability, and CI on every change.

---

## What's implemented so far

- **`counter_publisher`** — publishes an incrementing integer on `/fake/counter` at 10Hz. Early scaffolding, will be replaced by real sensor data in later stages.
- **`counter_subscriber`** — subscribes to `/fake/counter`, runs it through a threshold check, and publishes a `Bool` status on `/status/warning`.
- **`threshold_logic.py`** — the actual decision logic, kept as a plain function with no ROS dependency, so it can be tested without spinning up any nodes.
- **Unit tests** — parametrized tests on the threshold logic covering the boundary cases.
- **Node-level tests** — check that the node actually publishes the right thing, using a small reusable test-subscriber node.

The plan is to keep decision logic separated from ROS code, so the logic can be tested on its own and the ROS node is just a thin wrapper around it.

---

## Running it

```bash
colcon build --packages-select fake_sensors
source install/setup.bash

# two terminals
ros2 run fake_sensors counter_publisher
ros2 run fake_sensors counter_subscriber

# watch the derived status
ros2 topic echo /status/warning
```

Tests:
```bash
cd src/fake_sensors
python3 -m pytest test/ -v
```

## License

MIT — see `LICENSE`.