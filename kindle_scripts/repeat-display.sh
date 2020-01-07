#!/bin/sh

cd "$(dirname "$0")"

while ./display-out.sh;

do sleep 60;

done