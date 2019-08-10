import sys
import traceback

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

from datetime import date

import time

import tomlkit as toml

from slack_bot import write_toml, read_toml

from scrape_page import scrape, Listing

# config_file = open("config.toml", "r")
# config = toml.loads(config_file.read())
# config_file.close()
# config = read_toml("config.toml")
# print(config['start_date'])

def crawl_airbnb(browser):
    browser.get("https://www.airbnb.com/")

    time.sleep(2)
    # click on search bar to choose location
    try:
        location_input_element = wait.until(
            expected.visibility_of(
                browser.find_element_by_id("Koan-magic-carpet-koan-search-bar__input")
            ),
            "could not find location input element",
        )
    except NoSuchElementException:
        print("Could not find location input element")
        raise

    location_input_element.send_keys(config["location"])

    time.sleep(2)

    try:
        first_location_option = browser.find_element_by_id(
            "Koan-magic-carpet-koan-search-bar__option-0"
        )
    except NoSuchElementException:
        print("Could not find first location option")
        raise 
    else:
        # first_location_option.click() and actions.click() don't click for some reason
        # so execute_script is necessary
        browser.execute_script('arguments[0].click();', first_location_option)

    start_date = date.fromisoformat(config["start_date"])
    end_date = date.fromisoformat(config["end_date"])

    try:
        assert start_date < end_date
    except AssertionError:
        print("start date doesn't precede the end date in the configuration")
        raise 

    try:
        assert date.today() < start_date
    except AssertionError:
        print("start date precedes today's date")
        raise 

    # find month and year on airbnb calendar
    # Use this to figure out which month of the calendar is currently visible
    current_month = date.today()
    # current month object allows me to increment the date by a month
    # each time browser searches for the current month on the calendar
    current_month = date(current_month.year, current_month.month, 1)

    month_and_year_xpath = f'//strong[contains(text(), "{current_month:%B %Y}")]'
    try:
        month_and_year = browser.find_element_by_xpath(month_and_year_xpath)
    except NoSuchElementException:
        print("Couldn't find month and year strong element on airbnb calendar")
        raise

    time.sleep(3)

    next_month_arrow_xpath = '//div[@class="_1h5uiygl" and @aria-label="Move forward to switch to the next month."]'
    try:
        next_month_arrow = browser.find_element_by_xpath(next_month_arrow_xpath)
    except NoSuchElementException:
        print("Couldn't find next month arrow")
        raise

    while month_and_year.text != f"{start_date:%B %Y}".format(start_date):
        # increment year if december isn't the start date month
        if current_month.month == 12:
            current_month = date(current_month.year + 1, 1, current_month.day)
        else:
            current_month = date(
                current_month.year, current_month.month + 1, current_month.day
            )

        next_month_arrow.click()
        time.sleep(1)

        month_and_year_xpath = f'//strong[contains(text(), "{current_month:%B %Y}")]'
        try:
            month_and_year = browser.find_element_by_xpath(month_and_year_xpath)
        except NoSuchElementException:
            print("Couldn't find month and year strong element on airbnb calendar")


    # find and click start date
    start_date_element_xpath = f'//td[@aria-label="Choose {start_date:%A, %B {start_date.day}, %Y} as your start date. It\'s available."]'

    try:
        start_date_element = browser.find_element_by_xpath(start_date_element_xpath)
    except NoSuchElementException:
        print("Couldn't find start date td element that specifies the day")
    else:
        start_date_element.click()

    time.sleep(2)


    month_and_year = browser.find_element_by_xpath(month_and_year_xpath)
    next_month_arrow_xpath = '//div[@class="_1h5uiygl" and @aria-label="Move forward to switch to the next month."]'
    while month_and_year.text != f"{end_date:%B %Y}":
        if current_month.month == 12:
            current_month = date(current_month.year + 1, 1, current_month.day)
        else:
            current_month = date(
                current_month.year, current_month.month + 1, current_month.day
            )

        next_month_arrow.click()
        time.sleep(1)

        month_and_year_xpath = f'//strong[contains(text(), "{current_month:%B %Y}")]'
        try:
            month_and_year = browser.find_element_by_xpath(month_and_year_xpath)
        except NoSuchElementException:
            print("Couldn't find month and year strong element on airbnb calendar")
            raise

    # find and click end date
    end_date_element_xpath = f'//td[@aria-label="Choose {end_date:%A, %B {end_date.day}, %Y} as your end date. It\'s available."]'
    try:
        end_date_element = browser.find_element_by_xpath(end_date_element_xpath)
    except NoSuchElementException:
        print("Couldn't find specific date number and month")
    else:
        end_date_element.click()

    time.sleep(2)

    # start search
    home_search_button_xpath = (
        '//button[@class="_1vs0x720" and @type="submit" and @aria-busy="false"]'
    )
    try:
        home_search_button = browser.find_element_by_xpath(home_search_button_xpath)
    except NoSuchElementException:
        print("Couldn't find search button that submits the form")
    else:
        home_search_button.click()

    entire_homes_xpath = '//img[@alt="Entire homes"]'
    try:
        entire_homes = wait.until(
            expected.visibility_of(browser.find_element_by_xpath(entire_homes_xpath)),
            "entire homes not found",
        )
    except NoSuchElementException:
        # If entire home button is not found then stays button is clicked
        stays_button_xpath = '//a[@class="_10l4eyf" and @aria-busy="false" and @data-veloute="explore-nav-card:/homes"]'
        stays_button = wait.until(
            expected.visibility_of(browser.find_element_by_xpath(stays_button_xpath)),
            "couldn't find stays button",
        )
        stays_button.click()

        time.sleep(3)
        # finds and clicks type of place filter
        type_of_place_xpath = '//button[@class="_1i67wnzj" and @type="button" and @aria-controls="menuItemComponent-room_type"]'
        type_of_place = wait.until(
            expected.visibility_of(browser.find_element_by_xpath(type_of_place_xpath)),
            "could not find type of place filter/button",
        )
        type_of_place.click()

        time.sleep(2)
        # finds and click entire home checkbox
        entire_home_checkbox_id = (
            "DynamicFilterCheckboxItem-Type_of_place-room_types-Entire_home/apt"
        )
        entire_home_checkbox = browser.find_element_by_id(entire_home_checkbox_id)
        entire_home_checkbox.click()

        # saves the new filter for type of place
        save_type_of_place_button_xpath = (
            '//button[@class="_b0ybw8s" and @type="button" and @aria-busy="false"]'
        )
        save_type_of_place_button = wait.until(
            expected.visibility_of(
                browser.find_element_by_xpath(save_type_of_place_button_xpath)
            ),
            "couldn't find save type of place button",
        )
        save_type_of_place_button.click()
    else:
        entire_homes.click()

    time.sleep(3)

    # click on price filter button
    price_button = wait.until(
        expected.visibility_of(
            browser.find_element_by_xpath(
                r'//button[@aria-controls="menuItemComponent-price_range"]'
            )
        ),
        "couldn't find price button",
    )
    time.sleep(2)
    price_button.click()
    time.sleep(2)

    # change minimum price
    price_filter_min = browser.find_element_by_id("price_filter_min")
    for i in range(len(price_filter_min.get_attribute("value"))):
        price_filter_min.send_keys(Keys.BACK_SPACE)

    price_filter_min.send_keys(str(config["min_price"]))

    time.sleep(2)
    # change max price
    price_filter_max = browser.find_element_by_id("price_filter_max")
    for i in range(len(price_filter_max.get_attribute("value"))):
        price_filter_max.send_keys(Keys.BACK_SPACE)

    time.sleep(2)
    price_filter_max.send_keys(str(config["max_price"]))

    apply_price = wait.until(
        expected.visibility_of(
            browser.find_element_by_xpath(
                '//button[@class="_b0ybw8s" and @type="button" and @aria-busy="false"]'
            )
        )
    )
    apply_price.click()

    # wait is necessary so that it gives the browser time to load the results before
    # getting the page_source
    time.sleep(20)

    page_source = browser.execute_script(
        "return new XMLSerializer().serializeToString(document);"
    )
    return page_source


if __name__ == "__main__":
    config = read_toml("config.toml")
    options = Options()
    # options.add_argument('-headless')
    browser = Firefox(executable_path=config['driver_path'], options=options)
    browser.implicitly_wait(30)
    wait = WebDriverWait(browser, timeout=15)
    actions = ActionChains(browser)

    listings = []

    try:
        page_source = crawl_airbnb(browser)
    except AssertionError:
        # type, value, traceback_value = sys.exc_info()
        # print(f'Error finding element {value} of type {type}\n{traceback_value}')
        traceback.print_exc()
    except NoSuchElementException:
        # type, value, traceback = sys.exc_info()
        # print('Error finding element {value} of type {type}\n{traceback}')
        traceback.print_exc()
    else:
        listings = scrape(page_source)
        print(len(listings))
        if len(listings) > 0:
            print(listings[0])

        # for listing in listings:
        #     print(listing)
    finally:
        browser.quit()

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
