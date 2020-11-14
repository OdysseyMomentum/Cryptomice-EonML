import subprocess


def elementsToSVM(index, elements):
    line = f'{index}'
    i = 1
    for e in elements:
        line = f'{line} {i}:{e}'
        i = i + 1
    return(line)

def writeSVM(filename, payload):
    with open(filename, 'a') as myfile:
        myfile.write(payload)
        myfile.write('\n')

def readSVM(filename):
    with open (filename, 'r') as myfile:
        rows = [x.strip() for x in myfile.readlines()]
    return rows

def listElement(pattern, modelname):
    elements_list = []
    try:
        models = subprocess.check_output(pattern, shell=True).decode().splitlines()
        for model in models:
            elements = model.split(' ')
            if len(elements) > 2:
                elements_list.append(elements[-1].split(f'{modelname}/')[1].split('.model')[0])
    except:
        pass
    return(elements_list)

def listFile(pattern):
    files_list = []
    try:
        for row in subprocess.check_output(pattern, shell=True).decode().splitlines():
            file = row.split(' ')
            if len(file) > 2:
                files_list.append(file[-1])
    except:
        pass
    return(files_list)
