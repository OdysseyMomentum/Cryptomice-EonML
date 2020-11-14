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
import configparser
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
from markupsafe import escape
import svm_lib

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
    commands.append({'path': '/', 'type': 'GET', 'description': 'Information about SVM_SERVER commands.' })
    commands.append({'path': '/model', 'type': 'GET', 'description': 'Get a list of known models.' })
    commands.append({'path': '/model/<modelname>', 'type': 'GET', 'description': 'Get informations connected to model <modelname>.' })
    commands.append({'path': '/model/<modelname>/train', 'type': 'POST', 'description': 'Create a new model called <modelname>.' })
    commands.append({'path': '/model/<modelname>/predict', 'type': 'GET/POST', 'description': 'Create a prediction using model <modelname> and passed dataset.' })
    return jsonify({'name':NAME, 'version':VERSION, 'commands':commands})


@app.route('/model')
def models():
    results = svm_lib.listElement(f'ls -l {svmModels}/*.model', svmModels)
    json_result = {'results': results}
    return jsonify(json_result)


@app.route('/model/<mymodel>')
def model(mymodel):
    model = escape(mymodel)
    results = {}
    results['models'] = svm_lib.listFile(f'ls -l {svmModels}/{model}.model')
    results['trainings'] = svm_lib.listFile(f'ls -l {svmTrainings}/{model}.training')
    results['datasets'] = svm_lib.listFile(f'ls -l {svmPredictions}/{model}*.data')
    results['predictions'] = svm_lib.listFile(f'ls -l {svmPredictions}/{model}*.predictions')
    return jsonify({'results': results})


def checkPayload(payload):
    if payload is None:
        return False, {'results': 'Missing JSON payload.'}
    if not 'dataset' in payload:
        return False, {'results': 'Missing data field.'}
    return True, ''

@app.route('/model/<mymodel>/train', methods=['GET', 'POST'])
def train(mymodel):
    if request.method == 'POST':
        model = escape(mymodel)
        timestr = time.strftime("%Y%m%d-%H%M%S")+'-'+str(time.time())
        received_dataset = f'# dataset - {timestr}'
        # check received data
        payload = request.get_json()
        result, message = checkPayload(payload)
        if not result:
            return jsonify(message)

        # check if model is not present if needed
        append = False
        if 'append' in payload:
            append = payload['append']
        if append == False:
            if os.path.isfile(f'{svmTrainings}/{model}.training'):
                json_result = {'results': 'Model is present, change name or use append.'}
                return jsonify(json_result)

        # elaborate dataset
        elements_num = -1
        for row in payload['dataset']:
            if not 'data' in row:
                return jsonify({'results': 'Missing data field.'})
            if not 'result' in row:
                return jsonify({'results': 'Missing result field.'})

            elements = row['data'].split(',')
            if elements_num == -1:
                elements_num = len(elements)
            else:
                if (elements_num != len(elements)):
                    return jsonify({'results': 'Data field has a wrong size.'})

            # create {model}.training lines
            line = svm_lib.elementsToSVM(row["result"], elements)
            received_dataset = f'{received_dataset}\n{line}'

        # create {model}.training file
        svm_lib.writeSVM(f'{svmTrainings}/{model}.training', received_dataset)
        status = subprocess.check_output(f'{svmPath}/svm_learn -z r {svmTrainings}/{model}.training {svmModels}/{model}.model', shell=True).decode().splitlines()
        results = svm_lib.readSVM(f'{svmModels}/{model}.model')
        return jsonify({'status': status, 'results': results})
    else: # if it's not a post call fail
        return jsonify({'results': 'Use a POST call.'})


@app.route('/model/<mymodel>/predict', methods=['GET', 'POST'])
def predict(mymodel):
    model = escape(mymodel)
    timestr = time.strftime("%Y%m%d-%H%M%S")+'-'+str(time.time())
    received_dataset = f'# dataset - {timestr}'
    if request.method == 'POST':
        # check received data
        payload = request.get_json()
        result, message = checkPayload(payload)
        if not result:
            return jsonify(message)

        # check if model is present
        if not os.path.isfile(f'{svmModels}/{model}.model'):
            return jsonify({'results': 'Model is not present.'})

        # elaborate dataset
        elements_num = -1
        j = 1
        for row in payload['dataset']:
            if not 'data' in row:
                return jsonify({'results': 'Missing data field.'})

            elements = row['data'].split(',')
            if elements_num == -1:
                elements_num = len(elements)
            else:
                if (elements_num != len(elements)):
                    return jsonify({'results': 'Data field has a wrong size.'})

            # create {model}.training lines
            line = svm_lib.elementsToSVM(j, elements)
            received_dataset = f'{received_dataset}\n{line}'

        # create {model}.training file
        svm_lib.writeSVM(f'{svmPredictions}/{model}-{timestr}.data', received_dataset)
        status = subprocess.check_output(f'{svmPath}/svm_classify {svmPredictions}/{model}-{timestr}.data {svmModels}/{model}.model {svmPredictions}/{model}-{timestr}.predictions', shell=True).decode().splitlines()
        dat = svm_lib.readSVM(f'{svmPredictions}/{model}-{timestr}.data')
        res = svm_lib.readSVM(f'{svmPredictions}/{model}-{timestr}.predictions')
        results = []
        for x in range(0,len(dat)-1):
            results.append({'data':dat[x+1], 'result':res[x]})
        return jsonify({'status': status, 'results': results})
    elif request.method == 'GET': # if noget
        if 'data' in request.values:
            line = received_dataset+'\n'+elementsToSVM('1', request.values['data'].split(','))
            svm_lib.writeSVM(f'{svmPredictions}/{model}-{timestr}.data', line)
            status = subprocess.check_output(f'{svmPath}/svm_classify {svmPredictions}/{model}-{timestr}.data {svmModels}/{model}.model {svmPredictions}/{model}-{timestr}.predictions', shell=True).decode().splitlines()
            results = svm_lib.readSVM(f'{svmPredictions}/{model}-{timestr}.predictions')
            return jsonify({'results': results})
        else:
            return jsonify({'results': 'Missing data.'})
    else:
        return jsonify({'results': 'Use a POST call.'})


if __name__ == '__main__':
    print(BANNER)
    print(f'{NAME} {VERSION}')
    app.import_name = '.'
    socketio.run(app, host='0.0.0.0', port=5005)
