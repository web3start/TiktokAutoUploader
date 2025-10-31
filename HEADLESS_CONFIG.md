# Headless Mode Configuration Guide

This document describes the configurable headless mode feature added to the TikTok uploader.

## Overview

The uploader now supports configurable headless mode through environment variables and config files. This allows users to:

1. **Force headless mode** - Run without GUI even when a display is available
2. **Force headed mode** - Always use GUI even in headless environments 
3. **Auto-detect** (default) - Automatically determine based on the DISPLAY environment variable
4. **Preserve headed login** - Keep login in GUI mode by default for better compatibility

## Configuration Options

### Environment Variables (.env)

Two new configuration options have been added:

```bash
# Headless mode: 'auto' (detect based on DISPLAY), 'true' (force headless), 'false' (force headed)
HEADLESS=auto

# Keep login in headed mode by default to preserve local workflows
HEADLESS_LOGIN=false
```

### Config File (config.txt)

The same options are available in config.txt:

```
HEADLESS= auto
HEADLESS_LOGIN= false
```

## Configuration Values

### HEADLESS

Controls the browser mode for uploads and general operations:

- **`auto`** (default): Automatically detects headless environment
  - On Linux without DISPLAY: Uses headless mode
  - On Linux with DISPLAY: Uses headed mode
  - On Windows/macOS: Uses headed mode
  
- **`true`**: Forces headless mode regardless of environment
  - Useful for CI/CD pipelines
  - Useful for Docker containers
  - Useful for remote servers without X11
  
- **`false`**: Forces headed mode (GUI) regardless of environment
  - Useful for debugging
  - Useful when X11 forwarding is available

### HEADLESS_LOGIN

Controls the browser mode specifically for login/cookie generation:

- **`false`** (default): Always uses headed mode for login
  - Recommended for interactive login
  - Preserves existing local workflows
  - Better compatibility with TikTok's login challenges
  
- **`true`**: Uses headless mode for login
  - Only use if you have working cookies
  - May not work with interactive login challenges

## Anti-Detection Features

When headless mode is active, the following anti-detection measures are automatically applied:

### Critical Linux/Container Flags
- `--headless=new` - Modern headless mode
- `--no-sandbox` - Required for containers/restricted environments
- `--disable-setuid-sandbox` - Alternative sandbox for restricted environments
- `--disable-dev-shm-usage` - Prevents crashes due to limited shared memory
- `--disable-gpu` - Disables GPU hardware acceleration
- `--disable-software-rasterizer` - Prevents software rendering issues

### Anti-Detection Tweaks
- `--disable-blink-features=AutomationControlled` - Hides automation markers
- `--disable-extensions` - Reduces automation indicators
- `--disable-plugins-discovery` - Suppresses plugin detection
- `--disable-infobars` - Removes automation warnings
- Removes automation extension flags
- Suppresses "Chrome is being controlled" messages

### Stability Flags
- `--disable-web-security` - Prevents CORS issues in automation
- `--disable-features=IsolateOrigins,site-per-process` - Improves stability
- `--window-size=1920,1080` - Sets consistent viewport
- `--start-maximized` - Ensures full window size

## Usage Examples

### Example 1: Default Auto-Detection (Recommended)

```bash
# .env
HEADLESS=auto
HEADLESS_LOGIN=false
```

This will:
- Use headless mode on servers without GUI
- Use headed mode on local machines with GUI
- Always use headed mode for login (recommended)

### Example 2: Force Headless for CI/CD

```bash
# .env
HEADLESS=true
HEADLESS_LOGIN=false
```

This will:
- Always use headless mode for uploads
- Use headed mode for login (you'll need to login once locally first)

### Example 3: Force Headed Mode (Debugging)

```bash
# .env
HEADLESS=false
HEADLESS_LOGIN=false
```

This will:
- Always use headed mode with GUI
- Useful for debugging issues

### Example 4: Full Headless (Advanced)

```bash
# .env
HEADLESS=true
HEADLESS_LOGIN=true
```

This will:
- Use headless mode for everything
- **Warning**: May not work with interactive login challenges

## CLI Commands

The configuration is automatically applied to all CLI commands:

```bash
# Login (uses HEADLESS_LOGIN setting)
python cli.py login -n my_account

# Upload (uses HEADLESS setting)
python cli.py upload --user my_account -v video.mp4 -t "My Title"
```

## Technical Details

### Browser Singleton Pattern

The Browser class uses a singleton pattern with lazy initialization:

- First call to `Browser.get()` creates the instance with the specified mode
- Subsequent calls return the same instance
- To change modes, restart the application

### Force Headed Mode for Login

The login function automatically forces headed mode when `HEADLESS_LOGIN=false`:

```python
# In tiktok.py
headless_login = os.getenv('HEADLESS_LOGIN', 'false').lower().strip().strip('"')
force_headed = headless_login != 'true'
browser = Browser.get(force_headed=force_headed)
```

### Mode Detection Logic

```python
def _should_use_headless(headless_config, force_headed):
    if force_headed:
        return False
    
    if headless_config == 'true':
        return True
    elif headless_config == 'false':
        return False
    else:  # 'auto' or any other value
        is_linux = sys.platform.startswith('linux')
        has_display = bool(os.environ.get('DISPLAY'))
        return is_linux and not has_display
```

## Testing

### Test Headless Configuration

```bash
export IMAGEMAGICK_BINARY=/usr/bin/convert
python3 test_headless.py
```

### Test Integration with Signature Generation

```bash
export IMAGEMAGICK_BINARY=/usr/bin/convert
python3 test_integration.py
```

### Test Different Configurations

```bash
# Test auto mode (default)
export HEADLESS=auto
python3 test_integration.py

# Test forced headless
export HEADLESS=true
python3 test_integration.py

# Test forced headed (requires DISPLAY)
export HEADLESS=false
export DISPLAY=:0
python3 test_integration.py
```

## Troubleshooting

### "Browser instance already exists in headless mode, but headed mode requested"

This warning occurs when:
1. Browser was initialized in headless mode
2. Login function requests headed mode
3. Singleton pattern prevents re-initialization

**Solution**: Restart the application to create a new browser instance.

### Upload hangs in headless mode

If uploads still hang after configuration:

1. Verify Playwright dependencies are installed:
   ```bash
   cd tiktok_uploader/tiktok-signature
   npx playwright install chromium
   sudo npx playwright install-deps chromium
   ```

2. Check system memory (minimum 1GB free recommended)

3. Verify Node.js is working:
   ```bash
   node --version
   ```

4. Test signature generation:
   ```bash
   export IMAGEMAGICK_BINARY=/usr/bin/convert
   python3 test_integration.py
   ```

### Login fails in headless mode

**Recommended**: Use `HEADLESS_LOGIN=false` (default)

Login should run in headed mode because:
- Interactive challenges require GUI
- QR code scanning requires display
- Better compatibility with TikTok's security measures

If you must use headless login:
1. Ensure you have valid cookies from a previous headed login
2. Or use a tool like Xvfb for virtual display

## Compatibility

### Operating Systems
- **Linux**: Full support for both headed and headless modes
- **Windows**: Works normally (headless mode available but less tested)
- **macOS**: Works normally (headless mode available but less tested)

### Environments
- **Local machine with GUI**: Use `HEADLESS=auto` or `HEADLESS=false`
- **Docker container**: Use `HEADLESS=true`, `HEADLESS_LOGIN=false`
- **CI/CD pipeline**: Use `HEADLESS=true`, `HEADLESS_LOGIN=false`
- **Remote server via SSH**: Use `HEADLESS=auto` (will auto-detect)

## Migration Guide

### Upgrading from Previous Version

The old code used automatic detection only:
```python
is_headless = is_linux and not os.environ.get('DISPLAY')
```

New code supports configuration:
```python
headless_config = os.getenv('HEADLESS', 'auto')
is_headless = self._should_use_headless(headless_config, force_headed)
```

**No changes required** - the default `HEADLESS=auto` preserves the old behavior.

### For Users Who Modified Browser.py

If you previously modified `Browser.py` to force headless mode:
1. Remove your modifications
2. Set `HEADLESS=true` in .env instead
3. Your customizations are preserved through configuration

## Best Practices

1. **Use auto mode by default**: Let the system detect the appropriate mode
2. **Keep login in headed mode**: Set `HEADLESS_LOGIN=false` for reliability
3. **Test locally first**: Always login with GUI locally before deploying headless
4. **Use proper flags**: The built-in flags are optimized for stability
5. **Monitor memory**: Headless Chrome needs ~500MB+ RAM
6. **Install dependencies**: Run Playwright dependency installer on new systems

## Related Files

- `/tiktok_uploader/Browser.py` - Browser initialization with headless logic
- `/tiktok_uploader/Config.py` - Configuration management
- `/tiktok_uploader/tiktok.py` - Login and upload functions
- `/.env` - Environment variables
- `/config.txt` - Config file
- `/test_headless.py` - Headless configuration tests
- `/test_integration.py` - Integration tests with signature generation
