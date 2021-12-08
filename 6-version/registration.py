#!/usr/bin/python

###Path for telegram api_id and api_hash
import sys
sys.path.insert(2, "/path_to_your_variables/variables")

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
from quart import Quart, render_template, jsonify, request
import hypercorn.asyncio
'''
HOW TO CONFIGURE HYPERCORN (lines 31-36)
First, we need to import the config class, that will allow us to create a config object with all the standard configurations.
Second, we set the configurations as we need, here, I used: 
- ".bind" to set the IP and port the server should use, 
- ".certfile" and ".keyfile" for the crt and private_key of my server respectively
- ".ciphers" to set the cipher suit we want, here, I am using the same as Smallstep
NOTE: Quart, by default, uses almost the same suite as Smallstep, but I want to put it clear just in case
'''
from hypercorn.config import Config
config = Config()
config.bind = ["0.0.0.0:8000"]
config.certfile = "/path_to_your_crt/quart_crt.pem"
config.keyfile = "/path_to_your_key/quart_key.pem"
config.ciphers = "ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256"


from datetime import datetime, timedelta
from random import randint
from os import popen
from variables import api_id, api_hash
from telethon import TelegramClient
import json

# Remember to use your own values from my.telegram.org!
client = TelegramClient('registration', api_id, api_hash)

app = Quart(__name__)
app.secret_key = 'password'

@app.route('/registration', methods=['POST'])
async def registration():
  number = await request.get_data();
  number = json.loads(number);
  number = number['number'];
  '''
  Ifelse test to see if input is correct
  '''
  if (number.isnumeric()) and (len(number) == 14):
      token = randint(10000, 99999);
      print(token);
            
      temp_number = number[:2] + number[3:];#this line thanks to the brazilian telephonic system, adapt as necessary
      prazo = datetime.now() + timedelta(minutes=5);
      await client.send_message(temp_number, f"Bem vindo! Seu token é {token}, ele dura apenas 5 minutos.");
            
      query = "insert into temp_token values (%s, %s, %s)";
      values = (number, token, str(prazo));
      cur.execute(query, values);
      cur.execute("commit;");
      
      return "1111";
            
  else:
      return "Erro";

        
@app.route('/send_token', methods=['POST'])
async def send_token(): 
    '''
    Processing the POST request in order to store the values in appropriate variables
    '''
    number = await request.get_data();
    number = json.loads(number);
    token = number['token'];
    number = number['number'];
    '''
    Ifelse test to see if input is correct
    '''
    if (number.isnumeric()) and (len(number) == 14) and (token.isnumeric()):
        agora = datetime.now();
        token = int(token);
        cur.execute(f"select * from temp_token where number = '{number}' and token = {token} and hour > '{agora}';");
        print(f"select * from temp_token where number = '{number}' and token = {token} and hour > '{agora}';");
        saida = len(cur.fetchall());
            
        if saida == 1:
            cur.execute(f"delete from temp_token where number = '{number}' and token = {token};");
            cur.execute("commit;");
                
            step_token = f"step ca token '{number}' --password-file pass.txt";
            stream = popen(step_token);
            step_token = str(stream.read());
            return jsonify(msg=step_token);
        
    else:
        return "Erro, tente novamente";
        
        
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
