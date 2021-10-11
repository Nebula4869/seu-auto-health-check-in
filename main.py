from selenium import webdriver
from selenium import common
import func_timeout
import datetime
import requests
import zipfile
import winreg
import sys
import os


def send_massage(content: str):
    """
    发送短信/邮件
    :param content: 邮件内容
    :return: None
    """
    # TODO: 发送短信/邮件
    print(content)


@func_timeout.func_set_timeout(30)
def download_chrome_driver():
    """
    下载Chrome引擎
    :return: None
    """
    chrome_version = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon'), 'version')[0]
    while True:
        res = requests.get('https://npm.taobao.org/mirrors/chromedriver/{}/chromedriver_win32.zip'.format(chrome_version), stream=True)
        if res.status_code == 200:
            with open('chromedriver_win32.zip', 'wb') as f:
                f.write(res.content)
            with zipfile.ZipFile('chromedriver_win32.zip', 'r') as f:
                f.extract('chromedriver.exe')
            os.remove('chromedriver_win32.zip')
            break
        else:
            chrome_version = '.'.join(chrome_version.split('.')[:-1]) + '.' + str(int(chrome_version.split('.')[-1]) - 1)


@func_timeout.func_set_timeout(60)
def check_in(driver: webdriver, username: str, password: str, bbt: str) -> int:
    """
    自动上报
    :param driver: Chrome爬虫引擎
    :param username: 统一身份认证用户名
    :param password: 统一身份认证密码
    :param bbt: 上报体温值
    :return: 0: 成功 -1: 失败
    """
    try:
        # 登录界面
        driver.get('http://ehall.seu.edu.cn/appShow?appId=5821102911870447')
        while len(driver.find_elements_by_id('username')) == 0 or len(driver.find_elements_by_id('password')) == 0 or len(driver.find_elements_by_class_name('auth_login_btn')) == 0:
            pass
        input_username = driver.find_element_by_id('username')
        input_username.click()
        input_username.send_keys(username)
        input_password = driver.find_element_by_id('password')
        input_password.click()
        input_password.send_keys(password)
        button_xsfw = driver.find_element_by_class_name('auth_login_btn')
        button_xsfw.click()

        # 每日健康申报界面
        while len(driver.find_elements_by_xpath('/html/body/main/article/section/div[2]/div[1]')) == 0:
            pass
        button_add = driver.find_element_by_xpath('/html/body/main/article/section/div[2]/div[1]')
        button_add.click()

        # 新增上报界面
        while (len(driver.find_elements_by_name('DZ_JSDTCJTW')) == 0 or len(driver.find_elements_by_id('save')) == 0) and len(driver.find_elements_by_class_name('bh-dialog-center')) == 0:
            pass

        if len(driver.find_elements_by_class_name('bh-dialog-center')) != 0:
            if '每日健康申报截止时间15:00' in driver.page_source:
                print('每日健康申报截止时间15:00')
            if '目前每日健康打卡时间是1时～15时，请在此时间内填报。' in driver.page_source:
                print('目前每日健康打卡时间是1时～15时，请在此时间内填报。')
            else:
                print('今日已填报！')
            driver.quit()
            return -1

        # 填写体温并提交
        input_bbt = driver.find_element_by_name('DZ_JSDTCJTW')
        input_bbt.click()
        input_bbt.send_keys(bbt)
        button_save = driver.find_element_by_id('save')
        button_save.click()

        while len(driver.find_elements_by_class_name('bh-bg-primary')) == 0:
            pass
        button_add = driver.find_element_by_class_name('bh-bg-primary')
        button_add.click()

        return 0

    except Exception as e:
        print(e)
        return -1


def main(check_in_time: str, username: str, password: str, bbt: str, headless: bool):
    """
    定时运行
    :param check_in_time: 每日脚本运行时间
    :param username: 统一身份认证用户名列表
    :param password: 统一身份认证密码列表
    :param bbt: 上报体温值列表
    :param headless: 是否隐藏浏览器界面
    :return: None
    """
    # 检测引擎存在
    if not os.path.exists('chromedriver.exe'):
        download_chrome_driver()

    # 检测引擎版本
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome('chromedriver.exe', options=options)
        driver.quit()
    except common.exceptions.SessionNotCreatedException:
        download_chrome_driver()

    while True:
        if str(datetime.datetime.now().time())[:8] == check_in_time:
            driver = None
            try:
                # 初始化引擎
                options = webdriver.ChromeOptions()
                options.add_experimental_option('excludeSwitches', ['enable-automation'])
                options.add_argument('--disable-blink-features=AutomationControlled')
                if headless:
                    options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                driver = webdriver.Chrome('chromedriver.exe', options=options)
                driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})
            except Exception as e:
                print(e)

            try:
                content = '{} {} 上报{}！'.format(username, datetime.datetime.now().today(), '成功' if check_in(driver, username, password, bbt) == 0 else '失败')
            except func_timeout.exceptions.FunctionTimedOut:
                content = '{} {} 上报失败！'.format(username, datetime.datetime.now().today())

            try:
                driver.quit()
            except Exception as e:
                print(e)

            try:
                send_massage(content)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], True)
