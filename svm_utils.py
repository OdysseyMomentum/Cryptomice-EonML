import configparser


def printBanner(configurations):
    print("""
    :'######::'##::::'##:'##::::'##:::::::::::'######::'########:'########::'##::::'##:'########:'########::
    '##... ##: ##:::: ##: ###::'###::::::::::'##... ##: ##.....:: ##.... ##: ##:::: ##: ##.....:: ##.... ##:
     ##:::..:: ##:::: ##: ####'####:::::::::: ##:::..:: ##::::::: ##:::: ##: ##:::: ##: ##::::::: ##:::: ##:
    . ######:: ##:::: ##: ## ### ##::::::::::. ######:: ######::: ########:: ##:::: ##: ######::: ########::
    :..... ##:. ##:: ##:: ##. #: ##:::::::::::..... ##: ##...:::: ##.. ##:::. ##:: ##:: ##...:::: ##.. ##:::
    '##::: ##::. ## ##::: ##:.:: ##::::::::::'##::: ##: ##::::::: ##::. ##:::. ## ##::: ##::::::: ##::. ##::
    . ######::::. ###:::: ##:::: ##:'#######:. ######:: ########: ##:::. ##:::. ###:::: ########: ##:::. ##:
    :......::::::...:::::..:::::..::.......:::......:::........::..:::::..:::::...:::::........::..:::::..::
    """)
    print(f'{configurations["NAME"]} {configurations["VERSION"]}')

def parseConfig(configurations):
    printBanner(configurations)
    config = configparser.RawConfigParser()
    config.read('svm_server.conf')
    configurations['svmPath'] = config.get('SVM', 'path')
    configurations['svmModels'] = config.get('SVM', 'models')
    configurations['svmPredictions'] = config.get('SVM', 'predictions')
    configurations['svmTrainings'] = config.get('SVM', 'trainings')
    return configurations
