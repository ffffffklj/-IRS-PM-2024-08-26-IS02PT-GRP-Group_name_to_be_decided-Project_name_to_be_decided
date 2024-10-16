import spacy
# !python -m spacy download en_core_web_md
import en_core_web_md

nlpm = en_core_web_md.load()

import re
import nltk
from nltk.corpus import wordnet
import wikipediaapi

nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('words')
nltk.download('wordnet')
from nltk.corpus import words
from nltk.metrics.distance import jaccard_distance
from nltk.util import ngrams


def lower_casing(sentence):
    new_sentence = sentence.lower()
    return new_sentence


def expand_abbriviation(sentence):
    replacement_patterns = [
        (r'won\'t', 'will not'),
        (r'can\'t', 'cannot'),
        (r'i\'m', 'i am'),
        (r'ain\'t', 'is not'),
        (r'(\w+)\'ll', '\g<1> will'),
        (r'(\w+)n\'t', '\g<1> not'),
        (r'(\w+)\'ve', '\g<1> have'),
        (r'(\w+)\'s', '\g<1> is'),
        (r'(\w+)\'re', '\g<1> are'),
        (r'(\w+)\'d', '\g<1> would')]
    patterns = [(re.compile(regex), repl) for (regex, repl) in replacement_patterns]

    new_sentence = sentence
    for (pattern, repl) in patterns:
        (new_sentence, count) = re.subn(pattern, repl, new_sentence)
    return new_sentence


def punctuation_removal(sentence):
    # Remove the all the punctuations except '
    new_sentence = re.sub(',|!|\?|\"|<|>|\(|\)|\[|\]|\{|\}|@|#|\+|\=|\-|\_|~|\&|\*|\^|%|\||\$|/|`|\.|\'',
                          '', sentence, count=0, flags=0)
    return new_sentence


def get_wordnet_pos(word):
    pack = nltk.pos_tag([word])
    tag = pack[0][1]
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV

    else:
        return None


def lemmatization(sentence):
    lemmatizer = nltk.stem.WordNetLemmatizer()
    new_sentence = [lemmatizer.lemmatize(word, get_wordnet_pos(word) or wordnet.NOUN) for word in sentence.split()]
    return new_sentence


def spell_correction(sentence):
    new_sentence = []
    correct_words = words.words()
    for word in sentence:
        if word not in correct_words:
            # word spells wrong
            min_distance = 1
            word1 = set(ngrams(word, 2))
            for correct_word in correct_words:
                word2 = set(ngrams(correct_word, 2))
                distance = jaccard_distance(word1, word2)
                if distance < min_distance:
                    min_distance = distance
                    word = correct_word
        new_sentence.append(word)
    return new_sentence


def text_preprocessing(raw_sentence):
    sentence = lower_casing(raw_sentence)
    sentence = expand_abbriviation(sentence)
    sentence = punctuation_removal(sentence)
    sentence = lemmatization(sentence)
    sentence = spell_correction(sentence)
    sentence = ' '.join(sentence)
    return sentence


keyWords = ['city', 'cost', 'transport', 'temperature', 'climate', 'air']
keyWordsVec = [nlpm(word) for word in keyWords]


def chatbot_request(user_response):
    # starting the bot
    result = {}
    # sentence process
    user_response = text_preprocessing(user_response)
    if (user_response.lower() == 'bye'):
        reply = "CHATTY: Bye! take care."
        return result, reply
    elif (user_response.lower() == 'enough'):
        reply = "CHATTY: Try to click the button 'Search for city' to get your ideal travel city!"
        return result, reply
    else:
        doc = nlpm(user_response)
        # displacy.serve(doc, style="dep")

        for token in doc:
            if token.pos_ == 'NOUN':
                max_confidence = 0
                for keyWordVec in keyWordsVec:
                    # match the keywords
                    confidence = nlpm(token.text).similarity(keyWordVec)
                    if confidence >= 0.8 and confidence > max_confidence:
                        # print(token.text + " " + str(keyWordVec) + " " + str(confidence))
                        max_confidence = confidence
                        adj_words = []
                        # adjectives modify nouns
                        for child in token.children:
                            if child.dep_ == 'amod' or child.dep_ == 'compound':
                                adj_words.append(child.text)
                                for grandchild in child.children:
                                    if grandchild.dep_ == 'neg':
                                        adj_words.append("not")
                            # combine which, that
                            if child.dep_ == 'relcl':
                                for grandchild in child.children:
                                    if grandchild.dep_ == 'neg':
                                        adj_words.append("not")
                                    if grandchild.dep_ == 'acomp':
                                        adj_words.append(grandchild.text)
                        # Subject-Predicate structure
                        if not adj_words:
                            if token.dep_ == 'nsubj':
                                for head_child in token.head.children:
                                    if head_child.dep_ == 'neg':
                                        adj_words.append("not")
                                    if head_child.dep_ == 'acomp':
                                        adj_words.append(head_child.text)
                        if not adj_words:
                            for head_child in token.head.children:
                                if head_child.dep_ == 'amod' or head_child.dep_ == 'compound':
                                    adj_words.append(head_child.text)
                        result[keyWordVec] = adj_words

        result = {str(key): value for key, value in result.items()}
        missKeyWords = keyWordsVec - result.keys()
        reply = ""
        return result, reply


def chatbot_response(city_name):
    wiki = wikipediaapi.Wikipedia(
        user_agent='chat_bot',
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI
    )
    page = wiki.page(city_name)
    # use split('\n') get the first paragraph
    first_paragraph = page.summary.split('\n')[0]
    description = first_paragraph
    return description
