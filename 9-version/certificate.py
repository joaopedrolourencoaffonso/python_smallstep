'''
João Pedro L. Affonso
Date: 17/02/22
Full registration.py/step ca client, capable of generating, renewing and revoking certificate, as well as logging the steps for later analysis.
'''

#sys
import sys
sys.path.insert(2, "C:\\path_to_your_telegram_variables")

# Telethon
from variables import api_id, api_hash #my id and hash are stored on a "variables.py" file on the: "C:\\path_to_your_telegram_variables", directory
from telethon import TelegramClient, events, utils
import asyncio
import requests;
import json
from os import popen
from time import sleep

#Logging
import logging
Log_Format = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(level=logging.INFO,filename = "certificate.log",format=Log_Format)
logger = logging.getLogger();

client = TelegramClient('aplicacao', api_id, api_hash)

def get_new_certificate(number):
    '''
    ----------------------------------------
    Getting Smallstep certificates
    ----------------------------------------
    obs: my step ca is installed on a Oracle VM, so I reserved an IP for it.
    '''
    try:
        url = "https://192.168.0.155:8000/registration";

        '''
        We need to convert to json to send for the registration.py
        '''
        to_send = json.dumps({'number':f"{number}"});

        response = requests.post(url, data=to_send, verify="ca_bundle.pem");

        '''
        Test that I use to synchronize the scripts
        '''

        if str(response.text) == "1111":
            token = input("Type the number you received on Telegram: ");
            to_send = json.dumps({'number':f"{number}",'token':f"{token}"});

            url = "https://192.168.0.155:8000/send_token";

            response = requests.post(url, data=to_send, verify="ca_bundle.pem");

            ca_token = str(response.text);
            ca_token = json.loads(ca_token);
            ca_token = ca_token["msg"];

            if ca_token.find("Error,") == 0:
                return ca_token;

            if ca_token == "Server error":
                return "Server error";

            comand = f"openssl genrsa -out {number}.pem 4096"
            popen(comand);
            '''
            This sleep is due to the fact that the popen runs in a *subprocess*, that is, in parallel.
            This means that if there is no action between one popen and another, there is a chance that the second popen will activate before the
            first bit ends, like it did in version 3. I don't like these sleeps, but at the moment
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

            print("\n-----Response------\n",response.text,"\n-----");

            '''
            Writing the certificate on a file
            '''

            response = json.loads(response.text);
            file = open(f"{number}_crt.pem", "w");
                
            file.write(response["crt"] + response["ca"]);
            file.close()
            print("\n----Your certificate----\n",response["crt"] + response["ca"]);

            open("token.txt","w").write(ca_token);

            logger.info("Got a new certificate");

            return "\n=========New certificate downloaded with success!==========\n";

        else:
            logger.error(response.text);
            return str(response.text);

    except Exception as e:
        logger.error(str(e));
        return "Erro: \n" + str(e);
        

def renew_certificate(number):
    try:
        url = "https://192.168.0.155:8443/1.0/renew";

        response = requests.post(url, verify="ca_bundle.pem", cert=(f"{number}_crt.pem",f"{number}.pem"));
        response = json.loads(response.text);

        print(response);

        open(f"{number}_crt.pem", "w").write(response["crt"] + response["ca"]);

        logger.info("Renewed certificate");

        return "=======\nRenewed certificate!\n=======";

    except Exception as e:
        logger.error(str(e));
        return "Erro " + str(e);

def revoke_certificate(number):
    try:
        #
        print('''What is the cause?
0 - Unspecified
1 - KeyCompromise
2 - CACompromise
3 - AffiliationChanged
4 - Superseded
5 - CessationOfOperation
6 - CertificateHold
8 - RemoveFromCRL
9 - PrivilegeWithdrawn
10 - AACompromise''');
        reasonCode = int(input("--> "));

        if reasonCode not in [0,1,2,3,4,5,6,8,9,10]:
            logger.error("Erro de input");
            return "Erro de input"
        #
        else:
            reason = input("What the reason?\n-->")
            
            url = "https://192.168.0.155:8000/revoke_token";

            to_send = json.dumps({'number':f"{number}"});

            response = requests.post(url, data=to_send, verify="ca_bundle.pem");

            ott = str(response.text);
            ott = json.loads(ott);
            ott = ott["msg"];

            if ott.find("Error,") == 0:
                return ott;

            if ott == "Server error":
                return "Server error";
            
            url = "https://192.168.0.155:8443/1.0/revoke";

            serial_hex = popen(f"openssl x509 -noout -serial -in {number}_crt.pem").read();
            serial_hex = serial_hex.replace("serial=","").replace("\n","")
            serial_dec = str(int(serial_hex,16));
            
            ott = json.dumps({"serial":serial_dec,"ott":ott,"passive":True,"reasonCode":reasonCode,"reason":reason});
            
            response = requests.post(url, data=ott, verify="ca_bundle.pem", cert=(f"{number}_crt.pem",f"{number}.pem"));

            response = json.loads(response.text);

            print(response);

            logger.info("Revoked certificate");

            return "=======\nRevoked certificate!\n=======";

    except Exception as e:
        logger.error(str(e));
        return "Erro " + str(e);
        

async def main():
    try:
        logger.info("certificate.py has been started");
        ME = await client.get_me();
        number = ME.id

        print('''
    Type:
1 - To get a new certificate.
2 - To renew your certificate.
3 - To revoke a certificate.''');
        choice = input("--> ");

        if choice == "1":
            result = get_new_certificate(number);

            print(result);

        elif choice == "2":
            result = renew_certificate(number);

            print(result);

        elif choice == "3":
            result = revoke_certificate(number);

            print(result);

        else:
            print("Sorry, try again");        

    except Exception as e:
        logger.error(str(e));
        print(e);
        


with client:
    client.loop.run_until_complete(main());
    
