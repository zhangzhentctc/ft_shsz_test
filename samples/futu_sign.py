from selenium import webdriver  #导入Selenium的webdriver
from selenium.webdriver.common.keys import Keys  #导入Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from time import *
from datetime import *

link = "https://www.futunn.com/"
File_Acc = "./acc.txt"

def log(str):
    now_time = datetime.now()
    now_time_str = datetime.strftime(now_time, '%Y-%m-%d %H:%M:%S')
    localtime = now_time_str.split(' ')[1]
    print("[" + localtime + "]" + str)

def do_work(acc, passwd):
    #driver = webdriver.PhantomJS()
    driver = webdriver.Chrome()
    driver.get(link)
    try:
        login_sign = driver.find_element_by_xpath("//*[@class='a01 ui-login-link']")
        login = False
    except:
        login = True


    if login == False:
        print("Did not log in")
        ### Log in
        login_button = driver.find_element_by_xpath("//*[@class='ui-login']")
        login_button.click()
        sleep(5)
        login_form = driver.find_element_by_id("loginFormWrapper")
        email_e = login_form.find_element_by_xpath("//*[@class='ui-input-wrapper ui-content-email']")
        email_input = email_e.find_element_by_name("email").send_keys(acc)
        log("Input Email")
        passwd_e = login_form.find_element_by_xpath("//*[@class='ui-input-wrapper']")
        passwd_input = passwd_e.find_element_by_name("password").send_keys(passwd)
        log("Input Password")
        btn = driver.find_element_by_xpath("//*[@class='ui-submit ui-form-submit']")
        btn.click()
        log("Log in")
        sleep(5)
    else:
        print("Already log in")

    ### Sign
    sign_button = driver.find_element_by_xpath("//*[@class='sign-btn']")
    driver.execute_script("arguments[0].click();", sign_button)
    log("Sign")
    sleep(5)

    ### Read Article
    news_button = driver.find_element_by_xpath("//*[@href='https://news.futunn.com/']")
    driver.execute_script("arguments[0].click();", news_button)
    log("Enter news")
    sleep(5)
    anews_button = driver.find_element_by_xpath("//*[@class='news-title']")
    driver.execute_script("arguments[0].click();", anews_button)
    log("Click News")
    sleep(5)
    #pg_src = driver.page_source
    #print(pg_src)
    log("Finished")
    #pg_src = driver.page_source
    #print(pg_src)
    # print(pg_src)
    driver.quit()
    return


file = open(File_Acc, 'r')
all_line_txt = file.readlines()
acc = all_line_txt[0].strip('\n')
passwd = all_line_txt[1].strip('\n')
while True:
    do_work(acc, passwd)
    sleep(6 * 60 * 60)



exit(0)