#!/bin/sh

cd "$(dirname "$0")"

rm out-crush.png
eips -c
eips -c

if wget http://10.0.0.5:2121/out-crush.png; then
	eips -g out-crush.png
else
	eips -g out-crush.png
fi