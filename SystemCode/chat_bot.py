import spacy
from spacy import displacy
# !python -m spacy download en_core_web_md
#load the model
import en_core_web_md
nlpm = en_core_web_md.load()

# preprocess
import re
import nltk
from nltk.corpus import wordnet
nltk.download('averaged_perceptron_tagger')
nltk.download('words')
nltk.download('wordnet')
from nltk.corpus import words
from nltk.metrics.distance import jaccard_distance
from nltk.util import ngrams

def lower_casing(sentence):
    # Quiz: How to implement this function without using str.lower()?
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
                          '', sentence,count=0, flags=0)
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

def chatbot_request():
    #starting the bot
    flag=True
    result = {}
    print("CHATTY: My name is CHATTY. I will recommend some cities according to your requirement. If you want to end the conversation, type Bye!")
    while flag==True:
        user_response = input()
        # 句子预处理
        user_response = text_preprocessing(user_response)
        if(user_response.lower() =='bye'):
            flag=False
            print("CHATTY: Bye! take care...")
        elif(user_response.lower() == 'enough'):
            # 开始推荐
            flag = False
            print("CHATTY: Here are cities recommended for you! Have a nice trip!")
        else:
            doc = nlpm(user_response)
            # displacy.render(doc, jupyter=True)

        for token in doc:
            if token.pos_ == 'NOUN':
                max_confidence = 0
                for keyWordVec in keyWordsVec:
                    confidence = nlpm(token.text).similarity(keyWordVec) #和关键词进行匹配
                    if confidence>=0.8 and confidence>max_confidence:
                        # print(token.text + " "+ str(keyWordVec) + " " + str(confidence))
                        max_confidence = confidence
                        adj_words = []
                        # 形容词修饰名词
                        for child in token.children:
                            if child.dep_=='amod' or child.dep_=='compound':
                                adj_words.append(child.text)
                                for grandchild in child.children:
                                    if grandchild.dep_=='neg':
                                        adj_words.append("not")
                        # 主系表结构
                        if not adj_words:
                            if token.dep_=='nsubj':
                                for head_child in token.head.children:
                                    if head_child.dep_=='neg':
                                        adj_words.append("not")
                                    if head_child.dep_=='acomp':
                                        adj_words.append(head_child.text)
                        if not adj_words:
                            for head_child in token.head.children:
                                if head_child.dep_=='amod' or head_child.dep_=='compound':
                                    adj_words.append(head_child.text)
                        result[keyWordVec] = adj_words
        print("Result: " + str(result))
        missKeyWords = keyWordsVec - result.keys()
        # print("Miss Key Words: " + str(missKeyWords))
        print("CHATTY: Could you please add more information on {}? If you think it's enough, type 'enough'.".format(', '.join([word.text for word in missKeyWords])))

# !pip install Wikipedia-API
import wikipediaapi

input = {
    "city": "Shanghai",
    "city_type": "Humanities",
    "cost": "Medium",
    "transport": "Bad",
    "avg_temp": 20,
    "climate": "Temper",
    "air_quality": "Bad"
}
    
def chatbot_response(input):
    wiki = wikipediaapi.Wikipedia(
        user_agent='chat_bot',
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI
    )
    page = wiki.page(input["city"])
    language = "zh"
    lpage = page.langlinks[language]  # fr es ...
    first_paragraph = page.summary.split('\n')[0]  # 使用 split('\n') 分割段落，取第一段
    print(first_paragraph)
    description = input["city"]+" The city type is "+input["city_type"]+". The cost is "+input["cost"]+". The transport is "+input["transport"]+". The avg temp is "+str(input["avg_temp"])+". The climate is "+input["climate"]+". The air quality is "+input["air_quality"]+first_paragraph
    print(description)
