# Mikrotik IP Accounting TimeSeries App

An app that gathers and saves Mikrotik IP Accounting data to QuestDB timeseris database.

## Build

Run `make build_app`

## Run

1. Change `docker-compose.yml` or use `sample.env` to set variables app uses.
2. Run `docker-compose up -d` and checkout container logs.
3. Go to `http://localhost:9000` to use QuestDB's UI to run queries and explore.

## Stack

* Python
* Docker
* QuestDB