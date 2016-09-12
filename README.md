#newsdiscover

Select and discover Newsitem worth reading with naive bayesian filters, based on the title.

#Summary

- Pocket provides SAVED items
  - to train the bayesian filter (SAVED = "Worth reading")
  - to discover rss feeds to parse
- Owncloud News provides READ items
  - to train the bayesian filter when items is READ but not SAVED

#Ouput

A rss feed with selected items

#Work in progress

##Concepts

###Status of items
- CANDIDATE : any article (item)
- VIEWED : item viewed (read item from feed reader)
- SAVED : item saved (pocket, or starred in feed reader, or ...)
- SHARED : item shared (example : Buffer, Twitter, etc... or a starred SAVED item)
- STARRED : private flag indicating a higher level for an item
  - VIEWED and STARRED = SAVED
  - SAVED and STARRED = SHARED

###Sources

Sources of items :
- API based (OCN, Buffer, Twitter, Pocket, ...)
- url based (feed)

###Parallelization

Concurrent flow with thread AND process, depending of the worker
flows dict  { 'sources' : [futures], 'shared' : [futures], etc... }
Results are consumed in sequence (the flow)
- shared source : get shared items, launch discovering flow in parallel
- saved source 

###Modelisation
- Worker :
  - function called as a thread or process
  - return ( [ (worker, *data, flow) ], [item] )
    - worker : func
    - *data : tuple of datas
    - flow : id of the flow queue for handling the results
    - items : item objects
  - Instances :
    - DiscoverPocket.worker(self, start, stop)
    - DiscoverOcn.worker(self, start, stop)
    - ...
    - spider_worker(url, level)
    - feed_worker(url)
- Item (title, canonical_url, description, status)
  - status : SHARED, SAVED, VIEWED
  - object for storing Items
  - descendants :
    - PocketItem(**dict),
    - OCNItem(**dict)
    - Page(url)

##Quick todo list

- UNIT : Bayesian positive training : linkedin share : Not Doable anymore (closed linkedin API)
- UNIT : Extract canonical url from page
- UNIT : retrieve shares from linkedin network : Not Doable anymore (closed linkedin API)

##Ideas
- IDEA : limiter les news à moins de x jours
- IDEA : affiche top10 des words des title
- IDEA : bayesian filter 3 days, one week, one month, one year
- IDEA : use bayesian score to rank items ? or not ?
- IDEA : crawl n level outsite each items to get new feeds
- IDEA : Read social firefox
- IDEA : Fine tuning of the wty for the training
- IDEA : use BUFFER to train SHARED status

#Reference Links
- Pocket : https://getpocket.com/developer/docs/rate-limits
- Pocket : https://getpocket.com/developer/docs/v3/retrieve
- Pocket : https://github.com/rakanalh/pocket-api (PIP:pocket-api)
- OCNews : https://github.com/owncloud/news/wiki
- OCNews : https://github.com/owncloud/news/wiki/Feeds-1.2
- Newspaper : https://github.com/codelucas/newspaper
- Python : https://docs.python.org/3/library/pathlib.html
- Python : https://docs.python.org/3/library/urllib.parse.html
- FeedParser : https://github.com/kurtmckee/feedparser
- LinkedIn : https://github.com/linkedin/api-get-started/blob/master/python/tutorial.py
- LinkedIn : https://github.com/ozgur/python-linkedin
- LinkedIn : https://github.com/michaelhelmick/linkedin
- Requests : http://docs.python-requests.org
- Requests / Cache : https://github.com/reclosedev/requests-cache
- Requests / CacheControl : http://cachecontrol.readthedocs.io/en/latest/usage.html
- BeautifulSoup : https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- BeautifulSoup : https://www.crummy.com/software/BeautifulSoup/bs4/doc/#output-encoding
- NLTK : http://www.nltk.org/book/ch06.html
- Textblob : https://textblob.readthedocs.io/en/latest/classifiers.html (PIP:textblob)
- SCRAPY : http://scrapy.org/ && http://doc.scrapy.org/en/1.1/topics/ubuntu.html
- SCrapy cloud : https://scrapinghub.com/scrapy-cloud/
- Python Futures : http://masnun.com/2016/03/29/python-a-quick-introduction-to-the-concurrent-futures-module.html
