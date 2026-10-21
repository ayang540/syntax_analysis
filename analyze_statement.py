import spacy
import pandas as pd

nlp = spacy.load("en_core_web_sm")
df = pd.read_csv("data/voter_guide.csv")

def analyze_statement(text):
    doc = nlp(text)
    tokens = [
        token for token in doc
        if not token.is_punct and not token.is_space
    ]

    tok_count = len(tokens)
    pos_counts = {
        "noun_count": sum(
            1 for token in tokens
            if token.pos_ == "NOUN"
        ),
        "proper_noun_count": sum(
            1 for token in tokens
            if token.pos_ == "PROPN"
        ),

        "verb_count": sum(
            1 for token in tokens
            if token.pos_ == "VERB"
        ),

        "auxiliary_count": sum(
            1 for token in tokens
            if token.pos_ == "AUX"
        ),

        "adjective_count": sum(
            1 for token in tokens
            if token.pos_ == "ADJ"
        ),

        "adverb_count": sum(
            1 for token in tokens
            if token.pos_ == "ADV"
        ),

        "pronoun_count": sum(
            1 for token in tokens
            if token.pos_ == "PRON"
        ),
    }

    sentences = list(doc.sents)
    sent_count = len(sentences)
    avg_sent_length = (sum(sum(1 for token in sentence if not token.is_punct and not token.is_space)
    for sentence in sentences) / sent_count if sent_count > 0 else 0)

    return {
        "token_count": tok_count,
        "sentence_count": sent_count,
        "average_sentence_length": avg_sent_length,
        **pos_counts
    }

results = df["Statement"].apply(analyze_statement)
features = pd.DataFrame(results.tolist())
output = pd.concat([df.reset_index(drop=True), features], axis=1)
output.to_csv("results.csv", index=False)
print(output)