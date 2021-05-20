import os
import sys
import traceback
from pynus.utils import progress
from selenium import webdriver
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException
)
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.chrome.options import Options as copt
from selenium.webdriver.firefox.options import Options as fopt
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from time import sleep


# Stop the browser and terminate the program
def terminate(browser):
    progress.spinner_continue('Terminating all running process')
    if browser is not None:
        browser.quit()
    progress.spinner_stop()
    progress.spinner.join()


# Alert the user regarding bad connection
def slow_connection(browser):
    print('Your connection to BINUSMAYA is currently unstable.')
    sys.exit(0)


# Wait for an element to load based on the class name
def load_by_class(browser, class_name, timeout):
    sleep(1)
    try:
        WebDriverWait(browser, timeout=timeout).until(
            lambda f: f.find_element_by_class_name(class_name).text != '')
    except TimeoutException:
        slow_connection(browser)
    except StaleElementReferenceException:
        load_by_class(browser, class_name, timeout)
    sleep(1)


def load_by_id(browser, idx, timeout):
    sleep(1)
    try:
        WebDriverWait(browser, timeout=timeout).until(
            lambda f: f.find_element_by_id(idx).text != '')
    except TimeoutException:
        slow_connection(browser)
    except StaleElementReferenceException:
        load_by_id(browser, idx, timeout)
    sleep(1)


# Wait for the home page to load
def load_homepage(browser, timeout):
    sleep(1)
    try:
        WebDriverWait(browser, timeout=timeout).until(
            lambda f: f.find_element_by_css_selector(
                '#login_error, .aUsername'))
    except TimeoutException:
        slow_connection(browser)
    sleep(1)


# Wait for dropdown menu to load based on the id
def load_dropdown(browser, idx, timeout):
    sleep(1)
    try:
        WebDriverWait(browser, timeout=timeout).until(
            lambda f: len(Select(browser.find_element_by_id(idx)).options) > 0)
    except TimeoutException:
        slow_connection(browser)
    sleep(1)


# Wait for forum threads to load
def load_thread(browser, xpath, timeout, iteration=1):
    if iteration == 3:
        return False

    sleep(1)
    try:
        WebDriverWait(browser, timeout=timeout).until(
            lambda f: f.find_element_by_xpath(xpath).text != '')
    except TimeoutException:
        browser.refresh()
        return load_thread(browser, xpath, timeout, iteration + 1)

    return True


# Setup webdriver browser based on argument value
def setup_browser(browser_name, debug=False, headless=True):
    os.environ['WDM_LOG_LEVEL'] = '0'
    directory = os.path.dirname(os.path.realpath(__file__))

    try:
        if browser_name == 'chrome':
            profile_path = os.path.abspath(os.path.join(directory, os.pardir,
                                                        'profile',
                                                        'chrome'))
            options = copt()
            prefs = {'profile.default_content_setting_values': {
                     'images': 2, 'plugins': 2, 'popups': 2, 'geolocation': 2,
                     'notifications': 2, 'auto_select_certificate': 2,
                     'fullscreen': 2, 'mouselock': 2, 'mixed_script': 2,
                     'media_stream': 2, 'media_stream_mic': 2,
                     'media_stream_camera': 2, 'protocol_handlers': 2,
                     'ppapi_broker': 2, 'automatic_downloads': 2,
                     'midi_sysex': 2, 'push_messaging': 2,
                     'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2,
                     'protected_media_identifier': 2, 'app_banner': 2,
                     'site_engagement': 2, 'durable_storage': 2},
                     'protocol_handler': {
                        'allowed_origin_protocol_pairs': {
                            'https://binus.zoom.us': {'zoommtg':True}
                    }}}
            options.add_experimental_option('prefs', prefs)
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_argument('disable-infobars')
            options.add_argument('--disable-extensions')
            options.add_argument('--use-fake-ui-for-media-stream')
            options.add_argument('--user-data-dir=' + profile_path)
            if headless:
                options.add_argument('--headless')
            options.add_argument('--log-level=3')
            path = ChromeDriverManager().install()
            browser = webdriver.Chrome(executable_path=path, options=options)
            browser.set_window_position(-10000, 0)

        elif browser_name == 'msedge':
            try:
                from msedge.selenium_tools import EdgeOptions as eopt
                from msedge.selenium_tools import Edge
            except ModuleNotFoundError:
                progress.spinner_pause()
                print('Install msedge-selenium-tools using pip to use Microsoft Edge browser.')
                sys.exit(0)

            profile_path = os.path.abspath(os.path.join(directory, os.pardir, 
                                                        'profile', 'edge'))

            options = eopt()
            options.use_chromium = True
            prefs = {'profile.default_content_setting_values': {
                     'images': 2, 'plugins': 2, 'popups': 2, 'geolocation': 2,
                     'notifications': 2, 'auto_select_certificate': 2,
                     'fullscreen': 2, 'mouselock': 2, 'mixed_script': 2,
                     'media_stream': 2, 'media_stream_mic': 2,
                     'media_stream_camera': 2, 'protocol_handlers': 2,
                     'ppapi_broker': 2, 'automatic_downloads': 2,
                     'midi_sysex': 2, 'push_messaging': 2,
                     'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2,
                     'protected_media_identifier': 2, 'app_banner': 2,
                     'site_engagement': 2, 'durable_storage': 2,
                     'do_not_create_desktop_shortcut': True},
                     'protocol_handler': {
                        'allowed_origin_protocol_pairs': {
                            'https://binus.zoom.us': {'zoommtg':True}
                    }}}
            options.add_experimental_option('prefs', prefs)
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_argument('disable-infobars')
            options.add_argument('--disable-extensions')
            options.add_argument('--use-fake-ui-for-media-stream')
            options.add_argument('--user-data-dir=' + profile_path)
            if headless:
                options.add_argument('--headless')
            options.add_argument('--log-level=3')
            path = EdgeChromiumDriverManager().install()
            browser = Edge(executable_path=path, options=options)
            browser.set_window_position(-10000, 0)

        elif browser_name == 'firefox':
            profile_path = os.path.abspath(os.path.join(directory, os.pardir,
                                                        'profile',
                                                        'firefox'))
            options = fopt()
            if headless:
                options.add_argument('--headless')
            path = GeckoDriverManager().install()
            profile = webdriver.FirefoxProfile(profile_path)
            browser = webdriver.Firefox(executable_path=path, options=options,
                                        firefox_profile=profile)
    except ValueError:
        progress.spinner_pause()
        print('This browser is currently not supported on your OS.')
        if debug:
            traceback.print_exc()
        sys.exit(0)

    return browser


if __name__ == '__main__':
    print('Run pynus.py to use Pynus.')
