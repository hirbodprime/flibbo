# Flibbo

Flibbo is a Django REST API backend for a social content app with built-in AI tools. Users post tweets (text, photo, video), podcasts, and books, follow each other, chat in real time, and earn points and referral rewards. An AI studio wraps OpenAI, Stability, HeyGen, D-ID Studio, and Fliki to generate chat replies, images, speech, avatar videos, and translations. NFT products can be bought with crypto through Plisio, and push notifications are sent through Firebase Cloud Messaging.

## Features

- Accounts with JWT/token auth, dj-rest-auth registration, and Google / Apple social login (django-allauth)
- Posts: tweets with images/video, likes, saves, views, shares, comments, replies, pinned/hidden comments, reports
- Podcasts and books (with pages and reading progress), each with comments
- Home feed, followings feed, favorite categories, explore section
- Following system with follow requests
- Direct messages, plus WebSocket endpoints for home, explore, and activity (`/ws/home/`, `/ws/explore/`, `/ws/activity/`) via Django Channels + Redis
- Notifications via FCM (fcm-django, firebase-admin)
- AI studio (`/openai/`): OpenAI chat, image, image edit, audio and text-to-speech; chat history and prompt suggestions; HeyGen avatar/translation videos and talking photos; D-ID Studio talks, clips and animations; Fliki video, image and voice generation; per-user usage limits
- Points, referral codes, gold/normal user lists, and withdrawal requests
- NFT marketplace with Plisio crypto payments, user wallets and owned NFTs
- Categories, support requests, and management commands (e.g. `add_categories`, `create_token`, `unban_users`, `add_prompts`)

## Tech stack

- Python 3, Django 4.2, Django REST Framework, Simple JWT
- dj-rest-auth, django-allauth, django-cors-headers, django-countries
- Django Channels, Daphne, channels-redis, Redis
- PostgreSQL
- OpenAI, stability-sdk, HeyGen / D-ID Studio / Fliki HTTP APIs
- fcm-django, firebase-admin, Plisio
- OpenCV, MoviePy, Pillow (media processing)

## Project structure

```
flibbo/            Settings, URLs, ASGI/WSGI, WebSocket routing
accounts/          Users, auth, permissions, middleware
posts/             Tweets, podcasts, books, comments
chat_openai/       AI studio integrations (OpenAI, HeyGen, Studio, Fliki, Stability)
following_system/  Follows and follow requests
message_system/    Direct messages
activity/          Activity feed (WebSocket consumer)
notification/      FCM devices and notifications
point/             Points, referrals, withdrawals
marketplace/       NFT products and Plisio payments
wallet/            Wallets and user NFTs
category/, explore/, tokens/, flibbo_base/   Categories, explore, tokens, support
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

You also need PostgreSQL and Redis running locally. Note: `requirements.txt` is saved as UTF-16; convert it to UTF-8 if pip cannot read it.

## Configuration

Create a `.env` file in the project root:

```
DJANGO_SECRET_KEY=change-me
DEBUG=True
HOST=https://your-domain.example

DB_NAME=flibbo
DB_USER=postgres
DB_PASSWORD=your-db-password

MAIL_SERVER_DEFAULT_FROM_EMAIL=no-reply@example.com
MAIL_SERVER_EMAIL_HOST_USER=your-email-user
MAIL_SERVER_EMAIL_HOST_PASSWORD=your-email-password

GOOGLE_CLIEND_ID=your-google-client-id
GOOGLE_SECRET=your-google-secret
APPLE_CLIEND_ID=your-apple-client-id
APPLE_SECRET=your-apple-secret
APPLE_KEY=your-apple-key-id
APPLE_CERTIFICATE_KEY=your-apple-private-key

FCM_SERVER_KEY=your-fcm-server-key

OPENAI_API_KEY=your-openai-key
OPENAI_ORG_API_KEY=your-openai-org-id
HEYGEN_API_KEY=your-heygen-key
FLIKI_API_KEY=your-fliki-key
STUDIO_API_KEY=your-studio-key
STUDIO_USERNAME=your-studio-username
STUDIO_PASSWORD=your-studio-password
```

(`GOOGLE_CLIEND_ID` and `APPLE_CLIEND_ID` are spelled this way in the code.) The database host/port and Redis hosts for the channel layer are set in `flibbo/settings.py`. Some keys (Stability, Plisio, Firebase dynamic links) are currently set in code and should be moved to environment variables.

## Running

```bash
python manage.py runserver
```

For WebSocket support, run the ASGI app with Daphne:

```bash
daphne flibbo.asgi:application
```

Main routes: `/account/`, `/posts/`, `/openai/`, `/network/`, `/market/`, `/wallet/`, `/point/`, `/activity/`, `/notification/`, `/category/`, `/explore/`, `/token/`, `/base/`, `/accounts/` (allauth), `/admin/`.
