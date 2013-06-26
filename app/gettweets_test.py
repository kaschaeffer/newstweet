from flask import render_template, jsonify, request
# from app import app
import json

import oauth2 as oauth
import urllib2 as urllib

# Credentials
access_token_key = '1484063558-2rxxwvMJbuN1UBt6W7gFu1AvnCcj4FVo9Bsuv89'
access_token_secret = 'RDatqGuGNDk9fdo72GK9E87Jbtj6vJrobOx8del8'

consumer_key = 'mk3pDBFvIOh6yj6vKgaUA'
consumer_secret = 'fMjU1EYyGOd8isqnujjJp403NQJeIH8ZPzdJuJ2IQ'

_debug = 0

oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
oauth_consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)

signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

http_method = "GET"


http_handler  = urllib.HTTPHandler(debuglevel=_debug)
https_handler = urllib.HTTPSHandler(debuglevel=_debug)

'''
Construct, sign, and open a twitter request
using the hard-coded credentials above.
'''
def twitterreq(url, method, parameters):
  req = oauth.Request.from_consumer_and_token(oauth_consumer,
                                             token=oauth_token,
                                             http_method=http_method,
                                             http_url=url, 
                                             parameters=parameters)


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

  return response

def fetch(location):
  lat=location['lat']
  lon=location['lon']
  url='https://api.twitter.com/1.1/search/tweets.json?geocode='+str(lat)+','+str(lon)+',10mi&count=100'
  url='https://api.twitter.com/1.1/search/tweets.json?geocode=37.781157,-122.398720,10mi&count=100'
  response = json.load(twitterreq(url, "GET", []))
  #response='foo'
  return response['statuses']


# @app.route('/')
# @app.route('/index')
# def index():
#     return render_template("index.html")

# @app.route('/get_tweet',methods=['POST'])
# def get_tweet():
#     #foo = request.args.get('location',0,type=int)
#     lat = request.form['lat']
#     lon = request.form['lon']
#     tweets = fetch({'lat':lat,'lon':lon})
#     #tweets = fetch(199)
#     top_tweet='sample tweet'
#     if 'text' in tweets[0]:
#          top_tweet=tweets[0]['text']
#     foo = 22

#     #print foo
#     return jsonify(result={'text': top_tweet,'loc num': foo})

if __name__ == '__main__':
#  pass
  response=fetch({'lat':37.781157,'lon':-122.398720})
  print response[2]['text']