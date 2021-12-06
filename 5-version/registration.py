#!/usr/bin/python

###Path for telegram api_id and api_hash
import sys
sys.path.insert(2, "/your_varibles_directory_path")

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
'''Lines 33 - 38
If you remember: *#I edited quart's config.py so the default IP is "0.0.0.0"*
So, I finally managed to find the correct way to configure Hypercorn, you just need to look in the following links:

- https://pgjones.gitlab.io/quart/how_to_guides/background_tasks.html?highlight=post
- https://pgjones.gitlab.io/hypercorn/how_to_guides/http_https_redirect.html
- https://pgjones.gitlab.io/hypercorn/how_to_guides/configuring.html

Now, not only I can configure Hypercorn properly, but I can also configure the use of SSL. However, I am still struggling
to make python's requests accept them, so, I am going to use "verify=false" for now, but I will fix this in the future.
I am also using the ".pem" format, as I think it make things easier.
'''
import hypercorn.asyncio
from hypercorn.config import Config
config = Config()
config.bind = ["0.0.0.0:8000"]
config.certfile = "/your_path/quart_crt.pem"
config.keyfile = "/your_path/quart_key.pem"

from datetime import datetime, timedelta
from random import randint
from os import popen
from variables import api_id, api_hash
from telethon import TelegramClient

# Remember to use your own values from my.telegram.org!
client = TelegramClient('registration', api_id, api_hash)

app = Quart(__name__)
app.secret_key = 'password';

@app.route('/registration/<number>')
async def registration(number):
    if (number.isnumeric()) and (len(number) == 14):
        token = randint(10000, 99999);
        print(token);
        
        temp_number = number[:2] + number[3:];#this line thanks to the brazilian telephonic system, adapt as necessary
        prazo = datetime.now() + timedelta(minutes=5);
        await client.send_message(temp_number, f"Welcome, your token is *{token}*. Hurry up! It only lasts 5 minutes!.")
        
        query = "insert into temp_token values (%s, %s, %s)";
        values = (number, token, str(prazo));
        cur.execute(query, values);
        cur.execute("commit;");
        
        return "1111";
        
    else:
        return "Erro";
        
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
	        stream = popen(step_token);
	        step_token = str(stream.read());
	        return jsonify(msg=step_token);
	        
	    else:
	        return "Error, try again";
    else:
        return "Error, try again";
        
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
    await hypercorn.asyncio.serve(app, config)

    
if __name__ == '__main__':
    client.loop.run_until_complete(main())
