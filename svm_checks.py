import os
import svm_lib

def checkPayload(payload):
    if payload is None:
        return False, {'results': 'Missing JSON payload.'}
    if not 'dataset' in payload:
        return False, {'results': 'Missing data field.'}
    return True, ''

def checkTrainingElements(elements, received_dataset):
    elements_num = -1
    for row in elements:
        if not 'data' in row:
            return False, {'results': 'Missing data field.'}
        if not 'result' in row:
            return False, {'results': 'Missing result field.'}
        elements = row['data'].split(',')
        if elements_num == -1:
            elements_num = len(elements)
        else:
            if (elements_num != len(elements)):
                return False, {'results': 'Data field has a wrong size.'}
        line = svm_lib.elementsToSVM(row["result"], elements)
        received_dataset = f'{received_dataset}\n{line}'
    return True, received_dataset

def checkPredictElements(predict_elements, predict_dataset):
    elements_num = -1
    j = 1
    for predict_row in predict_elements:
        if not 'data' in predict_row:
            return False, {'results': 'Missing data field.'}
        predict_elements = predict_row['data'].split(',')
        if elements_num == -1:
            elements_num = len(predict_elements)
        else:
            if (elements_num != len(predict_elements)):
                return False, {'results': 'Data field has a wrong size.'}
        line = svm_lib.elementsToSVM(j, predict_elements)
        j = j + 1
        predict_dataset = f'{predict_dataset}\n{line}'
    return True, predict_dataset

def checkAppend(obj, configurations):
    payload = obj['payload']
    model = obj['model']
    append = False
    if 'append' in payload:
        append = payload['append']
    if append == False:
        if os.path.isfile(f'{configurations["svmTrainings"]}/{model}.training'):
            return False, {'results': 'Model is present, change name or use append.'}
    return True, ''

def checkPresent(obj, configurations):
    payload = obj['payload']
    model = obj['model']
    if not os.path.isfile(f'{configurations["svmTrainings"]}/{model}.training'):
            return False, {'results': 'Model not is present, change model name.'}
    return True, ''

def checkTrainingAll(obj, configurations):
    payload = obj['payload']
    model = obj['model']
    result, message = checkPayload(payload)
    if not result:
        return False, message
    result, message = checkAppend({'payload':payload, 'model':model}, configurations)
    if not result:
        return False, message
    return True, ''

def checkPredictAll(obj, configurations):
    payload = obj['payload']
    model = obj['model']
    result, message = checkPayload(payload)
    if not result:
        return False, message
    result, message = checkPresent({'payload':payload, 'model':model}, configurations)
    if not result:
        return False, message
    return True, ''
