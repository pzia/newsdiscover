#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import requests
import urllib.parse
import json
import logging
import lib

config = lib.get_config()


ocn_user = config['ocn']['user']
ocn_pwd = config['ocn']['password']
ocn_url = config['ocn']['url']
ocn_news_base_api = config['ocn']['base_api']

def get_url(route):
    logging.debug("Get url for route %s" % route)
    newsurl = urllib.parse.urljoin(ocn_url, ocn_news_base_api)
    ret = newsurl+route
    return ret

def get_params(**kwargs):
    logging.debug("Make params")
    kwargs.update({'auth' : (ocn_user, ocn_pwd), 'verify' : False})
    return kwargs

def route_get(route):
    url = get_url(route)
    params = get_params()
    logging.debug("Calling %s" % url)
    r = requests.get(url, **params)
    return json.loads(r.text)
    
def api_get(api, **kwargs):
    url = get_url("/"+api)
    args = get_params(**kwargs)
    logging.debug("Calling %s" % url)
    r = requests.get(url, **args)
    return json.loads(r.text)[api]
    
