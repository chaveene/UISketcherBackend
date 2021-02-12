from flask import Flask, request
import spacy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
nlp = spacy.load("en_core_web_sm")
lemmatizer = nlp.get_pipe("lemmatizer")
ruler = nlp.add_pipe("entity_ruler")
# supported UI elements
patterns = [{"label": "UI", "pattern": "button"}, {"label": "UI", "pattern": "textinput"},
            {"label": "UI", "pattern": "card"}, {"label": "UI", "pattern": "imageview"},
            {"label": "UI", "pattern": "header"}, {"label": "UI", "pattern": "textview"}]
ruler.add_patterns(patterns)
all_stopwords = nlp.Defaults.stop_words

# supported attributes
attribute_list = ['title', 'placeholder']


@app.route('/extract/data', methods=['GET', 'POST'])
def extract_data():
    # Preparing data for tokenizing
    doc = nlp(" ".join(request.data.decode('UTF-8').lower().split()))

    # Lemmatisation process
    doc_after_lemmatizer = nlp(' '.join(map(str, [token.lemma_ for token in doc])))

    # Tokenizing , stop words removing and unnecessary characters removing
    tokens = [token.text for token in doc_after_lemmatizer if not token.is_punct if not token.is_stop]

    # Preparing to entity recognition
    doc_after_text_processing = nlp(' '.join(map(str, tokens)))

    # entity recognition
    entity_recognition = [(ent.text, ent.label_) for ent in doc_after_text_processing.ents]

    # Extraction of attribute value if there is any
    attribute_value = extract_attribute(attribute_list, tokens)

    if len(entity_recognition) == 0:
        response_type = {
            "data": {
                "element": "",
                "attribute": ""
            },
            "error": "No UI elements detected"
        }
        return response_type
    else:
        if len(entity_recognition) < 2:
            # Preparing the response json
            response_type = {
                "data": {
                    "element": ' '.join(map(str, [ent.text for ent in doc_after_text_processing.ents])),
                    "attribute": attribute_value
                },
                "error": ""
            }
            return response_type
        else:
            response_type = {
                "data": {
                    "element": "",
                    "attribute": ""
                },
                "error": "Multiple UI Element Detected"
            }
            return response_type


def extract_attribute(attributes, tokens):
    for t in attributes:
        for term in tokens:
            if term != t:
                pass
            elif term == t:
                return tokens[tokens.index(term) + 1]


if __name__ == '__main__':
    app.run()
