#!/usr/bin/env bash

git pull
docker-compose stop
docker-compose up -d
