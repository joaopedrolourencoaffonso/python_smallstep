# python_smallstep_api
An python API that uses [Quart](https://pgjones.gitlab.io/quart/index.html), [Telethon](https://telethonn.readthedocs.io/en/latest/) and [Step ca](https://smallstep.com/)  to provide a simple Registration Authority for P2P.

## Latest update
### Better Security

New [version 6](https://github.com/joaopedrolourencoaffonso/python_smallstep/tree/main/6-version) on the air! This time was a little more conceptual and hence needed some more explanation as you can see [here](https://github.com/joaopedrolourencoaffonso/python_smallstep/blob/main/6-version/README.md). This new version provides:

- Full SSL protection, including verification of certificate with python requests
- Use of POST request rather than GET.
- Setting an specific cypher suite for Hypercorn server.

I must warn that my next update may take a little longer, as now I must make the actual p2p communication with my SSL certificates, but when I'm finished, I going to take care of the revoke and renew API's.
