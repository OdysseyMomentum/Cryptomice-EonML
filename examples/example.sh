#!/bin/sh

curl http://localhost:5005/model/supplychain123/train -d @training.json -H 'Content-Type: application/json' | jq

curl http://localhost:5005/model/supplychain123/predict -d @dataset.json -H 'Content-Type: application/json' | jq
