from flask import render_template, jsonify, request
from app import app
import json

import gevent
import gevent.monkey
gevent.monkey.patch_all()

import oauth2 as oauth
import urllib2 as urllib
import tweet_downloader
import numpy as np
import re
import random

# The credentials file defines the Twitter authentication variables:
#  access_token_key
#  access_token_secret
#  consumer_key
#  consumer_secrets
import credentials

#from cacher import cacher

#Import the Naive Bayes model...
import pickle
pkl_file = open('./app/naiveb_model.pkl', 'rb')
clf = pickle.load(pkl_file)
pkl_file.close()

pkl_file = open('./app/word_ind.pkl', 'rb')
word_ind = pickle.load(pkl_file)
pkl_file.close()

#Load a list of offensive words to filter out...
bad_words = [line.strip() for line in open("./app/bad-words.txt").readlines()]


_debug = 0

oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
oauth_consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)

signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

http_method = "GET"


http_handler  = urllib.HTTPHandler(debuglevel=_debug)
https_handler = urllib.HTTPSHandler(debuglevel=_debug)

# Sets the radius for all searches
RADIUS = 150

# How to perturb the longitude and latitude if the twitter API
# doesn't give next url
PERT = 1.5

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


'''
Construct, sign, and open a twitter request
using the hard-coded credentials above.
'''
def twitterreq(url):
  req = oauth.Request.from_consumer_and_token(oauth_consumer,
                                             token=oauth_token,
                                             http_method="GET",
                                             http_url=url, 
                                             parameters=[])


  req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)

  headers = req.to_header()

  if http_method == "POST":
    encoded_post_data = req.to_postdata()
  else:
    encoded_post_data = None
    url = req.to_url()

  opener = urllib.OpenerDirector()
  opener.add_handler(http_handler)
  opener.add_handler(https_handler)
  #response=''
  response = opener.open(url, encoded_post_data)

  return json.load(response)

def get_html(id_str):
  url='https://api.twitter.com/1.1/statuses/oembed.json?id='+id_str
  try:
    response = twitterreq(url)
    print response.keys()
    print response
    return response['html']
  except:
    print 'Error getting fancy tweet styling'
    return ''

def fetch(location):
  lat=float(location['lat'])
  lon=float(location['lon'])
  
  #Get first tweet
  
  next_url_flag=False
  call_count=0
  max_call=3

  all_response=[]
  max_ids=[0,0]

  url='https://api.twitter.com/1.1/search/tweets.json?geocode='+str(lat)+','+str(lon)+','+str(RADIUS)+'mi&count=100&lang=en&include_entities=1'
  try:
    response = twitterreq(url)
  except:
    print 'Error talking to Twitter API...'
  
  if 'statuses' not in response:
    return response

  print response.keys()
  print len(response['statuses'])
  id=''
  i=0
  while not id:
    if 'id_str' in response['statuses'][i]:
      print i
      print response['statuses'][i]['id_str']
      id=response['statuses'][i]['id_str']
      break
    i=i+1
  max_ids[0]=int(id)

  diff= -1701694583194
  ncalls=9
  max_id_list=[(max_ids[0]+(diff*(i+1))) for i in range(ncalls)]
  url='https://api.twitter.com/1.1/search/tweets.json?geocode='+str(lat)+','+str(lon)+','+str(RADIUS)+'mi&count=100&lang=en&include_entities=1&max_id='
  urls=[(url+str(max_id)) for max_id in max_id_list]
  print 'preparing to make asynchronous calls...'
  jobs = [gevent.spawn(twitterreq,q) for q in urls]
  print 'ready to join asynchronous calls...'
  gevent.joinall(jobs,timeout=10)
  print 'asynchronous calls joined...'
  # try:
  #   for job in jobs:
  #     for tw in job.value['statuses']:
  #       print tw['text']
  # except:
  #   print 'error processing incoming tweets'
  for job in jobs:
    try:
      #print 'threaded number of tweets is '+str(len(job.value['statuses']))
      all_response.extend(job.value['statuses'])
    except:
      print 'could not access statuses...'
      #all_response.extend(tweets)
  print len(all_response)
  return all_response


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/get_tweet',methods=['POST'])
def get_tweet():
    #foo = request.args.get('location',0,type=int)
    try:
      lat = request.form['lat']
      lon = request.form['lon']
      tweets = fetch({'lat':lat,'lon':lon})
    except:
      print 'error getting'

    # This is just here for diagnostics....should comment out later...
    try:
      text_tweets=[]
      for tweet in tweets:
        if 'text' in tweet:
          text_tweets.append(tweet['text'])
      text_tweets=list(set(text_tweets))
      print 'number of any raw tweets pulled in: '+str(len(text_tweets))

      if len(text_tweets)<300:
        return jsonify(result={'other_tweets': '','news_tweets': '','errors': 1})
      live_tweets=[]
      for tweet in tweets:
        if 'text' in tweet and 'retweet_count' in tweet:
          if len(tweet['text'])>100:
            live_tweets.append((tweet['text'],tweet['retweet_count'],tweet['id_str']))
            #print tweet['id_str']
    except:
      print 'error getting tweets blah'

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
        just_tweets.append((tweet[0],tweet[2]))
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

    try:
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
              live_news.append((live_tweets[i][0],live_tweets[i][1],live_pred_prob[i][0]))
          else:
              live_other.append((live_tweets[i][0],live_tweets[i][1],live_pred_prob[i][0]))
    except:
      print 'error filtering'
      live_news=['a']
      live_other=['b']

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

    try:
      return jsonify(result={'other_tweets': list(zip(*live_other)[0]),'other_tweets_prob': list(zip(*live_other)[2]), 'news_tweets': list(zip(*live_news)[0]),'news_tweets_prob': list(zip(*live_news)[2]), 'errors': 0})
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