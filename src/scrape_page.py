from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

import time

class Listing:
    def __init__(self, title, url, image_url, home_type, rating, price, review_count, weighted_rating):
        self.title = title
        self.url = url
        self.image_url = image_url
        self.review_count = review_count
        self.rating = rating
        self.price = price
        self.home_type = home_type
        self.weighted_rating = weighted_rating

    def __str__(self):
        return f"title: {self.title}\nurl: {self.url}\nimage url: {self.image_url}\nreview count: {self.review_count}\nrating: {self.rating}\nprice: {self.price}\nhome type: {self.home_type}\nweighted rating: {self.weighted_rating}"

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

    # get an image url to display image of listing on slack
    image_urls = soup.find_all("div", attrs={"class": "_1i2fr3fi", "role": "img"})
    for i, url in enumerate(image_urls):
        image_urls[i] = url["style"].split('"')[1]

    # get home types for the listings
    home_types = soup.find_all("span", style="color: rgb(118, 118, 118);")
    for i, home_type in enumerate(home_types):
        home_types[i] = home_type.text.split(" ", 1)[1]

    # gets prices for the listings
    prices = soup.select("span._j2qalb2 > span._j2qalb2 > span._krjbj")
    for i, price in enumerate(prices):
        prices[i] = int(price.parent.text.split("$", 1)[1].replace(',', ''))

    # gets the number of reviews for each listing
    review_counts = soup.select("span._1gvnvab > span._j2qalb2")
    if len(review_counts) == 0:
        review_counts = soup.select("div._s4ipbau > span._1plk0jz1")
    for i, review_count in enumerate(review_counts):
        review_counts[i] = int(review_count.text.replace('(', '').replace(')', ''))

    # gets the ratings for each listing
    ratings = soup.find_all("span", class_="_rs3rozr", role="img", style="width: 50px;")
    if len(ratings) == 0:
        ratings = soup.find_all("div", class_="_10qgzd5i", role="img")
    for i, rating in enumerate(ratings):
        if rating['aria-label'] == "":
            ratings[i] = 0.0
        else:
            ratings[i] = float(ratings[i]['aria-label'].split(" ", 2)[1])

    listings = []
    for title, url, image_url, home_type, review_count, price, rating in zip(
        titles, listing_urls, image_urls, home_types, review_counts, prices, ratings
    ):
        # append only those that are not guest type listing 
        if "guest" in home_type.lower():
            continue
        elif review_count < 50:
            continue
        elif rating < 4.8:
            continue

        price_max = 3600
        review_count_max = 500
        rating_max = 5.0 
        price_rating = (1 - price / price_max) * 0.55
        review_rating = review_count / review_count_max * 0.35
        rating_after_weight = rating / rating_max * 0.1
        weighted_rating = round(10 * (price_rating + review_rating + rating_after_weight), 2)

        new_listing = Listing(title, url, image_url, home_type, rating, price, review_count, weighted_rating)

        listings.append(new_listing)

    return listings

# 200 - 3600 price
# 50 - 2000 review count
# 4.8 - 5 rating
# price formula ( 1 - price / price max * 0.55 )
# review count formula ( review count / review count max * 0.35 )
# rating formula ( (5.0 - rating) / 0.2 * 0.1 ) 


def get_page(link):

    browser.get(link)
    time.sleep(15)
    return browser.page_source

# from airbnb_spider import crawl_airbnb
if __name__ == "__main__":
    html_source = open("first_type_of_results.html")
    # html_source = crawl_airbnb()
    # html_source = open("second_type_results.html")

    # listings = scrape(html_source.read())
    # html_source.close()

    # print(listings[0])
    # print(home_types["APARTMENT"])
    # soup = BeautifulSoup(html_source, "html.parser")
    listings = scrape(html_source)
    for listing in listings:
        print(listing)
        print()


