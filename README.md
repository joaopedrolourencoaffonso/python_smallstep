# Python step ca API for P2P
An python API that uses [Quart](https://pgjones.gitlab.io/quart/index.html), [Telethon](https://telethonn.readthedocs.io/en/latest/) and [Step ca](https://smallstep.com/)  to provide a simple Registration Authority for P2P.

## Latest update
### The End (for now)

New [version 11](https://github.com/joaopedrolourencoaffonso/python_smallstep/tree/main/11-version) on the air!

This new version brings:
- Integration with prometheus's Node Exporter. To use, first add the [statistics.sh](https://github.com/joaopedrolourencoaffonso/python_smallstep/blob/main/11-version/statistics.sh) to your cron using the interval that fits your taste, then, run the command below to activate the Node Exporter using the custom metrics:
```bash
./node_exporter --collector.textfile.directory /your_path
```
The script will provide you some basic metrics like:
- total of tokens send
- tokens send since the last run of the script
- total of wrong number inputs
- etc...

You can use it as a foundation to create your own scripts.

## You didn't wanted to do more?
Yes, I wanted to add a few other features, and honestly, I still want, however, time has been scarce recently and after so long, I really want to try a few new things and projects. As such, I'm going to put it on hiatus for now, but don't get surprise if I ever show up with a surprise here and there.

Thanks for you attention, hope it's usefull.
