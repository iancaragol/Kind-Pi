#!/bin/sh

cd "$(dirname "$0")"

rm out.png
eips -c
eips -c

if wget http://10.0.0.5:2121/images/out.png; then
	eips -g out.png
else

fi