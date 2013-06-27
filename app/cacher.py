import mysql.connector
from mysql.connector import errorcode
import time

# This module is used for storing past geographical search queries.
# Can be useful if the twitter API fails and we need backup data...

DB_NAME=cache

def cacher(tweets,lat,lon):
  cnx = mysql.connector.connect(user='kevinschaeffer')
  cursor = cnx.cursor()
  cursor.execute('USE '+DB_NAME)
  now=int(time.time())
  insert_str="INSERT INTO events(time,lat,lon) VALUES(%f,%f,%f);"
  data = [now,lat,lon]
  cursor.execute("START TRANSACTION;")
  try:
    cursor.execute(insert_str,data)
  except mysql.connector.Error as err:
    print("Failed to insert data")
  cursor.execute("COMMIT;")
  cursor.execute("START TRANSACTION;")
  insert_str="INSERT INTO tweets(time,tweet,news) VALUES(%f,%s,%d);"
  try:
    for tweet in tweets:
        data=[now,tweet[0],tweet[1]]
        cursor.execute(insert_str,data)
  except mysql.connector.Error as err:
    print("Failed to insert data")
  cursor.execute("COMMIT;")
  cursor.close()
  cnx.close()

