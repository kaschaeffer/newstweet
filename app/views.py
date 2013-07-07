from flask import render_template, jsonify, request
from app import app

import numpy as np
import re
import sys
import random
import pickle

from TwitterApi import TwitterAPI
from cacher import cacher,loader

# config.py holds the Twitter API and Google Maps API authentication variables
from config import ACCESS_TOKEN_SECRET, ACCESS_TOKEN_KEY, CONSUMER_KEY, CONSUMER_SECRET
from config import GOOGLE_API_KEY

#Import the Naive Bayes model...
#Set root directory (for some reason needs to be explicitly set
#when using uwsgi)
root_dir='./'
#root_dir='/home/ubuntu/newstweet/'

pkl_file = open(root_dir+'app/model/naiveb_model.pkl', 'rb')
clf = pickle.load(pkl_file)
pkl_file.close()

pkl_file = open(root_dir+'app/model/word_ind.pkl', 'rb')
word_ind = pickle.load(pkl_file)
pkl_file.close()

#import filter for removing any tweets containing offensive content
filter_words = [line.strip() for line in open(root_dir+"app/model/filter-words.txt").readlines()]


# Sets the radius for all searches
RADIUS = 150


def process(tweet):
    tweet_out=tweet
    regex=re.compile(r'http:')
    tweet_out = (regex.split(tweet_out))[0]
    regex=re.compile(r':')
    tweet_out = regex.sub(' : ',tweet_out)
    regex=re.compile(r';')
    tweet_out = regex.sub(' ; ',tweet_out)
    regex=re.compile(r',')
    tweet_out = regex.sub(' , ',tweet_out)
    regex=re.compile(r'-')
    tweet_out = regex.sub(' - ',tweet_out)
    regex=re.compile(r'\?')
    tweet_out = regex.sub(' \? ',tweet_out)
    regex=re.compile(r'!')
    tweet_out = regex.sub(' ! ',tweet_out)
    regex=re.compile(r'\.')
    tweet_out = regex.sub(r' . ',tweet_out)
    regex=re.compile(r'-')
    tweet_out = regex.sub(' - ',tweet_out)
    regex=re.compile(r"'")
    tweet_out = regex.sub(r" ' ",tweet_out)
    regex=re.compile(r'"')
    tweet_out = regex.sub(r' " ',tweet_out)
    regex=re.compile(r'@[A-Za-z0-9_]*')
    tweet_out = regex.sub('@',tweet_out)
    regex=re.compile(r'#[A-Za-z0-9_]*')
    tweet_out = regex.sub('#',tweet_out)
    regex=re.compile(r'\\U')
    tweet_out = regex.sub(r' \\U ',tweet_out)
    return tweet_out

def processfilter(tweet):
    tweet_out=tweet
    regex=re.compile(r'http:')
    tweet_out = (regex.split(tweet_out))[0]
    regex=re.compile(r':')
    tweet_out = regex.sub(' : ',tweet_out)
    regex=re.compile(r';')
    tweet_out = regex.sub(' ; ',tweet_out)
    regex=re.compile(r',')
    tweet_out = regex.sub(' , ',tweet_out)
    regex=re.compile(r'-')
    tweet_out = regex.sub(' - ',tweet_out)
    regex=re.compile(r'\?')
    tweet_out = regex.sub(' \? ',tweet_out)
    regex=re.compile(r'!')
    tweet_out = regex.sub(' ! ',tweet_out)
    regex=re.compile(r'\.')
    tweet_out = regex.sub(r' . ',tweet_out)
    regex=re.compile(r'-')
    tweet_out = regex.sub(' - ',tweet_out)
    regex=re.compile(r'\_')
    tweet_out = regex.sub(' _ ',tweet_out)
    regex=re.compile(r"'")
    tweet_out = regex.sub(r" ' ",tweet_out)
    regex=re.compile(r'"')
    tweet_out = regex.sub(r' " ',tweet_out)
    regex=re.compile(r'\@')
    tweet_out = regex.sub(' @ ',tweet_out)
    regex=re.compile(r'\#')
    tweet_out = regex.sub(' # ',tweet_out)
    regex=re.compile(r'\\U')
    tweet_out = regex.sub(r' \\U ',tweet_out)
    return tweet_out

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

@app.route('/contact')
def contact():
    return render_template("contact.html",category='Contact',categories=categories)

@app.route('/get_tweet',methods=['POST'])
def get_tweet():
    # Get the latitute and longitude for the request
    lat = request.form['lat']
    lon = request.form['lon']

    try:
      tweets = twitter.get_geotweets({'lat':lat,'lon':lon},150)
    except IOError as e:
      #try to pull tweets from cache
      print 'going to cache...'
      news_tweets,other_tweets = loader(lat,lon)
      # print list(zip(*other_tweets)[0])
      # print list(zip(*other_tweets)[1])
      # print list(zip(*news_tweets)[0])
      # print list(zip(*news_tweets)[1])
      print other_tweets
      print news_tweets

      if len(news_tweets)>0:
        return jsonify(result={'other_tweets': list(zip(*other_tweets)[0]),'other_tweets_names': list(zip(*other_tweets)[1]),
          'news_tweets': list(zip(*news_tweets)[0]),'news_tweets_names': list(zip(*news_tweets)[1]),'errors': 0})
      else:
        print 'nothing in cache...'
        return jsonify(result={'other_tweets': '','news_tweets': '','errors': 2})
    #tweets = twitter.get_geotweets({'lat':lat,'lon':lon},150)

    #test out loading older tweets from the cache...
    loader(lat,lon)

    text_tweets=[]
    for tweet in tweets:
      if 'text' in tweet:
        text_tweets.append(tweet['text'])
    text_tweets=list(set(text_tweets))
    print 'number of any raw tweets pulled in: '+str(len(text_tweets))

    if len(text_tweets)<200:
      #try to pull tweets from cache
      print 'going to cache...'
      news_tweets,other_tweets = loader(lat,lon)
      print news_tweets
      print other_tweets
      if len(news_tweets)>0:
        return jsonify(result={'other_tweets': zip(*other_tweets)[0],'other_tweets_names': zip(*other_tweets)[1],
          'news_tweets': zip(*news_tweets)[0],'news_tweets_names': zip(*news_tweets)[1],'errors': 0})
      else:
        print 'nothing in cache...'
        return jsonify(result={'other_tweets': '','news_tweets': '','errors': 1})
    live_tweets=[]
    # print tweets[0]['user'].keys()
    for tweet in tweets:
      if 'text' in tweet and 'retweet_count' in tweet:
        if len(tweet['text'])>100:
          screen_name=''
          tweet_text=tweet['text']
          tweet_rtcount=tweet['retweet_count']
          if 'user' in tweet:
            if 'screen_name' in tweet['user']:
              screen_name=tweet['user']['screen_name']

          # check to see if its a retweet
          # if so use the original message
          if 'retweeted_status' in tweet:
            if 'text' in tweet['retweeted_status']:
              tweet_text=tweet['retweeted_status']['text']
            if 'user' in tweet['retweeted_status'] and 'screen_name' in tweet['retweeted_status']['user']:
              screen_name=tweet['retweeted_status']['user']['screen_name']
          live_tweets.append((tweet_text,tweet_rtcount,tweet['id_str'],screen_name))
          


    # Remove duplicates
    tweet_text_list=[]
    live_tweets2=[]
    try:
      for tweet in live_tweets:
        if tweet[0] not in tweet_text_list:
          live_tweets2.append(tweet)
          tweet_text_list.append(tweet[0])
      print 'with duplicates removed: '+str(len(live_tweets2))
      print 'with no duplicates: '+str(len(live_tweets))
    except:
      print 'error removing duplicates'

    try:
      live_tweets=live_tweets2
    except:
      print 'error removing a 2'

    try:
      live_tweets=list(set(live_tweets))
      print 'number of long raw tweets pulled in: '+str(len(live_tweets))
    except:
      print 'error removing duplicates...'

    #print 'length = '+str(len(live_tweets))
    try:
      live_tweets.sort(key=(lambda x: x[1]),reverse=True)
      #live_tweets=list(set(live_tweets))
      max_size=150
      if len(live_tweets)>max_size:
        live_tweets=live_tweets[:max_size]
      just_tweets=[]

      # print 'the # of retweets are...'
      # for tweet in live_tweets:
      #   print tweet[0]
      #   print tweet[1]

      for tweet in live_tweets:
        just_tweets.append((tweet[0],tweet[2],tweet[3]))
      # for i in range(20):
      #   print live_tweets[i][0]
      #   print live_tweets[i][1]
      live_tweets=list(set(just_tweets))
    except:
      print 'blah'

    try:
      good_tweets=[]
      for tweet in live_tweets:
          filterout=False
          tsplit = processfilter(tweet[0]).split()
          for word in tsplit:
            if word.lower() in filter_words:
              filterout=True
              break
          if filterout==False:
            good_tweets.append(tweet)
    except:
      print 'error filtering...'

    try:
      live_tweets=good_tweets
      nfeatures=len(word_ind)
      nlive=len(live_tweets)
      live_mat=np.zeros((nlive,nfeatures))
    except:
      print 'error initializing classification features'


    for n_ind in range(len(live_tweets)):
        tsplit = process(live_tweets[n_ind][0]).split()
        for word in tsplit:
            if word in word_ind:
                lword=word.lower()
                live_mat[n_ind,word_ind[lword]]+=1
    live_pred = list(clf.predict(live_mat))
    live_pred_prob = list(clf.predict_proba(live_mat))
    live_news=[]
    live_other=[]
    for i in range(len(live_pred)):
        if live_pred[i]:
            live_news.append((live_tweets[i][0],live_tweets[i][1],live_pred_prob[i][0],live_tweets[i][2]))
        else:
            live_other.append((live_tweets[i][0],live_tweets[i][1],live_pred_prob[i][0],live_tweets[i][2]))

    try:
      live_news.sort(key=(lambda x:x[2]))
    except:
      print 'error sorting again!'

    ntweets_send=3

    try:
      if len(live_news)>ntweets_send:
        live_news=live_news[:ntweets_send]
    except:
      print 'error truncating live_news'

    try:
      for tw in live_news:
        pass
        #print tw
    except:
      print 'error printing out news'

    try:
      if len(live_other)>ntweets_send:
        live_other=live_other[:ntweets_send]
    except:
      print 'error truncating live_news'

    try:
      for tw in live_other:
        pass
        #print tw
    except:
      print 'error printing out news'

    cache_tweets=[]
    for tweet in live_news:
      cache_tweets.append([tweet[0],tweet[3],1])
    for tweet in live_other:
      cache_tweets.append([tweet[0],tweet[3],0])
    cacher(cache_tweets,lat,lon)
    try:
      pass
    except:
      print 'error caching tweets'
    try:
      return jsonify(result={'other_tweets': list(zip(*live_other)[0]),'other_tweets_prob': list(zip(*live_other)[2]),'other_tweets_names': list(zip(*live_other)[3]), 'news_tweets': list(zip(*live_news)[0]),'news_tweets_prob': list(zip(*live_news)[2]),'news_tweets_names': list(zip(*live_other)[3]), 'errors': 0})
    except:
      print 'error returning'
      return jsonify(result={'other_tweets': '','news_tweets': '','errors': 1})

if __name__ == '__main__':
#  pass
  response=fetch({'lat':41.03,'lon':28.92})
  print response
