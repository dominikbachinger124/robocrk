#!/usr/bin/env python3
"""Connect to RoboMaster S1 with multiple fallback methods."""

import sys
import time
import argparse


def try_connection_method(method_name, connect_func):
    """Try a connection method and handle errors gracefully."""
    print(f"\n{'=' * 50}")
    print(f"🔌 Trying: {method_name}")
    print(f"{'=' * 50}")

    ep_robot = None
    try:
        ep_robot = connect_func()
        if ep_robot:
            print(f"✅ {method_name}: SUCCESS")
            return ep_robot
    except Exception as e:
        print(f"❌ {method_name}: FAILED - {e}")

    return None


def method_direct_ip(ip):
    """Connect directly to specified IP."""
    from robomaster import robot, config

    print(f"   Target IP: {ip}")
    config.ROBOT_IP_ADDR = ip

    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="sta")
    return ep_robot


def method_ap_mode():
    """Connect to robot in AP mode (default IP)."""
    return method_direct_ip("192.168.2.1")


def method_localhost():
    """Connect via ADB port forwarding."""
    return method_direct_ip("127.0.0.1")


def method_broadcast():
    """Connect using broadcast discovery."""
    from robomaster import robot

    print("   Using broadcast discovery")
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="sta")
    return ep_robot


def method_rndis():
    """Try RNDIS (ethernet over USB) mode."""
    # RNDIS typically uses 192.168.42.x range
    return method_direct_ip("192.168.42.2")


def test_robot(ep_robot):
    """Test robot connection by getting basic info."""
    print("\n📋 Testing robot connection...")

    results = {}

    # Test version
    try:
        results["version"] = ep_robot.get_version()
        print(f"   ✅ Version: {results['version']}")
    except Exception as e:
        results["version"] = None
        print(f"   ❌ Version: {e}")

    # Test SN
    try:
        results["sn"] = ep_robot.get_sn()
        print(f"   ✅ SN: {results['sn']}")
    except Exception as e:
        results["sn"] = None
        print(f"   ❌ SN: {e}")

    # Test battery
    try:
        results["battery"] = ep_robot.battery.get_battery()
        print(f"   ✅ Battery: {results['battery']}%")
    except Exception as e:
        results["battery"] = None
        print(f"   ❌ Battery: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Connect to RoboMaster S1 with fallback methods"
    )
    parser.add_argument("--ip", type=str, default=None, help="Try specific IP first")
    parser.add_argument(
        "--keep-alive", action="store_true", help="Keep connection alive after testing"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🤖 RoboMaster S1 Connection Tool")
    print("=" * 60)

    # Check SDK is installed
    try:
        from robomaster import robot, config

        print("✅ SDK loaded successfully")
    except ImportError:
        print("❌ robomaster SDK not installed!")
        print("   Run: pip install robomaster")
        return 1

    ep_robot = None

    # Try methods in order
    methods = []

    if args.ip:
        methods.append((f"Direct IP ({args.ip})", lambda: method_direct_ip(args.ip)))

    methods.extend(
        [
            ("ADB Port Forward (127.0.0.1)", method_localhost),
            ("AP Mode (192.168.2.1)", method_ap_mode),
            ("RNDIS Mode (192.168.42.2)", method_rndis),
            ("Broadcast Discovery", method_broadcast),
        ]
    )

    for method_name, connect_func in methods:
        ep_robot = try_connection_method(method_name, connect_func)
        if ep_robot:
            break
        time.sleep(0.5)  # Brief pause between attempts

    if not ep_robot:
        print("\n" + "=" * 60)
        print("❌ All connection methods failed!")
        print("=" * 60)
        print()
        print("🔧 Troubleshooting:")
        print("   1. Check robot is powered on (listen for 2 chimes)")
        print("   2. Verify USB connection to Micro USB port")
        print("   3. Check ADB: adb devices")
        print("   4. Check port forwarding: adb forward --list")
        print("   5. Try: adb shell (to test ADB works)")
        print("   6. Check robot IP: adb shell ip addr show wlan0")
        return 1

    # Test the connection
    print("\n" + "=" * 60)
    print("✅ Connected! Testing robot...")
    print("=" * 60)

    results = test_robot(ep_robot)

    if args.keep_alive:
        print("\n📴 Connection kept alive.")
        print("   Press Ctrl+C to disconnect.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nDisconnecting...")

    # Cleanup
    print("\n📴 Closing connection...")
    try:
        ep_robot.close()
        print("   ✅ Disconnected")
    except Exception as e:
        print(f"   ⚠️  Cleanup warning: {e}")

    print("\n" + "=" * 60)
    print("✅ Connection test complete!")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
