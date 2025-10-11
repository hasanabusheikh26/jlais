#!/usr/bin/env python3
"""
Quick test script to verify PiDog agent setup.
Tests mock mode without needing hardware.
"""

import sys

def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    
    try:
        from livekit import agents
        print("  ✅ livekit-agents")
    except ImportError as e:
        print(f"  ❌ livekit-agents: {e}")
        return False
    
    try:
        from livekit.plugins import google
        print("  ✅ livekit-plugins-google")
    except ImportError as e:
        print(f"  ❌ livekit-plugins-google: {e}")
        return False
    
    try:
        import cv2
        print("  ✅ opencv-python")
    except ImportError as e:
        print(f"  ❌ opencv-python: {e}")
        return False
    
    try:
        import numpy
        print("  ✅ numpy")
    except ImportError as e:
        print(f"  ❌ numpy: {e}")
        return False
    
    return True


def test_controller():
    """Test PiDog controller in mock mode"""
    print("\nTesting PiDog controller...")
    
    try:
        from pidog_controller import PiDogController
        
        controller = PiDogController()
        print(f"  ✅ Controller initialized (mode: {controller.mode})")
        
        # Test camera
        frame = controller.get_camera_frame()
        if frame is not None:
            print(f"  ✅ Camera frame: {frame.shape}")
        else:
            print("  ❌ Camera frame failed")
            return False
        
        # Test action
        result = controller.perform_action("sit")
        if result["success"]:
            print(f"  ✅ Action executed: {result}")
        else:
            print(f"  ❌ Action failed: {result}")
            return False
        
        # Cleanup
        controller.shutdown()
        print("  ✅ Shutdown successful")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Controller test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_actions():
    """Test action definitions"""
    print("\nTesting action definitions...")
    
    try:
        from pidog_actions import get_pidog_functions, PIDOG_ACTIONS
        
        functions = get_pidog_functions()
        print(f"  ✅ {len(functions)} action functions defined")
        print(f"  ✅ {len(PIDOG_ACTIONS)} total actions available")
        
        # Show a few examples
        print("\n  Sample actions:")
        for i, action in enumerate(list(PIDOG_ACTIONS.keys())[:5]):
            print(f"    • {action}: {PIDOG_ACTIONS[action]}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Actions test failed: {e}")
        return False


def test_env():
    """Test environment configuration"""
    print("\nTesting environment configuration...")
    
    import os
    from pathlib import Path
    
    if Path(".env").exists():
        print("  ✅ .env file found")
        
        # Load env vars
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET", "GOOGLE_API_KEY"]
        missing = []
        
        for var in required_vars:
            value = os.getenv(var)
            if value and not value.startswith("your") and not value.startswith("wss://your"):
                print(f"  ✅ {var} is set")
            else:
                print(f"  ⚠️  {var} needs configuration")
                missing.append(var)
        
        if missing:
            print(f"\n  ⚠️  Configure these in .env: {', '.join(missing)}")
            return False
        
        return True
    else:
        print("  ⚠️  .env file not found")
        print("  ℹ️  Copy .env.example to .env and configure it")
        return False


def main():
    print("=" * 60)
    print("🐕 PiDog Agent - Local Test")
    print("=" * 60)
    
    results = {
        "Imports": test_imports(),
        "Controller": test_controller(),
        "Actions": test_actions(),
        "Environment": test_env(),
    }
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<20} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! Ready to run:")
        print("   python pidog_agent.py dev")
    else:
        print("\n⚠️  Some tests failed. Fix issues above before running agent.")
        sys.exit(1)


if __name__ == "__main__":
    main()
