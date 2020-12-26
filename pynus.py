import sys
from getpass import getpass
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from time import sleep

INDEX = 'https://binusmaya.binus.ac.id/newStudent/#/index'
LOGIN = 'https://binusmaya.binus.ac.id/login/'
FORUM = 'https://binusmaya.binus.ac.id/newStudent/#/forum/class'

options = Options()
# options.headless = True
browser = webdriver.Firefox(options=options)


def finish():
    browser.quit()
    sys.exit(0)


browser.get(LOGIN)
sleep(3)

currentUrl = browser.current_url
if currentUrl != LOGIN:
    print("Binusmaya is currently unreachable")
    sys.exit(0)

username = input("Username: ")
password = getpass()

xpaths = {
    'userID': '//*[@id="login"]/form/div/label/input',
    'pass': '//*[@id="login"]/form/p[1]/span/input',
    'submit': '//*[@id="login"]/form/p[4]/input'
}

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
numCourses = len(Select(browser.find_element_by_id('ddlCourse')).options)

notReplied = []

for i in range(numCourses):
    courses = Select(browser.find_element_by_id('ddlCourse'))
    courses.select_by_visible_text(courses.options[i].text)
    sleep(2)
    numClasses = len(Select(browser.find_element_by_id('ddlClass')).options)
    for j in range(numClasses):
        courses = Select(browser.find_element_by_id('ddlCourse'))
        courses.select_by_visible_text(courses.options[i].text)
        sleep(2)
        classes = Select(browser.find_element_by_id('ddlClass'))
        classes.select_by_visible_text(classes.options[j].text)
        sleep(10)
        topics = Select(browser.find_element_by_id('ddlTopic'))
        print(f"Selecting {topics.options[-1].text} from {courses.options[i].text}.")
        topics.select_by_visible_text(topics.options[-1].text)
        sleep(30)
        table = browser.find_element_by_id('threadtable')
        links = [str(title.get_attribute('href')) for title in table.find_elements_by_tag_name('a')][:-1]
        for link in links:
            print(f"Currently checking: {link}")
            browser.get(link)
            browser.refresh()
            sleep(10)
            names = browser.find_elements_by_class_name('iUserName')
            if student_name not in [name.text for name in names]:
                notReplied.append(link)

        browser.get(FORUM)
        sleep(3)

print(notReplied)
finish()
