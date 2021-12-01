'''
João Pedro L. Affonso
Data: 01/12/21

'''

import requests
import json
from os import popen
from time import sleep

def read_certificate(number):
    output = 0;
    try:
        output = popen(f"openssl genrsa -out {number}.pem 4096");
        comand = "openssl req -new -key " + str(number) + ".pem -out " + str(number) + '.csr -subj "/C=country/ST=state/L=city/O=organization/OU=group/CN=' + str(number) + '"';
        output = popen(comand);

        #In the future I may add some additional Inputs if the user wants to customize the "-subj" fields
        file = open(f"{number}.csr", "r");
        csr = file.read();
        file.close();
        
        return csr;
        

    except Exception as e:
        print(e, "\n-----\n", output);

def main():
    try:
        number = input('''Type your phone number on the internation format.
Example: 55021999999999
--> ''');
        #Don't forget to use your own IP
        url = "http://192.168.0.102:8000/registration/" + number;
        response = requests.get(url);

        if str(response.text) == "1111":
            token = input("Type the number you received on Telegram: ");
            url = "http://192.168.0.102:8000/send_token/" + number + ":" + token;
            response = requests.get(url);
            ca_token = str(response.text);
            ca_token = json.loads(ca_token);
            ca_token = ca_token["msg"];

            csr = read_certificate(number);
            print("======\nChaves e pedido de assinatura gerados\n======");
            
            url = "https://192.168.0.102:8443/1.0/sign";

            csr = csr;
            ott = ca_token;
            sign_request = json.dumps({
                'csr':csr,
                'ott':ott,
                });
            
            response = requests.post(url, data=sign_request, verify=False);
            '''
                I am using false thanks to some problems with the DNS I set when first installed.
                I accidentally set it to 0.0.0.0, since then I am having problems to change.
                I will, eventually, get around it, but now I have some priorities to address.
            '''
            print("=====Your Certificate======")
            print(response.text);

            #writing certificate on file
            response = json.loads(response.text);
            file = open(f"{number}.pem", "w");
            file.write(response["crt"]);
            file.close()
            print(response["crt"]);
            


    except Exception as e:
        print(e);



if __name__ == "__main__":
    main();
