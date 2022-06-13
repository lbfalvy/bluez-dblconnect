#!/bin/sh
cd "$(dirname "$0")"
git fetch
git pull
python3 ./main.py "${@}"