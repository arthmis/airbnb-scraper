from bs4 import BeautifulSoup
# import html5lib

class Listing:
    def __init__(self, title, url, superhost):
        self.title = title
        self.url = url
        self.superhost = superhost

    def __str__(self):
        return "title: {}\nurl: {}\nsuperhost: {}".format(self.title, self.url, self.superhost)

def scrape(html):
    soup = BeautifulSoup(html, 'html.parser')

    first_listings = soup.find_all("div", class_="_1dss1omb")

    # get the listing names
    for i, listings in enumerate(first_listings):
        first_listings[i] = first_listings[i].text

    listing_urls = soup.find_all("a", attrs={"data-check-info-section": "true", "class":"_1ol0z3h"})

    # retrieve and format urls for the listings
    for i, url in enumerate(listing_urls):
        listing_urls[i] = "https://www.airbnb.com{}".format(listing_urls[i]['href'])

    # find which listings are from a superhost
    superhosts = soup.find_all("div", class_="_aq2oyh")
    for i, thing in enumerate(superhosts):
        if len(thing.contents) > 1:
            superhosts[i] = True
        else:
            superhosts[i] = False


    listings = []
    for title, url, superhost in zip(first_listings, listing_urls, superhosts):
        listings.append(Listing(title, url, superhost))

    return listings

if __name__ == "__main__":
    html_source = open("test.html")
    listings = scrape(html_source.read())
    html_source.close()
    print(listings[0])
