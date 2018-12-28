#!/usr/bin/env python3

"""
Author: Polyakov Konstantin
Date: 2018-12-19
Place: Yeysk, Russia
"""

import time
import os
import requests
import config_site_avito as cs
import parser_tools as pt
import process_images_avito as pi
import urllib3

import selenium
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0

import selenium.webdriver.chrome.service as service

import argparse

cli_parser = argparse.ArgumentParser(description='')
cli_parser.add_argument('--only-absent', default=None)

cli_args = cli_parser.parse_args()

# https://selenium-python.readthedocs.io/api.html#selenium.webdriver.firefox.firefox_profile.FirefoxProfile.set_proxy

# https://docs.seleniumhq.org/docs/
# https://docs.seleniumhq.org/docs/03_webdriver.jsp#introducing-webdriver
# https://stackoverflow.com/questions/40208051/selenium-using-python-geckodriver-executable-needs-to-be-in-path
# https://github.com/mozilla/geckodriver/releases
# https://askubuntu.com/questions/79280/how-to-install-chrome-browser-properly-via-command-line
# export PATH=$PATH:/root/parsers/geckodriver/
# https://www.linux.org.ru/forum/general/13353871

# https://stackoverflow.com/questions/50642308/org-openqa-selenium-webdriverexception-unknown-error-devtoolsactiveport-file-d

# https://habr.com/company/mosigra/blog/433968/
# https://habr.com/post/339238/

# http://avreg.net/howto_x-org-server.html

# /opt/google/chrome/google-chrome

# WebDriveApi
# https://selenium-python.readthedocs.io/api.html

'''headers = {
#"accept":"*/*",
#"accept-language":"ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
#"cache-control":"no-cache",
#'pragma': 'no-cache',
'referer': url,
#'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
'x-requested-with': 'XMLHttpRequest',
}'''

def get_driver(proxy_str):
    # http://chromedriver.chromium.org/getting-started

    options = webdriver.ChromeOptions()
    #options.add_argument('start-maximized')
    #options.add_argument('disable-infobars')
    #options.add_argument('--disable-extensions')
    #options.add_argument('--disable-gpu')
    #options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    print(dir(options))
    options.add_experimental_option("useAutomationExtension", False)

    #service = service.Service('/usr/lib/chromium/chromedriver')
    _service = service.Service('/usr/bin/chromedriver')
    _service.start()
    #capabilities = {'chrome.binary': '/usr/bin/google-chrome-stable'}
    capabilities = {'chrome.binary': '/usr/bin/google-chrome-stable'}

    proxy = webdriver.Proxy()
    proxy.httpsProxy = proxy_str#.split('//')[1]
    proxy.proxyType = {'ff_value': 4, 'string': 'AUTODETECT'}
    proxy.add_to_capabilities(capabilities)
    print(capabilities)

    driver = webdriver.Remote(_service.service_url, capabilities, options=options)
    
    #print(dir(webdriver))
    
    #driver = webdriver.Chrome("/usr/bin/chromedriver")
    #driver = webdriver.Firefox("/root/parsers/geckodriver/")
    
    return driver

if __name__ == '__main__':

    curIndex = pt.CurIndex(os.path.join(cs.path_data, 'cur_user_id2.txt'))
    cur_id = curIndex.get()

    c, cu = cs.get_db()
    c2, cu2 = cs.get_db()
    
    proxies = pt.Proxies(c2, cu2, 'avito', cs.path_data)

    driver = get_driver(proxies+0)

    sql = "SELECT `user_id`, `user_url` FROM `user` WHERE `user_id`>=?"
    res = cu.execute(sql, (cur_id, )).fetchall()
    for user in res:

        base64_path = 'data/images/'+str(user['user_id'])+'.txt'
    	
        if cli_args.only_absent and os.path.exists(base64_path):
            continue

        sql = "SELECT `realty_id`, `realty_ext_id`, `realty_url` FROM `realty` WHERE `realty_user_id`=? AND `realty_is_redirect` is NULL AND `realty_url` IS NOT NULL ORDER BY `realty_id` DESC LIMIT 5"
        res2 = cu2.execute(sql, (user['user_id'], )).fetchall()
        for obj in res2:

            success = 0
            while success == 0:
                try:
                    driver.get(cs.domain_url + obj['realty_url']);
                    success = 1
                except:
                    driver.quit()
                    driver = get_driver(proxies+1)
                    '''except urllib3.exceptions.MaxRetryError as e:
                    driver.quit()
                    driver = get_driver(proxies+1)
                except urllib3.exceptions.NewConnectionError as e:
                    print(1)
                except ConnectionRefusedError as e:
                    print(2)'''
                except selenium.common.exceptions.TimeoutException:
                    print(1)
                except selenium.common.exceptions.WebDriverException:
                    print(2)
                finally:
                    if success == 0:
                        driver.quit()
                        os.spawnv(os.P_NOWAIT, '/usr/bin/python3', ['/root/parsers/collect_users_phones.py'])

            print(obj['realty_id'], user['user_id'], driver.current_url)
            #print(dir(driver))
            btn = driver.find_elements_by_css_selector('a.js-item-phone-button_card')
            if btn:
                btn = btn[0]
            else:
                curIndex.save(user['user_id'])
                continue
            btn.click()
            
            # получаем изображение

            img = []
            count_trying = 7
            while count_trying > 0:
            
                img = driver.find_elements_by_css_selector('div.item-phone-big-number img')
                if img: break
                else: count_trying -= 1

                time.sleep(0.3)

            if img:
                img = img[0]
                base = img.get_attribute('src')
                ipp = pi.ImagePhoneProcessor(base)
                ipp.do_all(user['user_id'], c2, cu2)
                #with open(base64_path, 'w') as f: f.write(base)
                break
            else:
                print('    The image was not found for '+str(user['user_id']) +' '+obj['realty_url'])
                with open('data/images_screen/'+str(user['user_id'])+'.png', 'wb') as f: f.write(driver.get_screenshot_as_png())
                continue

            #proxy.httpProxy = (cs.proxies+1)#.split('//')[1]
            #proxy.add_to_capabilities(capabilities)

            #pkey = "28e1674f53e431d553bd2abb6e96b4f4"
            #url = cs.domain_url+"/items/phone/"+str(obj['realty_ext_id'])+"?pkey="+pkey+"&vsrc=r&searchHash=799mjbqn3z4080sco80owogsosoo84c"
            #headers = { 'referer': cs.domain_url+user['user_url'], 'x-requested-with': 'XMLHttpRequest'}
            #r = cs.proxies.open_url(url, headers=headers)
            
            #json = r.json()
            
            #print(json)

        curIndex.save(user['user_id'])
        
    driver.quit()

    # закомментииовано, чтобы при следуещем старте продолжить загрузку новых телефонов
    #curIndex.save(1) 
    
""" driver
add_cookie
application_cache
back
capabilities
close
command_executor
create_web_element
current_url
current_window_handle
delete_all_cookies
delete_cookie
desired_capabilities
error_handler
execute
execute_async_script
execute_script
file_detector
file_detector_context
find_element
find_element_by_class_name
find_element_by_css_selector
find_element_by_id
find_element_by_link_text
find_element_by_name
find_element_by_partial_link_text
find_element_by_tag_name
find_element_by_xpath
find_elements
find_elements_by_class_name
find_elements_by_css_selector
find_elements_by_id
find_elements_by_link_text
find_elements_by_name
find_elements_by_partial_link_text
find_elements_by_tag_name
find_elements_by_xpath
forward
fullscreen_window
get
get_cookie
get_cookies
get_log
get_screenshot_as_base64
get_screenshot_as_file
get_screenshot_as_png
get_window_position
get_window_rect
get_window_size
implicitly_wait
log_types
maximize_window
minimize_window
mobile
name
orientation
page_source
quit
refresh
save_screenshot
session_id
set_page_load_timeout
set_script_timeout
set_window_position
set_window_rect
set_window_size
start_client
start_session
stop_client
switch_to
switch_to_active_element
switch_to_alert
switch_to_default_content
switch_to_frame
switch_to_window
title
w3c
window_handles
"""

""" html element
 'clear', 'click', 'find_element', 'find_element_by_class_name', 'find_element_by_css_selector', 'find_element_by_id', 'find_element_by_link_text', 'find_element_by_name', 'find_element_by_partial_link_text', 'find_element_by_tag_name', 'find_element_by_xpath', 'find_elements', 'find_elements_by_class_name', 'find_elements_by_css_selector', 'find_elements_by_id', 'find_elements_by_link_text', 'find_elements_by_name', 'find_elements_by_partial_link_text', 'find_elements_by_tag_name', 'find_elements_by_xpath', 'get_attribute', 'get_property', 'id', 'is_displayed', 'is_enabled', 'is_selected', 'location', 'location_once_scrolled_into_view', 'parent', 'rect', 'screenshot', 'screenshot_as_base64', 'screenshot_as_png', 'send_keys', 'size', 'submit', 'tag_name', 'text', 'value_of_css_property'
"""


"""
#!/usr/bin/env bash

#./realty-a flat sell --m2-common 100 --count-rooms 3 --user-type "Частное лицо"

#wget https://download.mozilla.org/?product=firefox-latest-ssl&os=linux64&lang=en-US
#wget https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz

# Основные переменные
user="root"    # пользователь из под которого будет запускаться приложение
resolution="700x500x24"    # разрешение экрана виртуального X-сервера
command="python3 collect_user_phones.py"    # программа, которая будет запускаться в фоне

# Запуск виртуального X-сервера и нашей программы внутри него, где
# xvfb-run - скрипт-обёртка для Xvfb
# /tmp/${user}.xvfb.auth - файл, в который запишется MAGIC-COOKIE для авторизации в X-сервере. К этому файлу имеет доступ на чтение только $user
# -screen 0 ${resolution} -auth /tmp/${user}.xvfb.auth - параметры передаваемые Xvfb при запуске
# Номер X-сервера по умолчанию :99, но его можно изменить используя ключ --server-num, если это необходимо

start_command="/usr/bin/xvfb-run -f /tmp/${user}.xvfb.auth -s '-screen 0 ${resolution} -auth /tmp/${user}.xvfb.auth' $command"

# Проверяем имя пользователя. Если оно не совпадает с $user, то запускаем с помощью "su".
# Это необходимо для правильного запуска из под пользователя root (например, при старте системы)

if ( [ "$(whoami)" = "$user" ] ) then
        bash -c "$start_command"
else
        su -c "$start_command" -l $user
fi
"""