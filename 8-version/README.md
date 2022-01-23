# Process Automation
I have managed to automate the renew of the quart_bundle.pem. I have also managed to find and fix some new bugs as well as correct some wrong mistakes.

## Python 3.7
I may not have posted this before, but I'm currently working within an virtual enviroment. This was not important as this virtualenviroment is for the support of quart (that isn't called on the ```certificate.py```), however, one day, I tried o run the script from within the enviroment, and it showed this error message:
```
('Connection aborted.', OSError(0, 'Error'))
...
OSError: [Errno 0] Error
...
urllib3.exceptions.ProtocolError: ('Connection aborted.', OSError(0, 'Error'))
...
requests.exceptions.ConnectionError: ('Connection aborted.', OSError(0, 'Error'))
```
These are just the most important lines, but you get the picture. After some search I realized that the problem is that I have 2 versions of python on my machine: 3.7.0 and 3.8.5, each supports a differente version of Openssl ('OpenSSL 1.1.0h  27 Mar 2018' and 'OpenSSL 1.1.1g  21 Apr 2020').

If you use the: ```ssl.HAS_TLSv1_3``` with each of these versions, you will see that the first one does not support TLS version 3, which is a problem, given that registration.py was configured to exclusively accept TLS version 3.

I solved the problem by creating a new virtual enviroment based on python 3.8 with: 
```python
virtualenv teste_3 --python C:\Python38\python.exe
```

## Automation of quart_crt.pem renew
Originally, I was manually renewing the quart_crt.pem every few days, but as this was getting boresome, I updated the registration.py to renew it everytime it starts working:
```python
def cert_updater():
    import requests, json
    
    url = "https://192.168.0.155:8443/1.0/renew";
    
    response = requests.post(url, verify="ca_bundle.pem", cert=("quart_crt.pem","quart_key.pem"));
    response = json.loads(response.text);
    
    open("quart_crt.pem", "w").write(response["crt"] + response["ca"]);
    
    return "ok";

async def main():
    _ = cert_updater();
    await hypercorn.asyncio.serve(app, config)
```
As you can see, cert_updater() works as a blocking function, so to avoid the registration.py to start working with an old certificate. You may also notice that I removed the "data" field. As it turns out, the step-ca don't actually need the post request to contain anything, it only need the mTLS flow to work out and it will give a renewed certificate for you.

## ca_bundle.pem rather than quart_bundle.pem
As it turns out, in the beginning of the project, I commited a conceptual mistake. Basically, I was using the registration authority's own certificate to authenticate itself. Technically speaking, it worked and provided authenticity, but, it required me to continuously renew the client side certificate, what was unnecessary work.

I have since updated the "certificate.py" to remove the necessity of the "quart_bundle.pem", using the "ca_bundle.pem" instead. 
