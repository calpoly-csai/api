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
from nimbus_nlp.question_classifier import QuestionClassifier

class NIMBUS_NLP:

    @staticmethod
    def predict_question(input_question):
        '''
        Runs through variable extraction and the question classifier to
        predict the intended question.

        Args: input_question (string) - user input question to answer

        Return: nlp_props (dict) - contains the user's input question,
                                   the variable extracted input question,
                                   the entity extracted, and the predicted
                                   answer

        '''

        # Instantiate the variable extraction class
        variable_extraction = Variable_Extraction()

        # Obtain the properties from variable extraction
        nlp_props = variable_extraction.extract_variables(input_question)

        # Instantiate the question classifier class
        classifier = QuestionClassifier()
        classifier.load_latest_classifier()
        
        # Classify the question and add it to the nlp properties dictionary 
        nlp_props["question class"] = classifier.\
                classify_question(nlp_props["normalized question"])
        
        return nlp_props
    

class Variable_Extraction:
    def __init__(self):

        self.model_name = "projects/550037488827/locations/us-central1/models/TEN122771468357468160"
        credential_path = os.getcwd() + "/auth.json"
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

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

        Return: (dict) -    "entity" - extracted entity 
                            "tag" - tag of the extracted entity 
                            "normalized entity" - stripped entity
                            "input question" - input question from the user
                            "normalized question" - variable-replaced question
        '''

        # Make the prediction
        request = self.get_prediction(sent)

        # Obtain the entity in the sentence
        entity = request.payload[0].text_extraction.text_segment.content 
        
        # Obtain the predicted tag 
        tag = request.payload[0].display_name

        # Removes excessive words from the entity
        normalized_entity = Variable_Extraction.excess_word_removal(entity, tag)

        # Replaces the entity of input question with its corresponding tag
        normalized_question = sent.replace(entity, '[' + tag + ']')
        
        return {
                    "entity"                : entity,
                    "tag"                   : tag,
                    "normalized entity"     : normalized_entity,
                    "input question"        : sent,
                    "normalized question"   : normalized_question
               }

    @staticmethod    
    def excess_word_removal(entity, tag):
        '''
        Checks the tag and determines which excess word removal function to use

        Args: entity (string) - extracted entity from the input question

        Return: (string) - returns the normalized entity string

        '''

        if (tag == 'PROF'):
            return Variable_Extraction.strip_titles(entity)

        else:
            return entity

    @staticmethod
    def strip_titles(entity):
        '''
        Strips titles from input entities

        Args: entity (string) - extracted entity from the input question

        Return: norm_entity (string) - the normalized, title-stripped entity

        '''

        # list of titles for removal
        titles = {"professor", "dr.", "dr", "doctor", "prof", "instructor", "mrs.",\
                  "mr.", "ms.", "mrs", "mr", "ms", "mister"}

        # tokenizes the entity
        for name in entity.split():

            # checks each token with the titles set and replaces the title
            # if it is within the word
            if name.lower() in titles:
                return entity.replace(name + " ", "")

        # returns the original entity string 
        # if there is no title in the word
        return entity

#TODO: Add the Question_Classifier code directly into this file
class Question_Classifier:
    pass

if __name__ == '__main__':
    while True:
        question = input("Enter a question: ")
        answer = NIMBUS_NLP.predict_question(question)
        print(answer)
