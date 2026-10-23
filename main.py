# input text come from Alameda County voter guide and a sample of text
# from each candidate's website. result files are:

# text_stats.csv total keyword hits for each text source
# matching_sentences.csv shows each sentence where any keyword was flagged so we can see
# candidate_keywords.csv total keyword hits for each candidate, aggregate across text sources
# candidate_keywords_norm.csv normalized keyword match counts for each candidate, per 1000 words
# candidate_sentences.csv what percentage of sentences use keyword for a given topic

import pandas as pd
import spacy

import analyze_keywords
from topics import TOPICS

nlp = spacy.load("en_core_web_sm")

VOTER_GUIDE = "data/voter_guide.csv"
WEBSITE_TEXT = "data/website_text.csv"
TEXT_BANK = "data/text_bank.csv"

TEXT_STATS = "results/text_stats.csv"
MATCHING_SENTENCES = "results/matching_sentences.csv"
CANDIDATE_KEYWORDS = "results/candidate_keywords.csv"
CANDIDATE_KEYWORDS_NORM = "results/candidate_keywords_norm.csv"
CANDIDATE_SENTENCES = "results/candidate_sentences.csv"

guide = pd.read_csv(VOTER_GUIDE)
website = pd.read_csv(WEBSITE_TEXT)

guide = guide.rename(columns={"statement" : "text"})
guide["source"] = "voter guide"
guide["subject"] = "statement"
website["source"] = "campaign website"

text_bank = pd.concat([guide, website])
text_bank = text_bank[text_bank["text"] != ""].copy()
text_bank["text id"] = range(len(text_bank))

text_bank.to_csv(TEXT_BANK, index=False)

text_stats = analyze_keywords.analyze_texts(text_bank)
text_stats.to_csv(TEXT_STATS, index=False)

matching_sentences = analyze_keywords.collect_sentences(text_bank, TOPICS)
matching_sentences.to_csv(MATCHING_SENTENCES, index=False)

candidate_keywords, candidate_keywords_norm = analyze_keywords.candidate_keyword_count(text_bank)
candidate_keywords.to_csv(CANDIDATE_KEYWORDS, index=False)
candidate_keywords_norm.to_csv(CANDIDATE_KEYWORDS_NORM, index=False)
candidate_sentences = analyze_keywords.candidate_sentence_pct(text_bank)
candidate_sentences.to_csv(CANDIDATE_SENTENCES, index=False)
