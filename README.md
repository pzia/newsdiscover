# newsdiscover

Select and discover Newsitem worth reading with naive bayesian filters, based on the title.

# Sources

- Pocket provides SAVED items
  - to train the bayesian filter (SAVED = "Worth reading")
  - to discover rss feeds to parse
- Owncloud News provides READ items
  - to train the bayesian filter when items is READ but not SAVED

#Ouput

A rss feed.

#Work in progress

##Concepts

- DEF : a like : something put into pocket
- DEF : a match is a like 
- DEF : a match : something shared in social

##Quick todo list

- UNIT : Bayesian positive training : linked in share
- UNIT : Extract canonical url from page (need cache !)
- UNIT : retrieve shares from linkedin network

##Ideas
- IDEA : limiter les news à moins de x jours
- IDEA : utiliser multiprocess/thread : futures python3
- IDEA : affiche top10 des words des title
- IDEA : bayesian filter 3 days, one week, one month, one year (based on date of 
- IDEA : category : tech, dgfip, etat
- IDEA : Classement des Catchs
- IDEA : crawl n level outsite each match to get new feeds
- IDEA : Pocket proxy app
- IDEA : read social firefox
- IDEA : Train with as many Pocket than OCN Read and not in Pocket ?
- IDEA : Transform url in pocket into real one when from google news
- IDEA : use buffer to train pocket against CATCH
- IDEA : Use SCRAPY ?

##Done
- UNIT : limit pocket to word_count > x (100 ?)
- UNIT : redirection solver : input url and get an url (and solve google news redirect)
- UNIT : retrieve articles from pocket
- UNIT : rss extractor : from a page, get the rss feed
- UNIT : Read feeds from oc news
- UNIT : Read items from oc news
- UNIT : Match items between oc news & pocket
- UNIT : Bayesian naive training : "pocket" match from "oc news"
- UNIT : Bayesian rating from items in rss feeds
- UNIT : retrieve shares from buffer

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
- Textblob : https://textblob.readthedocs.io/en/latest/classifiers.html#classifying-text (PIP:textblob)
- SCRAPY : http://scrapy.org/ && http://doc.scrapy.org/en/1.1/topics/ubuntu.html
- SCrapy cloud : https://scrapinghub.com/scrapy-cloud/
- Python Futures : http://masnun.com/2016/03/29/python-a-quick-introduction-to-the-concurrent-futures-module.html
