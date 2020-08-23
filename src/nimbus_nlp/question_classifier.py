import json
import numpy as np
import spacy
import sklearn.neighbors

from .save_and_load_model import save_model, load_latest_model, PROJECT_DIR
from typing import Tuple

# TODO: move the functionality in this module into class(es), so that it can be more easily used as a dependency


class QuestionClassifier:
    def __init__(self, db):
        self.db = db
        self.classifier = None
        self.nlp = spacy.load('en_core_web_sm')
        self.WH_WORDS = {'WDT', 'WP', 'WP$', 'WRB'}
        self.overall_features = {}

    def train_model(self):
        self.classifier = self.build_question_classifier(question_pairs=self.db.get_all_answerable_pairs())
        save_model(self.classifier, "nlp-model")

    def load_latest_classifier(self):
        self.classifier = load_latest_model()
        with open(PROJECT_DIR + '/models/features/overall_features.json', 'r') as fp:
            self.overall_features = json.load(fp)

    # Added question pairs as a parameter to remove database_wrapper as a dependency
    # Including database_wrapper introduces circular dependencies
    def build_question_classifier(self, question_pairs: Tuple[str, str]):
        """
        Build overall feature set for each question based on feature vectors of individual questions.
        Train KNN classification model with overall feature set.
        """
        questions = [q[0] for q in question_pairs]
        question_features = [self.get_question_features(self.nlp(str(q))) for q in questions]

        for feature in question_features:
            for key in feature:
                self.overall_features[key] = 0
        self.overall_features["not related"] = 0

        vectors = []
        for feature in question_features:
            vector_gen = [
                feature[k] if k in feature else 0 for k in self.overall_features
            ]
            vectors.append(np.array(vector_gen))

        vectors = np.array(vectors)
        y_train = np.array(questions)
        new_classifier = sklearn.neighbors.KNeighborsClassifier(n_neighbors=1)
        new_classifier.fit(vectors, y_train)

        with open(PROJECT_DIR + "/models/features/overall_features.json", "w") as fp:
            json.dump(self.overall_features, fp)

        return new_classifier

    def is_wh_word(self, token):
        return token.tag_ in self.WH_WORDS

    def filter_wh_tags(self, spacy_doc):
        return [t.text for t in spacy_doc if self.is_wh_word(t)]

    def validate_wh(self, s1, s2):
        # only parses as a spacy doc if necessary
        doc1 = s1 if type(s1) == spacy.tokens.doc.Doc else self.nlp(s1)
        doc2 = s2 if type(s2) == spacy.tokens.doc.Doc else self.nlp(s2)
        return self.filter_wh_tags(doc1) == self.filter_wh_tags(doc2)

    def get_question_features(self, spacy_doc):
        features = dict()

        for token in spacy_doc:

            # Filters stop words, punctuation, and symbols
            if token.is_stop or not (token.is_digit or token.is_alpha):
                continue

            # Add [VARIABLES] with weight 90.
            # token.i returns the index of the token, and token.nbor(n) return the token
            # n places away. Only the left neighbor is tested for brevity.
            elif token.i != 0 and token.nbor(-1).text == "[":
                features[token.text] = 90

            # Add WH words with weight 60
            # elif self.is_wh_word(token):
                # .lemma_ is already lowercase; no .lower() needed
            #    features[token.lemma_] = 3

            # Add all other words with weight 30
            else:
                features[token.lemma_] = 30

        # Replace the stemmed main verb with weight 60
        sent = next(spacy_doc.sents)
        stemmed_main_verb = sent.root.lemma_
        features[stemmed_main_verb] = 60

        return features

    def classify_question(self, question):
        if self.classifier is None:
            raise ValueError("Classifier is not initialized")

        # Create the spacy doc. Handles pos tagging, stop word removal, tokenization,
        # lemmatization, etc
        doc = self.nlp(question)
        test_features = self.get_question_features(doc)

        array_gen = [
            test_features[k] if k in test_features else 0 for k in self.overall_features
        ]
        test_array = np.array(array_gen)

        # Flatten array into a vector
        test_vector = test_array.reshape(1, -1)

        min_dist = np.min(self.classifier.kneighbors(test_vector, n_neighbors=1))

        if min_dist > 150:
            return "I don't think that's a Statistics related question! Try asking something about the STAT curriculum."

        # Cast to string because the classifier returns a numpy.str_, which causes issues
        # with the validate_wh function below.
        predicted_question = str(self.classifier.predict(test_vector)[0])
        # wh_words_match = self.validate_wh(doc, predicted_question)

        return predicted_question
