#!/bin/sh
ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

pipenv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
