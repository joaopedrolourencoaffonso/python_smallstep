# Complete Client and Server
## New registration.py
The new [registration.py](https://github.com/joaopedrolourencoaffonso/python_smallstep/blob/main/9-version/registration.py), is now able to issue certificates revocation tokens through the ```/revoke_token``` API as below:
```python
@app.route('/revoke_token', methods=['POST'])
async def revoke_token():
    #print("revoke")
    try:
        if request.method == 'POST':
            '''
            Processing the received post request
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
```
You will notice that the API does not send a test message via Telegram, this is due to the fact that the step ca uses mTLS to verify that the user holds the private key of the aforementioned certificate.

Version 9 also uses the logging module, using the separator: ";;" which can be used to explore the file: ```registration.log``` as if it were a csv, allowing treatment by Excel, PowerBI or pandas. This module works together with the command: ```request.remote_addr``` to provide information about the origin of a request and therefore detect possible attacks.

Additionally, new version 9 presents a system to check if a given user requesting a token to generate a certificate has already requested a token in the last five minutes. To do this, the script checks the database to see if there is an entry for that number (assuming that ```cleaner.py``` is running).
```python
cur.execute(f"select * from temp_token where number = '{number}';");
output = cur.fetchall();
output = len(output)
print(output);
cur.execute("commit;");
```
Note that, despite not making changes to the database, the "commit" is necessary to force the script to access the most recent version of the database, otherwise it cannot update to the previous version.

**tip**: Before using the server, go to ```registration.log``` and add: "type ;; date ;; message ;; ip_address", so it can work as column titles on any data analysis software.

## cleaner.py
[Script](https://github.com/joaopedrolourencoaffonso/python_smallstep/blob/main/9-version/cleaner.py) that accesses the database and deletes all entries older than five minutes behind. It should be executed by the cron tab every 1 minute, in order to keep it always updated. However, note that you must always use the command: "commit" to make sure that python will access the most recent version of the database.

## New certificate.py
The new [certificate.py](https://github.com/joaopedrolourencoaffonso/python_smallstep/blob/main/9-version/certificate.py) is a user friendly client that is able to obtain, renew and revoke a ```step ca``` certificate. ```certificate.py``` also has a logging module implementation that allows you to keep track of errors and actions.

The most interesting, however, is the option to revoke certificates. The step ca revoke API by default needs at least:

- a valid revocation token: ```step ca token {number} --revoke --key token.key --password-file pass.txt``` in registration.py
- the value of the serial numbers which we get using the command:```serial_hex = popen(f"openssl x509 -noout -serial -in {number}_crt.pem").read();```, however , by default openssl provides the serial numbers in hexadecimal format, to compensate we use: ```serial_hex = serial_hex.replace("serial=","").replace("\n",""); serial_dec = str(int(serial_hex,16));```
- A field in the json stating that the form of revocation is passive: ```..."passive":True...```.

Despite this, the API is still capable of storing information in the form of:
- Reason code, an integer numeric value detailing the type of reason for certificate revocation:```..."reasonCode":reasonCode...```
- A short string explaining the reason: ```..."reason":reason...```

An example request would be:
```python
ott = json.dumps({"serial":serial_dec,"ott":ott,"passive":True,"reasonCode":reasonCode,"reason":reason});
            
response = requests.post(url, data=ott, verify="ca_bundle.pem", cert=(f"{number}_crt.pem",f"{number}.pem"));
```

## certificate_test.py
Small script to perform an simulated SPAM attack. Basically, the scripts obtain an token for a Telegram number but doesn't finish the flow. Thanks to the new safety measurements, even if the attacker proceed with attack anyway, it can be detected through log analysis, which reveal the attackers IP address and the time of the attack.
