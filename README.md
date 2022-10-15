# Python step ca API for P2P
An python API that uses [Quart](https://pgjones.gitlab.io/quart/index.html), [Telethon](https://telethonn.readthedocs.io/en/latest/) and [Step ca](https://smallstep.com/)  to provide a simple Registration Authority for P2P.

## Latest update
### further security, logs and revoke

New [version 10](https://github.com/joaopedrolourencoaffonso/python_smallstep/tree/main/10-version) on the air!

This new version brings:
- Use of cryptography library to provide independence from OpenSSL
- Generate both ECC and RSA keys

## Next steps
Currently, my objectives include:

- Provide the API with an prometheus/grafana endpoint for monitoring.
- Make the API indepent of step to provide JWTs.
- Find and correct further security weakness.
