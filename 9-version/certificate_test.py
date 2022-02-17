'''
Small script to make make requests for Telegram Token without finishing the authentication flow. 
Is just an example of the kind of script that an attacker would use to spam an victim with unsolicited tokens.
'''

import requests;
import json

number = an_Telegram_user_id;#integer

url = "https://192.168.0.155:8000/registration";

to_send = json.dumps({'number':f"{number}"});

response = requests.post(url, data=to_send, verify="ca_bundle.pem");

print(response.text)
