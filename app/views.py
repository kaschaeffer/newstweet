from flask import render_template, jsonify, request
from app import app

import numpy as np
import re
import sys
import random

from TwitterApi import TwitterAPI
from cacher import cacher,loader

# config.py holds the Twitter API and Google Maps API authentication variables
from config import ACCESS_TOKEN_SECRET, ACCESS_TOKEN_KEY, CONSUMER_KEY, CONSUMER_SECRET
from config import GOOGLE_API_KEY

# import filters used for processing and classifying tweets
from process import process, processfilter, classify

# Sets the radius for all searches
RADIUS = 150

# Name of all pages in the site
categories=[{'name': 'Home','url': 'index'},
            {'name': 'About','url': 'about'},
            {'name': 'Contact','url': 'contact'}]

# Create a twitter API object
twitter = TwitterAPI(ACCESS_TOKEN_SECRET,
          ACCESS_TOKEN_KEY, 
          CONSUMER_KEY, 
          CONSUMER_SECRET)

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
                          category='Home',
                          categories=categories,
                          APIkey=GOOGLE_API_KEY)

@app.route('/about')
def about():
    return render_template("about.html",category='About',categories=categories)

@app.route('/about')
def about():
    return render_template("about.html",category='About',categories=categories)

@app.route('/contact')
def contact():
    return render_template("contact.html",category='Contact',categories=categories)

@app.route('/get_tweet',methods=['POST'])
def get_tweet():
    # Get the latitute and longitude for the request
    lat = request.form['lat']
    lon = request.form['lon']

    # Make a call to the Twitter API
    try:
      tweets = twitter.get_geotweets({'lat':lat,'lon':lon},RADIUS)
    except IOError as e:
      # If there's a communication error with twitter (e.g. rate limiting)
      # try to pull tweets from cache
      print 'going to cache...'
      news_tweets,other_tweets = loader(lat,lon)

      if len(news_tweets)>0:
        return jsonify(result={'other_tweets': list(zip(*other_tweets)[0]),'other_tweets_names': list(zip(*other_tweets)[1]),
          'news_tweets': list(zip(*news_tweets)[0]),'news_tweets_names': list(zip(*news_tweets)[1]),'errors': 0})
      else:
        print 'nothing in cache...'
        return jsonify(result={'other_tweets': '','news_tweets': '','errors': 2})

    # Clean up tweets and use the Naive Bayes Model to
    # classify the top news and non-news tweets
    live_news,live_other = classify(tweets)

    # Cache tweets for future use
    cache_tweets=[]
    for tweet in live_news:
      cache_tweets.append([tweet[0],tweet[3],1])
    for tweet in live_other:
      cache_tweets.append([tweet[0],tweet[3],0])
    cacher(cache_tweets,lat,lon)

    try:
      return jsonify(result={'other_tweets': list(zip(*live_other)[0]),'other_tweets_prob': list(zip(*live_other)[2]),'other_tweets_names': list(zip(*live_other)[3]), 'news_tweets': list(zip(*live_news)[0]),'news_tweets_prob': list(zip(*live_news)[2]),'news_tweets_names': list(zip(*live_other)[3]), 'errors': 0})
    except:
      print 'error returning'
      return jsonify(result={'other_tweets': '','news_tweets': '','errors': 1})

if __name__ == '__main__':
  # Unit test to make sure that the loader
  # is correctly pulling the necessary tweets
  tweets = twitter.get_geotweets({'lat':41.03,'lon':28.92},RADIUS)
  print tweets
