# input text come from Alameda County voter guide and a sample of text
# from each candidate's website. result files are:

# text_stats.csv total keyword hits for each text source
# matching_sentences.csv shows each sentence where any keyword was flagged so we can see
# candidate_keywords.csv total keyword hits for each candidate, aggregate across text sources
# candidate_keywords_norm.csv normalized keyword match counts for each candidate, per 1000 words
# candidate_sentences.csv what percentage of sentences use keyword for a given topic

import pandas as pd
import spacy

import analysis.analyze_keywords as analyze_keywords
from analysis.topics import TOPICS

nlp = spacy.load("en_core_web_sm")

VOTER_GUIDE = "data/voter_guide.csv"
WEBSITE_TEXT = "data/website_text.csv"
TEXT_BANK = "data/text_bank.csv"
VOTER_GUIDE_P = "data/voter_guide_processed.csv"
WEBSITE_P = "data/website_processed.csv"

TEXT_STATS = "results/text_stats.csv"
MATCHING_SENTENCES = "results/matching_sentences.csv"
CANDIDATE_KEYWORDS = "results/candidate_keywords.csv"
CANDIDATE_KEYWORDS_NORM = "results/candidate_keywords_norm.csv"
CANDIDATE_SENTENCES_PCT = "results/candidate_sentences_pct.csv"
CANDIDATE_SENTENCES = "results/candidate_sentences.csv"
DISTRICT_SENTENCES = "results/district_sentences.csv"
DISTRICT_SENTENCES_PCT = "results/district_sentences_pct.csv"
STATEMENT_KWS = "results/statement_keywords.csv"
STATEMENT_KWS_NORM = "results/statement_keywords_norm.csv"
WEBSITE_KWS = "results/website_keywords.csv"
WEBSITE_KWS_NORM = "results/website_keywords_norm.csv"

guide = pd.read_csv(VOTER_GUIDE)
website = pd.read_csv(WEBSITE_TEXT)

guide = guide.rename(columns={"statement" : "text"})
guide["source"] = "voter guide"
guide["subject"] = "statement"
website["source"] = "campaign website"

guide = guide[guide["text"] != ""].copy()
guide["text id"] = range(len(guide))
guide.to_csv(VOTER_GUIDE_P, index=False)

website = website[website["text"] != ""].copy()
website["text id"] = range(len(website))
website.to_csv(WEBSITE_P, index=False)

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
candidate_sentences, candidate_sentences_pct = analyze_keywords.candidate_sentences(text_bank)
candidate_sentences.to_csv(CANDIDATE_SENTENCES, index=False)
candidate_sentences_pct.to_csv(CANDIDATE_SENTENCES_PCT, index=False)

district_sentences, district_sentences_pct = analyze_keywords.district_sentences(candidate_sentences)
district_sentences.to_csv(DISTRICT_SENTENCES, index=False)
district_sentences_pct.to_csv(DISTRICT_SENTENCES_PCT, index=False)

statement_kws, statement_kws_norm = analyze_keywords.candidate_keyword_count(guide)
statement_kws.to_csv(STATEMENT_KWS, index=False)
statement_kws_norm.to_csv(STATEMENT_KWS_NORM, index=False)

website_kws, website_kws_norm = analyze_keywords.candidate_keyword_count(website)
website_kws.to_csv(WEBSITE_KWS, index=False)
website_kws_norm.to_csv(WEBSITE_KWS_NORM, index=False)
