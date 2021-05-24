import csv
import re
import os
import sys
import threading
from datetime import datetime, timedelta, timezone
from getpass import getpass
from pynus.utils import progress, webbrowser
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from time import time, sleep

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

already_replied = []
not_replied = []
newly_replied = []
links = []


def fetch_links():
    # Get the user's courses
    courses = Select(browser.find_element_by_id('ddlCourse'))

    # Fetch the links of the threads
    for my_course in courses.options:
        courses.select_by_visible_text(my_course.text)
        webbrowser.load_dropdown(browser, 'ddlClass', timeout)

        progress.spinner_text = f'Fetching user\'s class list for {my_course.text}'
        classes = Select(browser.find_element_by_id('ddlClass'))
        for my_class in classes.options:
            classes.select_by_visible_text(my_class.text)

            webbrowser.load_dropdown(browser, 'ddlTopic', timeout)
            webbrowser.load_by_class(browser, 'tabledata', timeout)

            progress.spinner_text = f'Fetching user\'s thread list for {my_course.text} - {my_class.text}'

            topics = Select(browser.find_element_by_id('ddlTopic'))
            topics.select_by_visible_text(topics.options[-1].text)

            webbrowser.load_by_class(browser, 'tabledata', timeout)

            table = browser.find_element_by_id('threadtable')
            threads = [[my_course.text, my_class.text,
                       str(title.get_attribute('href'))]
                       for title in table.find_elements_by_tag_name('a')][:-1]
            links.extend(threads)

            progress.spinner_text = f'Found {len(threads)} thread(s) in {my_course.text} - {my_class.text}'


def check_link(br, args):
    global browser, timeout, debug, limit
    browser = br
    timeout = args.timeout
    debug = args.debug
    limit = args.limit

    # Open the login page
    progress.spinner_continue('Accessing BINUSMAYA')
    browser.get(LOGIN)
    webbrowser.load_by_class(browser, 'email-suffix', timeout)
    progress.spinner_pause()

    # Prompt user for login info and try to login
    while True:
        username = input('Username: ').lower().split('@')[0]
        password = getpass()

        print()
        if username == "" or password == "":
            print('Username/password must not be \033[93mblank\033[0m.')
            sys.exit(0)

        progress.spinner_continue('Logging user in')

        browser.find_element_by_xpath(XPATHS['userID']).clear()
        browser.find_element_by_xpath(XPATHS['pass']).clear()

        browser.find_element_by_xpath(XPATHS['userID']).send_keys(username)
        browser.find_element_by_xpath(XPATHS['pass']).send_keys(password)
        browser.find_element_by_xpath(XPATHS['submit']).click()

        password = ''
        webbrowser.load_homepage(browser, timeout)
        currentUrl = browser.current_url

        progress.spinner_pause()

        if re.match('^' + INDEX, currentUrl):
            break

        username_field = browser.find_element_by_xpath(
            XPATHS['userID']).get_attribute('value')

        if username_field == "":
            print('Your username/password is \033[91mincorrect\033[0m!')
            sys.exit(0)
        else:
            webbrowser.slow_connection(browser)

    start_time = time()

    # Open the forum page
    progress.spinner_continue('Fetching user\'s details')
    browser.get(FORUM)
    browser.refresh()
    webbrowser.load_by_class(browser, 'tabledata', timeout)
    progress.spinner_pause()

    # Welcome the user
    student_name = browser.find_element_by_class_name('aUsername').text
    print(f'Welcome, {student_name}.')

    # Create the file pynus_data.csv
    pynus_data = open('pynus_data.csv', 'a')
    pynus_data.close()
    # Read the content of pynus_data.csv
    with open('pynus_data.csv', 'r') as pynus_data:
        reader = csv.reader(pynus_data)
        for row in reader:
            if row[0] == username:
                already_replied.append(row[1])

    # Fetch forum thread links
    progress.spinner_continue('Fetching user\'s courses list')
    fetch_links()
    fetch_time = time()-start_time

    # Check for unreplied forum threads
    for link in links:
        if link[2] in already_replied:
            continue

        browser.get(link[2])
        browser.refresh()

        if webbrowser.load_thread(browser, XPATHS['threadtitle'],
                                  timeout) is False:
            not_replied.append({
                'course': link[0] + ' - ' + link[1],
                'source': link[2],
                'status': 'unchecked'
            })
            continue

        title = browser.find_element_by_xpath(XPATHS['threadtitle']).text
        posted = browser.find_element_by_xpath(XPATHS['threaddate']).text
        names = browser.find_elements_by_class_name('iUserName')

        progress.spinner_text = f'Checking thread [{title}]'

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

    progress.spinner_pause()

    write_replied()
    print_thread_list()

    if debug:
        print(f'\nFetching threads took {fetch_time} seconds.')
        print(f'Process finished in {time()-start_time} seconds.')

        
# Add newly replied threads to csv
def write_replied():
    with open('pynus_data.csv', 'a', newline='') as pynus_data:
        csv.writer(pynus_data).writerows(
            [replied[0], replied[1]] for replied in newly_replied)


# Print unreplied/unchecked threads
def print_thread_list():
    print(f'Checked {len(links)} thread(s).',
          f'Found {len(not_replied)} \033[91munreplied\033[0m/\033[93munchecked\033[0m.')

    time_limit = (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=limit)).date()
    printed = False

    print('\n', f'Displaying thread(s) within your time range:', sep='')
    for unreplied in not_replied:
        if unreplied['status'] == 'unchecked':
            printed = True
            print('\n', f'Course: {unreplied["course"]}', sep='')
            print(f'Source: {unreplied["source"]}')
            print('Status: \033[93munchecked\033[0m')
        else:
            time_posted = (datetime.strptime(
                unreplied['posted'], '%d/%m/%Y %H:%M') - timedelta(hours=7)).date()
            if time_posted >= time_limit:
                printed = True
                print('\n', f'{unreplied["title"]}', sep='')
                print(f'Course: {unreplied["course"]}')
                print(f'Posted: {unreplied["posted"]}')
                print(f'Source: {unreplied["source"]}')
                print('Status: \033[91munreplied\033[0m')
                    
    if printed is False:
        print(f'All threads from the past {limit} day(s) has been replied.')


if __name__ == '__main__':
    print('Run pynus.py to use Pynus.')
