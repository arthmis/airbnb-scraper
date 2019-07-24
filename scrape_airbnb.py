from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

# options = Options()
# # options.add_argument('-headless')
# browser = Firefox(executable_path='geckodriver', options=options)
# browser.implicitly_wait(20)
# wait = WebDriverWait(browser, timeout=15)
# actions = ActionChains(browser)
# browser.get("https://www.airbnb.com/")
#
# # click on search bar to choose location
# location = "San Francisco, CA"
# location_input_element = wait.until(expected.visibility_of(browser.find_element_by_id("Koan-magic-carpet-koan-search-bar__input")), "could not find location input element")
# location_input_element.send_keys(location)
#
# # waits until first selection is visible then clicks on it
# # first_location_option = wait.until(expected.visibility_of(browser.find_element_by_id(
#     # "Koan-magic-carpet-koan-search-bar__option-0")),
#     # "could not find first location option")
# first_location_option = browser.find_element_by_id("Koan-magic-carpet-koan-search-bar__option-0")
# first_location_option.click()
#
# # find and click start date
# start_date_xpath = '//td[@aria-label="Choose {}, {} {}, {} as your {} date. It\'s available."]'.format("Friday", "July", 26, 2019, "start")
# start_date = wait.until(expected.visibility_of(browser.find_element_by_xpath(
#    start_date_xpath
# )), "could not get first date")
# start_date.click()
#
# # find and click end date
# end_date_xpath = '//td[@aria-label="Choose {}, {} {}, {} as your {} date. It\'s available."]'.format("Wednesday", "July", 31, 2019, "end")
# end_date = wait.until(expected.visibility_of(browser.find_element_by_xpath(
#    end_date_xpath
# )), "could not get first date")
# end_date.click()
#
# # start search
# home_search_button_xpath = '//button[@class="_1vs0x720" and @type="submit" and @aria-busy="false"]'
# home_search_button = wait.until(expected.visibility_of(browser.find_element_by_xpath(home_search_button_xpath)), "could not find home search button")
# home_search_button.click()
#
# entire_homes_xpath = '//img[@alt="Entire homes"]'
# try:
#     entire_homes = wait.until(expected.visibility_of(browser.find_element_by_xpath(entire_homes_xpath)), "entire homes not found")
#     entire_homes.click()
# except Exception as error:
#     print("exception type: {}".format(error))
#     # If entire home button is not found then stays button is clicked
#     # finds and clicks stays button
#     stays_button_xpath = '//a[@class="_10l4eyf" and @aria-busy="false" and @data-veloute="explore-nav-card:/homes"]'
#     stays_button = wait.until(expected.visibility_of(browser.find_element_by_xpath(stays_button_xpath)), "couldn't find stays button")
#     stays_button.click()
#
#     # finds and clicks type of place filter 
#     type_of_place_xpath = '//button[@class="_1i67wnzj" and @type="button" and @aria-controls="menuItemComponent-room_type"]'
#     type_of_place = wait.until(expected.visibility_of(browser.find_element_by_xpath(type_of_place_xpath)), "could not find type of place filter/button")
#     type_of_place.click()
#
#     # finds and click entire home checkbox
#     entire_home_checkbox_id = 'DynamicFilterCheckboxItem-Type_of_place-room_types-Entire_home/apt'
#     entire_home_checkbox = browser.find_element_by_id(entire_home_checkbox_id)
#     entire_home_checkbox.click()
#
#     # saves the new filter for type of place
#     save_type_of_place_button_xpath = '//button[@class="_b0ybw8s" and @type="button" and @aria-busy="false"]'
#     save_type_of_place_button = wait.until(expected.visibility_of(browser.find_element_by_xpath(save_type_of_place_button_xpath)), "couldn't find save type of place button")
#     save_type_of_place_button.click()
#
#
#
#
#
#
# price_button = wait.until(expected.visibility_of(browser.find_element(
#     By.XPATH,
#     r'//button[@aria-controls="menuItemComponent-price_range"]')))
# actions.click(price_button)
# actions.perform()
#
# # change minimum price
# price_filter_min = wait.until(expected.visibility_of(browser.find_element_by_id("price_filter_min")))
# price_filter_min.send_keys(Keys.BACK_SPACE)
# price_filter_min.send_keys(Keys.BACK_SPACE)
# price_filter_min.send_keys("100")
#
# # change max price
# price_filter_max = wait.until(expected.visibility_of(browser.find_element_by_id("price_filter_max")))
# price_filter_max.send_keys(Keys.BACK_SPACE)
# price_filter_max.send_keys(Keys.BACK_SPACE)
# price_filter_max.send_keys(Keys.BACK_SPACE)
# price_filter_max.send_keys(Keys.BACK_SPACE)
# price_filter_max.send_keys(Keys.BACK_SPACE)
# price_filter_max.send_keys("200")
#
# apply_price = wait.until(expected.visibility_of(browser.find_element_by_xpath('//button[@class="_b0ybw8s" and @type="button" and @aria-busy="false"]')))
# apply_price.click()
#
# page_source = browser.page_source
# print(page_source)

# file = open("test.html", "w")
# file.write(page_source)
# file.close()




from bs4 import BeautifulSoup
html = open("test.html")
soup = BeautifulSoup(html, 'html.parser')

# print(soup.prettify())
# print(soup.find("div", id='listing-555596'))
# print(soup.find("div"))
