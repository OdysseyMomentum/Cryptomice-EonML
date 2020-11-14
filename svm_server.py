# :'######::'##::::'##:'##::::'##:::::::::::'######::'########:'########::'##::::'##:'########:'########::
# '##... ##: ##:::: ##: ###::'###::::::::::'##... ##: ##.....:: ##.... ##: ##:::: ##: ##.....:: ##.... ##:
#  ##:::..:: ##:::: ##: ####'####:::::::::: ##:::..:: ##::::::: ##:::: ##: ##:::: ##: ##::::::: ##:::: ##:
# . ######:: ##:::: ##: ## ### ##::::::::::. ######:: ######::: ########:: ##:::: ##: ######::: ########::
# :..... ##:. ##:: ##:: ##. #: ##:::::::::::..... ##: ##...:::: ##.. ##:::. ##:: ##:: ##...:::: ##.. ##:::
# '##::: ##::. ## ##::: ##:.:: ##::::::::::'##::: ##: ##::::::: ##::. ##:::. ## ##::: ##::::::: ##::. ##::
# . ######::::. ###:::: ##:::: ##:'#######:. ######:: ########: ##:::. ##:::. ###:::: ########: ##:::. ##:
# :......::::::...:::::..:::::..::.......:::......:::........::..:::::..:::::...:::::........::..:::::..::
#
#
#
#

import time
import json
import os
import os.path
import subprocess
import configparser
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
from markupsafe import escape

NAME="SVM_SERVER"
VERSION="0.0.1-odyssey"
BANNER="""
:'######::'##::::'##:'##::::'##:::::::::::'######::'########:'########::'##::::'##:'########:'########::
'##... ##: ##:::: ##: ###::'###::::::::::'##... ##: ##.....:: ##.... ##: ##:::: ##: ##.....:: ##.... ##:
 ##:::..:: ##:::: ##: ####'####:::::::::: ##:::..:: ##::::::: ##:::: ##: ##:::: ##: ##::::::: ##:::: ##:
. ######:: ##:::: ##: ## ### ##::::::::::. ######:: ######::: ########:: ##:::: ##: ######::: ########::
:..... ##:. ##:: ##:: ##. #: ##:::::::::::..... ##: ##...:::: ##.. ##:::. ##:: ##:: ##...:::: ##.. ##:::
'##::: ##::. ## ##::: ##:.:: ##::::::::::'##::: ##: ##::::::: ##::. ##:::. ## ##::: ##::::::: ##::. ##::
. ######::::. ###:::: ##:::: ##:'#######:. ######:: ########: ##:::. ##:::. ###:::: ########: ##:::. ##:
:......::::::...:::::..:::::..::.......:::......:::........::..:::::..:::::...:::::........::..:::::..::
"""

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

config = configparser.RawConfigParser()
config.read('svm_server.conf')
svmPath = config.get('SVM', 'path')
svmModels = config.get('SVM', 'models')
svmPredictions = config.get('SVM', 'predictions')
svmTrainings = config.get('SVM', 'trainings')


@app.route('/')
def home():
    df = subprocess.check_output('df -h /', shell=True)
    commands = []
    commands.append({
        'path': '/',
        'type': 'GET',
        'description': 'Information about SVM_SERVER commands.' })
    commands.append({
        'path': '/model',
        'type': 'GET',
        'description': 'Get a list of known models.' })
    commands.append({
        'path': '/model/<modelname>',
        'type': 'GET',
        'description': 'Get informations connected to model <modelname>.' })
    commands.append({
        'path': '/model/<modelname>/train',
        'type': 'POST',
        'description': 'Create a new model called <modelname>.' })
    commands.append({
        'path': '/model/<modelname>/predict',
        'type': 'GET/POST',
        'description': 'Create a prediction using model <modelname> and passed dataset.' })

    json_result = {'name':NAME, 'version':VERSION, 'commands':commands}
    return jsonify(json_result)


@app.route('/model')
def models():
    models = subprocess.check_output(f'ls -l {svmModels}/*.model', shell=True).decode().splitlines()
    results = []
    for model in models:
        elements = model.split(' ')
        if len(elements) > 2:
            results.append(elements[-1].split(f'{svmModels}/')[1].split('.model')[0])
    json_result = {'results': results}
    return jsonify(json_result)

@app.route('/model/<mymodel>')
def model(mymodel):
    model = escape(mymodel)
    results = {'models':[], 'trainings':[], 'datasets':[], 'predictions':[]}

    for row in subprocess.check_output(f'ls -l {svmModels}/{model}.model', shell=True).decode().splitlines():
        elements = row.split(' ')
        if len(elements) > 2:
            results['models'].append(elements[-1])

    for row in subprocess.check_output(f'ls -l {svmTrainings}/{model}.training', shell=True).decode().splitlines():
        elements = row.split(' ')
        if len(elements) > 2:
            results['trainings'].append(elements[-1])

    for row in subprocess.check_output(f'ls -l {svmPredictions}/{model}*.data', shell=True).decode().splitlines():
        elements = row.split(' ')
        if len(elements) > 2:
            results['datasets'].append(elements[-1])

    for row in subprocess.check_output(f'ls -l {svmPredictions}/{model}*.predictions', shell=True).decode().splitlines():
        elements = row.split(' ')
        if len(elements) > 2:
            results['predictions'].append(elements[-1])

    json_result = {'results': results}
    return jsonify(json_result)


@app.route('/model/<mymodel>/train', methods=['GET', 'POST'])
def train(mymodel):
    if request.method == 'POST':
        model = escape(mymodel)
        timestr = time.strftime("%Y%m%d-%H%M%S")+'-'+str(time.time())
        received_dataset = f'# dataset - {timestr}'
        # check received data
        elements_num = -1
        payload = request.get_json()
        if payload is None:
            json_result = {'results': 'Missing JSON payload.'}
            return jsonify(json_result)
        if not 'dataset' in payload:
            json_result = {'results': 'Missing data field.'}
            return jsonify(json_result)

        # check if model is not present if needed
        append = False
        if 'append' in payload:
            append = payload['append']
        if append == False:
            if os.path.isfile(f'{svmTrainings}/{model}.training'):
                json_result = {'results': 'Model is present, change name or use append.'}
                return jsonify(json_result)

        # elaborate dataset
        for row in payload['dataset']:
            if not 'data' in row:
                json_result = {'results': 'Missing data field.'}
                return jsonify(json_result)
            if not 'result' in row:
                json_result = {'results': 'Missing result field.'}
                return jsonify(json_result)

            elements = row['data'].split(',')
            if elements_num == -1:
                elements_num = len(elements)
            else:
                if (elements_num != len(elements)):
                    json_result = {'results': 'Data field has a wrong size.'}
                    return jsonify(json_result)

            # create {model}.training lines
            line = f'{row["result"]}'
            i = 1
            for e in elements:
                line = f'{line} {i}:{e}'
                i = i + 1
            received_dataset = f'{received_dataset}\n{line}'

        # create {model}.training file
        with open(f'{svmTrainings}/{model}.training', 'a') as myfile:
            myfile.write(received_dataset)
            myfile.write('\n')

        status = subprocess.check_output(f'{svmPath}/svm_learn -z r {svmTrainings}/{model}.training {svmModels}/{model}.model', shell=True).decode().splitlines()
        with open (f'{svmModels}/{model}.model', 'r') as myfile:
            results = [x.strip() for x in myfile.readlines()]
        json_result = {'status': status, 'results': results}
        return jsonify(json_result)
    else:
        json_result = {'results': 'Use a POST call.'}
        return jsonify(json_result)


@app.route('/model/<mymodel>/predict', methods=['GET', 'POST'])
def predict(mymodel):
    model = escape(mymodel)
    timestr = time.strftime("%Y%m%d-%H%M%S")+'-'+str(time.time())
    received_dataset = f'# dataset - {timestr}'
    if request.method == 'POST':
        # check received data
        elements_num = -1
        payload = request.get_json()
        if payload is None:
            json_result = {'results': 'Missing JSON payload.'}
            return jsonify(json_result)
        if not 'dataset' in payload:
            json_result = {'results': 'Missing data field.'}
            return jsonify(json_result)

        # check if model is present
        if not os.path.isfile(f'{svmModels}/{model}.model'):
            json_result = {'results': 'Model is not present.'}
            return jsonify(json_result)

        # elaborate dataset
        j = 1
        for row in payload['dataset']:
            if not 'data' in row:
                json_result = {'results': 'Missing data field.'}
                return jsonify(json_result)

            elements = row['data'].split(',')
            if elements_num == -1:
                elements_num = len(elements)
            else:
                if (elements_num != len(elements)):
                    json_result = {'results': 'Data field has a wrong size.'}
                    return jsonify(json_result)

            # create {model}.training lines
            line = f'{j}'
            j = j + 1
            i = 1
            for e in elements:
                line = f'{line} {i}:{e}'
                i = i + 1
            received_dataset = f'{received_dataset}\n{line}'

        # create {model}.training file
        with open(f'{svmPredictions}/{model}-{timestr}.data', 'a') as myfile:
            myfile.write(received_dataset)
            myfile.write('\n')

        status = subprocess.check_output(f'{svmPath}/svm_classify {svmPredictions}/{model}-{timestr}.data {svmModels}/{model}.model {svmPredictions}/{model}-{timestr}.predictions', shell=True).decode().splitlines()
        with open (f'{svmPredictions}/{model}-{timestr}.data', 'r') as myfile:
            dat = [x.strip() for x in myfile.readlines()]
        with open (f'{svmPredictions}/{model}-{timestr}.predictions', 'r') as myfile:
            res = [x.strip() for x in myfile.readlines()]
        results = []
        for x in range(0,len(dat)-1):
            results.append({'data':dat[x+1], 'result':res[x]})
        json_result = {'status': status, 'results': results}
        return jsonify(json_result)
    else:
        if 'data' in request.values:
            elements = request.values['data'].split(',')
            line = '1'
            i = 1
            for e in elements:
                line = f'{line} {i}:{e}'
                i = i + 1
            received_dataset = f'{received_dataset}\n{line}'

            # create {model}.training file
            with open(f'{svmPredictions}/{model}-{timestr}.data', 'a') as myfile:
                myfile.write(received_dataset)
                myfile.write('\n')

            status = subprocess.check_output(f'{svmPath}/svm_classify {svmPredictions}/{model}-{timestr}.data {svmModels}/{model}.model {svmPredictions}/{model}-{timestr}.predictions', shell=True).decode().splitlines()
            with open (f'{svmPredictions}/{model}-{timestr}.predictions', 'r') as myfile:
                results = [x.strip() for x in myfile.readlines()]
            json_result = {'results': results}
            return jsonify(json_result)

        else:
            json_result = {'results': 'Use a POST call.'}
            return jsonify(json_result)


if __name__ == '__main__':
    print(BANNER)
    print(f'{NAME} {VERSION}')
    app.import_name = '.'
    socketio.run(app, host='0.0.0.0', port=5005)
