#!/bin/sh

wget http://download.joachims.org/svm_light/current/svm_light.tar.gz
mkdir svm_light
cd svm_light
gunzip -c ../svm_light.tar.gz | tar xvf -
make
cd ..
rm svm_light.tar.gz

virtualenv -p python3 venv3
. venv3/bin/activate
pip install -r requirements.txt
deactivate
