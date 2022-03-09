# Telethon Problem

So, in 01/12/2021 Telegram seems to have made an update to the MTProto in order to enforce 64-bit identifiers for users. This has made Telethon's "TelegramClient" stop working, effectively locking every app that uses Telethon out of the API.
You can see more [here](https://github.com/LonamiWebs/Telethon/issues/3215), as well as in [Pyrogram](https://github.com/pyrogram/pyrogram/issues/794).

As a way around, I am going to keep building the application without Telethon (I only use the function send once anyway) then, when Telethon is updated, I will readpat it to use Telethon. Until then, the random token will be printed on the Quart log and you must print it from there.
