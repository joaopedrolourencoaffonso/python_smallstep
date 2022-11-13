#!/usr/bin/python

'''
João Pedro L. Affonso
Date: 13/11/2022
'''

###Path for telegram api_id and api_hash
import sys
sys.path.insert(2, "/path_to_your_variables")

##mysql
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="registration",
  password="senha",
  database="registration"
);

cur = mydb.cursor();

###
from quart import Quart, render_template, jsonify, request
import hypercorn.asyncio

from hypercorn.config import Config
config = Config()
config.bind = ["0.0.0.0:8000"]
config.certfile = "/path_to_yourt_quart_crt.pem"
config.keyfile = "/path_to_yourt_quart_key.pem"
config.ciphers = "ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256"


from datetime import datetime, timedelta
from random import randint
from os import popen
from variables import api_id, api_hash
from telethon import TelegramClient
import json

#logging
import logging
log_format = "%(levelname)s ;; %(asctime)s ;; %(message)s";# the ";;" are used as a custom separator for later analysis on any software of your choice.
logging.basicConfig(level=logging.INFO,filename="registration.log",format=log_format);
logger = logging.getLogger();

''' 1 - This segment is to simply log into telegram without an support script
    2 - Remember to use your own values from my.telegram.org!'''
client = TelegramClient('registration', api_id, api_hash)

async def myTelegram_login():
    await client.send_message('me', 'Starting registration.py!')
    
with client:
    client.loop.run_until_complete(myTelegram_login());
########

app = Quart(__name__)
app.secret_key = 'password'

@app.route('/registration', methods=['POST'])
async def registration():
    
    try:
        if request.method == 'POST':
            
            '''
            Processing post request
            '''
            number = await request.get_data();
            number = json.loads(number);
            number = number['number'];
            
            cur.execute(f"select * from temp_token where number = '{number}';");
            output = cur.fetchall();
            saida = len(output)
            print(output);
            cur.execute("commit;")#without this it reads an old version of the database
            
            if (number.isnumeric()) and saida == 0:
                token = randint(10000, 99999);
                print(token);
                
                temp_number = int(number);
                prazo = datetime.now() + timedelta(minutes=5);
                
                await client.send_message(temp_number, f"Welcome! Your token is {token}, it lasts only 5 minutes.");
                
                query = "insert into temp_token values (%s, %s, %s)";
                values = (number, token, str(prazo));
                cur.execute(query, values);
                cur.execute("commit;");
                
                logger.info(f"Token {token} sent for {number} ;; {request.remote_addr}");
            
                return "1111";
                
            elif saida > 0:
                logger.error(f"registration Multiple token requests for {number} ;; {request.remote_addr}");
                return "Error, multiple token requests";
            
            else:
                logger.error(f"registration Invalid number ;; {request.remote_addr}");
                return "Error, invalid number";
            
        else:
            logger.error("registration User tried to use 'get' request ;; {request.remote_addr}");
            return "2222";
        
    except Exception as e:
        print(e);
        logger.error("registration " + str(e) + " ;; " + request.remote_addr);
        return "Server Error"
        
@app.route('/send_token', methods=['POST'])
async def send_token():
    try:
        if request.method == 'POST':
            '''
            Processing post request
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
                    
                    logger.info(f"Access token send to {number} ;; " + request.remote_addr);
                    
                    return jsonify(msg=step_token);
                    
                else:
                    logger.error(f"send_token User {number} used wrong Telegram token ;;" + request.remote_addr);
                    return jsonify(msg="Error, wrong Telegram token");
            
            else:
                logger.error(f"send_token Invalid Telegram token or number {token} {number} ;; " + request.remote_addr);
                return jsonify(msg="Error, invalid number or Telegram token");
        
        else:
            logger.error("send_token User tried to use get request ;; " + request.remote_addr);
            return jsonify(msg="Error, only post request");
            
    except Exception as e:
        logger.error("send_token " + str(e));
        return jsonify(msg="Server error");

@app.route('/revoke_token', methods=['POST'])
async def revoke_token():
    #print("revoke")
    try:
        if request.method == 'POST':
            '''
            Processing post request
            '''
            number = await request.get_data();
            number = json.loads(number);
            number = number['number'];
            
            step_token = f"step ca token {number} --revoke --key token.key --password-file pass.txt";
            stream = popen(step_token);
            step_token = str(stream.read());
            
            logger.info(f"revoke_token {number} got a revoke token ;; " + request.remote_addr);
            
            return jsonify(msg=step_token);
            
        else:
            logger.error("revoke_token User tried to use get request ;; " + request.remote_addr);
            return jsonify(msg="Error, only post request");
        
    except Exception as e:
        logger.error("revoke_token " + str(e));
        return jsonify(msg="Server error");

        
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
    try:
        import requests, json
        
        url = "https://192.168.0.155:8443/1.0/renew";
        
        response = requests.post(url, verify="ca_bundle.pem", cert=("quart_crt.pem","quart_key.pem"));
        response = json.loads(response.text);
        
        open("quart_crt.pem", "w").write(response["crt"] + response["ca"]);
        
        logger.info("Certificate has been renewd.");
        
        return 0;
        
    except Exception as e:
        logger.error("cert_updater: " + str(e));
        return 1
        
async def main():
    logger.info("Server has started");
    result = cert_updater();
    
    if result == 1:
        print("Error trying to start");
        
    else:
        await hypercorn.asyncio.serve(app, config);
        
    logger.info("Server has finished.");

    
if __name__ == '__main__':
    client.loop.run_until_complete(main())
