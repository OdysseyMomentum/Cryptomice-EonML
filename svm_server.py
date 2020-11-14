# :'######::'##::::'##:'##::::'##:::::::::::'######::'########:'########::'##::::'##:'########:'########::
# '##... ##: ##:::: ##: ###::'###::::::::::'##... ##: ##.....:: ##.... ##: ##:::: ##: ##.....:: ##.... ##:
#  ##:::..:: ##:::: ##: ####'####:::::::::: ##:::..:: ##::::::: ##:::: ##: ##:::: ##: ##::::::: ##:::: ##:
# . ######:: ##:::: ##: ## ### ##::::::::::. ######:: ######::: ########:: ##:::: ##: ######::: ########::
# :..... ##:. ##:: ##:: ##. #: ##:::::::::::..... ##: ##...:::: ##.. ##:::. ##:: ##:: ##...:::: ##.. ##:::
# '##::: ##::. ## ##::: ##:.:: ##::::::::::'##::: ##: ##::::::: ##::. ##:::. ## ##::: ##::::::: ##::. ##::
# . ######::::. ###:::: ##:::: ##:'#######:. ######:: ########: ##:::. ##:::. ###:::: ########: ##:::. ##:
# :......::::::...:::::..:::::..::.......:::......:::........::..:::::..:::::...:::::........::..:::::..::
#
#                          https://github.com/OdysseyMomentum/Cryptomice-EonML

import time
import json
import os
import os.path
import subprocess
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
from markupsafe import escape
import svm_lib
import svm_utils
import svm_checks

configurations = {'NAME': 'SVM_SERVER', 'VERSION': '0.0.2-odyssey'}
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

@app.route('/')
def home():
    df = subprocess.check_output('df -h /', shell=True)
    commands = []
    commands.append({'path': '/', 'type': 'GET', 'description': 'Information about SVM_SERVER commands.' })
    commands.append({'path': '/model', 'type': 'GET', 'description': 'Get a list of known models.' })
    commands.append({'path': '/model/<modelname>', 'type': 'GET', 'description': 'Get informations connected to model <modelname>.' })
    commands.append({'path': '/model/<modelname>/train', 'type': 'POST', 'description': 'Create a new model called <modelname>.' })
    commands.append({'path': '/model/<modelname>/predict', 'type': 'GET/POST', 'description': 'Create a prediction using model <modelname> and passed dataset.' })
    return jsonify({'name':configurations['NAME'], 'version':configurations['VERSION'], 'commands':commands})

@app.route('/model')
def models():
    results = svm_lib.listElement(f'ls -l {configurations["svmModels"]}/*.model', configurations["svmModels"])
    json_result = {'results': results}
    return jsonify(json_result)

@app.route('/model/<mymodel>')
def model(mymodel):
    model = escape(mymodel)
    results = {}
    results['models'] = svm_lib.listFile(f'ls -l {configurations["svmModels"]}/{model}.model')
    results['trainings'] = svm_lib.listFile(f'ls -l {configurations["svmTrainings"]}/{model}.training')
    results['datasets'] = svm_lib.listFile(f'ls -l {configurations["svmPredictions"]}/{model}*.data')
    results['predictions'] = svm_lib.listFile(f'ls -l {configurations["svmPredictions"]}/{model}*.predictions')
    return jsonify({'results': results})

def performTrain(received_dataset, model):
    svm_lib.writeSVM(f'{configurations["svmTrainings"]}/{model}.training', received_dataset)
    status = subprocess.check_output(f'{configurations["svmPath"]}/svm_learn -z r {configurations["svmTrainings"]}/{model}.training {configurations["svmModels"]}/{model}.model', shell=True).decode().splitlines()
    results = svm_lib.readSVM(f'{configurations["svmModels"]}/{model}.model')
    return status, results

@app.route('/model/<mymodel>/train', methods=['GET', 'POST'])
def train(mymodel):
    if request.method == 'POST':
        model = escape(mymodel)
        timestr = time.strftime("%Y%m%d-%H%M%S")+'-'+str(time.time())
        received_dataset = f'# dataset - {timestr}'
        payload = request.get_json()
        result, message = svm_checks.checkTrainingAll({'payload':payload, 'model':model}, configurations)
        if not result:
            return jsonify(message)
        result, received_dataset = svm_checks.checkTrainingElements(payload['dataset'], received_dataset)
        if not result:
            return jsonify(received_dataset)
        status, results = performTrain(received_dataset, model)
        return jsonify({'status': status, 'results': results})
    return jsonify({'results': 'Use a POST call.'})

def performPredict(received_dataset, obj):
    model = obj['model']
    timestr = obj['timestr']
    svm_lib.writeSVM(f'{configurations["svmPredictions"]}/{model}-{timestr}.data', received_dataset)
    status = subprocess.check_output(f'{configurations["svmPath"]}/svm_classify {configurations["svmPredictions"]}/{model}-{timestr}.data {configurations["svmModels"]}/{model}.model {configurations["svmPredictions"]}/{model}-{timestr}.predictions', shell=True).decode().splitlines()
    dat = svm_lib.readSVM(f'{configurations["svmPredictions"]}/{model}-{timestr}.data')
    res = svm_lib.readSVM(f'{configurations["svmPredictions"]}/{model}-{timestr}.predictions')
    return status, dat, res

def performPredictGet(received_dataset, obj):
    request = obj['request']
    model = obj['model']
    timestr = obj['timestr']
    line = received_dataset+'\n'+svm_lib.elementsToSVM('1', request.values['data'].split(','))
    svm_lib.writeSVM(f'{configurations["svmPredictions"]}/{model}-{timestr}.data', line)
    status = subprocess.check_output(f'{configurations["svmPath"]}/svm_classify {configurations["svmPredictions"]}/{model}-{timestr}.data {configurations["svmModels"]}/{model}.model {configurations["svmPredictions"]}/{model}-{timestr}.predictions', shell=True).decode().splitlines()
    results = svm_lib.readSVM(f'{configurations["svmPredictions"]}/{model}-{timestr}.predictions')
    return results

@app.route('/model/<mymodel>/predict', methods=['GET', 'POST'])
def predict(mymodel):
    model = escape(mymodel)
    timestr = time.strftime("%Y%m%d-%H%M%S")+'-'+str(time.time())
    received_dataset = f'# dataset - {timestr}'
    if request.method == 'POST':
        payload = request.get_json()
        result, message = svm_checks.checkPredictAll({'payload':payload, 'model':model}, configurations)
        if not result:
            return jsonify(message)
        result, received_dataset = svm_checks.checkPredictElements(payload['dataset'], received_dataset)
        if not result:
            return jsonify(received_dataset)
        status, dat, res = performPredict(received_dataset, {'model':model, 'timestr':timestr})
        results = []
        for x in range(0,len(dat)-1):
            results.append({'data':dat[x+1], 'result':res[x]})
        return jsonify({'status': status, 'results': results})
    elif request.method == 'GET': # if get
        if 'data' in request.values:
            """line = received_dataset+'\n'+elementsToSVM('1', request.values['data'].split(','))
            svm_lib.writeSVM(f'{configurations["svmPredictions"]}/{model}-{timestr}.data', line)
            status = subprocess.check_output(f'{configurations["svmPath"]}/svm_classify {configurations["svmPredictions"]}/{model}-{timestr}.data {svmModels}/{configurations["svmModels"]}.model {configurations["svmPredictions"]}/{model}-{timestr}.predictions', shell=True).decode().splitlines()
            results = svm_lib.readSVM(f'{configurations["svmPredictions"]}/{model}-{timestr}.predictions')"""
            results = performPredictGet(received_dataset, {'request':request, 'model':model, 'timestr':timestr})
            return jsonify({'results': results})
        else:
            return jsonify({'results': 'Missing data.'})
    else:
        return jsonify({'results': 'Use a POST call.'})

if __name__ == '__main__':
    configuration = svm_utils.parseConfig(configurations)
    app.import_name = '.'
    socketio.run(app, host='0.0.0.0', port=5005)
