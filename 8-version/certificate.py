'''
João Pedro L. Affonso
Date: 22/01/22
what it does: It provides a way of the client to get a signed certificate from step-ca using Telegram as identity provisioner.
Basically, it sends a request to registration.py using SSL, provokig registration.py to send an random token to the informed
number through Telegram. Once and if the person informs the correct token, registration.py provides an jwt to the client that
then uses it to interact directly with the step-ca through it's API.
'''

#sys
import sys
sys.path.insert(2, "C:\\path_to_the_directory_where_you_stored_your_credentials\\variables.py")

# Telethon
from variables import api_id, api_hash  #Telegram credentials
from telethon import TelegramClient, events, utils
import asyncio
import logging
import sys
from os import mkdir#
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

client = TelegramClient('aplicacao', api_id, api_hash)


async def main():
    try:
        '''
        ----------------------------------------
        Getting Smallstep certificates
        ----------------------------------------
        '''
        import requests;
        import json
        from os import popen
        from time import sleep

        ME = await client.get_me();
        number = ME.id
        '''
        my step ca is installed on a Oracle VM, so I reserved an IP for it.
        '''
        url = "https://192.168.0.155:8000/registration";

        '''
        We need to convert to json to send for the registration.py
        '''
        to_send = json.dumps({'number':f"{number}"});

        response = requests.post(url, data=to_send, verify="ca_bundle.pem");
        
        '''
        Teste que eu uso para sincronizar os dois scripts
        '''
        if str(response.text) == "1111":
            token = input("Type the number you received on Telegram: ");
            to_send = json.dumps({'number':f"{number}",'token':f"{token}"});

            url = "https://192.168.0.155:8000/send_token";
            
            response = requests.post(url, data=to_send, verify="ca_bundle.pem");

            ca_token = str(response.text);
            ca_token = json.loads(ca_token);
            ca_token = ca_token["msg"];

            comand = f"openssl genrsa -out {number}.pem 4096"
            popen(comand);
            '''
            This sleep is due to the fact that the popen runs in a *subprocess*, that is, in parallel.
            This means that if there is no action between one popen and another, there is a chance that the second popen will activate before the
            first bit ends, like it did in version 3. I don't like many of these sleeps, but at the moment
            they keep things running, plus the jwt lasts 5 min, so we're in the safe zone.
            '''
            print("======\nPrivate Key generated\n======");
            
            sleep(5);
            
            comand = 'openssl req -new -key {number}.pem -out {number}.csr -subj "/C=BR/ST=RJ/L=Niteroi/O=UFF/OU=TCC/CN={number}"';
            comand = comand.replace("{number}", str(number));
            popen(comand);

            sleep(5);

            file = open(f"{number}.csr", "r");
            csr = file.read();
            file.close();
            
            print("======\nSignature Request Generated\n======");
            
            url = "https://192.168.0.155:8443/1.0/sign";
            sign_request = json.dumps({
                'csr':csr,
                'ott':ca_token,
                });
            print("\n-----\n",sign_request,"\n---------");
            
            response = requests.post(url, data=sign_request, verify="ca_bundle.pem");
            '''
            OLD COMMENT, but It's important so I'm keeping it
            ---
            response = requests.post(url, sign_request, verify="ca_certificate.pem");
            the false above was due to the fact that CA is homegrown, if you make
            him try to use Smallstep he won't be able to understand correctly.
            It has been already fixed.
            ---
            '''
            print("\n-----Response------\n",response.text,"\n-----");

            '''
            Writing the certificate on a file
            '''
            response = json.loads(response.text);
            file = open(f"{number}_crt.pem", "w");
            
            file.write(response["crt"] + response["ca"]);
            file.close()
            print("\n----Your certificate----\n",response["crt"] + response["ca"]);

            print("\n=========Installation complete==========\n");
        

    except Exception as e:
        print(e);
        


with client:
    client.loop.run_until_complete(main());
    
