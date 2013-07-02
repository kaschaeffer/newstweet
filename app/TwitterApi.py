''' 
TwitterApi.py
Kevin Schaeffer
(newstweet project)
June 2013

twitterapi is a module that gives a wrapper for the Twitter API v1.1.

'''

import oauth2 as oauth
import urllib2 as urllib
import json

import gevent
import gevent.monkey
gevent.monkey.patch_all()


class TwitterAPI(object):
    '''
    TwitterAPI wrapper class.

    __init__(ACCESS_TOKEN_SECRET,
            ACCESS_TOKEN_KEY, 
            CONSUMER_KEY, 
            CONSUMER_SECRET)        -the constructor takes oAuth keys and tokens ( all strings)
                                    that are generated when registering the app with Twitter.

    _request(url)                   -private method that sends an oAuth GET request
                                    to url (string) and returns a dictionary

    get_geotweets(location,radius)  -returns a list of tweets (each a dictionary) coming from 
                                    location (dict with keys 'lat' and 'lon').  Inludes everything 
                                    that is at most a distance radius (int) in miles away from 
                                    the location.
    '''

    signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

    http_handler  = urllib.HTTPHandler(debuglevel=0)
    https_handler = urllib.HTTPSHandler(debuglevel=0)

    def __init__(self,
                ACCESS_TOKEN_SECRET,
                ACCESS_TOKEN_KEY, 
                CONSUMER_KEY, 
                CONSUMER_SECRET):
        ''' Constructs the oauth token and consumer keys
        and initializes the http and https handlers
        '''
        self.oauth_token    = oauth.Token(key=ACCESS_TOKEN_KEY, secret=ACCESS_TOKEN_SECRET)
        self.oauth_consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)

    def _request(self,url):
        ''' Private method that sends an oAuth GET request to url 
        and returns the response as a dictionary object. 
        '''

        # Construct the oAuth request
        req = oauth.Request.from_consumer_and_token(self.oauth_consumer,
                                                 token=self.oauth_token,
                                                 http_method="GET",
                                                 http_url=url, 
                                                 parameters=[])

        # Sign the request
        req.sign_request(self.signature_method_hmac_sha1, self.oauth_consumer, self.oauth_token)

        # Update request url using oAuth authentication info
        url = req.to_url()

        # Open URL and get response
        opener = urllib.OpenerDirector()
        opener.add_handler(self.http_handler)
        opener.add_handler(self.https_handler)
        response = opener.open(url, None)

        # Close URL
        opener.close()

        # Convert the JSON object into a dictionary and return it
        return json.load(response)

    def get_geotweets(self,location,radius):
        ''' Asks the Twitter API for the most recent tweets that are within
        radius (in miles) of the location, which is specified by latitute (location['lat'])
        and longitude (location['lon']).  

        Returns a list of dictionaries
        where each dictionary is a tweet and includes both the tweet text
        and tweet metadata (geotag, user info, retweet count, etc...).
        '''

        # Extract the latitude and longitude from location
        lat=float(location['lat'])
        lon=float(location['lon'])

        # Initialize array that will hold all the tweets.
        all_response=[]

        # Construct the URL for the Twitter API request
        url='https://api.twitter.com/1.1/search/tweets.json?geocode='
        url=url+str(lat)+','+str(lon)+','+str(radius)+'mi&count=100&lang=en&include_entities=1'
        
        # Get first 100 tweets from the Twitter API
        response = self._request(url)

        all_response.extend(response)

        # Check to see if there are any statuses in response.
        # If not, raise exception using Twitter error message if it exists
        # Often this occurs if the API rate limit is exceeded, resulting
        # in error code 88
        if 'statuses' not in response:
            if 'errors' in response:
                print response['errors']
                raise IOError, response['errors'][0]['code']
            else:
                raise IOError, 'Twitter API error with no message'

        id=0

        for tweet in response['statuses']:
            if 'id_str' in tweet:
                id=int(tweet['id_str'])
                break

        if not id:
            return all_response

        # We need to obtain more than 100 tweets from the twitter API.  This can be done by 
        # explicitly including max_id=xxx in the query, where max_id is the maximum tweet id
        # (id_str) that we allow.  Since tweet ids are *roughly* sequential, a lower max_id
        # allows us to collect slightly older tweets.  
        #
        # By decrementing the max_id we can collect a larger batch of (older) tweets, 100 at 
        # a time.  diff is the amount by which we decrement for each search.  It was chosen
        # experimentally...
        #
        # Note this is all a hack to get around paging being eliminated from the
        # Twitter API in going from v1 to v1.1.
        diff= -1701694583194

        # Number of calls to the twitter API
        # ncalls * 100 = total number of tweets collected
        ncalls=9

        # Create list of max ids
        max_ids=[id+(diff*(_+1)) for _ in range(ncalls)]

        # Define search url template
        url='https://api.twitter.com/1.1/search/tweets.json?geocode='+str(lat)+','+str(lon)+','
        url=url+str(radius)+'mi&count=100&lang=en&include_entities=1&max_id='

        # Create list of search urls with max_ids
        urls=[(url+str(max_id)) for max_id in max_ids]

        # Making sequential calls to the Twitter API is too slow.
        # We use greenlets to make fast asynchronous calls
        # and require them to finish after timeout seconds.
        timeout=10
        jobs = [gevent.spawn(self._request,url) for url in urls]
        gevent.joinall(jobs,timeout=timeout)

        # Extract tweets from the greenlet jobs
        # and add them to all_response
        if jobs:
            for job in jobs:
                if job.value and 'statuses' in job.value:
                    all_response.extend(job.value['statuses'])

        return all_response

