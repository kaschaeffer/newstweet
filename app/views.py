from flask import render_template, jsonify, request
from app import app

import numpy as np
import re
import sys
import random

from TwitterApi import TwitterAPI

# The credentials file defines the Twitter authentication variables:
#  ACCESS_TOKEN_KEY
#  ACCESS_TOKEN_SECRET
#  CONSUMER_KEY
#  CONSUMER_SECRET
from config import ACCESS_TOKEN_SECRET, ACCESS_TOKEN_KEY, CONSUMER_KEY, CONSUMER_SECRET
from config import GOOGLE_API_KEY

print "ACCESS_TOKEN_KEY = "+ACCESS_TOKEN_KEY
print "ACCESS_TOKEN_SECRET = "+ACCESS_TOKEN_SECRET
print "CONSUMER_KEY = "+CONSUMER_KEY
print "CONSUMER_SECRET = "+CONSUMER_SECRET

# from cacher import cacher

#Import the Naive Bayes model...
import pickle

#Set root directory (for some reason needs to be explicitly set
#when using uwsgi)
# root_dir='./'
root_dir='/home/ubuntu/newstweet/'

pkl_file = open(root_dir+'app/naiveb_model.pkl', 'rb')
clf = pickle.load(pkl_file)
pkl_file.close()

pkl_file = open(root_dir+'app/word_ind.pkl', 'rb')
word_ind = pickle.load(pkl_file)
pkl_file.close()

#Load a list of offensive words to filter out...
bad_words = [line.strip() for line in open(root_dir+"app/bad-words.txt").readlines()]


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
      #print "I/O error({0}): {1}".format(e.errno, e.strerror)
      return jsonify(result={'other_tweets': '','news_tweets': '','errors': 2})
    #tweets = twitter.get_geotweets({'lat':lat,'lon':lon},150)

    # This is just here for diagnostics....should comment out later...

    text_tweets=[]
    for tweet in tweets:
      if 'text' in tweet:
        text_tweets.append(tweet['text'])
    text_tweets=list(set(text_tweets))
    print 'number of any raw tweets pulled in: '+str(len(text_tweets))

    if len(text_tweets)<200:
      return jsonify(result={'other_tweets': '','news_tweets': '','errors': 1})
    live_tweets=[]
    # print tweets[0]['user'].keys()
    for tweet in tweets:
      if 'text' in tweet and 'retweet_count' in tweet:
        if len(tweet['text'])>100:
          screen_name=''
          if 'user' in tweet:
            if 'screen_name' in tweet['user']:
              screen_name=tweet['user']['screen_name']
          live_tweets.append((tweet['text'],tweet['retweet_count'],tweet['id_str'],screen_name))
          #print tweet['id_str']


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
          isbad=False
          tsplit = processfilter(tweet[0]).split()
          for word in tsplit:
            if word.lower() in bad_words:
              isbad=True
              #print 'BAD WORD IS: '+word
              #print tweet
              break
          if isbad==False:
            good_tweets.append(tweet)
    except:
      print 'error filtering out bad words...'

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
    #live_other.sort(key=(lambda x:x[1]),reverse=True)

    # #print tweets[0]
    # #tweets = fetch(199)

    # print len(live_news)
    # for tweet in live_news:
    #   print tweet
    # print len(live_other)
    # for tweet in live_other:
    #   print tweet

    # print 'NEWS:'
    # for tweet in live_news:
    #   print tweet[0]
    #   print tweet[1]

    # print 'OTHER:'
    # for tweet in live_other:
    #   print tweet[0]
    #   print tweet[1]

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

    # try:
    #   cache_tweets=[]
    #   for tweet in live_news:
    #     cache_tweets.append([tweet[0],1])
    #   for tweet in live_other:
    #     cache_tweets.append([tweet[0],0])
    #   cacher(cache_tweets,lat,lon)
    # except:
    #   print 'error caching tweets'
    try:
      return jsonify(result={'other_tweets': list(zip(*live_other)[0]),'other_tweets_prob': list(zip(*live_other)[2]),'other_tweets_names': list(zip(*live_other)[3]), 'news_tweets': list(zip(*live_news)[0]),'news_tweets_prob': list(zip(*live_news)[2]),'news_tweets_names': list(zip(*live_other)[3]), 'errors': 0})
    except:
      print 'error returning'
      return jsonify(result={'other_tweets': '','news_tweets': '','errors': 1})
# def fetch(location):
#   #lat=location['lat']
#   #lon=location['lon']
#   #url='https://api.twitter.com/1.1/search/tweets.json?geocode='+lat+','+lon+',10mi&count=100'
#   #arameters = []
#   #response = json.load(twitterreq(url))
#   response = 'test'
#   return response

# @app.route('/_add_numbers',methods=['POST'])
# def add_numbers():
# #    """Add two numbers server side, ridiculous but well..."""
# #    #a = request.args.get('a', 0, type=int)
# #    #b = request.args.get('b', 0, type=int)
#     fooa = -10
#     foob = -1
#     return jsonify(result=fooa+foob)

if __name__ == '__main__':
#  pass
  response=fetch({'lat':41.03,'lon':28.92})
  print response
