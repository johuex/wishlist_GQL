#!/usr/bin/env bash

# Install dependencies
cd $HOME/wishlist_GQL
if [ ! -e ./venv ]
then
  python3 -m virtualenv venv
fi
source venv/bin/activate
pip install -r requirements.txt
if [ ! -e .env ]
then
  cp $HOME/deploy/.env $HOME/wishlist_GQL # copy dotenv
fi
if [ ! -e ./cert ]
then
  mkdir $HOME/wishlist_GQL/cert
fi
if [ ! -e ./cert/privkey.pem ]
then
  cp -H $HOME/deploy/cert/privkey.pem $HOME/wishlist_GQL/cert # copy https key
fi
if [ ! -e ./cert/fullchain.pem ]
then
  cp -H $HOME/deploy/cert/fullchain.pem $HOME/wishlist_GQL/cert # copy https key
fi

# Restart services
supervisorctl restart gql_api # start/restart deploying
