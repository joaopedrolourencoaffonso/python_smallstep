'''
João Pedro L. Affonso
Data: 23/12/21
what it does: Script that renew certificates. You simply need to send an json with the certificate to be renewd, the step-ca will use mTLS to authenticate you and proceed to sign it.
'''

import requests

import json
from os import popen
from time import sleep

def main():
    try:
        url = "https://192.168.0.155:8443/1.0/renew";

        to_send = open("{your_crt}.pem", "r").read();
        to_send = json.dumps({"crt":to_send});

        response = requests.post(url, data=to_send, verify="ca_bundle.pem", cert=("{your_crt}.pem","{your_private_key}.pem"));

        response = json.loads(response.text);

        print(response.text);
        open("{your_renewed_crt}.pem", "w").write(response["crt"]);
        
    except Exception as e:
        print(e);

if __name__ == "__main__":
    main();
