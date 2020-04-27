import spacy
import numpy as np
import sklearn.neighbors
from nimbus_nlp.save_and_load_model import save_model, load_latest_model, PROJECT_DIR
import json
from QA import db


# TODO: move the functionality in this module into class(es), so that it can be more easily used as a dependency


class QuestionClassifier:
    def __init__(self):
        self.classifier = None
        self.nlp = spacy.load('en_core_web_sm')
        self.WH_WORDS = {'WDT', 'WP', 'WP$', 'WRB'}
        self.overall_features = {}

    def train_model(self):
        self.save_model = save_model

        # The possible WH word tags returned through NLTK part of speech tagging


        self.classifier = self.build_question_classifier()
        save_model(self.classifier, "nlp-model")


    def load_latest_classifier(self):
        self.classifier = load_latest_model()
        with open(PROJECT_DIR+ '/models/features/overall_features.json', 'r') as fp:
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

        # Disable named entity recognition for speed
        self.nlp = spacy.load("en_core_web_sm", disable=["ner"])
        self.WH_WORDS = {"WDT", "WP", "WP$", "WRB"}
        self.overall_features = {}

    # Added question pairs as a parameter to remove database_wrapper as a dependency
    # Including database_wrapper introduces circular dependencies
    def build_question_classifier(self, question_pairs: Tuple[str, str]):
        """
        Build overall feature set for each question based on feature vectors of individual questions.
        Train KNN classification model with overall feature set.
        """

        questions = [q[0] for q in question_pairs]
        question_features = [self.get_question_features(
            self.nlp(q)) for q in questions]

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

    def train_model(self, question_pairs: Tuple[str, str]):
        self.classifier = self.build_question_classifier(question_pairs)
        save_model(self.classifier, "nlp-model")

    def load_latest_classifier(self):
        self.classifier = load_latest_model()
        with open(PROJECT_DIR + "/models/features/overall_features.json", "r") as fp:
            self.overall_features = json.load(fp)

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
            elif self.is_wh_word(token):
                # .lemma_ is already lowercase; no .lower() needed
                features[token.lemma_] = 60

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

        min_dist = np.min(self.classifier.kneighbors(
            test_vector, n_neighbors=1))

        if min_dist > 150:
            return "I don't think that's a Statistics related question! Try asking something about the STAT curriculum."

        # Cast to string because the classifier returns a numpy.str_, which causes issues
        # with the validate_wh function below.
        predicted_question = str(self.classifier.predict(test_vector)[0])
        wh_words_match = self.validate_wh(doc, predicted_question)

        if not wh_words_match:
            return "WH Words Don't Match"

        return predicted_question




