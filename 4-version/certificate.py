'''
João Pedro L. Affonso
Data: 04/12/21
what it does: It send and http request to the registration.py API, the registration.py send's an temp token through Telegram. 
The user then must type the token on the command line. With that done, the script get's the token, generates an private key and
sends the corresponding csr to the step ca.
'''

import requests
import json
from os import popen

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
            comand = comand.replace("{number}", number);
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
            print(sign_request);
            
            response = requests.post(url, data=sign_request, verify=False);
            '''
            response = requests.post(url, sign_request, verify="ca_certificate.pem");
            the false above is due to the fact that CA is homegrown, if you make him try to use Smallstep he won't be able to understand correctly.
            In the future I will fix it.
            '''
            print(response.text);

            '''
            Writing the certificate on a file
            '''
            response = json.loads(response.text);
            file = open(f"{number}_crt.pem", "w");
            file.write(response["crt"]);
            file.close()
            print(response["crt"]);

    except Exception as e:
        print(e);

if __name__ == "__main__":
    main();
