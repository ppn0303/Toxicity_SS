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

try:
    from lightgbm import LGBMClassifier
except: 
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "lightgbm"])
    from lightgbm import LGBMClassifier

warnings.filterwarnings('ignore')

from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')


def main():
    x, y = load_data()

    params_dict = {
        'objective': ['multiclass'],
        'num_leaves': [15, 21, 27, 31, 33],
        'max_depth': [-1, 2],
        'n_estimators': [5, 10, 50, 100, 130],
        'min_child_samples': [10, 20, 25, 30]
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
                model = LGBMClassifier(random_state = seed_, **params[p])
            except: 
                model = LGBMClassifier(**params[p])
                
            model.fit(x_train, y_train)
            pred = model.predict(x_test)
            
            result['precision']['model'+str(p)].append(precision_score(y_test, pred, average = 'macro'))
            result['recall']['model'+str(p)].append(recall_score(y_test, pred, average = 'macro'))
            result['f1']['model'+str(p)].append(f1_score(y_test, pred, average = 'macro'))
            result['accuracy']['model'+str(p)].append(accuracy_score(y_test, pred))
            
            # r_ = CV(x, 
            #         y, 
            #         LGBMClassifier, 
            #         params[p], 
            #         seed = seed_)
            
            # result['precision']['model'+str(p)].append(r_['val_precision'])
            # result['recall']['model'+str(p)].append(r_['val_recall'])
            # result['f1']['model'+str(p)].append(r_['val_f1'])
            # result['accuracy']['model'+str(p)].append(r_['val_accuracy'])
        
    json.dump(result, open('../results/test_results/lgb.json', 'w'))


if __name__ == '__main__':
    main()
