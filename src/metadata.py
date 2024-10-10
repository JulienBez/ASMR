from .utils import *

def tokenProportions():
    """"""
    num_sentences = 0
    num_token = 0
    vocabulary = set()
    for path in glob.glob("data/*.json"):
        data = openJson(path)
        for entry in data:
            list_tok = entry["parsing"]["TOK"]
            num_token += len(list_tok)
            num_sentences += 1
            vocabulary.update(list_tok)
    total_vocabulary = len(vocabulary)
    print(f"Tokens total: {num_token}")
    print(f"Sentences total: {num_sentences}")
    print(f"Vocabulary total: {total_vocabulary}")
    print(f"Mean number of token per sentence: {num_token/num_sentences}")
    print(f"Type to token ratio: {total_vocabulary/num_token}")
