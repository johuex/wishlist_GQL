#!/usr/bin/env bash

# Install dependencies
cd /home/ubuntu/wishlist_GQL
if [ ! -e ./venv ]
then
  python3 -m virtualenv venv
fi
source venv/bin/activate
pip install -r requirements.txt
if [ ! -e .env ]
then
  cp /home/ubuntu/deploy/.env /home/ubuntu/wishlist_GQL # copy dotenv
fi
if [ ! -e ./cert ]
then
  mkdir /home/ubuntu/wishlist_GQL/cert
fi
if [ ! -e ./cert/privkey.pem ]
then
  cp -H /home/ubuntu/deploy/cert/privkey.pem /home/ubuntu/wishlist_GQL/cert # copy https key
fi
if [ ! -e ./cert/fullchain.pem ]
then
  cp -H /home/ubuntu/deploy/cert/fullchain.pem /home/ubuntu/wishlist_GQL/cert # copy https key
fi

# Restart services
supervisorctl restart gql_api # start/restart deploying
