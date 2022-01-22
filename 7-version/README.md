# Provisioners

After some reading I found that the ```/provisioners``` endpoint is not privately accessible to Smallstep's local machine, but rather publicly accessible. This API provides a list of [Identity Provisioners](https://smallstep.com/docs/step-ca/provisioners#managing-provisioners), including an encrypted version of the **private key**. According to the team at Smallstep, this is not a problem if you set up a good [IdP](https://github.com/smallstep/certificates/discussions/668#discussioncomment-1854913) and if you have a [good password](https://github.com/smallstep/certificates/discussions/668#discussioncomment-1860002).

Still, I wasn't comfortable with the idea of keeping _any_ version of the private key somewhere publicly accessible, so I decided to change that.

You can get more in depth explanation [here](https://github.com/smallstep/certificates/discussions/668) and [here](https://github.com/smallstep/certificates/discussions/734), as well as the sources bellow.

## First solution
AAs you can see [here](https://github.com/smallstep/certificates/discussions/668#discussioncomment-1860002) it's not necessary to leave the private key encrypted in ca.json, so I cut the key out of it , leaving the field blank and stored it in a file called: token.key. Now, to get a signed token, we need to add the ```key``` flag to the command:
```bash
step ca token joao_teste --key token.key --password-file pass.txt
```

## Second Solution (X5C)
This would be a more complete solution since the Smallstep team recommends that we do not use the default provisioner created during the step-ca installation.

Basically, it consists of adding a new provisioner based on X5C certificates that would be used to sign the tokens instead of the jwt ones. To do this, we first need to create a chain of certificates from a second certification authority:
```bash
$ step certificate create registration registration_crt.pem registration_key.pem --profile root-ca --kty RSA --size 4096
$ step certificate create intermediate intermediate_crt.pem intermediate_key.pem --profile intermediate-ca --kty RSA --size 4096 --ca registration_crt.pem --ca-key registration_key.pem
$ step certificate create leaf leaf_crt.pem leaf_key.pem --kty RSA --size 4096 --ca intermediate_crt.pem --ca-key intermediate_key.pem --bundle
```
Don't forget to use **different passwords** for each private_key as well as to store them on txt files. Now we use this command:
```bash
step ca provisioner add registration --type X5C --x5c-root intermediate_crt.pem
```
To get a signed token, we do:
```bash
step ca token joao_test --x5c-cert leaf_crt.pem --x5c-key leaf_key.pem --password-file pass_leaf_X5C.tx
```
This version provides more security, however, it requires a greater workload on the part of the application, in addition to making it more difficult to test the signing process. So **for the moment** I will use the first solution, having made the necessary changes to registration.py, but in January I will adapt the application to use this second solution.

## Sources
For better understanding the concepts above, you can go to:
- https://smallstep.com/docs/step-ca/certificate-authority-core-concepts
- https://smallstep.com/docs/step-ca/getting-started
- https://smallstep.com/docs/step-ca/certificate-authority-server-production
- https://smallstep.com/docs/step-ca/provisioners
- https://smallstep.com/docs/step-cli/reference/ca/provisioner
- https://github.com/smallstep/certificates/blob/master/docs/provisioners.md
- https://smallstep.com/docs/step-cli/reference/ca/provisioner/add
- https://smallstep.com/docs/step-cli/reference/ca/provisioner/remove

# Tokens signed using Python
At the moment, the application uses ```popen``` to get tokens signed directly by step-ca, but Smallstep's own team suggested that it would be better to migrate to a pure python solution. I'm currently evaluating the feasibility of using the rsa.py library and in the future I plan to install jwt.py and cryptography.py, both used by the Smallstep team.

