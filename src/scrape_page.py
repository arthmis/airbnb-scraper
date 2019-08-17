from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

import time

# options = Options()
# browser = Firefox(executable_path=config['driver_path'], options=options)
# browser = Firefox(executable_path="geckodriver", options=options)


# class HomeType:
#     APARTMENT = 1 
#     HOUSE = 2
#     COTTAGE = 3
#     LOFT = 4 
#     TOWNHOUSE = 5
#     VILLA = 6 
#     CHALET = 7
#     BUNGALOW = 8

# home_types = {
#     "Apartment": HomeType.APARTMENT,
#     "House": HomeType.HOUSE,
#     "Cottage": HomeType.COTTAGE,
#     "Loft": HomeType.LOFT,
#     "Townhouse": HomeType.TOWNHOUSE,
#     "Villa": HomeType.VILLA,
#     "Chalet": HomeType.CHALET,
#     "BUNGALOW": HomeType.BUNGALOW,
# }

# class Listing:
#     def __init__(self, title, url, image_url, home_type, rating, price, review_count):
#         self.title = title
#         self.url = url
#         self.image_url = image_url
#         self.review_count = review_count
#         self.rating = rating
#         self.price = price
#         self.home_type = home_type
#
#     def __str__(self):
#         return "title: {self.title}\nurl: {self.url}\nimage url: {self.image_url}\nreview count: {self.review_count}\nrating: {self.rating}\nprice: {self.price}\nhome type: {self.home_type}"
#         )


def scrape(html):
    soup = BeautifulSoup(html, "html.parser")

    # get the listing titles 
    titles = soup.find_all("div", class_="_1dss1omb")
    for i, title in enumerate(titles):
        titles[i] = titles[i].text

    # retrieve and format urls for the listings
    listing_urls = soup.find_all(
        "a", attrs={"data-check-info-section": "true", "class": "_1ol0z3h"}
    )
    for i, url in enumerate(listing_urls):
        listing_urls[i] = f'https://www.airbnb.com{listing_urls[i]["href"]}'

    # find which listings are from a superhost
    # two possible classes for the div wrapping the superhost span
    # superhosts = soup.find_all("div", class_="_aq2oyh")
    # if len(superhosts) == 0:
    #     superhosts = soup.find_all("div", class_="_14pl6ge")

    # for i, thing in enumerate(superhosts):
    #     if len(thing.contents) > 1:
    #         superhosts[i] = True
    #     else:
    #         superhosts[i] = False

    # get an image url to display image of listing on slack
    image_urls = soup.find_all("div", attrs={"class": "_1i2fr3fi", "role": "img"})
    for i, url in enumerate(image_urls):
        image_urls[i] = url["style"].split('"')[1]

    # get home types for the listings
    listing_home_types = soup.find_all("span", style="color: rgb(118, 118, 118);")
    for i, home_type in enumerate(listing_home_types):
        listing_home_types[i] = home_type.text.split(" ", 1)[1]

    # gets prices for the listings
    prices = soup.select("span._j2qalb2 > span._j2qalb2 > span._krjbj")
    for i, price in enumerate(prices):
        price[i] = price.parent.text.split("$", 1)[1]

    # gets the number of reviews for each listing
    review_counts = soup.select("span._1gvnvab > span._j2qalb2")
    for i, review_count in enumerate(review_counts):
        review_counts[i] = review_count.text

    listings = []
    for title, url, image_url, home_type, review_count, price, rating in zip(
        titles, listing_urls, image_urls, home_types, review_counts, prices, ratings 
    ):
        # append only those that are not guess type listing 
        # if less 
        new_listing = Listing(title, url, image_url, home_type, rating, price, review_count)
        if "guest" in listing.home_type:
            continue
        elif review_count < 50:
            continue

        listings.append(new_listing)

    # for listing in listings:
    #     print(listing)

    return listings


def get_page(link):

    browser.get(link)
    time.sleep(15)
    return browser.page_source

from airbnb_spider import crawl_airbnb
if __name__ == "__main__":
    html_source = open("first_type_of_results.html")
    html_source = crawl_airbnb()
    # html_source = open("second_type_results.html")

    # listings = scrape(html_source.read())
    # html_source.close()

    # print(listings[0])
    # print(home_types["APARTMENT"])
    soup = BeautifulSoup(html_source, "html.parser")

    # listing_home_types = soup.find_all("span", style="color: rgb(118, 118, 118);")
    # for i, home_type in enumerate(listing_home_types):
    #     print(home_type.text)

    # prices = soup.select("span._j2qalb2 > span._j2qalb2 > span._krjbj")
    # for i, price in enumerate(prices):
    #     print(price.parent.text)
        # print(price.parent.text.split("$", 1)[1])
        # price[i] = price.parent.text.split("$", 1)[1]

    review_counts = soup.select("span._1gvnvab > span._j2qalb2")
    for i, review_count in enumerate(review_counts):
        review_counts[i] = review_count.text
        # print(review_count.text)

