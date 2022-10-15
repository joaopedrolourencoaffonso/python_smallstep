# Version 10

## New certificate.py (API client)
The new version of the certificate.py now is indepent of openssl, using the [cryptography](https://cryptography.io/en/latest/#) libray. It'also capable of generating ECC keys using the SECP384R1 curve.

### OpenSSL free

The new client no longer relies on OpenSSL for creating keys or certificates, in it's place, I created the "my_key" function, which uses [cryptography](https://cryptography.io/en/latest/#) libray, it now takes both the Telegram user ID and a variable that indicates what kind of certificate the user wants.

```python
def my_key(number,key_type):
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    
    if key_type == "1":
        from cryptography.hazmat.primitives.asymmetric import rsa
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

    # Write our CSR out to disk.
    with open(f"{number}.csr", "wb") as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))
``` 

### ECC keys
The user must now make an extra choice of generating an RSA key or an ECC key:

```python
if choice == "1":
            print('''
    Type:
1 - For an RSA key
2 - For an ECC key
            ''');
```
After that, I use the code bellow to generate a private ECC key and store it on the "key_temp" variable
```python
if key_type == "2":
        from cryptography.hazmat.primitives.asymmetric import ec
        
        key = ec.generate_private_key(ec.SECP384R1())
        
        key_temp = key.private_bytes(encoding=serialization.Encoding.PEM,format=serialization.PrivateFormat.PKCS8,encryption_algorithm=serialization.NoEncryption());
```
