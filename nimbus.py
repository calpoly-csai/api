# This import fixes a segfault on Ubuntu 18.04.1 LTS.  It doesn't seem to do anything,
# and doesn't seem to be used by anything, but if its removed, the program segfaults.
# See issue #90 on github. This segfault does not occur on Mac or Windows.
# Feel free to debug this if you would like.  Current dev hours counter on this issue:
# 30 hours
# Update the counter above if you work on this issue.
#
from werkzeug.exceptions import BadRequestKeyError
from QA import create_qa_mapping, generate_fact_QA
from nimbus_nlp.NIMBUS_NLP import NIMBUS_NLP


class Nimbus:
    def __init__(self):
        self.qa_dict = create_qa_mapping(generate_fact_QA("q_a_pairs.csv"))

    def answer_question(self, question):
        ans_dict = NIMBUS_NLP.predict_question(question)
        print(ans_dict)
        try:
            qa = self.qa_dict[ans_dict["question class"]]
        except KeyError:
            return "I'm sorry, I don't understand. Please try another question."
        else:
            answer = qa.answer(ans_dict)
            if answer is None:
                return (
                    "I'm sorry, I understand your question but was unable to find an answer. "
                    "Please try another question."
                )
            else:
                return answer


if __name__ == "__main__":
    nimbus = Nimbus()
    while True:
        question = input("Enter a question: ")
        print(nimbus.answer_question(question))
