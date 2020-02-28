import re
import nltk
import spacy
import numpy as np
import sklearn.neighbors
import pandas as pd
import sys
import json
from save_and_load_model import save_model, load_latest_model

# TODO: move the functionality in this module into class(es), so that it can be more easily used as a dependency


class QuestionClassifier:
    def __init__(self):
        self.classifier = None
        self.nlp = spacy.load('en_core_web_sm')
        self.WH_WORDS = {'WDT', 'WP', 'WP$', 'WRB'}
        self.overall_features = {}

    def train_model(self):
        self.save_model = save_model


        # REPLACE WITH API EVENTUALLY
        self.file_path = "question_set_clean.csv"

        # The possible WH word tags returned through NLTK part of speech tagging


        self.classifier = self.build_question_classifier()
        save_model(self.classifier, "nlp-model")


    def load_latest_classifier(self):
        self.classifier = load_latest_model()
        with open('models/features/overall_features.json', 'r') as fp:
            self.overall_features = json.load(fp)

    def get_question_features(self, question):
        # print("using new algorithm")
        """
        Method to extract features from each individual question.
        """
        features = {}

        # Extract the main verb from the question before additional processing
        main_verb = str(self.extract_main_verb(question))

        # ADD ALL VARIABLES TO THE FEATURE DICT WITH A WEIGHT OF 90
        matches = re.findall(r'(\[(.*?)\])', question)
        for match in matches:
            question = question.replace(match[0], '')
            features[match[0]] = 90

        question = re.sub('[^a-zA-Z0-9]', ' ', question)

        # PRE-PROCESSING: TOKENIZE SENTENCE, AND LOWER AND STEM EACH WORD
        words = nltk.word_tokenize(question)
        words = [word.lower() for word in words if '[' and ']' not in word]

        filtered_words = self.get_lemmas(words)

        # ADD THE LEMMATIZED MAIN VERB TO THE FEATURE SET WITH A WEIGHT OF 60
        stemmed_main_verb = self.nlp(main_verb)[0]
        features[stemmed_main_verb.text] = 60

        # TAG WORDS' PART OF SPEECH, AND ADD ALL WH WORDS TO FEATURE DICT
        # WITH WEIGHT 60
        words_pos = nltk.pos_tag(filtered_words)
        for word_pos in words_pos:
            if self.is_wh_word(word_pos[1]):
                features[word_pos[0]] = 60

        # ADD FIRST WORD AND NON-STOP WORDS TO FEATURE DICT
        filtered_words = [
            word for word in filtered_words if word not in nltk.corpus.stopwords.words('english')]
        for word in filtered_words:
            # ADD EACH WORD NOT ALREADY PRESENT IN FEATURE SET WITH WEIGHT OF 30
            if word not in features:
                features[word] = 30

        return features

    def get_question_features_old_algorithm(self, question):
        print("using old algorithm....")
        """
            Method to extract features from each individual question.
            """
        features = {}

        # ADD ALL VARIABLES TO THE FEATURE DICT WITH A WEIGHT OF 90
        matches = re.findall(r'(\[(.*?)\])', question)
        for match in matches:
            question = question.replace(match[0], '')
            features[match[0]] = 90
        question = re.sub('[^a-zA-Z0-9]', ' ', question)

        # PRE-PROCESSING: TOKENIZE SENTENCE, AND LOWER AND STEM EACH WORD
        words = nltk.word_tokenize(question)
        words = [word.lower() for word in words if '[' and ']' not in word]
        filtered_words = self.get_lemmas(words)

        # ADD FIRST WORD AND NON-STOP WORDS TO FEATURE DICT
        features[filtered_words[0]] = 60
        filtered_words = [
            word for word in filtered_words if word not in nltk.corpus.stopwords.words('english')]
        for word in filtered_words:
            features[word] = 30

        return features

    # EXTRACTS THE MAIN VERB FROM A QUESTION USING THE DEPENDENCY TREE
    # THE MAIN VERB OF THE QUESTION SHOULD BE THE ROOT OF THE TREE
    # Note: this method of extracting the main verb is not perfect, but
    # for single sentence questions that should have no ambiguity about the main verb,
    # it should be sufficient.
    def extract_main_verb(self, question):
        doc = self.nlp(question)
        sents = list(doc.sents)
        if len(sents) == 0:
            raise ValueError("Empty question")

        return sents[0].root

    def get_lemmas(self, words):
        return [self.nlp(word)[0].lemma_ for word in words]

    def is_wh_word(self, pos):
        return pos in self.WH_WORDS

    def build_question_classifier(self):
        """
        Build overall feature set for each question based on feature vectors of individual questions.
        Train KNN classification model with overall feature set.
        """

        # READ QUESTIONS
        questions = pd.read_csv('question_set_clean.csv')
        questions['features'] = questions['questionFormat'].apply(self.get_question_features)
        # old alg: questions['features'] = questions['questionFormat'].apply(self.get_question_features_old_algorithm)

        question_features = questions['features'].values.tolist()

        # BUILD OVERALL FEATURE SET FROM INDIVIDUAL QUESTION FEATURE VECTORS
        for feature in question_features:
            for key in feature:
                if key not in self.overall_features:
                    self.overall_features[key] = 0
        self.overall_features["not related"] = 0


        vectors = []
        for feature in question_features:
            vector = dict.fromkeys(self.overall_features, 0)
            for key in feature:
                vector[key] = feature[key]
            vectors.append(np.array(list(vector.values())))

        y_train = questions['questionFormat']
        vectors = np.array(vectors)
        y_train = np.array(y_train)
        new_classifier = sklearn.neighbors.KNeighborsClassifier(n_neighbors=1)
        new_classifier.fit(vectors, y_train)

        with open('models/features/overall_features.json', 'w') as fp:
            json.dump(self.overall_features, fp)

        return new_classifier

    def filterWHTags(self, question):
        # ADD ALL VARIABLES TO THE FEATURE DICT WITH A WEIGHT OF 90
        matches = re.findall(r'(\[(.*?)\])', question)
        for match in matches:
            question = question.replace(match[0], '')

        question = re.sub('[^a-zA-Z0-9]', ' ', question)

        # PRE-PROCESSING: TOKENIZE SENTENCE, AND LOWER AND STEM EACH WORD
        words = nltk.word_tokenize(question)
        words = [word.lower() for word in words if '[' and ']' not in word]

        filtered_words = self.get_lemmas(words)

        question_tags = nltk.pos_tag(filtered_words)
        question_tags = [
            tag for tag in question_tags if self.is_wh_word(tag[1])]
        return question_tags

    def validate_WH(self, test_question, predicted_question):
        """
        Assumes that only 1 WH word exists
        Returns True if the WH word in the test question equals the
        WH word in the predicted question
        """

        test_tags = self.filterWHTags(test_question)
        predicted_tags = self.filterWHTags(predicted_question)

        # Uncomment these lines below to see
        # print("Test")
        # print(test_tags)
        # print()

        # print("Predicted")
        # print(predicted_tags)
        # print()

        # Compares all WH words in the tags array and returns False if one doesn't match
        min_tag_len = min(len(test_tags), len(predicted_tags))
        wh_match = True
        i = 0
        while (wh_match and i < min_tag_len):
            wh_match = wh_match and (test_tags[i][0] == predicted_tags[i][0])
            i += 1
        return wh_match

    def classify_question(self, test_question):
        """
        Match a user query with a question in the database based on the classifier we trained and overall features we calculated.
        Return relevant question.
        """
        if self.classifier is None:
            raise ValueError("Classifier not initialized")

        #if self.use_new:
        test_features = self.get_question_features(test_question)
        #else:
        #    test_features = self.get_question_features_old_algorithm(
        #        test_question)
        test_vector = dict.fromkeys(self.overall_features, 0)
        for key in test_features:
            if key in test_vector:
                test_vector[key] = test_features[key]
            #else:
                # IF A WORD IS NOT IN THE EXISTING FEATURE SET, IT MAY BE A QUESTION WE CANNOT ANSWER.
            #    test_vector["not related"] += 250
        test_vector = np.array(list(test_vector.values()))
        test_vector = test_vector.reshape(1, -1)
        min_dist = np.min(self.classifier.kneighbors(test_vector, n_neighbors=1)[0])
        if min_dist > 150:
            return "I don't think that's a Statistics related question! Try asking something about the STAT curriculum."

        predicted_question = self.classifier.predict(test_vector)[0]

        wh_words_match = self.validate_WH(test_question, predicted_question)
        # Uncomment to print whether the WH words match
        # print("WH Words Match?:", wh_words_match)

        if (not wh_words_match):
            return "WH Words Don't Match"

        return predicted_question


def main():
    # use_new = False
    # print(sys.argv)
    # if len(sys.argv) > 1 and sys.argv[1] == 'new':
    #     use_new = True
    classifier = QuestionClassifier()
    # print(classifier.get_question_features(
    #     "What are Foaad Khosmood's office hours?"))
    # print(classifier.get_question_features(
    #     "Does Foaad Khosmood have office hours?"))
    # print(classifier.get_question_features("Who teaches CSC 480"))
    # print(classifier.get_question_features("CSC 480 is taught by who?"))
    # print(classifier.get_question_features("Khosmood teaches CSC 480?"))
    # print(classifier.get_question_features(
    #     "Whose office hours are between 1 and 2 pm?"))
    # print(classifier.get_question_features("Where is Franz Kurfess' office?"))
    # print(classifier.get_question_features("This is a normal sentence."))
    # print(classifier.get_question_features("[COURSE] is taught by who?"))
    # print(classifier.get_question_features("How do I register for classes?"))
    #classifier.train_model()
    classifier.load_latest_classifier()
    print(classifier.classify_question("Which [PROF] teaches [COURSE]?"))


if __name__ == "__main__":
    main()
