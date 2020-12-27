import csv
import sys
from getpass import getpass
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from time import sleep

INDEX = 'https://binusmaya.binus.ac.id/newStudent/#/index'
LOGIN = 'https://binusmaya.binus.ac.id/login/'
FORUM = 'https://binusmaya.binus.ac.id/newStudent/#/forum/class'

options = Options()
options.headless = True
browser = webdriver.Firefox(options=options)


def finish():
    browser.quit()
    sys.exit(0)


browser.get(LOGIN)
sleep(3)

username = input("Username: ")
password = getpass()

xpaths = {
    'userID': '//*[@id="login"]/form/div/label/input',
    'pass': '//*[@id="login"]/form/p[1]/span/input',
    'submit': '//*[@id="login"]/form/p[4]/input'
}

try:
    browser.find_element_by_xpath(xpaths['userID'])
except NoSuchElementException:
    print("Binusmaya is currently unreachable")
    finish()

browser.find_element_by_xpath(xpaths['userID']).clear()
browser.find_element_by_xpath(xpaths['userID']).send_keys(username)
browser.find_element_by_xpath(xpaths['pass']).clear()
browser.find_element_by_xpath(xpaths['pass']).send_keys(password)
browser.find_element_by_xpath(xpaths['submit']).click()

sleep(7)
currentUrl = browser.current_url
if currentUrl != INDEX:
    print("Your username/password is incorrect!")
    finish()

student_profile = browser.find_element_by_class_name('user-profile')
student_name = student_profile.find_element_by_class_name('student-name').text
print()
print(f"Welcome, {student_name}.")

browser.get(FORUM)
sleep(3)

alreadyReplied = []
notReplied = []
newlyReplied = []
links = []
courses = Select(browser.find_element_by_id('ddlCourse'))

with open('pynus_data.csv', 'r') as pynus_data:
    reader = csv.reader(pynus_data)
    for row in reader:
        alreadyReplied.append(row[0])

for my_course in courses.options:
    courses.select_by_visible_text(my_course.text)
    sleep(2)
    classes = Select(browser.find_element_by_id('ddlClass'))
    for my_class in classes.options:
        classes.select_by_visible_text(my_class.text)
        sleep(10)
        topics = Select(browser.find_element_by_id('ddlTopic'))
        topics.select_by_visible_text(topics.options[-1].text)
        sleep(30)
        table = browser.find_element_by_id('threadtable')
        threads = [str(title.get_attribute('href'))
                   for title in table.find_elements_by_tag_name('a')][:-1]
        links.extend(threads)

for link in links:
    if link in alreadyReplied:
        continue
    browser.get(link)
    browser.refresh()
    sleep(10)
    names = browser.find_elements_by_class_name('iUserName')
    try:
        replyButton = browser.find_element_by_class_name('reply')
    except NoSuchElementException:
        replyButton = None
    if student_name in [name.text for name in names] or \
       replyButton is None:
        newlyReplied.append(link)
    else:
        notReplied.append(link)

print(notReplied)

with open('pynus_data.csv', 'a') as pynus_data:
    csv.writer(pynus_data).writerows([replied] for replied in newlyReplied)

finish()
