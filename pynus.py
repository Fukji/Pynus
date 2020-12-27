import csv
import sys
from getpass import getpass
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.firefox.options import Options
from time import sleep, time

TIMEOUT = 75
INDEX = 'https://binusmaya.binus.ac.id/newStudent/#/index'
LOGIN = 'https://binusmaya.binus.ac.id/login/'
FORUM = 'https://binusmaya.binus.ac.id/newStudent/#/forum/class'
XPATHS = {
    'userID': '//*[@id="login"]/form/div/label/input',
    'pass': '//*[@id="login"]/form/p[1]/span/input',
    'submit': '//*[@id="login"]/form/p[4]/input',
    'threadtitle': '(//*[@class="iPostSubject"])[2]'
}

options = Options()
# options.headless = True
browser = webdriver.Firefox(options=options)

already_replied = []
not_replied = []
newly_replied = []
unchecked = []
links = []

def terminate():
    browser.quit()
    sys.exit(0)


def slowConnection():
    print('Your internet connection is currently unstable')
    terminate()


def loadClass(class_name):
    sleep(1)
    try:
        WebDriverWait(browser, timeout=TIMEOUT).until(
            lambda f: f.find_element_by_class_name(class_name).text != '')
    except TimeoutException:
        slowConnection()


def loadThread(xpath, iteration = 1):
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
    browser.get(LOGIN)
    sleep(3)

    try:
        browser.find_element_by_xpath(XPATHS['userID'])
    except NoSuchElementException:
        print('Binusmaya is currently unreachable')
        terminate()

    while True:
        username = input('Username: ')
        password = getpass()

        browser.find_element_by_xpath(XPATHS['userID']).clear()
        browser.find_element_by_xpath(XPATHS['userID']).send_keys(username)
        browser.find_element_by_xpath(XPATHS['pass']).clear()
        browser.find_element_by_xpath(XPATHS['pass']).send_keys(password)
        browser.find_element_by_xpath(XPATHS['submit']).click()

        sleep(7)
        currentUrl = browser.current_url
        if currentUrl != INDEX:
            try:
                browser.find_element_by_xpath(XPATHS['userID'])
            except NoSuchElementException:
                slowConnection()
            print('Your username/password is incorrect!\n')
        else:
            break

    loadClass('user-profile')
    student_profile = browser.find_element_by_class_name('user-profile')
    student_name = student_profile.find_element_by_class_name(
        'student-name').text
    print()
    print(f'Welcome, {student_name}.')

    browser.get(FORUM)
    browser.refresh()
    loadClass('tabledata')

    courses = Select(browser.find_element_by_id('ddlCourse'))

    pynus_data = open('pynus_data.csv', 'a')
    pynus_data.close()
    with open('pynus_data.csv', 'r') as pynus_data:
        reader = csv.reader(pynus_data)
        for row in reader:
            already_replied.append(row[0])

    for my_course in courses.options:
        courses.select_by_visible_text(my_course.text)
        sleep(2.5)
        classes = Select(browser.find_element_by_id('ddlClass'))
        for my_class in classes.options:
            classes.select_by_visible_text(my_class.text)

            loadClass('tabledata')

            topics = Select(browser.find_element_by_id('ddlTopic'))
            topics.select_by_visible_text(topics.options[-1].text)

            loadClass('tabledata')

            table = browser.find_element_by_id('threadtable')
            threads = [str(title.get_attribute('href'))
                       for title in table.find_elements_by_tag_name('a')][:-1]
            links.extend(threads)

    for link in links:
        if link in already_replied:
            continue
        browser.get(link)
        browser.refresh()

        if loadThread(XPATHS['threadtitle']) is False:
            unchecked.append(link)
            continue

        names = browser.find_elements_by_class_name('iUserName')

        try:
            replyButton = browser.find_element_by_class_name('reply')
        except NoSuchElementException:
            replyButton = None

        if student_name in [name.text for name in names] or \
           replyButton is None:
            newly_replied.append(link)
        else:
            not_replied.append(link)


if __name__ == '__main__':
    start_time = time()

    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print('Process terminated without error.')
    except:
        print('Unexpected error:', sys.exc_info()[0])

    with open('pynus_data.csv', 'a') as pynus_data:
        csv.writer(pynus_data).writerows(
            [replied] for replied in newly_replied)

    print(f'Checked {len(links)} links. Found',
          f'{len(not_replied)} unreplied',
          f'and {len(unchecked)} unchecked')

    print('UNREPLIED')
    for unreplied in not_replied:
        print(unreplied)

    print('UNCHECKED')
    for not_checked in unchecked:
        print(not_checked)

    print(f'Process finished in {time()-start_time} seconds.')
    terminate()


