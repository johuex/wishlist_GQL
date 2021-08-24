#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install -y python3 python3-pip supervisor
pip install -q wheel
pip install -q virtualenv