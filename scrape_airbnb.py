from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

options = Options()
# options.add_argument('-headless')
browser = Firefox(executable_path='geckodriver', options=options)
browser.implicitly_wait(5)
wait = WebDriverWait(browser, timeout=10)
browser.get("https://www.airbnb.com/")
location = "San Francisco, CA"

location_input_element = browser.find_element_by_css_selector("#Koan-magic-carpet-koan-search-bar__input")
actions = ActionChains(browser)
actions.move_to_element(location_input_element)
actions.click(location_input_element)
# actions.perform()

location_input_element.send_keys(location)
first_location_option = wait.until(browser.find_element_by_id("Koan-magic-carpet-koan-search-bar__option-0"), "could not find first location element")
actions.move_to_element(first_location_option)
actions.click(first_location_option)


first_date = browser.find_element_by_css_selector("#checkin_input");
# actions.move_to_element(first_date)
actions.click(first_date)
# actions.perform()

# first_date_number = browser.find_element_by_xpath("//td[@aria-label='Choose Thursday, July 4, 2019 as your start date. It's available.']")
# actions.move_to_element(first_date_number)
# actions.click(first_date_number)
actions.perform()
# location_input_element.submit()

# print(browser.page_source)

# browser.quit();


