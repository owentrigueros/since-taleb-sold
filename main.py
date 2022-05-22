#!/bin/env python

import os
from datetime import datetime, timedelta
import configparser

import requests
from requests_oauthlib import OAuth1

tweet_template = """
Today #BTC is valued at {btc_today}.

The price of bitcoin has gone {up_down} {change}% since Taleb sold.
"""

bot_user_id = "3805104374"
btc_when_taleb_sold = 47164.0

root_dir = os.path.dirname(os.path.realpath(__file__))
img_dir = os.path.join(root_dir, "img")

def main():
    config = configparser.RawConfigParser()
    config.read(os.path.join(root_dir, "keys.ini"))
    config_keys = config["keys"]

    consumer_key = config_keys["consumer_key"]
    consumer_secret = config_keys["consumer_secret"]
    access_token = config_keys["access_token"]
    access_token_secret = config_keys["access_token_secret"]

    auth = connect_to_oauth(consumer_key, consumer_secret,
                            access_token, access_token_secret)

    btc_today = get_btc()
    change_since_taleb_sold = round((((btc_today - btc_when_taleb_sold) / btc_when_taleb_sold ) * 100), 2)
    up = True if change_since_taleb_sold > 0 else False

    if up:
        files = {"media" : open(os.path.join(img_dir, 'taleb-bad.png'), 'rb')}
    else:
        files = {"media" : open(os.path.join(img_dir, 'taleb-good.png'), 'rb')}

    payload = {"media_category" : "TWEET_IMAGE", "additional_owners" : bot_user_id}
    media_id = upload_media(auth, payload, files)

    btc_today_formatted = "${:,.2f}".format(btc_today)
    text = tweet_template.format(btc_today=btc_today_formatted,
                                 up_down="up" if up else "down",
                                 change=change_since_taleb_sold)
    payload = {"text" : text, "media" : {"media_ids" : [media_id]}}
    tweet(auth, payload)

def connect_to_oauth(consumer_key, consumer_secret, access_token, access_token_secret):
    auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)
    return auth

def tweet(auth, payload):
    url = "https://api.twitter.com/2/tweets"
    r = requests.post(auth=auth, url=url, json=payload,
                      headers={"Content-Type": "application/json"})
    print(r.content)

def upload_media(auth, payload, files):
    url = "https://upload.twitter.com/1.1/media/upload.json"
    r = requests.post(auth=auth, url=url, data=payload, files=files)
    r_json = r.json()
    media_id = r_json["media_id_string"]
    return media_id

def get_btc():
    url = "https://api.coinbase.com/v2/prices/spot?currency=USD"
    r = requests.get(url)
    r_json = r.json()
    btc = float(r_json["data"]["amount"])
    return btc

if __name__=="__main__":
    main()
