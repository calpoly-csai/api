import glob
import os
import joblib
import pickle
from datetime import datetime


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
now = datetime.now()
date_time = now.strftime("_%m_%d_%Y_%H_%M_%S")


def save_model(model, model_name):
    save_path = (
        PROJECT_DIR + "/models/classification/" + model_name + date_time + ".pkl"
    )
    f = open(save_path, "wb")
    pickle.dump(model, f)
    f.close()
    print("Saved model :", save_path)


def load_model(model_name):
    train_path = PROJECT_DIR + "/models/classification/" + model_name + ".joblib"
    return joblib.load(train_path)


def load_latest_model():
    # https://stackoverflow.com/a/39327156
    train_path = PROJECT_DIR + "/models/classification/*"
    list_of_files = glob.glob(train_path)
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)
    return joblib.load(latest_file)
