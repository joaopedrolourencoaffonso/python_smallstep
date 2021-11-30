#!/usr/bin/python
#This script is being run on a Ubuntu virtual Machine

###Path for telegram api_id and api_hash, the file must be .py
import sys
sys.path.insert(2, "/path/to/file/containing/your_api_id_and_api_hash")

##mysql
import mysql.connector

#registration is the name of the database and user of the MySQL server
mydb = mysql.connector.connect(
  host="localhost",
  user="registration",
  password="password",
  database="registration"
);

cur = mydb.cursor();

###
from quart import Quart, render_template, jsonify
from variables import api_id, api_hash
import hypercorn.asyncio
from datetime import datetime, timedelta
from random import randint
from telethon import TelegramClient#
from os import popen

#I edited quart's config.py so the default IP is "0.0.0.0"

# Remember to use your own values from my.telegram.org!
client = TelegramClient('registration', api_id, api_hash)

app = Quart(__name__)
app.secret_key = 'senha'

@app.route('/registration/<number>')
async def registration(number):
    if (number.isnumeric()) and (len(number) == 14):
        token = randint(10000, 99999);
        
        number = number[:2] + number[3:];#this line thanks to the brazilian telephonic system, adapt as necessary
        prazo = datetime.now() + timedelta(minutes=5);
        await client.send_message(number, f"Welcome! Your token is {token}, it last only 5 minutes.")
        
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
	    saida = len(cur.fetchall());
	    if saida == 0:
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
    await hypercorn.asyncio.serve(app, hypercorn.Config())

    
if __name__ == '__main__':
    client.loop.run_until_complete(main())
