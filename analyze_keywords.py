import pandas as pd
import re
import spacy

from topics import TOPICS

nlp = spacy.load("en_core_web_sm")

lemma_cache = {}

def get_lemma(word):
    if word not in lemma_cache:
        lemma_cache[word] = nlp(word)[0].lemma_.lower()
    return lemma_cache[word]

def count_phrases(text, phrases):
    text = str(text).lower()
    count = 0

    for phrase in phrases:
        pattern = (r"\b" + re.escape(phrase.lower()) + r"\b")
        count += len(re.findall(pattern, text))

    return count

def analyze_texts(text_bank):
    results = []
    for _, row in text_bank.iterrows():
        text = str(row["text"])
        wc = len(text.split()) # approx wordcount
        result = {
            "text_id" : row["text id"],
            "candidate" : row["candidate"],
            "district" : row["district"],
            "source" : row["source"],
            "subject" : row["subject"],
            "approx. word count" : wc
        }
        for topic, phrases in TOPICS.items():
            result[topic] = count_phrases(text, phrases)

        results.append(result)
    return pd.DataFrame(results)

def candidate_keyword_count(text_bank):
    results = []
    results_norm = []
    for candidate, candidate_text in text_bank.groupby("candidate"):
        docs = [nlp(str(text)) for text in candidate_text["text"] if pd.notna(text) and str(text).strip()]
        sentences = [sent for doc in docs for sent in doc.sents if sent.text.strip()]
        total_sents = len(sentences)
        total_wc = candidate_text["text"].apply(
            lambda text: len(str(text).split())
        ).sum()
        candidate_result = {
            "candidate" : candidate,
            "word count": total_wc,
            "total sentences": total_sents
        }
        candidate_result_norm = {
                    "candidate" : candidate,
                    "word count": total_wc,
                    "total sentences": total_sents
                }
        for topic, phrases in TOPICS.items():
            kw_count = candidate_text["text"].apply(lambda text: count_phrases(text, phrases)).sum()
            if total_wc > 0:
                norm_count = (kw_count * 1000 / total_wc)
            else:
                norm_count = 0
            candidate_result[topic + " total keywords"] = kw_count
            candidate_result_norm[topic + " keyword per 1000 words"] = norm_count
        results.append(candidate_result)
        results_norm.append(candidate_result_norm)
    return pd.DataFrame(results), pd.DataFrame(results_norm)

def candidate_sentence_pct(text_bank):
    results = []
    for candidate, candidate_text in text_bank.groupby("candidate"):
        docs = [nlp(str(text)) for text in candidate_text["text"] if pd.notna(text) and str(text).strip()]
        sentences = [sent for doc in docs for sent in doc.sents if sent.text.strip()]
        total_sents = len(sentences)
        valid_texts = candidate_text["text"].fillna("").astype(str)
        total_wc = valid_texts.apply(lambda text: len(str(text).split())).sum()
        candidate_result = {
            "candidate" : candidate,
            "word count": total_wc,
            "total sentences": total_sents
        }
        for topic, phrases in TOPICS.items():
            matching_sents = sum(1 for sent in sentences if sent_matches(sent, phrases))
            if total_sents > 0:
                pct = (matching_sents / total_sents * 100)
            else:
                pct = 0
            candidate_result[topic + r" % of sentences"] = pct
        results.append(candidate_result)
    return pd.DataFrame(results)

def collect_sentences(text_bank, topics):
    results = []
    for _, row in text_bank.iterrows():
        text = str(row["text"])
        doc = nlp(text)
        for sentence in doc.sents:
            sent_text = sentence.text.strip()
            if not sent_text:
                continue
            # sent_lower = sent_text.lower()
            for topic, kws in topics.items():
                matched_kws = get_match_kws(sentence, kws)
                if matched_kws:
                    results.append({
                        "candidate": row["candidate"],
                        "source": row["source"],
                        "subject": row.get("subject", ""),
                        "topic": topic,
                        "matched_keywords": ", ".join(matched_kws),
                        "sentence": sent_text
                    })
    return pd.DataFrame(results)

def get_match_kws(sent, kws):
    sent_lemmas = {token.lemma_.lower() for token in sent if not token.is_punct and not token.is_space}
    sent_text = sent.text.lower()
    matched = []
    for kw in kws:
        kw = kw.lower().strip()
        if " " in kw:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, sent_text):
                matched.append(kw)
        else:
            kw_lemma = get_lemma(kw)
            if kw_lemma in sent_lemmas:
                matched.append(kw)
    return matched

def sent_matches(sent, kws):
    return len(get_match_kws(sent, kws)) > 0
