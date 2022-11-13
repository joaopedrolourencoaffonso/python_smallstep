'''
João Pedro L. Affonso
Date: 15/10/22
Full registration.py/step ca client, capable of generating, renewing and revoking certificate, as well as logging the steps for later analysis.
Main changes: the new script is capable of creating both ECC and RSA private keys, no longer being reliant on OpenSSL for creating CSR or renewing certificates
'''

#sys
import sys
sys.path.insert(2, "/path_to_directory_with_telegram_variables_file")

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


def my_key(number,key_type):
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    
    if key_type == "1":
        from cryptography.hazmat.primitives.asymmetric import rsa
        # Generate private key
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
        );
    
        key_temp = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        );
    
    if key_type == "2":
        from cryptography.hazmat.primitives.asymmetric import ec
        
        key = ec.generate_private_key(ec.SECP384R1())
        
        key_temp = key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.PKCS8,encryption_algorithm=serialization.NoEncryption());
    
    open(f"{number}.pem","w").write(key_temp.decode("UTF-8"));
    
    # Generate a CSR
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"BR"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"RJ"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Niteroi"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"TCC"),
        x509.NameAttribute(NameOID.COMMON_NAME, f"{number}"),
    ])).add_extension(
        x509.SubjectAlternativeName([
        x509.DNSName(f"{number}"),
    ]),
        critical=False,
    # Sign the CSR with our private key.
    ).sign(key, hashes.SHA256())

    # Write our CSR out to a file.
    with open(f"{number}.csr", "wb") as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))

    
#def crs(number):

def get_new_certificate(number,key_type):
    '''
    ----------------------------------------
    Getting Smallstep certificates
    ----------------------------------------
    obs: I'm now using the local DNS for simplicity, as, for some reason, the router kept giving the wrong address to the VM
    '''
    try:
        url = "https://joao-virtualbox.local:8000/registration";

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

            url = "https://joao-virtualbox.local:8000/send_token";

            response = requests.post(url, data=to_send, verify="ca_bundle.pem");

            ca_token = str(response.text);
            ca_token = json.loads(ca_token);
            ca_token = ca_token["msg"];

            if ca_token.find("Error,") == 0:
                return ca_token;

            if ca_token == "Server error":
                return "Server error";

            my_key(number,key_type);

            print("======\nPrivate Key generated\n======");

            file = open(f"{number}.csr", "r");
            csr = file.read();
            file.close();

            print("======\nSignature Request Generated\n======");
            url = "https://joao-virtualbox.local:8443/1.0/sign";
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
        url = "https://joao-virtualbox.local:8443/1.0/renew";

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
            
            url = "https://joao-virtualbox.local:8000/revoke_token";

            to_send = json.dumps({'number':f"{number}"});

            response = requests.post(url, data=to_send, verify="ca_bundle.pem");

            ott = str(response.text);
            ott = json.loads(ott);
            ott = ott["msg"];

            if ott.find("Error,") == 0:
                return ott;

            if ott == "Server error":
                return "Server error";
            
            url = "https://joao-virtualbox.local:8443/1.0/revoke";
            
            from cryptography import x509
            cert = open("1836713877_crt.pem","r").read().encode("UTF-8");
            cert = x509.load_pem_x509_certificate(cert);
            serial_dec = str(cert.serial_number);
            
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
            print('''
    Type:
1 - For an RSA key
2 - For an ECC key
            ''');
            key_type = input("--> ");
            if key_type == "1" or key_type == "2":
                result = get_new_certificate(number,key_type);
                
            else:
                result = "Sorry, try again"

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
