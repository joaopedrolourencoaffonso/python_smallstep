# Telethon problem is resolved
Telethon has updated it's use of identifiers. You can know more [here](https://github.com/LonamiWebs/Telethon/issues/3215). However, it's possible that there may be new
bugs in the future, if anything significant changes I will post a new version with observations.

# Send messages
The new script now can send tokens throught Telegram so users can prove their identity.

# Security
The registration.py doesn't regulate how many requisitions someone can do in any amount of time, so, in theory, it could be used to saturate an target with Spamm messages.
As I must tackle other aspects of my project for now, I will fix this later.

# Next Steps
- Resolve the security issue above
- Enable renew of certificates
- Enable elimination of certificates
- Any further suggestion is welcome!
