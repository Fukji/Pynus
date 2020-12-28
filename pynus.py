import argparse
import csv
import re
import sys
import traceback
from getpass import getpass
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options as copt
from selenium.webdriver.firefox.options import Options as fopt
from selenium.webdriver.support.ui import Select, WebDriverWait
from time import sleep, time

TIMEOUT = 75
INDEX = 'https://binusmaya.binus.ac.id/newStudent/'
LOGIN = 'https://binusmaya.binus.ac.id/login/'
FORUM = 'https://binusmaya.binus.ac.id/newStudent/#/forum/class'
XPATHS = {
    'userID': '//*[@id="login"]/form/div/label/input',
    'pass': '//*[@id="login"]/form/p[1]/span/input',
    'submit': '//*[@id="login"]/form/p[4]/input',
    'threadtitle': '(//*[@class="iPostSubject"])[2]'
}

already_replied = []
not_replied = []
newly_replied = []
links = []


# Stop the browser and terminate the program
def terminate():
    browser.quit()
    sys.exit(0)


# Alert the user regarding bad connection
def slowConnection():
    print('Your connection to Binusmaya is currently unstable')
    terminate()


# Wait for an element to load based on the class name
def load_by_class(class_name):
    sleep(1.5)
    try:
        WebDriverWait(browser, timeout=TIMEOUT).until(
            lambda f: f.find_element_by_class_name(class_name).text != '')
    except TimeoutException:
        slowConnection()
    sleep(1.5)


# Wait for the home page to load
def loadHomepage():
    sleep(1)
    try:
        WebDriverWait(browser, timeout=TIMEOUT).until(
            lambda f: f.find_element_by_css_selector(
                '#login_error, .aUsername'))
    except TimeoutException:
        slowConnection()
    sleep(1)


# Wait for dropdown menu to load based on the id
def loadDropdown(id):
    sleep(1)
    try:
        WebDriverWait(browser, timeout=TIMEOUT).until(
            lambda f: len(Select(browser.find_element_by_id(id)).options) > 0)
    except TimeoutException:
        slowConnection()
    sleep(1)


# Wait for forum threads to load
def loadThread(xpath, iteration=1):
    if iteration == 3:
        return False
    sleep(1)
    try:
        WebDriverWait(browser, timeout=TIMEOUT).until(
            lambda f: f.find_element_by_xpath(xpath).text != '')
    except TimeoutException:
        browser.refresh()
        return loadThread(xpath, iteration + 1)
    return True


def main():
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

        loadHomepage()
        currentUrl = browser.current_url
        if re.match('^' + INDEX, currentUrl):
            break
        else:
            username_field = browser.find_element_by_xpath(
                XPATHS['userID']).get_attribute('value')

            if username_field == "":
                print('Your username/password is incorrect!\n')
            else:
                slowConnection()

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
        loadDropdown('ddlClass')

        classes = Select(browser.find_element_by_id('ddlClass'))
        for my_class in classes.options:
            classes.select_by_visible_text(my_class.text)

            load_by_class('tabledata')

            topics = Select(browser.find_element_by_id('ddlTopic'))
            topics.select_by_visible_text(topics.options[-1].text)

            load_by_class('tabledata')

            table = browser.find_element_by_id('threadtable')
            threads = [str(title.get_attribute('href'))
                       for title in table.find_elements_by_tag_name('a')][:-1]
            links.extend(threads)

            if args.debug:
                print(f'Checking {my_course.text} - {my_class.text}.',
                      f'Found {len(threads)} links,',
                      f'for a total of {len(links)}.')

    # Check for unreplied forum threads
    for link in links:
        if link in already_replied:
            continue
        browser.get(link)
        browser.refresh()

        if loadThread(XPATHS['threadtitle']) is False:
            continue

        names = browser.find_elements_by_class_name('iUserName')

        # Try to find a reply button in the thread
        try:
            replyButton = browser.find_element_by_class_name('reply')
        except NoSuchElementException:
            replyButton = None

        if student_name in [name.text for name in names] or \
           replyButton is None:
            newly_replied.append((username, link))
        else:
            not_replied.append(link)

    if args.debug:
        print(f'Process finished in {time()-start_time} seconds.')


if __name__ == '__main__':
    # Parse user inputted arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help='enable debug mode',
                        action='store_true')
    parser.add_argument('-b', '--browser', help='enable custom browser')
    parser.add_argument('-t', '--timeout', help='enable custom timeout')
    args = parser.parse_args()

    if args.timeout:
        TIMEOUT = int(args.timeout)

    # Open the browser
    if args.browser is None or args.browser == "chrome":
        options = copt()
        # options.headless = True
        browser = webdriver.Chrome(options=options)
    elif args.browser == "firefox":
        options = fopt()
        # options.headless = True
        browser = webdriver.Firefox(options=options)

    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print('Process terminated without error.')
    except:
        traceback.print_exc()
        print('Unexpected error:', sys.exc_info()[0])

    with open('pynus_data.csv', 'a') as pynus_data:
        csv.writer(pynus_data).writerows(
            [replied[0], replied[1]] for replied in newly_replied)

    print(f'Checked {len(links)} links. Found',
          f'{len(not_replied)} unreplied')

    print('UNREPLIED')
    for unreplied in not_replied:
        print(unreplied)

    terminate()
