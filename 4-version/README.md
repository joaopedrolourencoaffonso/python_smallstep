# Bug Fix

I discovered that the script was only signing certificates for my own celphone number, after some debugging I found out that popen run in it's [own subprocess](https://docs.python.org/3.8/library/subprocess.html#popen-constructor), this means that, without an action between popens, there  is a chance that one of them may start working before the other one finishs. 
I have came up with a temporary solution to the problem, but in the future I will found a more efficient way to resolve it.

## Update (04/12/21)

After soma analysis I realized that I had misunderstood some concepts. One of them is using an **fixed** password. I am planning to adapt the second part of the API to receive a POST request containing the client's public key, so only the client can decode it using it's own private key.
