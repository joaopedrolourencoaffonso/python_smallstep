'''
João Pedro L. Affonso
Data: 02/12/21
what it does: It send and http request to the registration.py API, the registration.py send's an temp token through Telegram. 
The user then must type the token on the command line. With that done, the script get's the token, generates an private key and
sends the corresponding csr to the step ca.
'''

import requests
import json
from os import popen

def read_certificate(number):
    output = 0;
    try:
        output = popen(f"openssl genrsa -out {number}.pem 4096");
        
        comand = "openssl req -new -key " + str(number) + ".pem -out " + str(number) + '.csr -subj "/C=country/ST=state/L=city/O=place/OU=group/CN=' + str(number) + '"';
        output = popen(comand);

        file = open(f"{number}.csr", "r");
        csr = file.read();
        file.close();
        
        return csr;
        

    except Exception as e:
        print(e, "\n-----\n", output);

def main():
    try:
        number = input('''Type your phone number on the international format:
Exemplo: 55021999999999
--> ''');
        
        url = "http://192.168.0.155:8000/registration/" + number;#my step ca is installed on a Oracle VM, so I reserved an IP for it.
        response = requests.get(url);
        
        if str(response.text) == "1111":
            token = input("Type the number you received on Telegram: ");
            
            url = "http://192.168.0.155:8000/send_token/" + number + ":" + token;
            response = requests.get(url);
            ca_token = str(response.text);
            ca_token = json.loads(ca_token);
            ca_token = ca_token["msg"];

            csr = read_certificate(number);
            print("======\nKeys and CSR were generated\n======");
            
            url = "https://192.168.0.155:8443/1.0/sign";
            csr = csr;
            ott = ca_token;
            sign_request = json.dumps({
                'csr':csr,
                'ott':ott,
                });
            print(sign_request);
            print("==\nPreparing to send\n==");

            response = requests.post(url, data=sign_request, verify=False);
            #I am still working on make the "requests" accept the CA certificate, but once I do, I will post it here.
            print(response.text);

            #writing certificate on corresponding file
            response = json.loads(response.text);
            file = open(f"{number}_crt.pem", "w");
            file.write(response["crt"]);
            file.close()
            print("Your certificate is here:\n", response["crt"]);

    except Exception as e:
        print(e);

if __name__ == "__main__":
    main();
