#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import json
import urllib.parse
import pathlib
import requests
import logging
from bs4 import BeautifulSoup, UnicodeDammit
import random

def get_json(fname, k = None):
    with open(fname) as f :
        d = json.load(f)
    if k == None :
        return d
    else :
        return d[k]

config = get_json('config.json')
badwords = get_json(config['badwords']['filename'], 'badwords')

words_cleaned = {}


def strip_html(html):
    soup = BeautifulSoup(html, "lxml")
    return soup.getText()

def print_step(s):
    print("\n===\t"+s)

def get_mixed_dict(obj, *args, default=None):
    for a in args:
        if a in obj :
            return obj[a]
    return default

def is_url(u):
    return u[0:4] == 'http'

def clean(newtitle):

    newtitle = strip_html(newtitle)
    newtitle = newtitle.lower() #lowercase
    for c in " \n\t.,;?!:()[]{}+#$€%--_/ť='\"’–«»‘“": #remove punctuation FIXME : use french parser ?
        newtitle = newtitle.replace(c, " ")
        newtitle = newtitle.replace("  ", " ")
    #remove badwords - split, remove, join
    words = [w for w in newtitle.split(" ") if w not in badwords and len(w) > 1]
    for w in words :
        if w in words_cleaned :
            words_cleaned[w] += 1
        else :
            words_cleaned[w] = 1
    return " ".join(words)
    
def save_words():
    with open('logs/words.json.log', 'w') as outfile:
        json.dump(words_cleaned, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

def rss_extract(url, root = False):
    try :
        r = requests.get(url, allow_redirects=True)
    except :
        return []
    details_url = urllib.parse.urlparse(url)
    filename = pathlib.PurePosixPath(details_url.path).stem
    
    html_doc = r.text
    soup = BeautifulSoup(html_doc, "lxml")
    feeds = []
    # extract URL and type
    for t in ('rss', 'atom'):
        feed_urls = soup.findAll("link", rel="alternate", type="application/%s+xml" % t)

        for feed_link in feed_urls:
            feed = feed_link.get("href", None)
            # if a valid URL is there
            if not feed :
                continue
            if "comment" in feed :
                logging.debug("Discard(comment):\t", feed)
                continue
            if url in feed and not root :
                logging.debug("Discard(in feed):\t", feed)
                continue
            if len(filename) > 1 and filename in feed and not root:
                logging.debug("Discard(filename):\t", feed)
                continue

            feed = urllib.parse.urljoin(url, feed)
            if feed not in feeds :
                feeds.append(feed)
        if len(feeds) > 0 :
            break
        if not root :
            feeds += rss_extract(details_url.scheme+"://"+details_url.netloc, True)
    return feeds

def load_user_agents(uafile="datas/user_agents.txt"):
    """
    uafile : string
        path to text file of user agents, one per line
    """
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1-1])
    return random.choice(uas)

