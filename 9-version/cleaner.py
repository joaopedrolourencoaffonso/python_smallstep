#!/usr/bin/python

'''
João Pedro L. Affonso
Date: 17/02/2022
Small script for deleting old entries from de database. You should put it on the cron tab to run every 1 minute, so to keep the database always updated.
'''

##mysql
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="registration",
  password="password",
  database="registration"
);

cur = mydb.cursor();

from datetime import datetime, timedelta

five_minutes_ago = datetime.now() - timedelta(minutes=5);

cur.execute(f"delete from temp_token where hour < '{five_minutes_ago}'");
cur.execute("commit;");
