#!/usr/bin/env python3
#-*- coding:utf-8 -*-

#mines
import ocn
import mylib

#built out
import feedparser
import json
from pocket import Pocket, PocketException
from textblob.classifiers import NaiveBayesClassifier
import logging
#logging.basicConfig(level=logging.INFO)
import requests
import requests_cache
#monkey patching... FIXME use CacheControl
requests_cache.install_cache('.cache', backend='sqlite', expire_after=6*3600)
import datetime
import PyRSS2Gen

#get config
config = mylib.get_config()

#pocket library
pocketreader = Pocket(
    consumer_key = config['pocket']['consumer_key'],
    access_token = config['pocket']['access_token']
)

#datas
pocket_urls_set = set() #urls from pocket articles
pocket_rss_urls_set = set() #rss extracted from pocket url
ocn_urls_set = set() #urls from ocn articles
train_list = [] #training dataset, with pocket (good ones) and read owncloud news not in pocket (wrong ones)
test_list = [] #myfeed candidates
matches = [] #For the record : matches ocn vs pocket
catches_urls_set = set() #urls candidates
catches = [] #pocket candidates

#parms FIXME : to config ?
catch_qty = 100
pocket_qty = 200
ocn_qty = 500
ocn_chunk = 50
ocn_headers = {"User-Agent" : mylib.load_user_agents()}
ocn_params = {
    "batchSize": ocn_chunk,
    "type": 3, #the type of the query (Feed: 0, Folder: 1, Starred: 2, All: 3)
    "id": 0, #the id of the folder or feed, Use 0 for Starred and All
    "getRead": True #if true it returns all items, false returns only unread items
}


# Fetch a list of articles from pocket
mylib.print_step("Getting last {} Pocket...".format(pocket_qty))
with requests_cache.disabled():
    pocket_list = pocketreader.retrieve(offset=0, count=pocket_qty, state="all")['list']
for k in pocket_list:
    item = pocket_list[k]
    #both urls are stored for better matching
    if 'resolved_url' in item :
        url = item['resolved_url']
        pocket_urls_set.add(url)
    else :
        url = item['given_url']
    if 'resolved_title' in item :
        title = item['resolved_title']
    else :
        title = item['given_title']

    pocket_urls_set.add(item['given_url'])
    print("*\t{}\n\turl:\t{}".format(title, url))

    #extract rss from urls
    feeds = mylib.rss_extract(url = url)
    for f in feeds :
        print("\tfeed:\t{}".format(f))
        pocket_rss_urls_set.add(f)

    #train !
    train_list.append((mylib.clean(title, config['badwords']), 'pocket'))

# Fetch articles from ocn
mylib.print_step("Getting last {} OCN...".format(ocn_qty))
oldest = 100000
count = 0
while (count < ocn_qty) :
    ocn_params['offset'] = oldest
    mylib.print_step("Calling chunk of {}, already {} done ***".format(ocn_chunk, count))
    with requests_cache.disabled():
        items = ocn.api_get("items", params = ocn_params, headers = ocn_headers)
    for i in items :
        deco = ""
        oldest = min(i['id'], oldest)
        count += 1
        i['cleaned_title'] = mylib.clean(i['title'], config['badwords'])
        ocn_urls_set.add(i['url'])
        if mylib.is_url(i['guid']) :
            ocn_urls_set.add(i['guid'])
        if not i['unread'] :
            deco += "r"
        if i['unread']: #we may test this
            deco = "UNREAD"
            test_list.append(i)
        else : #already read, did we pocketize it ?
            if i['url'] in pocket_urls_set or i['guid'] in pocket_urls_set : #yes
                deco = "MATCH"
                train_list.append((i['cleaned_title'], 'pocket'))
                matches.append(i)
            else : #no
                deco = "READ"
                train_list.append((i['cleaned_title'], 'trash'))
        print("{}\t{}\n\turl:\t{}".format(deco, i['title'], i['url']))

mylib.print_step("Matches for the record: %d" % len(matches))
for m in matches :
    print("{}\t{}\n\turl:\t{}".format(m['id'], m['title'], m['url']))

#Training
mylib.print_step("Training with {}".format(len(train_list)))
cl = NaiveBayesClassifier(train_list)

#Catch with NEW from OCN
mylib.print_step("Catching from {} unread ones".format(len(test_list)))
for i in test_list :
    c = cl.classify(i['cleaned_title'])
    print("{}\t{}\n\turl:\t{}\n\tcleaned:\t{}".format(c, i['title'], i['url'], i['cleaned_title']))
    if c == "pocket" and i['url'] not in catches_urls_set and i['guid'] not in catches_urls_set :
        catches.append(i)
        catches_urls_set.add(i['url'])
        if mylib.is_url(i['guid']) :
            catches_urls_set.add(i['guid'])

#Catch with items from feeds
mylib.print_step("Catching from {} discovered feeds".format(len(pocket_rss_urls_set)))
for u in pocket_rss_urls_set :
    if catch_qty < 0 :
        break
    try :
        r = requests.get(u)
        f = feedparser.parse(r.text)
        print("FEED:\t{}".format(u))
        for e in f['items'] :
            cc = mylib.clean(e['title'], config['badwords'])
            c = cl.classify(cc)
            print("{}\t{}\n\turl:\t{}\n\tcleaned:\t{}".format(c, e['title'], e['link'], cc))
            if c == "pocket" and e['link'] not in catches_urls_set:
                catches_urls_set.add(e['link'])
                if "guid" in e and mylib.is_url(e['guid']) :
                    catches_urls_set.add(e['guid'])
                catches.append(e)
                catch_qty -= 1
    except :
        print("\nEXCEPTION in requesting %s\n\n" % u)

mylib.print_step("Save words")
mylib.save_words()

#display Catches
mylib.print_step("Print catches : %d" % len(catches))
rss = PyRSS2Gen.RSS2(
    title = "HB recommends",
    link = "http://hugues.clement-bernard.fr",
    description = "Recommandations",
    lastBuildDate = datetime.datetime.now(),
    )

for m in catches :
    title = mylib.get_mixed_dict(m, 'title', default="No Title")
    title = mylib.strip_html(title)
    url = mylib.get_mixed_dict(m, 'url', 'link')
    guid = mylib.get_mixed_dict(m, 'guid', default=url)
    description = mylib.get_mixed_dict(m, 'description', 'content')
    summary = mylib.get_mixed_dict(m, 'description', 'summary', default=description)
    published = mylib.get_mixed_dict(m, 'published', 'updated', 'created', default=datetime.datetime.now())

    if url in ocn_urls_set or (mylib.is_url(guid) and guid in ocn_urls_set) :
        new = "OCN"
    elif url not in pocket_urls_set and guid not in pocket_urls_set :
        new = "CATCH"
        item = PyRSS2Gen.RSSItem(
            title = title,
            link = url,
            description = description,
            pubDate = published,
            guid = guid
            )
        rss.items.append(item)
    else :
        new = "..."
    print("{}\t{}\n\turl:\t{}\n\t{}\n\t{}".format(new, m['title'], url, guid, published))
    
#generate RSS
mylib.print_step("Generate RSS")
rss.write_xml(open("my.rss.xml", "w"), encoding = "utf-8")

