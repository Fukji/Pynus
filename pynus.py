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

INDEX = 'https://binusmaya.binus.ac.id/newStudent/'
LOGIN = 'https://binusmaya.binus.ac.id/login/'
FORUM = 'https://binusmaya.binus.ac.id/newStudent/#/forum/class'
XPATHS = {
    'userID': '//*[@id="login"]/form/div/label/input',
    'pass': '//*[@id="login"]/form/p[1]/span/input',
    'submit': '//*[@id="login"]/form/p[4]/input',
    'threadtitle': '(//*[@class="iPostSubject"])[2]',
    'threaddate': '(//*[@class="iPostDate"])[2]'
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
        browser = webdriver.Firefox(executable_path=path, options=options)


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
def load_dropdown(id):
    sleep(1)
    try:
        WebDriverWait(browser, timeout=timeout).until(
            lambda f: len(Select(browser.find_element_by_id(id)).options) > 0)
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


# Print unreplied/unchecked threads
def print_thread_list():
    time_limit = (datetime.now() - timedelta(days=limit)).date()

    for unreplied in not_replied:
        if unreplied['status'] == 'unchecked':
            print('\n', f'Course: {unreplied["course"]}', sep='')
            print(f'Source: {unreplied["source"]}')
            print(f'Status: {unreplied["status"]}')
        else:
            time_posted = datetime.strptime(
                unreplied['posted'], '%d/%m/%Y %H:%M').date()
            if time_posted >= time_limit:
                print('\n', f'{unreplied["title"]}', sep='')
                print(f'Course: {unreplied["course"]}')
                print(f'Posted: {unreplied["posted"]}')
                print(f'Source: {unreplied["source"]}')
                print(f'Status: {unreplied["status"]}')


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
    args = parser.parse_args()

    # Change global variable based on argument value
    global timeout, debug, limit
    timeout = args.timeout
    debug = args.debug
    limit = args.limit

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
        check_link()
    except (KeyboardInterrupt, SystemExit):
        print('Process terminated without error.')
    except:
        if debug:
            traceback.print_exc()
        print('Unexpected error occured:', sys.exc_info()[0])

    # Write user's data to csv file
    with open('pynus_data.csv', 'a', newline='') as pynus_data:
        csv.writer(pynus_data).writerows(
            [replied[0], replied[1]] for replied in newly_replied)

    print(f'Checked {len(links)} links. Found',
          f'{len(not_replied)} unreplied/unchecked')

    print_thread_list()


if __name__ == '__main__':
    main()
