#!/usr/bin/env python3
"""
Test script to verify headless configuration logic
"""

import os
import sys

def test_config_loading():
    """Test that configuration values are loaded correctly"""
    print("=" * 70)
    print("Testing Configuration Loading")
    print("=" * 70)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    headless = os.getenv('HEADLESS', 'auto').lower().strip().strip('"')
    headless_login = os.getenv('HEADLESS_LOGIN', 'false').lower().strip().strip('"')
    
    print(f"\nHeadless mode configuration:")
    print(f"  HEADLESS = {headless}")
    print(f"  HEADLESS_LOGIN = {headless_login}")
    
    # Test the logic
    is_linux = sys.platform.startswith('linux')
    has_display = bool(os.environ.get('DISPLAY'))
    
    print(f"\nEnvironment detection:")
    print(f"  Platform: {sys.platform}")
    print(f"  Is Linux: {is_linux}")
    print(f"  Has DISPLAY: {has_display}")
    
    # Auto mode logic
    if headless == 'auto':
        would_use_headless = is_linux and not has_display
        print(f"\nWith HEADLESS=auto:")
        print(f"  Would use headless mode: {would_use_headless}")
    elif headless == 'true':
        print(f"\nWith HEADLESS=true:")
        print(f"  Would force headless mode: True")
    elif headless == 'false':
        print(f"\nWith HEADLESS=false:")
        print(f"  Would force headed mode: True")
    
    # Login mode
    force_headed_login = headless_login != 'true'
    print(f"\nLogin behavior:")
    print(f"  Force headed mode for login: {force_headed_login}")
    
    return True

def test_browser_module():
    """Test Browser module can be imported"""
    print("\n" + "=" * 70)
    print("Testing Browser Module Import")
    print("=" * 70)
    
    try:
        os.environ['IMAGEMAGICK_BINARY'] = '/usr/bin/convert'
        from tiktok_uploader.Browser import Browser
        print("\n[SUCCESS] Browser module imported successfully")
        
        # Test the detection method
        headless_config = os.getenv('HEADLESS', 'auto').lower().strip().strip('"')
        
        # We can't actually create Browser instance without starting Chrome,
        # but we can test the logic by accessing the class method
        print(f"\n[INFO] Browser class loaded with config: HEADLESS={headless_config}")
        
        return True
    except Exception as e:
        print(f"\n[ERROR] Failed to import Browser: {e}")
        return False

def test_config_class():
    """Test Config class for new properties"""
    print("\n" + "=" * 70)
    print("Testing Config Class")
    print("=" * 70)
    
    try:
        os.environ['IMAGEMAGICK_BINARY'] = '/usr/bin/convert'
        from tiktok_uploader.Config import Config
        
        # Load config
        config = Config.load('./config.txt')
        
        print(f"\n[INFO] Config loaded from config.txt")
        print(f"  Headless: {config.headless}")
        print(f"  Headless Login: {config.headless_login}")
        
        # Verify new properties exist
        assert hasattr(config, 'headless'), "Config missing 'headless' property"
        assert hasattr(config, 'headless_login'), "Config missing 'headless_login' property"
        
        print(f"\n[SUCCESS] Config class has new headless properties")
        return True
    except Exception as e:
        print(f"\n[ERROR] Config class test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("HEADLESS CONFIGURATION TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Configuration Loading", test_config_loading),
        ("Config Class", test_config_class),
        ("Browser Module", test_browser_module),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] Test '{name}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "=" * 70)
    print("TEST RESULTS")
    print("=" * 70)
    
    passed = 0
    failed = 0
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed out of {len(results)} tests")
    
    if failed == 0:
        print("\n" + "=" * 70)
        print("SUCCESS! All configuration tests passed.")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("FAILURE! Some tests failed.")
        print("=" * 70)
        sys.exit(1)
