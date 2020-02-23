import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction import DictVectorizer
from sklearn import svm
from sklearn.externals import joblib
import pickle
from datetime import datetime
from os import listdir
from os.path import isfile, join
import re

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
now = datetime.now()
date_time = now.strftime("_%m_%d_%Y_%H_%M_%S")


def save_model(model, model_name):
    save_path = PROJECT_DIR + '/models/' + model_name + date_time + '.pkl'
    f = open(save_path, 'wb')
    pickle.dump(model, f)
    f.close()
    print('Saved model :', save_path)


def load_model(model_name):
    train_path = PROJECT_DIR + '/models/' + model_name + '.joblib'
    return joblib.load(train_path)

def load_latest_model():
    train_path = PROJECT_DIR + '/models/'
    onlyfiles = [f for f in listdir(train_path) if isfile(join(train_path, f))]
    r = [(f, datetime.strptime(re.findall(r'([\d]+_[\d]+_[\d]+_[\d]+_[\d]+_[\d]+)', f)[0], '%m_%d_%Y_%H_%M_%S')) for f in onlyfiles]
    r = sorted(r, key=lambda x: x[1])
    model_path = r[-1][0]
    return joblib.load(train_path + model_path)


