import mysql.connector
from mysql.connector import errorcode
import time

# This module is used for storing past geographical search queries.
# Can be useful if the twitter API fails and we need backup data...

DB_NAME='cache'

def cacher(tweets,lat,lon):
  cnx = mysql.connector.connect(user='kevinschaeffer')
  cursor = cnx.cursor()
  cursor.execute('USE '+DB_NAME)
  now=int(time.time())
  #insert_str="INSERT INTO events(time,lat,lon) VALUES(%f,%f,%f);"
  #insert_str="INSERT INTO events(time,lat,lon) VALUES("+str(now)+","+str(lat)+","+str(lon)+")"
  print insert_str
  data = [now,lat,lon]
  cursor.execute("START TRANSACTION;")
  try:
    cursor.execute(insert_str)
  except mysql.connector.Error as err:
    print("Failed to insert event data")
  cursor.execute("COMMIT;")
  cursor.execute("START TRANSACTION;")
  try:
    for tweet in tweets:
        text=tweet[0].replace('"',"'")
        insert_str='INSERT INTO tweets(time,text,news) VALUES('+str(now)+',"'+text+'",'+str(tweet[1])+')'
        #print insert_str
        print ("Successfully inserted tweet data")
        cursor.execute(insert_str)
  except mysql.connector.Error as err:
    print("Failed to insert tweet data")
  cursor.execute("COMMIT;")
  cursor.close()
  cnx.close()
  return

