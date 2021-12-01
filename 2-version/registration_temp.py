#!/usr/bin/python

#Telegram has made an update that made Telethon stop working, so, for now, I will be using this one as a development script.
#For using it, you must be able to see the random token on the command line of script. When Telethon is updated I will post the new complete code here.
#I am sorry for any inconvenient.
import sys

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

#I edited quart's config.py so the default IP is "0.0.0.0"

app = Quart(__name__)
app.secret_key = 'senha'

@app.route('/registration/<number>')
async def registration(number):
    if (number.isnumeric()) and (len(number) == 14):
        token = randint(10000, 99999);
        print(token);
        
        prazo = datetime.now() + timedelta(minutes=5);
        
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
	    if saida == 1:
	        cur.execute(f"delete from temp_token where number = '{token[0]}' and token = {token[1]};");
	        cur.execute("commit;");
	        step_token = f"step ca token '{token[0]}' --password-file pass.txt";
	        stream = popen(step_token);
	        step_token = str(stream.read());
	        return jsonify(msg=step_token);
	        
	    else:
	        return "Erro, tente novamente";
    else:
        return "Erro, tente novamente";
        

#-------------------
@app.route('/')
@app.route('/index')
@app.route('/main')
async def index():
    return await render_template("index.html")
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000);
