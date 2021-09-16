from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import pickle
import platform
from Source.config import username, password


base_dir = os.getcwd()
print(base_dir)
start_time = time.time()


def load_auth_state():
    try:
        return pickle.load(open(base_dir+'/Shared/auth_state.pkl', 'rb'))
    except:
        return None


def save_auth_state(state):
    pickle.dump(state, open(base_dir+'/Shared/auth_state.pkl', 'wb+'))


def save_followers(data):
    pickle.dump(data, open(base_dir+'/Shared/followers.pkl', 'wb+'))


def save_cookies(browser: webdriver.Chrome):
    pickle.dump(browser.get_cookies(), open(base_dir+"/Shared/cookies.pkl", "wb"))


def load_cookies():
    try:
        return pickle.load(open(base_dir+"/Shared/cookies.pkl", "rb"))
    except:
        return None


def login(browser: webdriver.Chrome, username, password):
    browser.get('https://instagram.com')
    login_area = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@type="text"]')))
    login_area.send_keys(username)
    password_area = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@type="password"]')))
    password_area.send_keys(password)
    submit = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]')))
    submit.click()
    save_login_info = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@class="sqdOP  L3NKy   y3zKF     "]')))
    save_login_info.click()
    save_cookies(browser)


def get_feed(browser: webdriver.Chrome, username, password, headless=False):
    auth_state = load_auth_state()
    print(auth_state)
    if auth_state is not None:
        if auth_state[1]:
            cookies = load_cookies()
            browser.get('https://instagram.com')
            for cookie in cookies:
                browser.add_cookie(cookie)
            time.sleep(2)
            browser.get('https://instagram.com')
            print('auth completed')
    else:
        login(browser, username, password)
        auth_state = [time.time(), True]
        save_auth_state(auth_state)
        print('login successful')

    # doesnt work in headless mode
    if not headless:
        print('click not now')
        notifications = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@class="aOOlW   HoLwm "]')))
        notifications.click()
    print('feed loaded')


def get_profile(browser: webdriver.Chrome):
    avatar = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//span[@class="_2dbep qNELH"]')))
    avatar.click()
    profile = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[@class="-qQT3"]')))
    profile.click()
    browser.save_screenshot('failure.png')
    print('profile loaded')


def get_followers(browser: webdriver.Chrome):
    followers = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//a[@class="-nal3 "]')))
    followers.click()
    print('followers clicked')
    tryTime = 1.0
    # find all li elements in list
    fBody = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="isgrP"]')))

    scrollPossible = True
    attempts = 5
    last_height = driver.execute_script("return arguments[0].scrollTop", fBody)
    while scrollPossible:
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', fBody)
        time.sleep(tryTime)
        new_height = driver.execute_script("return arguments[0].scrollTop", fBody)
        if new_height > last_height:
            last_height = new_height
            attempts = 5
        elif new_height == last_height and attempts == 0:
            scrollPossible = False
        elif new_height == last_height and attempts > 0:
            attempts -= 1
    time.sleep(2)
    fList = browser.find_elements_by_xpath("//div[@class='isgrP']//li")
    print('followers loaded')
    fList = [element.text for element in fList]
    fList = [item.split('\n') for item in fList]

    result = []

    labels_local = {'Подписаться': 'Follow', 'Удалить': 'Remove'}
    for i in range(len(fList)):
        item = fList[i].copy()
        if '·' in fList[i]:
            try:
                item.remove(labels_local['Подписаться'])
                item.remove(labels_local['Удалить'])
            except:
                item.remove('Подписаться')
                item.remove('Удалить')
            item.remove('·')
            item.append('Вы не подписаны')
            result.append(item)
        else:
            try:
                item.remove(labels_local['Удалить'])
            except:
                item.remove('Удалить')
            item.append('Вы подписаны')
            result.append(item)
    close_button = browser.find_element_by_class_name("WaOAr")
    close_button.click()
    print('followers list loaded')
    return result


headless = False
options = webdriver.ChromeOptions()
options.headless = headless

base_dir = os.path.dirname(base_dir)

os_name = platform.system()

driver_name = ''

if os_name == 'Windows':
    driver_name = 'chromedriver_win.exe'
elif os_name == 'Darwin':
    driver_name = 'chromedriver_mac'

driver = webdriver.Chrome(base_dir + '/Executables/' + driver_name, options=options)

followers = None
followers_time = None

try:
    get_feed(driver, username, password, headless=headless)
    get_profile(driver)
    followers_time = time.time()
    followers = get_followers(driver)
    driver.quit()
    save_followers(followers)
except Exception as e:
    print('Failure!')
    print(e)
    driver.save_screenshot(base_dir+'/Shared/failure.png')

for f in followers:
    print(f)

driver.quit()
print('followers time elapsed:', int(time.time() - followers_time), 'sec')
print('time elapsed:', int(time.time() - start_time), 'sec')
