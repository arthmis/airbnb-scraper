import sys
import traceback
import time
from datetime import date
import logging
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

import tomlkit as toml

from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    RetryError,
    before_log,
    after_log,
    retry_if_exception_type,
)

from dotenv import load_dotenv

from utils import write_config, read_config
from scrape_page import scrape, Listing

# from scrape_page import scrape, Listing

logger = logging.getLogger(__name__)

load_dotenv(verbose=True)
GECKODRIVER = os.environ["GECKODRIVER"]


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=30),
    stop=stop_after_attempt(3),
    before=before_log(logger, logging.DEBUG),
    after=after_log(logger, logging.DEBUG),
    retry=retry_if_exception_type(NoSuchElementException),
)
def crawl_airbnb():
    try:
        config = read_config("config.toml")
    except FileNotFoundError:
        logger.exception("", exc_info=True)
        raise
    except Exception:
        logger.exception("", exc_info=True)
        raise
    options = Options()
    # options.add_argument("-headless")
    browser = Firefox(executable_path=GECKODRIVER, options=options)
    browser.implicitly_wait(30)
    wait = WebDriverWait(browser, timeout=15)
    actions = ActionChains(browser)
    browser.get("https://www.airbnb.com/")
    logger.debug("navigating to https://www.airbnb.com/")

    time.sleep(2)
    # click on search bar to choose location
    try:
        location_input_element = wait.until(
            expected.visibility_of(
                browser.find_element_by_id("Koan-magic-carpet-koan-search-bar__input")
            ),
            "",
        )
    except NoSuchElementException:
        logger.exception("Could not find location input element.", exc_info=True)
        raise
    else:
        logger.debug("Found location input search bar.")

    location_input_element.send_keys(config["location"])
    logger.debug(f'Sent the location: {config["location"]} with send keys')

    time.sleep(2)

    try:
        first_location_option = browser.find_element_by_id(
            "Koan-magic-carpet-koan-search-bar__option-0"
        )
    except NoSuchElementException:
        logger.exception("Could not find first location option.", exc_info=True)
        raise
    else:
        # first_location_option.click() and actions.click() don't click for some reason
        # so execute_script is necessary
        browser.execute_script("arguments[0].click();", first_location_option)
        logger.debug("Found first option for location search bar and clicked")

    start_date = date.fromisoformat(config["start_date"])
    end_date = date.fromisoformat(config["end_date"])

    try:
        assert start_date < end_date
    except AssertionError:
        logger.exception(
            f'Start date doesn\'t precede the end date in the configuration\nstart_date: {config["start_date"]}, end_date: {config["end_date"]}',
            exc_info=True,
        )
        raise

    try:
        assert date.today() < start_date
    except AssertionError:
        logger.exception(
            f'start date shouldn\'t precede today\'s date\nstart_date: {config["start_date"]}, today: {date.today()}',
            exc_info=True,
        )
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
        logger.exception(
            "Couldn't find month and year strong element on airbnb calendar",
            exc_info=True,
        )
        raise
    else:
        logger.debug("Found strong element that contains month and year")

    time.sleep(3)

    next_month_arrow_xpath = '//div[@class="_1h5uiygl" and @aria-label="Move forward to switch to the next month."]'
    try:
        next_month_arrow = browser.find_element_by_xpath(next_month_arrow_xpath)
    except NoSuchElementException:
        logger.exception("Couldn't find next month arrow on calendar", exc_info=True)
        raise
    else:
        logger.debug("Found next month arrow on calendar")

    while month_and_year.text != f"{start_date:%B %Y}":
        # check to see if somehow program moved past the correct month and year
        # this happened occasionally in testing
        # month_and_year_text = month_and_year.text.split()
        # if int(month_and_year_text[1]) > start_date.year:
        #     raise ValueError(f'Visible calendar year: {month_and_year_text[1]} is greater than start_date year: {start_date.year}')

        # increment year if december isn't the start date month
        if current_month.month == 12:
            current_month = date(current_month.year + 1, 1, current_month.day)
        else:
            current_month = date(
                current_month.year, current_month.month + 1, current_month.day
            )

        next_month_arrow.click()
        time.sleep(2)
        current_month_and_year_on_calendar = month_and_year.text

        month_and_year_xpath = f'//strong[contains(text(), "{current_month:%B %Y}")]'
        try:
            month_and_year = browser.find_element_by_xpath(month_and_year_xpath)
        except NoSuchElementException:
            logger.exception(
                f"Couldn't find month and year strong element on airbnb calendar:\nmonth and year on calendar:{current_month_and_year_on_calendar}, start date month and year: {start_date:%B %Y}",
                exc_info=True,
            )
            raise
        else:
            logger.debug("Clicked next month arrow.")

    logger.debug("Found start date year and month on calendar")
    # find and click start date
    start_date_element_xpath = f'//td[@aria-label="Choose {start_date:%A, %B {start_date.day}, %Y} as your start date. It\'s available."]'

    try:
        start_date_element = browser.find_element_by_xpath(start_date_element_xpath)
    except NoSuchElementException:
        logger.exception(
            "Couldn't find start date td element that specifies the day", exc_info=True
        )
        raise
    else:
        start_date_element.click()
        logger.debug("Found and clicked correct date for start date")

    time.sleep(3)

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
        time.sleep(2)

        current_month_and_year_on_calendar = month_and_year.text

        month_and_year_xpath = f'//strong[contains(text(), "{current_month:%B %Y}")]'
        try:
            month_and_year = browser.find_element_by_xpath(month_and_year_xpath)
        except NoSuchElementException:
            logger.exception(
                f"Couldn't find month and year strong element on airbnb calendar.\nmonth and year on calendar: {current_month_and_year_on_calendar}, end date month and year: {end_date:%B %Y}",
                exc_info=True,
            )
            raise
        else:
            logger.debug("Clicked next month arrow.")

    logger.debug("Found month and year for end date on calendar")
    # find and click end date
    end_date_element_xpath = f'//td[@aria-label="Choose {end_date:%A, %B {end_date.day}, %Y} as your end date. It\'s available."]'
    try:
        end_date_element = browser.find_element_by_xpath(end_date_element_xpath)
    except NoSuchElementException:
        logger.exception(
            "Couldn't find specific date number and month: ", exc_info=True
        )
        raise
    else:
        end_date_element.click()
        logger.debug("Found the end date on calendar and clicked")

    time.sleep(2)

    # start search
    home_search_button_xpath = (
        '//button[@class="_1vs0x720" and @type="submit" and @aria-busy="false"]'
    )
    try:
        home_search_button = browser.find_element_by_xpath(home_search_button_xpath)
    except NoSuchElementException:
        logger.exception(
            "Couldn't find search button that submits the form", exc_info=True
        )
    else:
        home_search_button.click()
        logger.debug("Found search/submit button for form on main page and clicked.")

    entire_homes_xpath = '//img[@alt="Entire homes"]'
    try:
        entire_homes = wait.until(
            expected.visibility_of(browser.find_element_by_xpath(entire_homes_xpath))
        )
    except NoSuchElementException:
        # If entire home button is not found then stays button is clicked
        logger.debug("Couldn't find entire homes button, trying to click stays button.")
        stays_button_xpath = '//a[@class="_10l4eyf" and @aria-busy="false" and @data-veloute="explore-nav-card:/homes"]'
        stays_button = wait.until(
            expected.visibility_of(browser.find_element_by_xpath(stays_button_xpath))
        )
        stays_button.click()
        logger.debug("Found and clicked on stays button.")

        time.sleep(3)
        # finds and clicks type of place filter
        type_of_place_xpath = '//button[@class="_1i67wnzj" and @type="button" and @aria-controls="menuItemComponent-room_type"]'
        type_of_place = wait.until(
            expected.visibility_of(browser.find_element_by_xpath(type_of_place_xpath))
        )
        type_of_place.click()
        logger.debug("Found and clicked on type place filter/button.")

        time.sleep(2)
        # finds and click entire home checkbox
        entire_home_checkbox_id = (
            "DynamicFilterCheckboxItem-Type_of_place-room_types-Entire_home/apt"
        )
        entire_home_checkbox = browser.find_element_by_id(entire_home_checkbox_id)
        entire_home_checkbox.click()
        logger.debug("Found and clicked on entire home checkbox.")

        # saves the new filter for type of place
        save_type_of_place_button_xpath = (
            '//button[@class="_b0ybw8s" and @type="button" and @aria-busy="false"]'
        )
        save_type_of_place_button = wait.until(
            expected.visibility_of(
                browser.find_element_by_xpath(save_type_of_place_button_xpath)
            )
        )
        save_type_of_place_button.click()
        logger.debug(
            "Found and clicked save button after checking entire place checkbox"
        )
    else:
        entire_homes.click()
        logger.debug("Found and clicked entire homes button.")

    time.sleep(3)

    # click on price filter button
    price_button = wait.until(
        expected.visibility_of(
            browser.find_element_by_xpath(
                r'//button[@aria-controls="menuItemComponent-price_range"]'
            )
        )
    )
    time.sleep(2)
    price_button.click()
    logger.debug("Found and clicked price filter button.")
    time.sleep(2)

    # change minimum price
    price_filter_min = browser.find_element_by_id("price_filter_min")
    for i in range(len(price_filter_min.get_attribute("value"))):
        price_filter_min.send_keys(Keys.BACK_SPACE)

    price_filter_min.send_keys(str(config["min_price"]))
    logger.debug(f'Changed minimum price to: {config["min_price"]}')

    time.sleep(2)
    # change max price
    price_filter_max = browser.find_element_by_id("price_filter_max")
    for i in range(len(price_filter_max.get_attribute("value"))):
        price_filter_max.send_keys(Keys.BACK_SPACE)

    time.sleep(2)
    price_filter_max.send_keys(str(config["max_price"]))
    logger.debug(f'Changed maximum price to: {config["max_price"]}')

    apply_price = wait.until(
        expected.visibility_of(
            browser.find_element_by_xpath(
                '//button[@class="_b0ybw8s" and @type="button" and @aria-busy="false"]'
            )
        )
    )
    apply_price.click()
    logger.debug("Clicked apply price for new min and max prices.")

    more_filters_xpath = '//button[@type="button" and @aria-controls="menuItemComponent-dynamicMoreFilters"]'
    time.sleep(2)
    more_filters_button = browser.find_element_by_xpath(more_filters_xpath)
    more_filters_button.click()
    logger.debug("Found and clicked on more filters button.")

    superhost_filter_id = "DynamicFilterSwitchItem-other_options-superhost-true--label"
    time.sleep(2)
    superhost_filter = browser.find_element_by_id(superhost_filter_id)
    superhost_filter.click()
    logger.debug("Found and clicked superhost filter.")

    show_stays_xpath = '//button[@class="_72kmbi0" and @type="button" and @aria-busy="false"]'
    time.sleep(2)
    show_stays_button = browser.find_element_by_xpath(show_stays_xpath)
    show_stays_button.click()
    logger.debug("Found and clicked on show stays button.")

    # wait is necessary so that it gives the browser time to load the results before
    # getting the page_source
    time.sleep(20)

    logger.debug("Waited 20 seconds for browser to load results.")
    page_source = browser.page_source
    logger.debug("Retrieved page source.")

    listings = []
    # loops until it goes through 5 pages of results or find 15 listings
    # that match the listing criteria
    for i in range(5):
        new_listings = scrape(browser.page_source)
        logger.debug(f"Retrieved page {i} source.")

        for i, _ in enumerate(new_listings):
            listings.append(new_listings[i])
            if len(listings) == 15:
                break

        if len(listings) == 15:
            break

        next_page_selector = "li._r4n1gzb > a._1ip5u88"
        try:
            next_page_arrow = browser.find_element_by_css_selector(next_page_selector)
        except NoSuchElementException:
            logger.debug("No more pages of listing results")
            break
        else:
            next_page_arrow.click()
            logger.debug("Found and clicked next page arrow")

        time.sleep(10)

    browser.quit()
    logger.debug("Exited browser.")

    return listings

def crawl_link():
    link = "https://www.airbnb.com/s/New-Orleans--LA--United-States/homes?refinement_paths%5B%5D=%2Fhomes&checkin=2019-08-23&checkout=2019-08-27&price_min=96&price_max=185&room_types%5B%5D=Entire%20home%2Fapt&query=New%20Orleans%2C%20LA%2C%20United%20States&place_id=ChIJZYIRslSkIIYRtNMiXuhbBts&search_type=filter_change"
    options = Options()
    # options.add_argument("-headless")
    browser = Firefox(executable_path=GECKODRIVER, options=options)
    browser.implicitly_wait(30)
    wait = WebDriverWait(browser, timeout=15)
    actions = ActionChains(browser)
    browser.get(link)

    more_filters_xpath = '//button[@type="button" and @aria-controls="menuItemComponent-dynamicMoreFilters"]'
    time.sleep(2)
    more_filters_button = browser.find_element_by_xpath(more_filters_xpath)
    more_filters_button.click()
    logger.debug("Found and clicked on more filters button.")

    superhost_filter_id = "DynamicFilterSwitchItem-other_options-superhost-true--label"
    time.sleep(2)
    superhost_filter = browser.find_element_by_id(superhost_filter_id)
    superhost_filter.click()
    logger.debug("Found and clicked superhost filter.")

    show_stays_xpath = '//button[@class="_72kmbi0" and @type="button" and @aria-busy="false"]'
    time.sleep(5)
    show_stays_button = browser.find_element_by_xpath(show_stays_xpath)
    logger.debug("Found show stays button.")
    show_stays_button.click()
    # actions.click(show_stays_button)
    # browser.execute_script("arguments[0].click();", show_stays_button)
    # logger.debug("Found and clicked on show stays button.")
    browser.quit()


if __name__ == "__main__":
    formatter = logging.Formatter(
        "%(levelname)s - %(asctime)s - %(name)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    listings = []
    # crawl_link()

    try:
        page_source = crawl_airbnb()
    except RetryError:
        logger.exception("All attempts at crawling airbnb failed.", exc_info=True)
    else:
        listings = scrape(page_source)
        logger.debug(
            f'Successfully scraped {config["location"]} on airbnb and found {len(listings)} listings.\nstart date: {config["start_date"]}, end date : {config["end_date"]}\nminimum price: {config["min_price"]}, maximum price: {config["max_price"]}'
        )

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
