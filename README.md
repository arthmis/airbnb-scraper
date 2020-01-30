# Airbnb Scraper

- Uses selenium(browser automation tool) to scrape airbnb 
- the scraper types in user selected location
- the scraper then picks the dates the user wants
- then the scraper submits the form
- From there the crawler tries to select entire homes or stays on the results page
- Once the crawler gets to the final results page, it will select the price range
- It will also add Superhost as one of the filters
- From here all the relevant results are visible, now the crawler will wait about 20 
seconds for the entire page to load then save the html for further scraping
- The crawler will move to the next page until it gets about 15 valid results, which
mean sufficient reviews
- Once all the listing pages are obtained, the program will scrape them and get the title,
the type of place and store them in a postgres database
- Once all of that is in place then a slackbot will be able to be queried for 10 listings
currently stored. 
- The slackbot also has the functionality where it can be told to modify the search parameters
like the location, price range and date range. 

I inevitably gave up on this project because while it worked a for a little while, Airbnb constantly
changed their website. The html classes, ids, and other attributes that were used constantly changed
so it wasn't feasible to keep up with them. When I improve this project, I will get rid of the web
crawler and instead of dealing with each individual parameter, will ask the slack user to input
the url with all the parameters they care about. From there the scraper can scrape the html page and maybe 
few others.
