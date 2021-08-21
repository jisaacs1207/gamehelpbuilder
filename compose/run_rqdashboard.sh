#!/usr/bin/env bash
cd ..
rq-dashboard -p 9181 --redis-url ${REDIS_URL}
