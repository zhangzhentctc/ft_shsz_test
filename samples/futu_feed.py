from selenium import webdriver  #导入Selenium的webdriver
from selenium.webdriver.common.keys import Keys  #导入Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from time import *

link = "https://seed.futunn.com/"
File_Acc = "./acc.txt"

def do_work(acc, passwd):
    #driver = webdriver.PhantomJS()
    driver = webdriver.Chrome()
    driver.get(link)

    login_form = driver.find_element_by_id("loginFormWrapper")

    email = login_form.find_element_by_xpath("//*[@class='ui-input-wrapper ui-content-email']")
    email_input = email.find_element_by_name("email").send_keys(acc)

    passwd = login_form.find_element_by_xpath("//*[@class='ui-input-wrapper']")
    passwd_input = passwd.find_element_by_name("password").send_keys(passwd)

    btn = driver.find_element_by_xpath("//*[@class='ui-submit ui-form-submit']")
    btn.click()

    sleep(5)

    pg_src = driver.page_source
    print(pg_src)
    # title = driver.find_element_by_tag_name("title")
    # print(title.text)

    waterProgress = driver.find_element_by_class_name("waterProgress")
    circle = waterProgress.find_elements_by_tag_name("circle")
    time = float(circle[1].get_attribute('stroke-dasharray'))
    print(time)

    waterCanvas = driver.find_element_by_id("waterCanvas")
    ActionChains(driver).double_click(waterCanvas).perform()
    # print(pg_src)
    driver.close()

    return time


file = open(File_Acc, 'r')
all_line_txt = file.readlines()
acc = all_line_txt[0].strip('\n')
passwd = all_line_txt[1].strip('\n')
while True:
    time = do_work(acc, passwd)
    sleep(2 * 60 * 60 * (time/60) + 60)



exit(0)