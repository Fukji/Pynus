import re
import os
import sys
from datetime import datetime, timedelta
from getpass import getpass
from pynus.utils import progress, webbrowser
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep, time


MYCLASS_INDEX = 'https://myclass.apps.binus.ac.id/Home/Index'
MYCLASS_LOGIN = 'https://myclass.apps.binus.ac.id/Auth'
XPATHS = {
    'userID': '//*[@id="login"]/form/div/label/input',
    'pass': '//*[@id="login"]/form/p[1]/span/input',
    'submit_myclass': '//*[@id="login"]/form/p[4]/button'
}


def logout():
    menu = browser.find_element_by_class_name('expand-action')
    logout_button = browser.find_element_by_id('logout')
    actions = ActionChains(browser)
    actions.click(menu)
    actions.pause(1)
    actions.click(logout_button)
    actions.perform()


def countdown(meeting):
    if meeting[0] < datetime.now():
        wait_time = 0
    else:
        wait_time = (meeting[0] - datetime.now().replace(
                     microsecond=0)).total_seconds()

    print(f'\n{meeting[3]} - {meeting[4]}')
    print(f'{meeting[2]}')
    MIN_WIDTH = 28
    while wait_time:
        out = '[\033[1m\033[93mNext\033[0m] ' + str(timedelta(seconds=wait_time))
        terminal_width = os.get_terminal_size().columns
        if terminal_width >= MIN_WIDTH:
            print(f'{out: <{MIN_WIDTH}}', end='\r')
        else:
            if len(out) < terminal_width:
                print(f'{out: <{terminal_width}}', end='\r')
            else:
                print(f'{out[:terminal_width-2]}..', end='\r')
        sleep(1)
        wait_time -= 1

    curr_time = datetime.now().strftime('%H:%M:%S')
    text = f'[\033[1m\033[92mOK\033[0m] Joined at {curr_time}'
    print(f'{text: <{MIN_WIDTH}}')


def fetch_meetings(username, password):
    browser.get(MYCLASS_LOGIN)
    webbrowser.load_by_class(browser, 'email-suffix', timeout)

    browser.find_element_by_xpath(XPATHS['userID']).send_keys(username)
    browser.find_element_by_xpath(XPATHS['pass']).send_keys(password)
    browser.find_element_by_xpath(XPATHS['submit_myclass']).click()

    webbrowser.load_by_id(browser, 'studentViconList', timeout)
    classes = browser.find_element_by_id('studentViconList')

    meeting_date = [str(date.text) for date
                    in classes.find_elements_by_class_name('iDate')[1:]]
    meeting_time = [re.findall('[0-9][0-9]:[0-9][0-9]:[0-9][0-9]',
                    time.text) for time
                    in classes.find_elements_by_class_name('iTime')[1:]]
    meeting_link = classes.find_elements_by_class_name('iAction')[1:]
    meeting_course = classes.find_elements_by_class_name('iCourse')[1:]
    meeting_classtype = classes.find_elements_by_class_name('iClass')[1:]

    meetings = []
    for i in range(len(meeting_link)):
        if meeting_link[i].text == '-':
            continue
        time = datetime.strptime(meeting_date[i] + ' ' + meeting_time[i][0],
                                 '%d %b %Y %H:%M:%S') + timedelta(minutes=-10)
        endtime = datetime.strptime(meeting_date[i] + ' ' + meeting_time[i][1],
                                    '%d %b %Y %H:%M:%S')
        link = str(meeting_link[i].find_element_by_tag_name('a')
                   .get_attribute('href'))
        course = meeting_course[i].text
        classtype = meeting_classtype[i].text
        meetings.append([time, endtime, link, course, classtype])

    logout()
    return meetings


def join_meeting(meeting):
    countdown(meeting)
    if browser.name == 'firefox':
        browser.get(meeting[2])
        webbrowser.load_by_class(browser, '_1FvRrPS6', timeout)
        browser.find_element_by_class_name('_1FvRrPS6').click()

    else:
        alt_browser = webbrowser.setup_browser(browser.name, headless=False)
        alt_browser.get(meeting[2])
        webbrowser.load_by_class(alt_browser, '_1FvRrPS6', timeout)
        alt_browser.find_element_by_class_name('_1FvRrPS6').click()
        alt_browser.quit()

    wait_time = (meeting[1] - datetime.now()).total_seconds()
    sleep(wait_time)
    sleep(60)


def standby(br, args):
    global browser, timeout, debug
    browser = br
    timeout = args.timeout
    debug = args.debug

    progress.spinner_continue('Accessing MYCLASS-BINUSMAYA')
    browser.get(MYCLASS_LOGIN)
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
        browser.find_element_by_xpath(XPATHS['submit_myclass']).click()

        webbrowser.load_homepage(browser, timeout)
        currentUrl = browser.current_url

        progress.spinner_pause()

        if re.match('^' + MYCLASS_INDEX, currentUrl):
            break

        login_error = browser.find_element_by_id('login_error')

        if login_error.text != "":
            print('Your username/password is \033[91mincorrect\033[0m!')
            sys.exit(0)
        else:
            slow_connection()

    progress.spinner_continue('Fetching user\'s details')
    student_name = browser.find_element_by_class_name('aUsername').text
    progress.spinner_pause()
    print(f'Welcome, {student_name}.')
    
    progress.spinner_continue('Fetching user\'s upcoming meetings')
    logout()

    start = time()
    meetings = fetch_meetings(username, password)
    progress.spinner_pause()

    if debug:
        print('\nFound links:')
        for meeting in meetings:
            print(f'[{meeting[0]}] {meeting[3]} - {meeting[4]}')
            print(f'{meeting[2]}')

    while True:
        if time() - start >= 5400:
            meetings = fetch_meetings(username, password)
            start = time()
        elif len(meetings) > 0:
            join_meeting(meetings[0])
            meetings = fetch_meetings(username, password)


if __name__ == '__main__':
    print('Run pynus.py to use Pynus.')
