def elementsToSVM(index, elements):
    line = f'{index}'
    j = j + 1
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
