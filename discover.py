#!/usr/bin/env python3
#-*- coding:utf-8 -*-

#mines
import lib
import ocn

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
requests_cache.install_cache('tmp/cache', backend='sqlite', expire_after=12*3600)
import datetime
import PyRSS2Gen

#get config
config = lib.config

#pocket library
pocketreader = Pocket(
    consumer_key = config['pocket']['consumer_key'],
    access_token = config['pocket']['access_token']
)

#print(dir(pocketreader))
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
pocket_qty = config['pocket']['qty']
ocn_qty = config['ocn']['qty']
ocn_chunk = config['ocn']['chunk']
ocn_headers = {"User-Agent" : lib.load_user_agents(config['crawler']['ua_filename'])}
ocn_params = {
    "batchSize": ocn_chunk,
    "type": 3, #the type of the query (Feed: 0, Folder: 1, Starred: 2, All: 3)
    "id": 0, #the id of the folder or feed, Use 0 for Starred and All
    "getRead": True #if true it returns all items, false returns only unread items
}


# Fetch a list of articles from pocket
lib.print_step("Getting last {} Pocket...".format(pocket_qty))
with requests_cache.disabled():
    pocket_list = pocketreader.get(offset=0, count=pocket_qty, state="all")[0]['list']
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
    feeds = lib.rss_extract(url = url)
    for f in feeds :
        print("\tfeed:\t{}".format(f))
        pocket_rss_urls_set.add(f)

    #train !
    train_list.append((lib.clean(title), 'pocket'))

# Fetch articles from ocn
lib.print_step("Getting last {} OCN...".format(ocn_qty))
oldest = 100000
count = 0
while (count < ocn_qty) :
    ocn_params['offset'] = oldest
    lib.print_step("Calling chunk of {}, already {} done ***".format(ocn_chunk, count))
    with requests_cache.disabled():
        items = ocn.api_get("items", params = ocn_params, headers = ocn_headers)
    for i in items :
        deco = ""
        oldest = min(i['id'], oldest)
        count += 1
        i['cleaned_title'] = lib.clean(i['title'])
        ocn_urls_set.add(i['url'])
        if lib.is_url(i['guid']) :
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

lib.print_step("Matches for the record: %d" % len(matches))
for m in matches :
    print("{}\t{}\n\turl:\t{}".format(m['id'], m['title'], m['url']))

#Training
lib.print_step("Training with {}".format(len(train_list)))
cl = NaiveBayesClassifier(train_list)

#Catch with NEW from OCN
lib.print_step("Catching from {} unread ones".format(len(test_list)))
for i in test_list :
    c = cl.classify(i['cleaned_title'])
    print("{}\t{}\n\turl:\t{}\n\tcleaned:\t{}".format(c, i['title'], i['url'], i['cleaned_title']))
    if c == "pocket" and i['url'] not in catches_urls_set and i['guid'] not in catches_urls_set :
        catches.append(i)
        catches_urls_set.add(i['url'])
        if lib.is_url(i['guid']) :
            catches_urls_set.add(i['guid'])

#Catch with items from feeds
lib.print_step("Catching from {} discovered feeds".format(len(pocket_rss_urls_set)))
for u in pocket_rss_urls_set :
    try :
        r = requests.get(u)
        f = feedparser.parse(r.text)
        print("FEED:\t{}".format(u))
        for e in f['items'] :
            cc = lib.clean(e['title'])
            c = cl.classify(cc)
            print("{}\t{}\n\turl:\t{}\n\tcleaned:\t{}".format(c, e['title'], e['link'], cc))
            if c == "pocket" and e['link'] not in catches_urls_set:
                catches_urls_set.add(e['link'])
                if "guid" in e and lib.is_url(e['guid']) :
                    catches_urls_set.add(e['guid'])
                catches.append(e)
    except :
        print("\nEXCEPTION in requesting %s\n\n" % u)

lib.print_step("Save words")
lib.save_words()

#display Catches
lib.print_step("Print catches : %d" % len(catches))
rss = PyRSS2Gen.RSS2(
    title = config['output']['title'],
    link = config['output']['link'],
    description = "Recommandations from newsdiscover",
    lastBuildDate = datetime.datetime.now(),
    )

#for m in catches :
now = datetime.datetime.now()
for m in sorted(catches, key=lambda x : str(lib.get_mixed_dict(x, 'published', 'updated', 'created', default=now)), reverse=True):
    if catch_qty < 0 :
        break

    title = lib.get_mixed_dict(m, 'title', default="No Title")
    title = lib.strip_html(title)
    url = lib.get_mixed_dict(m, 'url', 'link')
    guid = lib.get_mixed_dict(m, 'guid', default=url)
    description = lib.get_mixed_dict(m, 'description', 'content')
    summary = lib.get_mixed_dict(m, 'description', 'summary', default=description)
    published = lib.get_mixed_dict(m, 'published', 'updated', 'created', default=now)

    if url in ocn_urls_set or (lib.is_url(guid) and guid in ocn_urls_set) :
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
        catch_qty -= 1

    else :
        new = "..."
    print("{}\t{}\n\turl:\t{}\n\t{}\n\t{}".format(new, m['title'], url, guid, published))
    
#generate RSS
lib.print_step("Generate RSS")
rss.write_xml(open("tmp/my.rss.xml", "w"), encoding = "utf-8")


