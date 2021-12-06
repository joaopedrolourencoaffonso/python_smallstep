# Hypercorn and SSL
## Hypercorn 

I finally managed to discover how to properly configure Hypercorn without having to edit the "config.py" file. If, for any reason, you need to edit the config.py, you can do it by:

```
gedit /home/{your_user}/.local/lib/python{your_python_version}/site-packages/hypercorn/config.py`
```
However, I warn that the right way to do it is:
```
from hypercorn.config import Config
config = Config()
config.bind = ["0.0.0.0:8000"]
config.certfile = "/{path}/quart.crt"
config.keyfile = "/{path}/quart.key"
```
The lines above keep all other of Hypercorn's default configurations, while setting Quart to use port 8000, the public IP and specifies the files to use as crt, and private.key. If you run a "Hello World" script with these configurations, you will be able to access the main page on localhost:8000, but, if you decide to use a homemade certificate, your browser will probably ask if you want to proceed.

You can learn more in the [documentation](https://pgjones.gitlab.io/hypercorn/how_to_guides/configuring.html), or looking on registration.py.

**However**, I must point out a weird [bug](https://gitlab.com/pgjones/hypercorn/-/issues/100) from Hypercorn. Basically, if you try to run the script as it is, it will print:
```
ssl.SSLError: [SSL: APPLICATION_DATA_AFTER_CLOSE_NOTIFY] application after close notify (_ssl.c:2758)
```
According to [pgjones](https://gitlab.com/pgjones/hypercorn/-/issues/100) these errors cause no trouble and should have been supressed. I am going to read this thread further to see if I can make it stop, but as it has no bearing on service or security, I'm going to advance on other fronts first.

## SSL
As stated above, the new system is capable of using SSL, what protects, partially, against the MiM attack, however, as Python's requests modules has been hard to use with self-signed certificates, I'm gonna use the "verify=false" flag, for now.

You will probably notice that I'm also using "get" rather than "post", as the latter is safer than the former, I will try to fix it this week.
