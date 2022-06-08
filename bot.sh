#!/bin/sh

redis-server /etc/redis/redis.conf
python /root/src/bot.py
