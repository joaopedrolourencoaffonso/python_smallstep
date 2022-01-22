# Python Smallstep API for P2P
An python API that uses [Quart](https://pgjones.gitlab.io/quart/index.html), [Telethon](https://telethonn.readthedocs.io/en/latest/) and [Step ca](https://smallstep.com/)  to provide a simple Registration Authority for P2P.

## Latest update
### More security fixes and renew.py

New [version 8](https://github.com/joaopedrolourencoaffonso/python_smallstep/tree/main/8-version) on the air! This time I edit the [registration.py](https://github.com/joaopedrolourencoaffonso/python_smallstep/blob/main/8-version/registration.py) so it renews it's own certificate every time it runs, saving some work.

Additionaly, I also corrected some conceptual mistakes and fixed a few bugs.

## Next steps
Currently, my objectives include:

- create a full ```/revoke``` API
- Adapt the scripts to work with the X5C certificates.
- Adapt ```certificate.py``` to use python to generate the keys and csr.
- Adapt ```registration.py``` to use python to generate the signed token.
- Find and correct further security weakness.
