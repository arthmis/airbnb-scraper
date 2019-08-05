from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from datetime import date

import time

import toml

config_file = open("config.toml", "r")
config = toml.loads(config_file.read())
config_file.close()
# print(config['start_date'])

options = Options()
# options.add_argument('-headless')
browser = Firefox(executable_path='geckodriver', options=options)
browser.implicitly_wait(30)
wait = WebDriverWait(browser, timeout=15)
actions = ActionChains(browser)
browser.get("https://www.airbnb.com/")

# click on search bar to choose location
location_input_element = wait.until(expected.visibility_of(browser.find_element_by_id("Koan-magic-carpet-koan-search-bar__input")), "could not find location input element")
location_input_element.send_keys(config['location'])

# waits until first selection is visible then clicks on it
# first_location_option = wait.until(expected.visibility_of(browser.find_element_by_id(
#     "Koan-magic-carpet-koan-search-bar__option-0")),
#     "could not find first location option")
first_location_option = browser.find_element_by_id("Koan-magic-carpet-koan-search-bar__option-0")
# first_location_option.click()
actions.click(first_location_option)
actions.perform()

# TODO make sure start date isn't before current date
# TODO make sure start date is less than end date
start_date = date.fromisoformat(config['start_date'])
print(start_date)

end_date = date.fromisoformat(config['end_date'])
print(end_date)

# find month and year on airbnb calendar
current_month = date.today()
# current month object allows me to increment the date by a month
# each time browser searches for the current month on the calendar 
current_month = date(current_month.year, current_month.month, 1)

month_and_year_xpath = '//strong[contains(text(), "{0:%B} {0:%Y}")]'.format(current_month)
month_and_year = browser.find_element_by_xpath(month_and_year_xpath)

next_month_arrow_xpath = '//div[@class="_1h5uiygl" and @aria-label="Move forward to switch to the next month."]'

while month_and_year.text != "{0:%B} {0:%Y}".format(start_date):
    if current_month.month == 12:
        current_month = date(current_month.year + 1, 1, current_month.day)
    else:
        current_month = date(current_month.year, current_month.month + 1, current_month.day)

    next_month_arrow = browser.find_element_by_xpath(next_month_arrow_xpath)
    next_month_arrow.click()

    month_and_year_xpath = '//strong[contains(text(), "{0:%B} {0:%Y}")]'.format(current_month)
    month_and_year = browser.find_element_by_xpath(month_and_year_xpath)

# find and click start date
start_date_element_xpath = '//td[@aria-label="Choose {0:%A}, {0:%B} {1}, {0:%Y} as your {2} date. It\'s available."]'.format(start_date, start_date.day, "start")
start_date_element = wait.until(expected.visibility_of(browser.find_element_by_xpath(
   start_date_element_xpath
)), "could not get first date")
start_date_element.click()


month_and_year = browser.find_element_by_xpath(month_and_year_xpath)
next_month_arrow_xpath = '//div[@class="_1h5uiygl" and @aria-label="Move forward to switch to the next month."]'
while month_and_year.text != "{0:%B} {0:%Y}".format(end_date):
    if current_month.month == 12:
        current_month = date(current_month.year + 1, 1, current_month.day)
    else:
        current_month = date(current_month.year, current_month.month + 1, current_month.day)

    next_month_arrow = browser.find_element_by_xpath(next_month_arrow_xpath)
    next_month_arrow.click()

    month_and_year_xpath = '//strong[contains(text(), "{0:%B} {0:%Y}")]'.format(current_month)
    month_and_year = browser.find_element_by_xpath(month_and_year_xpath)

# find and click end date
end_date_element_xpath = '//td[@aria-label="Choose {0:%A}, {0:%B} {1}, {0:%Y} as your {2} date. It\'s available."]'.format(end_date, end_date.day, "end")
end_date_element = wait.until(expected.visibility_of(browser.find_element_by_xpath(
   end_date_element_xpath
)), "could not get first date")
end_date_element.click()

# start search
home_search_button_xpath = '//button[@class="_1vs0x720" and @type="submit" and @aria-busy="false"]'
home_search_button = wait.until(expected.visibility_of(browser.find_element_by_xpath(home_search_button_xpath)), "could not find home search button")
home_search_button.click()

entire_homes_xpath = '//img[@alt="Entire homes"]'
try:
    entire_homes = wait.until(expected.visibility_of(browser.find_element_by_xpath(entire_homes_xpath)), "entire homes not found")
    entire_homes.click()
except Exception as error:
    print("exception type: {}".format(error))
    # If entire home button is not found then stays button is clicked
    # finds and clicks stays button
    stays_button_xpath = '//a[@class="_10l4eyf" and @aria-busy="false" and @data-veloute="explore-nav-card:/homes"]'
    stays_button = wait.until(expected.visibility_of(browser.find_element_by_xpath(stays_button_xpath)), "couldn't find stays button")
    stays_button.click()

    # finds and clicks type of place filter 
    type_of_place_xpath = '//button[@class="_1i67wnzj" and @type="button" and @aria-controls="menuItemComponent-room_type"]'
    type_of_place = wait.until(expected.visibility_of(browser.find_element_by_xpath(type_of_place_xpath)), "could not find type of place filter/button")
    type_of_place.click()

    # finds and click entire home checkbox
    entire_home_checkbox_id = 'DynamicFilterCheckboxItem-Type_of_place-room_types-Entire_home/apt'
    entire_home_checkbox = browser.find_element_by_id(entire_home_checkbox_id)
    entire_home_checkbox.click()

    # saves the new filter for type of place
    save_type_of_place_button_xpath = '//button[@class="_b0ybw8s" and @type="button" and @aria-busy="false"]'
    save_type_of_place_button = wait.until(expected.visibility_of(browser.find_element_by_xpath(save_type_of_place_button_xpath)), "couldn't find save type of place button")
    save_type_of_place_button.click()

# click on price filter button
price_button = wait.until(expected.visibility_of(browser.find_element_by_xpath(r'//button[@aria-controls="menuItemComponent-price_range"]')), "couldn't find price button")
price_button.click()
# actions.click(price_button)
# actions.perform()

# change minimum price
# price_filter_min = wait.until(expected.visibility_of(browser.find_element_by_id("price_filter_min")))
price_filter_min = browser.find_element_by_id("price_filter_min")
for i in range(len(price_filter_min.get_attribute("value"))):
    price_filter_min.send_keys(Keys.BACK_SPACE)

price_filter_min.send_keys(str(config['min_price']))

# change max price
# price_filter_max = wait.until(expected.visibility_of(browser.find_element_by_id("price_filter_max")))
price_filter_max = browser.find_element_by_id("price_filter_max")
for i in range(len(price_filter_max.get_attribute("value"))):
    price_filter_max.send_keys(Keys.BACK_SPACE)

price_filter_max.send_keys(str(config['max_price']))

apply_price = wait.until(expected.visibility_of(browser.find_element_by_xpath('//button[@class="_b0ybw8s" and @type="button" and @aria-busy="false"]')))
apply_price.click()

# wait is necessary so that it gives the browser time to load the results before
# getting the page_source
time.sleep(20)

# page_source = browser.execute_script("return document.getElementsByTagName('html')[0].innerHTML;")
page_source = browser.execute_script("return new XMLSerializer().serializeToString(document);")

source = browser.page_source



# from bs4 import BeautifulSoup
# import html5lib
# source = open("test.html")
# soup = BeautifulSoup(html, 'html.parser')
# # soup = BeautifulSoup(source, 'html5lib')
# source.close()
#
# first_listings = soup.find_all("div", class_="_1dss1omb")
#
# # format the listing names
# for i, listings in enumerate(first_listings):
#     first_listings[i] = first_listings[i].text
#
# listing_urls = soup.find_all("a", attrs={"data-check-info-section": "true", "class":"_1ol0z3h"})
#
# # format urls for the listings 
# for i, url in enumerate(listing_urls):
#     listing_urls[i] = "https://www.airbnb.com{}".format(listing_urls[i]['href'])
#
# # find which listings are from a superhost
# superhosts = soup.find_all("div", class_="_aq2oyh")
# for i, thing in enumerate(superhosts):
#     if len(thing.contents) > 1:
#         superhosts[i] = True
#     else:
#         superhosts[i] = False
#
# class Listing:
#     def __init__(self, title, url, superhost):
#         self.title = title
#         self.url = url
#         self.superhost = superhost
#     def __str__(self):
#         return "title: {}\nurl: {}\nsuperhost: {}".format(self.title, self.url, self.superhost)
#
# listings = []
# for title, url, superhost in zip(first_listings, listing_urls, superhosts):
#     listings.append(Listing(title, url, superhost))
#
# # for listing in listings:
# #     print(listing)
# # for i, host in enumerate(superhosts):
# #     print("{}: {}".format(i, host))
# # for i, listing in enumerate(first_listings):
# #     print("{}: {}".format(i, listing))
# # for i, url in enumerate(urls):
# #     print("{}: {}".format(i, url))
#
# import sqlite3
# from sqlite3 import Error
# import database
#
# connection = database.create_connection("listings.db")
#
# database.create_table(connection, database.create_table_sql)
# for listing in listings:
#     database.add_listing(connection, listing)
#
# connection.close()
