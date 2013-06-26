
import time
import oauth2 as oauth
import urllib2 as urllib
import threading
from Queue import Queue
from random import choice
import json


def twitterreq(url, method, parameters):
    #print type(url)
    #url=urllib.quote(str(url))
    #url=urllib.quote(unicode(url).encode('utf-8'))
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
        #print url
    
    opener = urllib.OpenerDirector()
    opener.add_handler(http_handler)
    opener.add_handler(https_handler)
    #response=''
    response = opener.open(url, encoded_post_data)

    return response

def get_tweet(max_id,location):
    """ Download a random wikipiedia article"""
    try:
        lat=location['lat']
        lon=location['lon']
        search_param='geocode='+str(lat)+','+str(lon)+',10mi&lang=en&result_type=popular&max_id='+str(max_id)
    except:
        return "failed to form search url..."
    #search_param='geocode='+str(lat)+','+str(lon)+',10mi'
    try:
        #page = json.load(twitterreq('https://api.twitter.com/1.1/search/tweets.json?'+search_param,'GET',[]))
        #time.sleep(1.0)
        page = json.load(twitterreq('https://api.twitter.com/1.1/search/tweets.json?q=blue','GET',[]))
    except:
        return "error in talking to twitter API"
        #page='error'
    #page = 'foo'
    #time.sleep(0.6)
    try:
        #time.sleep(0.2)
        # 
        # Commenting out the code below causes the threads
        # to *sometimes* hang when calling .join()...
        #
        # if namespace != None: 
        #     url += '/' + namespace
        # req = urllib2.Request(url, None, { 'User-Agent' : 'x'})
        # page = urllib2.urlopen(req).readlines()
        # page = json.load(twitterreq('http://search.twitter.com/search.json?q=blue','GET',[]))
        # page = 'foo'
        return page
    except (urllib.HTTPError, urllib.URLError):
        print "Failed to get article"
        raise

class TweetDownloader(threading.Thread):
    """ A class to download a user's top Artists

    To be used as an individual thread to take
    a list of users from a shared queue and 
    download their top artists 
    """

    def __init__(self, queue,location):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.articles = []
        self.queue = queue
        self.location = location

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def get_articles(self):
        return self.articles

    def run(self):
        while True:
            if self.stopped():
                return
            if self.queue.empty(): 
                time.sleep(0.1)
                continue
            try:
                max_id = self.queue.get()
            except:
                pass
                #print "Failed to get off queue"
            try:
                #article = get_random_article(namespace)
                article = get_tweet(max_id,location)
            except:
                pass
                #print "Failed to call twitter API"
            try:
                self.articles.append(article)
            except:
                pass
                #print "Failed to append article"
            try:
                pass
                #print "Successfully processed max_id: ", max_id,
                #print " by thread: ", self.ident
                # No need for a 'queue.task_done' since we're 
                # not joining on the queue
            except:
                pass
                #print "Failed to print.."


def get_tweets(max_ids, location, num_threads=4):
    """ Download 'num_documents' random documents from
    the lastfm api.
    Each document contains the top artists for a random
    user from LastFM.
    These documents are downloaded in parallel using
    separate threads

    """

    wiki_namespaces = """
    Main
    User
    Wikipedia
    File
    MediaWiki
    Template
    Help
    Category
    Portal
    Book""".split()

    q = Queue()
    threads = []

    try:
        # Create the threads and 'start' them.
        # At this point, they are listening to the
        # queue, waiting to consume
        for i in xrange(num_threads):
            thread = TweetDownloader(q,location)
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)

        # We want to download one page for each namespace,
        # so we put every namespace in the queue, and
        # these will be processed by the threads
        for i in xrange(len(max_ids)):
            max_id = max_ids[i]
            q.put(max_id)

        # Wait for all entries in the queue
        # to be processed by our threads
        # One could do a queue.join() here, 
        # but I prefer to use a loop and a timeout
        while not q.empty():
            time.sleep(1.0)

        # Terminate the threads once our
        # queue has been fully processed
        for thread in threads:
            thread.stop()
        print "getting ready to join the threads..."
        for thread in threads:
            thread.join()
        print "threads joined..."

    except:
        print "Main thread hit exception"
        # Kill any running threads
        for thread in threads:
            thread.stop()
        for thread in threads:
            thread.join()
        raise

    # Collect all downloaded documents
    # from our threads
    documents = []
    for thread in threads:
        documents.extend(thread.get_articles())

    return documents


# if __name__ == "__main__":
#     # Credentials
#     access_token_key = '1484063558-2rxxwvMJbuN1UBt6W7gFu1AvnCcj4FVo9Bsuv89'
#     access_token_secret = 'RDatqGuGNDk9fdo72GK9E87Jbtj6vJrobOx8del8'

#     consumer_key = 'mk3pDBFvIOh6yj6vKgaUA'
#     consumer_secret = 'fMjU1EYyGOd8isqnujjJp403NQJeIH8ZPzdJuJ2IQ'

#     _debug = 0

#     oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
#     oauth_consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)

#     signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()

#     http_method = "GET"


#     http_handler  = urllib.HTTPHandler(debuglevel=_debug)
#     https_handler = urllib.HTTPSHandler(debuglevel=_debug)
#     location = {'lat': 37.781157,'lon': -122.398720}

#     max_ids=[346463645078790144, 346457327223820289, 346451009368850434, 346444691513880579, 346438373658910724]

#     documents = get_tweets(max_ids,location)
#     full_tweets=[]
#     for document in documents:
#         full_tweets.extend([tweet for tweet in document['statuses']])
#     for tweet in full_tweets:
#         print tweet['text']
#         if 'retweet_count' in tweet:
#             print tweet['retweet_count']
#     print "length of tweets = "+str(len(full_tweets))
#     #for document in documents:
#     #    print document[:10]
#     #print 'now try doing this without threading'
#     #tweet=get_tweet(12398)
#     #print tweet
