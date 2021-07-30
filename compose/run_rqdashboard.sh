#!/usr/bin/env bash
cd ..
rq-dashboard -p 9181 -u '${REDIS_URL}'
