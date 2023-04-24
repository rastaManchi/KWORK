import random
import requests
import json
import time
from multiprocessing import *
from seleniumwire import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Driver:
    def __init__(self):
        self.link = 'https://www.zara.com/tr/tr/shop/cart'
        self.start_driver()

    def restart(self):
        self.driver.quit()
        self.start_driver()

    def get_cookie(self):
        self.driver.refresh()
        try:
            self.driver.find_element(By.XPATH, "//button[@class='shop-cart-item-quantity__increase']").click()
        except:
            self.driver.get('https://www.zara.com/tr/tr/error/invalid-session')
            self.driver.find_element(By.XPATH, "//span[text()='Ana sayfaya git']").click()
        try:
            self.driver.find_element(By.XPATH, "//span[text()='Ana sayfaya git']").click()
        except Exception:
            pass
        time.sleep(10)
        self.driver.get(self.link)
        cookies = ''
        for cookie in self.driver.get_cookies():
            cookies += f'{cookie["name"]}={cookie["value"]};'
        return cookies

    def start_driver(self):
        chrm_caps = webdriver.DesiredCapabilities.CHROME
        chrm_caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        chrm_caps["marionette"] = True
        # from pyvirtualdisplay import Display
        # display = Display(visible=0, size=(1920, 1080))
        # display.start()
        options = Options()
        options.add_argument('--allow-profiles-outside-user-dir')
        options.add_argument("--no-sandbox")
        options.add_argument("--log-level=3")
        #options.add_argument('--user-data-dir=C:/Users/vacah/AppData/Local/Google/Chrome/User Data')
        #options.add_argument('--profile-directory=Default')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('disable-popup-blocking')
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get('https://www.zara.com/tr/')
        self.driver.implicitly_wait(5)
        time.sleep(4)
        try:
            self.driver.find_element(By.XPATH,
                                     "//button[@class='zds-button geolocation-modal__button zds-button--primary']").click()
            self.driver.find_element(By.XPATH,
                                     "//button[@class='zds-button geolocation-modal__button zds-button--primary']").click()
        except Exception:
            pass
        self.driver.get(self.link)



class Test:
    def __init__(self, mas, cookie):
        self.mas = mas
        self.json_answer = []
        self.cookie = cookie
        self.products_add = []
        self.product_ids = []
        for item in self.mas:
            self.products_add.append(
                {"datatype": "product", "parentId": int(item['color_id']), "gridParentId": int(item['color_id']),
                 "quantity": 10, "sku": int(item['size_id'])})
            self.product_ids.append(int(item['color_id']))
        print(self.mas)

    def start(self):
        len = -1
        self.session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            'cookie': self.cookie

        }
        r = self.session.get('https://www.zara.com/tr/tr/shop/cart', headers=headers)
        token = r.headers['itx-scr-token']
        payload = {"_csrf": token, "productsIds": self.product_ids, "initialRecommendedProducts": [],
                   "excludedProducts": []}
        r = self.session.post('https://www.zara.com/tr/tr/shop/cart/cross-selling?ajax=true', headers=headers,
                              json=payload)
        if r.status_code == 403:
            self.cookie = driver.get_cookie()
            headers['cookie'] = self.cookie
            r = self.session.post('https://www.zara.com/tr/tr/shop/cart/cross-selling?ajax=true',
                                  headers=headers, json=payload)
        token = r.headers['itx-scr-token']
        payload = {"_csrf": token, "products": self.products_add}
        print(payload)
        time.sleep(2)
        r = self.session.post('https://www.zara.com/tr/tr/shop/cart/add?ajax=true', headers=headers, json=payload)
        while r.status_code == 403:
            driver.restart()
            self.cookie = driver.get_cookie()
            headers['cookie'] = self.cookie
            r = self.session.post('https://www.zara.com/tr/tr/shop/cart/add?ajax=true', headers=headers,
                                  json=payload)

        print(f'ADD -- {r.content}')
        len += 1
        r = self.session.get('https://www.zara.com/tr/tr/shop/cart?ajax=true', headers=headers)
        items = json.loads(r.content)['shopCart']['items']
        token = r.headers['itx-scr-token']
        remove_payloads = []
        print(items)
        for item in items:
            if item['availability'] == 'in_stock':
                self.json_answer.append({'size_id': item['detail']['sku'], 'quantity': 10})
            else:
                self.json_answer.append({'size_id': item['detail']['sku'], 'quantity': item['availableQuantity']})
            remove_payloads.append({"id": item['id'], "itemId": item['id'], "isItemSet": False, "quantity": 0})
        r = self.session.get('https://www.zara.com/tr/tr/shop/cart', headers=headers)
        token = r.headers['itx-scr-token']
        payload = {"_csrf": token,
                   "products": remove_payloads}
        time.sleep(2)
        r = self.session.post('https://www.zara.com/tr/tr/shop/cart/update?ajax=true', headers=headers,
                              json=payload)
        while r.status_code == 403:
            driver.restart()
            self.cookie = driver.get_cookie()
            headers['cookie'] = self.cookie
            r = self.session.get('https://www.zara.com/tr/tr/shop/cart', headers=headers)
            token = r.headers['itx-scr-token']
            payload = {"_csrf": token, "productsIds": self.product_ids, "initialRecommendedProducts": [],
                       "excludedProducts": []}
            r = self.session.post('https://www.zara.com/tr/tr/shop/cart/cross-selling?ajax=true', headers=headers,
                                  json=payload)
            token = r.headers['itx-scr-token']
            payload = {"_csrf": token,
                       "products": remove_payloads}
            r = self.session.post('https://www.zara.com/tr/tr/shop/cart/update?ajax=true', headers=headers,
                                  json=payload)
        print(f'REMOVE -- {r.content}')
        # item_id = json.loads(r.content)['items'][0]['id']
        # payload = {"_csrf":token,"products":[{"id":item_id,"itemId":item_id,"isItemSet":False,"quantity":10}]}
        # time.sleep(2)
        # r = self.session.post('https://www.zara.com/tr/tr/shop/cart/update?ajax=true', headers=headers, json=payload)
        # if r.status_code == 403:
        #     self.cookie = driver.get_cookie()
        #     headers['cookie'] = self.cookie
        #     r = self.session.post('https://www.zara.com/tr/tr/shop/cart/update?ajax=true', headers=headers,
        #                           json=payload)
        # print(f'UPDATE -- {json.loads(r.content)}')
        # json_content = json.loads(r.content)
        # self.json_answer.append({'size_id': item['size_id'], 'quantity': json_content['shopCart']['items'][len]['quantity']})
        # token = r.headers['itx-scr-token']
        # payload = {"_csrf":token,"products": [{"id": item_id, "itemId": item_id, "isItemSet": False, "quantity": 0}]}
        # time.sleep(2)
        # r = self.session.post('https://www.zara.com/tr/tr/shop/cart/update?ajax=true', headers=headers,
        #                       json=payload)
        # print(f'REMOVE -- {r.content}')
        # time.sleep(random.randint(5, 10))
        # driver.restart()
        # self.cookie = driver.get_cookie()
        return self.json_answer


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


with open('products_info.json', 'r') as file:
    info = json.loads(file.read())
    all_mas = list(chunks(info[0:500], 50))
    driver = Driver()
    all_response = []
    for mas in all_mas:
        test = Test(mas, driver.get_cookie())
        all_response.append(test.start())
        driver.restart()
        print(all_response)
file.close()
#test.add_to_cart()
