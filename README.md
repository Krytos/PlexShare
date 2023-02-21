# PlexSharePay

Basically a simple webhook with a telegram bot to manage Stripe payment monitoring and then share / stop sharing Plex libraries with people who have an active sub on stripe using FastAPI, MongoDB and [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI)

 - Telegram Bot to send payment and account management links to users
 - Stripe webhook to check for active or changed subs
 - Automated Plex library sharing depending on sub status
 - Soon to come: Overseerr request ressetting once media has been deleted from plex server.
