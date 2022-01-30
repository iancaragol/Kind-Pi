#!/bin/sh

cd "$(dirname "$0")"

eips -c
eips -c
eips -cd

eips -g out.png