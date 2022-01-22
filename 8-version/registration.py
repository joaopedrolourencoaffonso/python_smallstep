#!/usr/bin/python

###Path for telegram api_id and api_hash
import sys
sys.path.insert(2, "/path_to_your_variables_directory/variables.py")

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

from hypercorn.config import Config
config = Config()
config.bind = ["0.0.0.0:8000"]
config.certfile = "/path_to_directory/quart_crt.pem"
config.keyfile = "/path_to_directory/quart_key.pem"
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
    print("registration")  
    if request.method == 'POST':
        '''
        Processing the post request
        '''
        number = await request.get_data();
        number = json.loads(number);
        number = number['number'];
        
        if (number.isnumeric()):
            token = randint(10000, 99999);
            print(token);
            
            temp_number = int(number);
            prazo = datetime.now() + timedelta(minutes=5);
            
            await client.send_message(temp_number, f"Welcome! Your token is {token}, it lasts 5 minutes.");
            
            query = "insert into temp_token values (%s, %s, %s)";
            values = (number, token, str(prazo));
            cur.execute(query, values);
            cur.execute("commit;");
            
            return "1111";
            
        else:
            return "Erro";
            
    else:
        return "2222";
        
@app.route('/send_token', methods=['POST'])
async def send_token(): 
    if request.method == 'POST':
        '''
        Processing the post request
        '''
        number = await request.get_data();
        number = json.loads(number);
        token = number['token'];
        number = number['number'];
        
        if (number.isnumeric()) and (token.isnumeric()):
            agora = datetime.now();
            token = int(token);
            cur.execute(f"select * from temp_token where number = '{number}' and token = {token} and hour > '{agora}';");
            print(f"select * from temp_token where number = '{number}' and token = {token} and hour > '{agora}';");
            saida = len(cur.fetchall());
            
            if saida == 1:
                cur.execute(f"delete from temp_token where number = '{number}' and token = {token};");
                cur.execute("commit;");
                
                step_token = f"step ca token '{number}' --key token.key --password-file pass.txt";
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

def cert_updater():
    import requests, json
    
    url = "https://192.168.0.155:8443/1.0/renew";
    
    response = requests.post(url, verify="ca_bundle.pem", cert=("quart_crt.pem","quart_key.pem"));
    response = json.loads(response.text);
    
    open("quart_crt.pem", "w").write(response["crt"] + response["ca"]);
    
    return "ok";

async def main():
    _ = cert_updater();
    await hypercorn.asyncio.serve(app, config)

    
if __name__ == '__main__':
    client.loop.run_until_complete(main())
