#!/bin/bash
set -e


echo 'Build frontend'

rm server/static/*
cd browser 
ng build --build-optimizer --base-href="/static/"
mv ../server/static/index.html ../server/templates/.