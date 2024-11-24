# 0xArtcade API
API powering some of the 0xArtcade games

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
- Background workers handling async tasks and cron jobs for recurring jobs