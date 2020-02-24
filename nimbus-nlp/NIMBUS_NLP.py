import nltk
import numpy as np
import os
import pandas as pd
import re
import sklearn.neighbors
import spacy
import sys

from google.api_core.client_options import ClientOptions
from google.cloud import automl_v1
from google.cloud.automl_v1.proto import service_pb2

# Temporary import for the classifier
from question_classifier import QuestionClassifier

class NIMBUS_NLP:

    @staticmethod
    def predict_question(input_question):
        '''
        Runs through variable extraction and the question classifier to
        predict the intended question.

        Args: input_question (string) - user input question to answer

        Return: return_tuple (tuple) - contains the user's input question,
                                       the variable extracted input question,
                                       the entity extracted, and the predicted
                                       answer

        '''

        variable_extraction = Variable_Extraction()
        entity, normalized_sentence = variable_extraction.\
                                        extract_variables(input_question)

        classifier = TrainQuestionClassifier(save_model=False)
        answer = classifier.classify_question(normalized_sentence)

        return_tuple = (input_question, normalized_sentence,
                        entity, answer)

        return return_tuple


class Variable_Extraction:
    def __init__(self):
        self.model_name = None # replace with the project model id
        credential_path = None # replace with the path to the credential json
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
        self.entity = ""

    def inline_text_payload(self, sent):
        '''
        Converts the input sentence into GCP's callable format

        Args: sent (string) - input sentence

        Return: (dict) - GCP NER input format

        '''

        return {'text_snippet': {'content': sent, 'mime_type': 'text/plain'} }

    def get_prediction(self, sent):
        '''
        Obtains the prediction from the input sentence and returns the
        normalized sentence

        Args: sent (string) - input sentence

        Return: request (PredictObject) - predictiton output
        ''' 
        
        params = {}
        
        # Setup API 
        options = ClientOptions(api_endpoint='automl.googleapis.com')
        
        # Create prediction object
        predictor = automl_v1.PredictionServiceClient(client_options=options)

        # Format input sentence
        payload = self.inline_text_payload(sent)
        
        # Make prediction API call
        request = predictor.predict(self.model_name, payload, params)

        # Return the output of the API call
        return request

    def extract_variables(self, sent):
        '''
        Takes the prediction and replaces the entity with its corresponding tag

        Args: sent (string) - input sentence

        Return: (tuple) - (normalized sentence, entity) 

        '''

        # Make the prediction
        request = self.get_prediction(sent)

        # Obtain the entity in the sentence
        self.entity = request.payload[0].text_extraction.text_segment.content 
        
        # Obtain the predicted tag 
        tag = request.payload[0].display_name
        
        return sent.replace(self.entity, '[' + tag + ']'), self.entity


#TODO: Add the Question_Classifier code directly into this file
class Question_Classifier:
    pass

if __name__ == '__main__':
    while True:
        question = input("Enter a question: ")
        answer = NIMBUS_NLP.predict_question(question)
        print(answer)
