#!/bin/bash

pip install -r /code/requirements.txt
flask run --host=$HOST --port=$PORT
