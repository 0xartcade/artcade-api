# 0xArtcade API
API powering the main 0xArtcade games

## Getting Started
1. Install [poetry](https://python-poetry.org/)
2. Ensure you have the proper python version install, per `.python-version`. It is best to use [pyenv](https://github.com/pyenv/pyenv) for managing python installations on your machine.
3. Run `poetry install`
4. Copy `.env.example` and rename to `.env` and fill out accordingly
5. Run `make run-infra`. This requires Docker to be installed and running.
6. Run `make run-server` and see the index page on [http://localhost:8000](http://localhost:8000)

## Why Django REST Framework?
A few reasons!

1. I f*ckin love python
2. It's a batteries-included API framework, built on one of the best ORMs out there
3. Has a large community behind it and is very stable

I believe Sun Tzu said this about API frameworks their critically aclaimed book, 'The Art of War':
> API frameworks should be boring so that you can build cool things with them easily

## Infrastructure Setup
- Server for handling API requests
- Background workers handling async tasks and cron jobs for recurring jobs (to come later)
- Postgres db

## User Authentication
Currently, the backend is setup to create user profiles based on a web3 sign in standard (Sign In With Ethereum). Users then can link their mobile phone to their account using one-time passcodes (OTP). In the future, we plan to enable users to sign in via email by using a similar OTP strategy. As part of onboarding an email-based user, we will guide them to creating a wallet either through Coinbase Smart Wallet (wen?) or another method of adding account abstraction. To start, we are focused on web3 cryptoart users, but acknowledge that we must broaden the user base in the future.

## Data Indexing
We utilize Alchemy webhooks for our data indexing. This is a robust method of getting notified of onchain events. We then process each event as it comes in from the webhook. As we don't have to fetch data from anywhere but what is passed through the custom graphql webhook, we have no need to setup a background pipeline process. In the future, if that is needed, we can set that up.
