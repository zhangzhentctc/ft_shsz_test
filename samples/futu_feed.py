from selenium import webdriver  #导入Selenium的webdriver
from selenium.webdriver.common.keys import Keys  #导入Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from time import *
from datetime import *

link = "https://seed.futunn.com/"
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

    #### Login
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

    #### Main Page
    pg_src = driver.page_source
    #print(pg_src)

    #### Pour water
    waterProgress = driver.find_element_by_class_name("waterProgress")
    circle = waterProgress.find_elements_by_tag_name("circle")
    #time = float(circle[1].get_attribute('stroke-dasharray').split(" ")[0])
    log("check water process ")

    waterCanvas = driver.find_element_by_id("waterCanvas")
    ActionChains(driver).double_click(waterCanvas).perform()

    #### Friends
    friends_ = driver.find_element_by_xpath("//*[@class='nav-icon icon_nav-friends']")
    friends_.click()
    log("Friends")
    sleep(5)


    ######## Load More
    hasMore_region = driver.find_element_by_xpath("//*[@ng-show='!friendsLoading']")
    driver.execute_script("arguments[0].click();", hasMore_region)
    sleep(5)
    log("More")
    hasMore_region = driver.find_element_by_xpath("//*[@ng-show='!friendsLoading']")
    driver.execute_script("arguments[0].click();", hasMore_region)
    sleep(5)
    log("More")
    hasMore_region = driver.find_element_by_xpath("//*[@ng-show='!friendsLoading']")
    driver.execute_script("arguments[0].click();", hasMore_region)
    log("More")
    sleep(5)
    hasMore_region = driver.find_element_by_xpath("//*[@ng-show='!friendsLoading']")
    driver.execute_script("arguments[0].click();", hasMore_region)
    log("More")
    sleep(5)

    friends_need = True
    while friends_need == True:
        try:
            thirsty_friends = driver.find_elements_by_xpath("//*[@class='can_fert icon_friends-fert']")
            driver.execute_script("arguments[0].click();", thirsty_friends[0])
            friends_need = True
        except:
            friends_need = False
            log("No friend needs")
            break
        log("Someone needs")
        if friends_need == True:
            sleep(5)
            #### Fert
            fert = driver.find_element_by_xpath("//*[@class='opIcon icon_fert']")
            fert.click()
            log("Fert")
            sleep(5)
            #### Back
            back = driver.find_element_by_xpath("//*[@class='back-text']")
            driver.execute_script("arguments[0].click();", back)
            log("Back")
            sleep(5)
            ######## Load More
            hasMore_region = driver.find_element_by_xpath("//*[@ng-show='!friendsLoading']")
            driver.execute_script("arguments[0].click();", hasMore_region)
            log("More")
            sleep(5)
            hasMore_region = driver.find_element_by_xpath("//*[@ng-show='!friendsLoading']")
            driver.execute_script("arguments[0].click();", hasMore_region)
            log("More")
            sleep(5)
            hasMore_region = driver.find_element_by_xpath("//*[@ng-show='!friendsLoading']")
            driver.execute_script("arguments[0].click();", hasMore_region)
            log("More")
            sleep(5)
            hasMore_region = driver.find_element_by_xpath("//*[@ng-show='!friendsLoading']")
            driver.execute_script("arguments[0].click();", hasMore_region)
            log("More")
            sleep(5)

    log("Finished")
    #pg_src = driver.page_source
    #print(pg_src)
    # print(pg_src)
    driver.close()
    time = 1
    return time


file = open(File_Acc, 'r')
all_line_txt = file.readlines()
acc = all_line_txt[0].strip('\n')
passwd = all_line_txt[1].strip('\n')
while True:
    time = do_work(acc, passwd)
    #print(time)
    sleep(2 * 60 * 60 + 60)



exit(0)