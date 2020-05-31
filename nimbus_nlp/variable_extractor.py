import os
import json
from google.api_core.client_options import ClientOptions
from google.cloud import automl_v1


class VariableExtractor:
    def __init__(self, config_file: str = "config.json"):

        with open(config_file) as json_data_file:
            config = json.load(json_data_file)

        if config.get("GOOGLE_CLOUD_NLP_MODEL_NAME", False):
            self.model_name = config["GOOGLE_CLOUD_NLP_MODEL_NAME"]
        else:
            msg = "config.json is missing {} field.".format(
                "GOOGLE_CLOUD_NLP_MODEL_NAME"
            )
            raise Exception(msg)

        credential_path = os.getcwd() + "/auth.json"
        # TODO: consider does this even do anything useful?
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_path

    @staticmethod
    def inline_text_payload(sent):
        """
        Converts the input sentence into GCP"s callable format
        Args: sent (string) - input sentence
        Return: (dict) - GCP NER input format
        """

        return {"text_snippet": {"content": sent, "mime_type": "text/plain"}}

    def get_prediction(self, sent):
        """
        Obtains the prediction from the input sentence and returns the
        normalized sentence
        Args: sent (string) - input sentence
        Return: request (PredictObject) - predictiton output
        """

        params = {}

        # Setup API
        options = ClientOptions(api_endpoint="automl.googleapis.com")

        # Create prediction object
        predictor = automl_v1.PredictionServiceClient(client_options=options)

        # Format input sentence
        payload = self.inline_text_payload(sent)

        # Make prediction API call
        request = predictor.predict(self.model_name, payload, params)

        # Return the output of the API call
        return request

    def extract_variables(self, sent):
        """
        Takes the prediction and replaces the entity with its corresponding tag
        Args: sent (string) - input sentence
        Return: (dict) -    "entity" - extracted entity
                            "tag" - tag of the extracted entity
                            "normalized entity" - stripped entity
                            "input question" - input question from the user
                            "normalized question" - variable-replaced question
        """

        # Make the prediction
        request = self.get_prediction(sent)

        # Create entity dictionary
        e = {"entities": [], "normalized question": None, "input question": None}

        normalized_question = sent

        for n in range(0, len(request.payload)):

            # Obtain the entity in the sentence
            entity = request.payload[n].text_extraction.text_segment.content

            # Obtain the predicted tag
            tag = request.payload[n].display_name

            # Removes excessive words from the entity
            normalized_entity = VariableExtractor.excess_word_removal(entity, tag)

            # Replaces the entity of input question with its corresponding tag
            normalized_entity_question = sent.replace(entity, "[" + tag + "]")

            # Replaces the entity of input question with its corresponding tag along with previous tags
            normalized_question = normalized_question.replace(entity, "[" + tag + "]")

            e['entities'].append({
                "entity": entity,
                "tag": tag,
                "normalized entity": normalized_entity,
                #"input question": sent,
                "normalized entity question": normalized_entity_question
            })

        # Add the raw question
        e['input question'] = sent

        # Add the question with all its corresponding tags replaced
        e['normalized question'] = normalized_question

        return e




    @staticmethod
    def excess_word_removal(entity, tag):
        """
        Checks the tag and determines which excess word removal function to use
        Args: entity (string) - extracted entity from the input question
        Return: (string) - returns the normalized entity string
        """

        if tag == "PROF":
            return VariableExtractor.strip_titles(entity)

        else:
            return entity

    @staticmethod
    def strip_titles(entity):
        """
        Strips titles from input entities
        Args: entity (string) - extracted entity from the input question
        Return: norm_entity (string) - the normalized, title-stripped entity
        """

        # list of titles for removal
        titles = {
            "professor",
            "dr.",
            "dr",
            "doctor",
            "prof",
            "instructor",
            "mrs.",
            "mr.",
            "ms.",
            "mrs",
            "mr",
            "ms",
            "mister",
        }

        # tokenizes the entity
        for name in entity.split():

            # checks each token with the titles set and replaces the title
            # if it is within the word
            if name.lower() in titles:
                return entity.replace(name + " ", "")

        # returns the original entity string
        # if there is no title in the word
        return entity
