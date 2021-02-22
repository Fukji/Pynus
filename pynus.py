import argparse
import csv
import re
import pyderman
import sys
import traceback
from datetime import datetime, timedelta
from getpass import getpass
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException
)
from selenium.webdriver.chrome.options import Options as copt
from selenium.webdriver.firefox.options import Options as fopt
from selenium.webdriver.support.ui import Select, WebDriverWait
from time import sleep, time

VERSION = 'v0.2.0'
BUILD = '22022021'

INDEX = 'https://binusmaya.binus.ac.id/newStudent/'
LOGIN = 'https://binusmaya.binus.ac.id/login/'
FORUM = 'https://binusmaya.binus.ac.id/newStudent/#/forum/class'
MYCLASS_INDEX = 'https://myclass.apps.binus.ac.id/Home/Index'
MYCLASS_LOGIN = 'https://myclass.apps.binus.ac.id/Auth'
XPATHS = {
    'userID': '//*[@id="login"]/form/div/label/input',
    'pass': '//*[@id="login"]/form/p[1]/span/input',
    'submit': '//*[@id="login"]/form/p[4]/input',
    'threadtitle': '(//*[@class="iPostSubject"])[2]',
    'threaddate': '(//*[@class="iPostDate"])[2]',
    'submit_myclass': '//*[@id="login"]/form/p[4]/button'
}

browser = None
timeout = 75
debug = False
limit = 7

already_replied = []
not_replied = []
newly_replied = []
links = []


# Stop the browser and terminate the program
def terminate():
    browser.quit()
    sys.exit(0)


# Check for positive integer in argument
def positive_int(value):
    try:
        value = int(value)
        if value <= 0:
            raise argparse.ArgumentTypeError(
                '%s is an invalid positive int value' % value)
        else:
            return value

    except ValueError:
        raise argparse.ArgumentTypeError(
            '%s is an invalid positive int value' % value)


# Setup webdriver browser based on argument value
def setup_browser(browser_name):
    global browser
    if browser_name == 'chrome':
        options = copt()
        prefs = {'profile.default_content_setting_values': {
                 'images': 2, 'plugins': 2, 'popups': 2, 'geolocation': 2,
                 'notifications': 2, 'auto_select_certificate': 2,
                 'fullscreen': 2, 'mouselock': 2, 'mixed_script': 2,
                 'media_stream': 2, 'media_stream_mic': 2,
                 'media_stream_camera': 2, 'protocol_handlers': 2,
                 'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2,
                 'push_messaging': 2, 'ssl_cert_decisions': 2,
                 'metro_switch_to_desktop': 2, 'protected_media_identifier': 2,
                 'app_banner': 2, 'site_engagement': 2, 'durable_storage': 2}}
        options.add_experimental_option('prefs', prefs)
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--use-fake-ui-for-media-stream")
        options.add_argument("user-data-dir=./profile/Pynus-chrome")
        options.add_argument("profile-directory=Profile 1")
        options.add_argument('--headless')
        options.add_argument('--log-level=3')
        path = pyderman.install(browser=pyderman.chrome, verbose=False,
                                chmod=True, overwrite=False, version=None,
                                filename=None, return_info=False)
        browser = webdriver.Chrome(executable_path=path, options=options)
    elif browser_name == 'firefox':
        options = fopt()
        options.add_argument('--headless')
        path = pyderman.install(browser=pyderman.firefox, verbose=False,
                                chmod=True, overwrite=False, version=None,
                                filename=None, return_info=False)
        profile = webdriver.FirefoxProfile('./profile/zxqcqwmr.Pynus-firefox')
        browser = webdriver.Firefox(executable_path=path, options=options,
                                    firefox_profile=profile)


# Alert the user regarding bad connection
def slow_connection():
    print('Your connection to Binusmaya is currently unstable')
    terminate()


# Wait for an element to load based on the class name
def load_by_class(class_name):
    sleep(1)
    try:
        WebDriverWait(browser, timeout=timeout).until(
            lambda f: f.find_element_by_class_name(class_name).text != '')
    except TimeoutException:
        slow_connection()
    except StaleElementReferenceException:
        load_by_class(class_name)
    sleep(1)


def load_by_id(idx):
    sleep(1)
    try:
        WebDriverWait(browser, timeout=timeout).until(
            lambda f: f.find_element_by_id(idx).text != '')
    except TimeoutException:
        slow_connection()
    except StaleElementReferenceException:
        load_by_id(idx)
    sleep(1)


# Wait for the home page to load
def load_homepage():
    sleep(1)
    try:
        WebDriverWait(browser, timeout=timeout).until(
            lambda f: f.find_element_by_css_selector(
                '#login_error, .aUsername'))
    except TimeoutException:
        slow_connection()
    sleep(1)


# Wait for dropdown menu to load based on the id
def load_dropdown(idx):
    sleep(1)
    try:
        WebDriverWait(browser, timeout=timeout).until(
            lambda f: len(Select(browser.find_element_by_id(idx)).options) > 0)
    except TimeoutException:
        slow_connection()
    sleep(1)


# Wait for forum threads to load
def load_thread(xpath, iteration=1):
    if iteration == 3:
        return False

    sleep(1)
    try:
        WebDriverWait(browser, timeout=timeout).until(
            lambda f: f.find_element_by_xpath(xpath).text != '')
    except TimeoutException:
        browser.refresh()
        return load_thread(xpath, iteration + 1)

    return True


def check_link():
    # Open the login page
    browser.get(LOGIN)
    load_by_class('email-suffix')

    # Prompt user for login info and try to login
    while True:
        username = input('Username: ').lower()
        password = getpass()

        if username == "" or password == "":
            print('Username/password must not be blank\n')
            continue

        browser.find_element_by_xpath(XPATHS['userID']).clear()
        browser.find_element_by_xpath(XPATHS['pass']).clear()

        browser.find_element_by_xpath(XPATHS['userID']).send_keys(username)
        browser.find_element_by_xpath(XPATHS['pass']).send_keys(password)
        browser.find_element_by_xpath(XPATHS['submit']).click()

        password = ''
        load_homepage()
        currentUrl = browser.current_url
        if re.match('^' + INDEX, currentUrl):
            break

        username_field = browser.find_element_by_xpath(
            XPATHS['userID']).get_attribute('value')

        if username_field == "":
            print('Your username/password is incorrect!\n')
        else:
            slow_connection()

    start_time = time()

    # Open the forum page
    browser.get(FORUM)
    browser.refresh()
    load_by_class('tabledata')

    # Welcome the user
    student_name = browser.find_element_by_class_name('aUsername').text
    print('\n', f'Welcome, {student_name}.', sep='')

    # Get the user's courses
    courses = Select(browser.find_element_by_id('ddlCourse'))

    # Create the file pynus_data.csv
    pynus_data = open('pynus_data.csv', 'a')
    pynus_data.close()
    # Read the content of pynus_data.csv
    with open('pynus_data.csv', 'r') as pynus_data:
        reader = csv.reader(pynus_data)
        for row in reader:
            if row[0] == username:
                already_replied.append(row[1])

    # Fetch the links of the threads
    for my_course in courses.options:
        courses.select_by_visible_text(my_course.text)
        load_dropdown('ddlClass')

        classes = Select(browser.find_element_by_id('ddlClass'))
        for my_class in classes.options:
            classes.select_by_visible_text(my_class.text)

            load_dropdown('ddlTopic')
            load_by_class('tabledata')

            topics = Select(browser.find_element_by_id('ddlTopic'))
            topics.select_by_visible_text(topics.options[-1].text)

            load_by_class('tabledata')

            table = browser.find_element_by_id('threadtable')
            threads = [[my_course.text, my_class.text,
                       str(title.get_attribute('href'))]
                       for title in table.find_elements_by_tag_name('a')][:-1]
            links.extend(threads)

            if debug:
                print(f'Checking {my_course.text} - {my_class.text}.',
                      f'Found {len(threads)} links,',
                      f'for a total of {len(links)}.')

    if debug:
        print(f'Link scraping finished in: {time()-start_time} seconds.')

    # Check for unreplied forum threads
    for link in links:
        if link[2] in already_replied:
            continue
        browser.get(link[2])
        browser.refresh()

        if load_thread(XPATHS['threadtitle']) is False:
            not_replied.append({
                'course': link[0] + ' - ' + link[1],
                'source': link[2],
                'status': 'unchecked'
            })
            continue

        title = browser.find_element_by_xpath(XPATHS['threadtitle']).text
        posted = browser.find_element_by_xpath(XPATHS['threaddate']).text
        names = browser.find_elements_by_class_name('iUserName')

        # Try to find a reply button in the thread
        try:
            replyButton = browser.find_element_by_class_name('reply')
        except NoSuchElementException:
            replyButton = None

        if student_name in [name.text for name in names] or \
           replyButton is None:
            newly_replied.append((username, link[2]))
        else:
            not_replied.append({
                'title': title,
                'course': link[0] + ' - ' + link[1],
                'posted': posted,
                'source': link[2],
                'status': 'unreplied'
            })

    if debug:
        print(f'Process finished in {time()-start_time} seconds.')


def logout():
    browser.find_element_by_class_name('expand-action').click()
    sleep(1)
    browser.find_element_by_id('logout').click()


def countdown(time_left):
    while time_left:
        print('Your class is starting in',
              f'{str(timedelta(seconds=time_left))}', end='\r')
        sleep(1)
        time_left -= 1
    print('Your class is starting now. Joining the Zoom meeting...')


def fetch_meetings(username, password):
    browser.get(MYCLASS_LOGIN)
    load_by_class('email-suffix')

    browser.find_element_by_xpath(XPATHS['userID']).send_keys(username)
    browser.find_element_by_xpath(XPATHS['pass']).send_keys(password)
    browser.find_element_by_xpath(XPATHS['submit_myclass']).click()

    load_by_id('studentViconList')
    classes = browser.find_element_by_id('studentViconList')

    meeting_date = [str(date.text) for date
                    in classes.find_elements_by_class_name('iDate')[1:]]
    meeting_time = [re.findall('[0-9][0-9]:[0-9][0-9]:[0-9][0-9]',
                    time.text) for time
                    in classes.find_elements_by_class_name('iTime')[1:]]
    meeting_link = classes.find_elements_by_class_name('iAction')[1:]

    meetings = []
    for i in range(len(meeting_link)):
        if meeting_link[i].text != '-':
            continue
        time = datetime.strptime(meeting_date[i] + ' ' + meeting_time[i][0],
                                 '%d %b %Y %H:%M:%S') + timedelta(minutes=-10)
        endtime = datetime.strptime(meeting_date[i] + ' ' + meeting_time[i][1],
                                    '%d %b %Y %H:%M:%S')
        link = str(meeting_link[i].find_element_by_tag_name(
                   'a').get_attribute('href'))
        meetings.append([time, endtime, link])

    logout()
    return meetings


def join_meeting(meeting):
    if meeting[0] < datetime.now():
        wait_time = 0
    else:
        wait_time = (meeting[0] - datetime.now().replace(
                     microsecond=0)).total_seconds()

    countdown(wait_time)
    browser.get(meeting[2])

    wait_time = (meeting[1] - datetime.now()).total_seconds()
    sleep(wait_time)
    sleep(60)


def class_standy():
    browser.get(MYCLASS_LOGIN)
    load_by_class('email-suffix')

    # Prompt user for login info and try to login
    while True:
        username = input('Username: ').lower()
        password = getpass()

        if username == "" or password == "":
            print('Username/password must not be blank\n')
            continue

        browser.find_element_by_xpath(XPATHS['userID']).clear()
        browser.find_element_by_xpath(XPATHS['pass']).clear()

        browser.find_element_by_xpath(XPATHS['userID']).send_keys(username)
        browser.find_element_by_xpath(XPATHS['pass']).send_keys(password)
        browser.find_element_by_xpath(XPATHS['submit_myclass']).click()

        load_homepage()
        currentUrl = browser.current_url
        if re.match('^' + MYCLASS_INDEX, currentUrl):
            break

        login_error = browser.find_element_by_id('login_error')

        print(login_error.text)

        if login_error.text != "":
            print('Your username/password is incorrect!\n')
        else:
            slow_connection()

    logout()

    start = time()
    meetings = fetch_meetings(username, password)

    if debug:
        for start_time, end_time, link in meetings:
            print(start_time, end_time, link)

    while True:
        if len(meetings) == 0 and time() - start >= 5400:
            meetings = fetch_meetings(username, password)
            start = time()
        elif len(meetings) > 0:
            join_meeting(meetings[0])
            meetings = fetch_meetings(username, password)


# Print unreplied/unchecked threads
def print_thread_list():
    time_limit = (datetime.now() - timedelta(days=limit)).date()
    printed = False

    for unreplied in not_replied:
        if unreplied['status'] == 'unchecked':
            printed = True
            print('\n', f'Course: {unreplied["course"]}', sep='')
            print(f'Source: {unreplied["source"]}')
            print(f'Status: {unreplied["status"]}')
        else:
            time_posted = datetime.strptime(
                unreplied['posted'], '%d/%m/%Y %H:%M').date()
            if time_posted >= time_limit:
                printed = True
                print('\n', f'{unreplied["title"]}', sep='')
                print(f'Course: {unreplied["course"]}')
                print(f'Posted: {unreplied["posted"]}')
                print(f'Source: {unreplied["source"]}')
                print(f'Status: {unreplied["status"]}')

    if printed is False:
        print(f'All threads from the past {limit} days has been replied.')


def main():

    # Parse user inputted arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='enable debug mode',
                        action='store_true')
    parser.add_argument('-b', '--browser', default='chrome',
                        help='select custom browser')
    parser.add_argument('-l', '--limit', default=7, type=positive_int,
                        help='limit output')
    parser.add_argument('-t', '--timeout', default=75, type=positive_int,
                        help='set custom timeout')
    parser.add_argument('-m', '--mode', default='forum',
                        help='choose mode')
    args = parser.parse_args()

    # Change global variable based on argument value
    global timeout, debug, limit
    timeout = args.timeout
    debug = args.debug
    limit = args.limit

    # Print version info
    if debug:
        print(f'Pynus {VERSION} build {BUILD}')

    # Setup the browser
    if args.browser.lower() == 'chrome':
        setup_browser('chrome')
    elif args.browser.lower() == 'firefox':
        setup_browser('firefox')
    else:
        print('Unrecognized browser, trying to use chrome instead.')
        setup_browser('chrome')

    # Fetch and check the links
    try:
        if args.mode.lower() == 'forum':
            check_link()
        elif args.mode.lower() == 'class':
            class_standy()
        else:
            print('Invalid mode, running in forum checking mode')
            check_link()
    except (KeyboardInterrupt, SystemExit):
        print('\nProcess terminated without error.')
    except TimeoutException:
        slow_connection()
    except:
        if debug:
            traceback.print_exc()
        print('Unexpected error occured:', sys.exc_info()[0])

    # Write user's data to csv file
    if args.mode.lower() == 'forum':
        with open('pynus_data.csv', 'a', newline='') as pynus_data:
            csv.writer(pynus_data).writerows(
                [replied[0], replied[1]] for replied in newly_replied)

        print(f'Checked {len(links)} links.',
              f'Found {len(not_replied)} unreplied/unchecked.')

        print('\n', f'Displaying threads within your time range:', sep='')
        print_thread_list()

    terminate()


if __name__ == '__main__':
    main()
