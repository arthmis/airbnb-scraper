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
browser.implicitly_wait(10)
wait = WebDriverWait(browser, timeout=10)
browser.get("https://www.airbnb.com/")

# click on search bar to choose location
# location_input_element = browser.find_element_by_css_selector("#Koan-magic-carpet-koan-search-bar__input") 
location_input_element = wait.until(expected.visibility_of_element_located((By.ID, "Koan-magic-carpet-koan-search-bar__input")), "could not find location input element")
actions = ActionChains(browser)
actions.move_to_element(location_input_element)
# actions.click(location_input_element)
actions.click()
actions.perform()

# send the location text to the search bar to initiate search
location = "San Francisco, CA"
location_input_element.send_keys(location)
# actions.send_keys_to_element(location_input_element, location)
# actions.perform()

# waits until first selection is visible then clicks on it
first_location_option = wait.until(expected.visibility_of_element_located(
    (By.ID, "Koan-magic-carpet-koan-search-bar__option-0")), 
    "could not find first location option")
actions.move_to_element(first_location_option)
actions.click(first_location_option)
actions.perform()

start_date = wait.until(expected.visibility_of(browser.find_element(
    By.ID, 
    "checkin_input")), "could not find start date input box")
actions.move_to_element(start_date)
actions.click(start_date)
actions.perform()

start_date_value = wait.until(expected.visibility_of_element_located((
    By.XPATH, 
    "//td[@aria-label=\"Choose Monday, July 8, 2019 as your start date. It's available.\"]")), "could not find the start date value")
actions.move_to_element(start_date_value)
actions.click(start_date_value)
actions.perform()

# location_input_element.submit()

browser.quit();


