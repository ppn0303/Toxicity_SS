import sys
sys.path.append('../')

import json
import warnings
import argparse

from tqdm import tqdm

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    precision_score,
    recall_score,
    accuracy_score,
    f1_score
)

from utils.read_data import load_data
from utils.smiles2fing import Smiles2Fing
from utils.common import ParameterGrid

from sklearn.neural_network import MLPClassifier

warnings.filterwarnings('ignore')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inhale-type", type=str, default="vapour")
    try:
        args = parser.parse_args()
    except:
        args = parser.parse_args([])

    x, y = load_data(inhale_type = args.inhale_type)

    params_dict = {
        'hidden_layer_sizes': [(50), (100, 50, 10), (100, 70, 50, 30, 10)],
        'activation': ['relu', 'tanh'],
        'solver': ['adam', 'sgd'],
        'alpha': [0.0001, 0.001],
        'learning_rate_init': [0.001, 0.01, 0.1],
        'max_iter': [50, 100, 200]
    }
    params = ParameterGrid(params_dict)


    result = {}
    result['model'] = {}
    result['precision'] = {}
    result['recall'] = {}
    result['f1'] = {}
    result['accuracy'] = {}

    for p in tqdm(range(len(params))):
        
        result['model']['model'+str(p)] = params[p]
        result['precision']['model'+str(p)] = []
        result['recall']['model'+str(p)] = []
        result['f1']['model'+str(p)] = []
        result['accuracy']['model'+str(p)] = []
        
        for seed_ in range(10):
            x_train, x_test, y_train, y_test = train_test_split(x, y, shuffle = True, random_state = seed_)
            
            try:
                model = MLPClassifier(random_state = seed_, **params[p])
            except: 
                model = MLPClassifier(**params[p])
                
            model.fit(x_train, y_train)
            pred = model.predict(x_test)
            
            result['precision']['model'+str(p)].append(precision_score(y_test, pred, average = 'macro'))
            result['recall']['model'+str(p)].append(recall_score(y_test, pred, average = 'macro'))
            result['f1']['model'+str(p)].append(f1_score(y_test, pred, average = 'macro'))
            result['accuracy']['model'+str(p)].append(accuracy_score(y_test, pred))
            
            # r_ = CV(x, 
            #         y, 
            #         MLPClassifier, 
            #         params[p], 
            #         seed = seed_)
            
            # result['precision']['model'+str(p)].append(r_['val_precision'])
            # result['recall']['model'+str(p)].append(r_['val_recall'])
            # result['f1']['model'+str(p)].append(r_['val_f1'])
            # result['accuracy']['model'+str(p)].append(r_['val_accuracy'])
        
    json.dump(result, open('../results/test_results/' + args.inhale_type + '_mlp.json', 'w'))


if __name__ == '__main__':
    main()
