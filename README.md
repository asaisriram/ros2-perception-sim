# ros2-perception-sim

[![CI](https://github.com/asaisriram/ros2-perception-sim/actions/workflows/ci.yml/badge.svg)](https://github.com/asaisriram/ros2-perception-sim/actions/workflows/ci.yml)

A ROS 2 (Jazzy) project focused on sensor perception, fusion, closed-loop control, and simulation — built with an emphasis on testing: fault injection, requirements traceability, and CI on every change.

---

## What's implemented so far

Two independent sensor nodes observe the same simulated physical quantity — a sawtooth
temperature ramp derived from absolute time — and a monitor node cross-checks them
against each other.

- **`counter_publisher`** — samples the ground-truth model and publishes a `Float32` on
  `/fake/counter` at 10 Hz. A raw, uncalibrated proxy for the measured quantity.
- **`temperature_publisher`** — samples the same model independently and publishes a
  calibrated `sensor_msgs/Temperature` on `/fake/temperature` at 4 Hz, with measurement
  noise and a populated header. Uses `qos_profile_sensor_data` (`BEST_EFFORT`).
- **`sensor_monitor`** — subscribes to both, runs a threshold check and a plausibility
  cross-check, and publishes a `Bool` on `/status/warning` (`RELIABLE`).
- **`simulation_logic_and_validity.py`** — the ground-truth model and all decision logic,
  as plain functions with no ROS dependency.

### limitations

- `/status/warning` is a `Bool`, but the system has three meaningful states — OK,
  warning, and not-yet-determinable. Noted for a later stage.
- The monitor does not check message age. A stale reading is treated as equally valid
  to a fresh one; the tolerance absorbs the resulting error rather than detecting it.
  Time synchronization is a later stage.

---

## Running it

Everything below assumes ROS 2 Jazzy on Ubuntu 24.04. If you'd rather not install it,
see [Running in Docker](#running-in-docker).

```bash
colcon build --packages-select fake_sensors
source install/setup.bash

# three terminals
ros2 run fake_sensors counter_publisher
ros2 run fake_sensors temperature_publisher
ros2 run fake_sensors sensor_monitor

# watch the derived status
ros2 topic echo /status/warning
```

Inspect the QoS of a topic's endpoints:

```bash
ros2 topic info /fake/temperature --verbose
```

## Tests

```bash
cd src/fake_sensors
python3 -m pytest test/ -v
```

`python3 -m pytest` runs only the project's own tests. `colcon test` additionally runs
the `ament_flake8`, `ament_pep257`, and `ament_copyright` lint checks — which is what CI
enforces, so run it before pushing:

```bash
colcon build --packages-select fake_sensors
colcon test --packages-select fake_sensors
colcon test-result --verbose
```

## Running in Docker

The `Dockerfile` defines the CI environment. It's the same image CI uses, so a green
run here means a green run there — no ROS 2 installation required on the host.

```bash
docker build -t ros2-perception-sim-ci .
docker run --rm -it ros2-perception-sim-ci bash -c "
  source /opt/ros/jazzy/setup.bash
  source install/setup.bash
  colcon test --packages-select fake_sensors
  colcon test-result --verbose
"
```

## License

MIT — see `LICENSE`.