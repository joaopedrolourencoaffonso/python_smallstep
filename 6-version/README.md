# Better Security

This new version provides a series of improvements in security, like the verification of the certificate, use of POST request and definition of a specific set of cipher suites.

## Full SSL
### Using OpenSSL
On my notebook's command line, I created a private key and its corresponding certificate using:
```
openssl req -out QUART.csr -new -newkey rsa:4096 -nodes -keyout QUART_PRIVATE.pem
```
After that, I filled in the csr fields with the normal information except for the **penultimate field**: '*common name*', if we were in production, with a truly public IP, we should use the website address/DNS, but since we are on a private network, I filled it in with the fixed IP address of my registrar authority (192.168.0.155).

Before continuing, I would like to emphasize that I chose the 4096-byte size as it is safer than the 2048 commonly used and given that our project doesn't handle large loads of information, I don't believe it will interfere with much of anything.

## Signing the certificate whith step-ca
With the files in hand, I transferred them to my virtual machine (where Smallstep and the registration authority are) and placed them both in the same directory as the registration authority. After that, I generated a token using the command below:
```
step ca token 192.168.0.155 --password-file pass.txt
```
It is important to note that the name provided for the token must be the same as the one used as the 'common name' for the certificate, since the library [requests](https://docs.python-requests.org/en/latest/) uses this field to verify the owner of the certificate. If I had a public IP with an associated domain name, I would use the name of that domain, so when requests made the http request, it would compare the name on the certificate with the domain name. For this example I used address 192.168.0.155 as common name.

Now, remembering that the token only lasts **5 minutes**, I used the curl command to get a signed certificate:
```
curl -k -X POST -H 'Content-Type: application/json' -d '{"csr": "-----BEGIN CERTIFICATE REQUEST-----\nMIIEdDCCAlwCAQAw....sd7o/DxM3DzyIdWuK78mXrPKqg==\n-----END CERTIFICATE REQUEST-----", "ott":"eyJhbGciOi...TcBiK7dqcTP6_OC0NCQ_zexs_iLMJfuB3eW0V6IGmQ"}' https://0.0.0.0:8443/1.0/sign

IMPORTANT: Don't forget that csr must be entered with the "\n" to set the end/beginning of line
```
Once this is done, the [API](https://github.com/joaopedrolourencoaffonso/python_smallstep/blob/main/6-version/registration.py) of the Registering Authority is now able to use SSL, you can verify this by going to the index.html file through the browser and ignoring the security alerts.

With the signed certificate in hand, we headed back to [certificate.py](https://github.com/joaopedrolourencoaffonso/python_smallstep/blob/main/6-version/certificate.py).

## Quart Bundle
The requests library uses, by default, another library called [certifi](https://certifiio.readthedocs.io/en/latest/) to find the official CA_Bundle available on the computer, as our registrar authority is not in this bundle (obviously), we need to provide a custom bundle. To do this, we go to the certificate.py directory, create the ```quart_bundle.pem``` file, and paste the certificate (NOTE: Replace the "\n" with real line breaks). After that, we take the certificate of our certifying authority (root_ca) and the intermediate authority (intermediate_ca) and paste it in the same document as the format below:
```
-----BEGIN CERTIFICATE-----
MIIBzDCCAXKgAwIBAgIQWefqrwt
qwuygebwhTQOEUWWONKSJSNSdwf
...(rest of your certificate)...
xKFGmVcyJsUtyI9mx6kmLpvEFsP0cEqGrcEKUk20pOM=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIBzDCCAXKgAwIBAgIQWefqrwt
qwuygebwhTQOEUWWONKSJSNSdwf
...(rest of the intermediary authority certificate)...
xKFGmVcyJsUtyI9mx6kmLpvEFsP0cEqGrcEKUk20pOM=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIBzDCCAXKgAwIBAgIQWefqrwt
qwuygebwhTQOEUWWONKSJSNSdwf
...(rest of the root certificate)...
xKFGmVcyJsUtyI9mx6kmLpvEFsP0cEqGrcEKUk20pOM=
-----END CERTIFICATE-----
```
With that done, we go to certificate.py and edit the: ```verify=False``` to: ```verify=quart_bundle.pem```. request.py is now able to use full SSL with the registering authority.

## Editing step-ca
As stated in the previous version, step-ca uses its own SSL certificate, which makes it difficult to access the Smallstep API in a truly secure way. For this, we must do two things:

1 - We should create a new file: ```ca_bundle.pem``` in this file, we paste the intermediate and root certificates of our CA:
```
-----BEGIN CERTIFICATE-----
MIIBzDCCAXKgAwIBAgIQWefqrwt
qwuygebwhTQOEUWWONKSJSNSdwf
...(rest of the intermediary authority certificate)...
xKFGmVcyJsUtyI9mx6kmLpvEFsP0cEqGrcEKUk20pOM=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIBzDCCAXKgAwIBAgIQWefqrwt
qwuygebwhTQOEUWWONKSJSNSdwf
...(rest of the root certificate)...
xKFGmVcyJsUtyI9mx6kmLpvEFsP0cEqGrcEKUk20pOM=
-----END CERTIFICATE-----
```
This tells python requests how to correctly verify the step ca certificate, however, if you try to use requests, you will likely get the error:
```
File "C:\Python38\lib\site-packages\requests\adapters.py", line 514, in send
    raise SSLError(e, request=request)
requests.exceptions.SSLError: HTTPSConnectionPool(host='192.168.0.155', port=8443): Max retries exceeded with url: / (Caused by SSLError(SSLCertVerificationError("hostname '192.168.0.155' doesn't match '0.0.0.0'")))
```
As stated earlier, python checks the certificate address against the one it is requesting (which makes perfect sense). In my case, when I installed step-ca, I wanted it to be able to get the same IP as my virtual machine, but I still hadn't set a fixed IP address for it (as I haven't thought of that yet), so, I used 0.0.0.0, which worked, but confused python. To solve this problem, we go to step 2.

2 - First, we need to correct the address and domain name ("dnsNames") of our CA, for that, on the same machine as our CA, we use the command:
```
gedit /home/{your_user}/.step/config/ca.json
```
After that, we edited the fields "address" and "dnsNames" and replaced: "0.0.0.0" by the fixed address of our virtual machine: "192.168.0.155". Now step-ca will operate normally at this address, but there is still the problem of ```step ca token```, which operates on the basis of defaults.json. For that, we do:
```
gedit /home/{your_user}/.step/config/defaults.json
```
And we edited the "ca-url" field from "0.0.0.0" to: "192.168.0.155", if you have a specific port set, keep it untouched.

*OBS: Don't forget to make a backup of ca.json and defaults.json before messing up with them*

## Using POST
```Post``` requests are (*slightly*) more secure than ```get``` requests, they are also easier to administer and more pythonic, hence I have enable it's use.

### certificate.py

Just edit: ```request.get``` to: ```request.post``` and use the option: ```data=to_send``` where ```to_send``` is a generated json object with ```json_dumps```.

### registration.py

First, we need to edit the decorators ("@app.route") in order to allow the use of the post method. To do this, we add to the decorator: ```methods=['POST']```.

After that, [we use](https://github.com/joaopedrolourencoaffonso/python_smallstep/blob/22dcacda7713001cdbbc045e57b48909994a8d94/6-version/registration.py#L84): ```await request.get_data()``` to effectively get the values received. Once that's done, just process the json object with ```loads``` the information is already available in an easily accessible dictionary.

These steps are repeated on both functions.

## Setting the cypher suite
In registration.py, I added the line:
```
config.ciphers = "ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256"
```
This line defines what kind of cipher suites I want to use, both are approved by Smallstep itself and are TLSv1.2 or 1.3, later, I may add more protocols.

In certificate.py it was not necessary to make changes, as the registration.py server itself necessarily selects which protocols are allowed, but to make a test, you can use this [stackoverflow](https://stackoverflow.com/questions/40373115/how-to-select-specific-the-cipher-while-sending-request-via-python-request-modul) code below:
```
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import create_urllib3_context
CIPHERS=('DH+3DES')
class ProtocolAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        return super(DESAdapter, self).init_poolmanager(*args, **kwargs)
    
    def proxy_manager_for(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        return super(DESAdapter, self).proxy_manager_for(*args, **kwargs)

s = requests.Session()
s.mount("https://192.168.0.155:8000", ProtocolAdapter())
```
An error message will appear as this protocol has been disabled on the server side.
We can now test with another protocol.
```
CIPHERS=('TLSv1.2')
s.mount("https://192.168.0.155:8000", ProtocolAdapter())
r = s.get("https://192.168.0.155:8000", verify="quart_bundle.pem")
print(r.text)
```
It will work perfectly. That way SSL is operational and using secure cipher suites.

## Next Steps
1) There's still the lack of control of how much certificate a peer can ask in a given period of time. This can causa a range of security issues that I am going to work now on
2) There's still no support for renew nor revoke.
3) The peer must be able to tell when they need to renew their certificates.

## Usefull links
- https://lukasa.co.uk/2017/02/Configuring_TLS_With_Requests/
- https://stackoverflow.com/questions/40373115/how-to-select-specific-the-cipher-while-sending-request-via-python-request-modul
- https://www.digitalocean.com/community/tutorials/processing-incoming-request-data-in-flask-pt
- https://www.educative.io/edpresso/get-vs-post
- https://www.w3schools.com/python/ref_requests_post.asp
- https://pgjones.gitlab.io/hypercorn/reference/source/hypercorn.config.html
- https://ciphersuite.info/cs/TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256/
- https://pgjones.gitlab.io/hypercorn/discussion/http2.html
- https://stackoverflow.com/questions/40373115/how-to-select-specific-the-cipher-while-sending-request-via-python-request-modul
- https://pgjones.gitlab.io/quart/reference/cheatsheet.html

