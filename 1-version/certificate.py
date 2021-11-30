'''
João Pedro L. Affonso
Data: 30/11/21
This script is still a test
'''

import requests
import json
from os import popen
from time import sleep

def read_certificate(number):
    #number is the phone number of the user
    output = 0;
    try:
        output = popen(f"openssl genrsa -out {number}.pem 4096");
        comand = "openssl req -new -key " + str(number) + ".pem -out " + str(number) + '.csr -subj "/C=your_country/ST=your_state/L=your_city/O=something/OU=something/CN=' + str(number) + '"';
        output = popen(comand);

        file = open(f"{number}.csr", "r");
        csr = file.read();
        file.close();
        
        return csr;
        

    except Exception as e:
        print(e, "\n-----\n", output);

def main():
    try:
        number = input('''Type your phone number on the internation format.
Exemplo: 55021999999999
--> ''');

        url = "http://192.168.0.108:8000/registration/" + number;
        response = requests.get(url);

        if str(response.text) == "1111":
            token = input("Type the number you received on Telegram: ");

            url = "http://192.168.0.108:8000/send_token/" + number + ":" + token;#dont forget to change to your own IP
            response = requests.get(url);
            ca_token = str(response.text);
            ca_token = json.loads(ca_token);
            ca_token = ca_token["msg"];

            csr = read_certificate(number);
            csr = csr.replace("\n", "\\n")

            print("======\nChaves e pedido de assinatura gerados\n======");

            url = "https://192.168.0.108:8443/1.0/sign";

            sign_request = '{"csr":"' + str(csr[:-2])  + '","ott":"' + str(ca_token[:-2]) + '"}';

            print(sign_request);
            print("==\npreparing to send\n==");
            
            sign_request = json.loads(sign_request);
            
            response = requests.post(url, sign_request, verify="ca_certificate.pem");

            print(response.text);

    except Exception as e:
        print(e);


if __name__ == "__main__":
    main();
