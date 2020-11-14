import os
import svm_lib

def checkPayload(payload, configurations):
    if payload is None:
        return False, {'results': 'Missing JSON payload.'}
    if not 'dataset' in payload:
        return False, {'results': 'Missing data field.'}
    return True, ''

def checkElements(elements, received_dataset, configurations):
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

def checkAppend(payload, model, configurations):
    append = False
    if 'append' in payload:
        append = payload['append']
    if append == False:
        if os.path.isfile(f'{configurations["svmTrainings"]}/{model}.training'):
            return False, {'results': 'Model is present, change name or use append.'}
    return True, ''

def checkAll(payload, model, configurations):
    result, message = checkPayload(payload, configurations)
    if not result:
        return False, message
    result, message = checkAppend(payload, model, configurations)
    if not result:
        return False, message
    return True, ''
