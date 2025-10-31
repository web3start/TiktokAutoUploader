from .cookies import load_cookies_from_file, save_cookies_to_file
from fake_useragent import UserAgent, FakeUserAgentError
import undetected_chromedriver as uc
import threading, os, sys, platform
from dotenv import load_dotenv


load_dotenv()
WITH_PROXIES = False

class Browser:
    __instance = None
    __lock = threading.Lock()

    @staticmethod
    def get(force_headed=False):
        # print("Browser.getBrowser() called")
        if Browser.__instance is None:
            with Browser.__lock:
                if Browser.__instance is None:
                    # print("Creating new browser instance due to no instance found")
                    Browser.__instance = Browser(force_headed=force_headed)
        elif force_headed and hasattr(Browser.__instance, '_is_headless') and Browser.__instance._is_headless:
            # If we need headed mode but current instance is headless, warn user
            print("[WARNING] Browser instance already exists in headless mode, but headed mode requested")
            print("[WARNING] To use headed mode, restart the application or clear the browser instance")
        return Browser.__instance

    def __init__(self, force_headed=False):
        if Browser.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Browser.__instance = self
        self.user_agent = ""
        options = uc.ChromeOptions()
        
        # Determine headless mode based on config/env
        headless_config = os.getenv('HEADLESS', 'auto').lower().strip().strip('"')
        is_headless = self._should_use_headless(headless_config, force_headed)
        self._is_headless = is_headless
        
        if is_headless:
            print("[INFO] Configuring browser for headless mode with anti-detection")
            # Modern headless mode
            options.add_argument('--headless=new')
            
            # Critical flags for Linux/container environments
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-setuid-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
            
            # Anti-detection tweaks
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins-discovery')
            options.add_argument('--disable-infobars')
            
            # Additional stability flags
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--start-maximized')
            
            # Suppress automation indicators
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
        else:
            if force_headed:
                print("[INFO] Forcing headed mode (GUI) for login/cookie generation")
            else:
                print("[INFO] Using default headed browser mode")
        
        # Proxies not supported on login.
        # if WITH_PROXIES:
        #     options.add_argument('--proxy-server={}'.format(PROXIES[0]))
        self._driver = uc.Chrome(options=options)
        self.with_random_user_agent()

    def _should_use_headless(self, headless_config, force_headed):
        """Determine if headless mode should be used based on config and environment"""
        if force_headed:
            return False
        
        if headless_config == 'true':
            return True
        elif headless_config == 'false':
            return False
        else:  # 'auto' or any other value
            # Auto-detect based on Linux and DISPLAY environment variable
            is_linux = sys.platform.startswith('linux')
            has_display = bool(os.environ.get('DISPLAY'))
            return is_linux and not has_display

    def with_random_user_agent(self, fallback=None):
        """Set random user agent.
        NOTE: This could fail with `FakeUserAgentError`.
        Provide `fallback` str to set the user agent to the provided string, in case it fails. 
        If fallback is not provided the exception is re-raised"""

        try:
            self.user_agent = UserAgent().random
        except FakeUserAgentError as e:
            if fallback:
                self.user_agent = fallback
            else:
                raise e

    @property
    def driver(self):
        return self._driver

    def load_cookies_from_file(self, filename):
        cookies = load_cookies_from_file(filename)
        for cookie in cookies:
            self._driver.add_cookie(cookie)
        self._driver.refresh()

    def save_cookies(self, filename: str, cookies:list=None):
        save_cookies_to_file(cookies, filename)


if __name__ == "__main__":
    import os
    # get current relative path of this file.
    print(os.path.dirname(os.path.abspath(__file__)))
