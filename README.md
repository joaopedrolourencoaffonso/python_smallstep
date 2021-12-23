# Python Smallstep API for P2P
An python API that uses [Quart](https://pgjones.gitlab.io/quart/index.html), [Telethon](https://telethonn.readthedocs.io/en/latest/) and [Step ca](https://smallstep.com/)  to provide a simple Registration Authority for P2P.

## Latest update
### More security fixes and renew.py

New [version 7](https://github.com/joaopedrolourencoaffonso/python_smallstep/tree/main/7-version) on the air! This time I managed to create the [renew.py](https://github.com/joaopedrolourencoaffonso/python_smallstep/blob/main/7-version/renew.py) that you can use to request a renewed certificate from the step-ca.

Additionaly, I also made some changes on the '''/provisioners''' endpoint, as I was not confortable with letting any version of the private key publicly available (special thanks to [Mariano Cano](https://github.com/maraino) for the speed and efficiency of the answers!).

## Next steps
Currently, my objectives include:

- create a full ```/revoke``` API
- Remove the necessity/mention of the root_ca.crt of any script.
- Adapt the scripts to work with the X5C certificates.
- Adapt ```certificate.py``` to use python to generate the keys and csr.
- Adapt ```registration.py``` to use python to generate the signed token.
- Find and correct further security weakness.
