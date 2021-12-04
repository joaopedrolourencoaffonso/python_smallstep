#!/usr/bin/python

'''
João Pedro L. Affonso
02/12/21
what it does: This is the registration side of the system. It works on Quart.
Basically, the system uses hypercorn to run 2 APIs, "registration" and "send_token". "registration" generates a random token, send's it
through Telegram to the phone number indicated and then stores it on a MySQL database. On the other hand, "send_token" receives the token
and if it is on the database, gives back an Smallstep jwt token, that the client side can use to sign an certificate.

NOTE: As you can notice, this is not very safe, as there still the problem of someone using the CA as way to SPAM messages and I don't handle errors very well.
This is because this script still on development, patience is needed.
'''


###Path for telegram api_id and api_hash
import sys
sys.path.insert(2, "/the_path_to_the_directory_with_your_Telegram_variables")
#note, I usa a variables.py file to store Telegram id and hash

##mysql
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="registration",
  password="password",
  database="registration"
);

cur = mydb.cursor();

###
from quart import Quart, render_template, jsonify
import hypercorn.asyncio
from datetime import datetime, timedelta
from random import randint
from os import popen
from variables import api_id, api_hash
from telethon import TelegramClient

#I edited Hypercorn's config.py so the default IP is "0.0.0.0"

# Remember to use your own values from my.telegram.org!
client = TelegramClient('registration', api_id, api_hash)

app = Quart(__name__)
app.secret_key = 'senha'#placeholder password

@app.route('/registration/<number>')
async def registration(number):
    if (number.isnumeric()) and (len(number) == 14):
        token = randint(10000, 99999);
        print(token);
        
        temp_number = number[:2] + number[3:];#this line thanks to the brazilian telephonic system, adapt as necessary
        prazo = datetime.now() + timedelta(minutes=5);
        await client.send_message(temp_number, f"Welcome! Your token is {token}, it only lasts 5 minutes.")
        
        query = "insert into temp_token values (%s, %s, %s)";
        values = (number, token, str(prazo));
        cur.execute(query, values);
        cur.execute("commit;");
        
        return "1111";
        
    else:
        return "Error";
        
@app.route('/send_token/<token>')
async def send_token(token):
    token = token.split(":");
    if (token[0].isnumeric()) and (len(token[0]) == 14) and (token[1].isnumeric()):
	    token[1] = int(token[1]);
	    agora = datetime.now();
	    
      cur.execute(f"select * from temp_token where number = '{token[0]}' and token = {token[1]} and hour > '{agora}';");
	    print(f"select * from temp_token where number = '{token[0]}' and token = {token[1]} and hour > '{agora}';");
	    saida = len(cur.fetchall());
	    
      if saida == 1:
	        cur.execute(f"delete from temp_token where number = '{token[0]}' and token = {token[1]};");
	        cur.execute("commit;");
	        step_token = f"step ca token '{token[0]}' --password-file pass.txt";
          '''
          runs step ca token, so we can get a jwt token from the Step ca
          '''
	        stream = popen(step_token);
	        step_token = str(stream.read());
	        return jsonify(msg=step_token);
	        
	    else:
	        return "Error, try again";
    else:
        return "Error, try again";

#You can learn more about lines 92-101, here: https://pgjones.gitlab.io/quart/how_to_guides/startup_shutdown.html
# Connect the client before we start serving with Quart
@app.before_serving
async def startup():
    await client.connect()

# After we're done serving (near shutdown), clean up the client
@app.after_serving
async def cleanup():
    await client.disconnect()

#-------------------
@app.route('/')
@app.route('/index')
@app.route('/main')
async def index():
    return await render_template("index.html")

async def main():
    await hypercorn.asyncio.serve(app, hypercorn.Config())

    
if __name__ == '__main__':
    client.loop.run_until_complete(main())
