import svm_lib
import svm_utils
import svm_checks


def test_svm_lib():
    assert svm_lib.elementsToSVM('1', ['1','2','3']) == '1 1:1 2:2 3:3'
    assert svm_lib.listElement('./', '') == []
    assert svm_lib.listFile('./') == []

def test_svm_utils():
    configurations = {'NAME': 'SVM_SERVER', 'VERSION': '9.9.9-test'}
    assert svm_utils.printBanner(configurations) == None
    assert svm_utils.parseConfig(configurations) == {'NAME': 'SVM_SERVER', 'VERSION': '9.9.9-test', 'svmPath': './svm_light', 'svmModels': './models', 'svmPredictions': './predictions', 'svmTrainings': './trainings'}
