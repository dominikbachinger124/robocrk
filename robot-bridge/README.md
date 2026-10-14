# RoboMaster S1 Robot Bridge

This directory contains scripts for connecting to the DJI RoboMaster S1 via the hacked SDK.

## ⚠️ Important: SDK Compatibility

The **official DJI RoboMaster SDK** (`pip install robomaster`) has compatibility issues with the hacked S1 firmware:
- ❌ Broadcast discovery fails
- ❌ Config attribute errors (`DEFAULT_CONN_PROTO`)
- ❌ Connection timeouts

**Solution**: Use the **plaintext protocol** directly via TCP (ports 40923, 40924, 40925).

---

## Prerequisites

- S1 must be rooted and hacked (see `/robomaster/hack.md`)
- S1 connected via USB cable to Micro USB port on intelligent controller
- ADB (Android Debug Bridge) installed
- Python 3.8 virtual environment set up

---

## Quick Start

### 1. Activate Virtual Environment

```bash
cd /home/komodor/robocrck/robot-bridge
source venv/bin/activate
```

### 2. Set Up ADB Port Forwarding

Since the hack enables ADB by default (disabling RNDIS ethernet), use ADB port forwarding:

```bash
# Set up port forwarding
python adb_bridge.py setup

# Or just forward ports (keeps running)
python adb_bridge.py forward
```

This forwards:
- Port 40923 (command/control)
- Port 40924 (video)
- Port 40925 (audio)

Verify with: `adb forward --list`

### 3. Test Connection

**Option A: Quick diagnostic**
```bash
python diagnose.py
```

**Option B: Test movement (recommended)**
```bash
python test_movement.py
```

This sends actual commands to verify the robot responds.

---

## Available Scripts

### Connection Scripts

| Script | Purpose |
|--------|---------|
| `adb_bridge.py` | ADB port forwarding helper |
| `diagnose.py` | Step-by-step connection diagnostics |
| `connect_lowlevel.py` | Plaintext protocol connection test |
| `test_movement.py` | Send actual movement commands to verify |

### SDK Wrappers

| Script | Purpose |
|--------|---------|
| `simple_sdk.py` | Simplified Python SDK using plaintext protocol |

### Legacy (May Not Work)

| Script | Purpose | Status |
|--------|---------|--------|
| `test_connection.py` | Official SDK connection test | ❌ Broken with hack |
| `connect.py` | Multi-method connection tool | ❌ Uses official SDK |

---

## Using the Simple SDK

The `simple_sdk.py` provides a Python API that works with the hacked S1:

```python
from simple_sdk import SimpleRobot

robot = SimpleRobot()
if robot.connect():
    # Get info
    print(robot.get_version())
    print(robot.get_gimbal_attitude())
    
    # Move gimbal
    robot.gimbal_moveto(pitch=10, yaw=20)
    
    # Set LEDs
    robot.led_gimbal(0, 255, 0)  # Green
    
    # Close
    robot.close()
```

### Interactive Mode

```bash
python simple_sdk.py
```

Type commands like:
- `gimbal_recenter()`
- `gimbal_moveto(10, 20)`
- `led_gimbal(255, 0, 0)`
- `blaster_fire()`

### Demo Mode

```bash
python simple_sdk.py --demo
```

---

## Plaintext Protocol Commands

Send commands directly via TCP to `127.0.0.1:40923`:

### Robot Info
```
version
robot mode ?
robot sn ?
```

### Gimbal
```
gimbal moveto p 10 y 20 vp 100 vy 100
gimbal move p 5 y -5
gimbal attitude ?
```

### Chassis
```
chassis move x 0.5 y 0 vxy 0.5
chassis wheel w1 100 w2 100 w3 100 w4 100
chassis speed x 0.3 z 10
```

### LEDs
```
led control comp top_all r 255 g 0 b 0 effect on
led control comp bottom_all r 0 g 255 b 0 effect breathing
```

### Blaster
```
blaster fire 1
```

**Note**: Commands must end with `;`

---

## Troubleshooting

### ADB Permission Issues

If `adb devices` shows "no permissions":

```bash
# Add udev rule
echo 'SUBSYSTEM=="usb", ATTR{idVendor}=="2ca3", MODE="0666", GROUP="plugdev"' | \
  sudo tee /etc/udev/rules.d/51-dji-robomaster.rules

# Reload
sudo udevadm control --reload-rules
sudo udevadm trigger

# Restart ADB
adb kill-server
adb start-server
```

Or temporarily:
```bash
sudo adb kill-server
sudo adb start-server
```

### TCP Works but No Movement

1. Check robot is in SDK mode (2 chimes on boot)
2. Verify hack is applied correctly
3. Try: `adb shell` to confirm ADB access
4. Check robot's IP: `adb shell ip addr show wlan0`

### Empty Responses

The hacked S1 may return empty responses. This is normal - commands may still work. Use `test_movement.py` to verify.

### Connection Refused

```bash
# Check port forwarding
adb forward --list

# Should show:
# 0123456789ABCDEF tcp:40923 tcp:40923

# If not, re-run:
python adb_bridge.py forward
```

---

## References

- [Official DJI RoboMaster SDK](https://github.com/dji-sdk/RoboMaster-SDK)
- [SDK Documentation (Chinese)](https://robomaster-dev.readthedocs.io/zh_CN/latest/)
- [S1 Hack Guide](/robomaster/hack.md)
- [Plaintext Protocol Reference](https://robomaster-dev.readthedocs.io/zh_CN/latest/text_sdk/protocol_api.html)
