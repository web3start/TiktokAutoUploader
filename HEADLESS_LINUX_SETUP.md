# Headless Linux Setup Guide

This document describes the changes made to support video uploads on headless Ubuntu systems (both ARM and AMD/x86_64) and provides setup instructions.

## Problem Description

Previously, video uploads would hang indefinitely at "Uploading video..." on headless Linux environments without a GUI. The root causes were:

1. **Missing browser flags**: Neither `undetected-chromedriver` nor Playwright were configured with the necessary flags for headless Linux environments
2. **Silent failures**: The Node.js subprocess that generates signatures didn't capture stderr or implement timeouts, causing silent hangs
3. **Missing dependencies**: System libraries required by Chromium weren't documented

## Changes Made

### 1. Browser Configuration (`tiktok_uploader/Browser.py`)

Added automatic detection of headless Linux environments and configuration of appropriate Chrome flags:

- `--headless=new`: Modern headless mode
- `--no-sandbox`: Required for running Chrome in containers/restricted environments
- `--disable-dev-shm-usage`: Prevents crashes due to limited shared memory in Docker/containers
- `--disable-gpu`: Disables GPU hardware acceleration (not available in headless)
- `--disable-software-rasterizer`: Prevents software rendering issues
- `--disable-extensions`: Reduces overhead
- `--disable-setuid-sandbox`: Alternative sandbox mode for restricted environments

### 2. Playwright Configuration (`tiktok_uploader/tiktok-signature/index.js`)

Added the same critical flags to the Playwright Chromium browser launch options to ensure it works in headless environments.

### 3. Subprocess Error Handling (`tiktok_uploader/bot_utils.py`)

Enhanced the `subprocess_jsvmp` function with:

- **Timeout**: 60-second timeout prevents indefinite hangs
- **stderr capture**: Error messages from Node.js are now visible
- **Exit code checking**: Detects when the signature generator fails
- **Informative error messages**: Clear feedback about what went wrong
- **Exception handling**: Handles missing Node.js, timeouts, and other errors gracefully

### 4. Error Messaging (`tiktok_uploader/tiktok-signature/browser.js`)

Added explicit error logging and proper exit codes when signature generation fails.

## System Requirements

### Required Software

1. **Node.js** (v14 or higher)
   ```bash
   node --version
   ```

2. **Python 3** (3.8 or higher)
   ```bash
   python3 --version
   ```

### Required System Libraries (Ubuntu/Debian)

For Playwright to work in headless mode, you need to install system dependencies:

```bash
# Option 1: Using Playwright's installer (recommended)
cd tiktok_uploader/tiktok-signature
sudo npx playwright install-deps chromium

# Option 2: Manual installation via apt
sudo apt-get install \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libdrm2 \
    libxkbcommon0 \
    libasound2
```

### Install Playwright Browsers

```bash
cd tiktok_uploader/tiktok-signature
npx playwright install chromium
```

## Architecture Notes

### ARM64 Support

Playwright officially supports ARM64 architecture. The flags added (`--no-sandbox`, `--disable-dev-shm-usage`, etc.) are particularly important on ARM systems where security restrictions may be tighter.

### Docker/Container Support

The changes specifically enable running in Docker containers and other restricted environments where:
- No X11 display is available (`DISPLAY` environment variable is not set)
- `/dev/shm` (shared memory) is limited
- Sandboxing may not work as expected

## Testing

A test script is provided to validate your setup:

```bash
python3 test_headless.py
```

This will check:
- Browser configuration for headless mode
- Node.js availability
- Signature generation with proper error handling

## Troubleshooting

### "Node.js signature generator timed out"

**Cause**: Playwright browser failed to start or is hanging

**Solutions**:
1. Install system dependencies (see above)
2. Check available memory (Chromium needs ~500MB)
3. Verify Playwright browsers are installed: `npx playwright install chromium`

### "Node.js not found"

**Cause**: Node.js is not installed or not in PATH

**Solution**: Install Node.js:
```bash
# Ubuntu/Debian
sudo apt-get install nodejs npm

# Or use NVM for version management
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install --lts
```

### "Host system is missing dependencies"

**Cause**: Required system libraries for Chromium are not installed

**Solution**: Run the dependency installer:
```bash
cd tiktok_uploader/tiktok-signature
sudo npx playwright install-deps chromium
```

### Memory Issues in Containers

If running in a container with limited memory, you may need to:

1. Increase container memory limit
2. Adjust shared memory size: `docker run --shm-size=2gb ...`
3. Set memory limits in Chrome: `--disable-dev-shm-usage` (already included)

## Environment Detection

The code automatically detects headless environments by checking:

```python
is_linux = sys.platform.startswith('linux')
is_headless = is_linux and not os.environ.get('DISPLAY')
```

You can force GUI mode by setting the `DISPLAY` environment variable (even to a dummy value), though this requires an X server or Xvfb to actually work.

## Compatibility

These changes maintain backward compatibility:

- **Windows**: Works as before (no headless flags added)
- **macOS**: Works as before (no headless flags added)
- **Linux with GUI**: Works as before (headless flags only added when `DISPLAY` is not set)
- **Linux headless**: Now works correctly with proper configuration

## Performance

Headless mode with the new flags typically:
- Starts faster than GUI mode (no window creation)
- Uses less memory (~100-200MB savings)
- Is equally reliable for automation tasks
