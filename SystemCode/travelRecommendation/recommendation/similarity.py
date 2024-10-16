import pandas as pd
import numpy as np
import nltk
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler
from sentence_transformers import SentenceTransformer
from nltk.corpus import wordnet

nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

df = pd.read_csv("recommendation/FinalDataset.csv")

# initialize encoder and scaler
city_type_encoder = OneHotEncoder(sparse_output=False)
cost_type_encoder = OneHotEncoder(sparse_output=False)
transport_encoder = OneHotEncoder(sparse_output=False)
climate_encoder = OneHotEncoder(sparse_output=False)
air_quality_encoder = OneHotEncoder(sparse_output=False)
cost_index_scaler = MinMaxScaler()
temp_scaler = MinMaxScaler()

# fit to the dataset
city_type_encoder.fit(df[['City_type']])
cost_type_encoder.fit(df[['Living Cost Type']])
transport_encoder.fit(df[['Transport']])
climate_encoder.fit(df[['Climate']])
air_quality_encoder.fit(df[['Air quality level']])
cost_index_scaler.fit(df[['Cost of Living Index']])
temp_scaler.fit(df[['AvgTemp']])

# load a pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')


def get_antonym(word):
    antonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            for ant in lemma.antonyms():
                antonyms.add(ant.name())
    if antonyms:
        return antonyms
    else:
        return None


def semantic_analysis(user_input):
    analyzed_input = {}

    # 定义类别名称列表
    categories = {
        'City_type': ['Balanced', 'Humanities', 'Nature'],
        'Climate': ['Cold', 'Warm', 'Temperate'],
        'Living Cost Type': ['Expensive', 'Medium', 'Cheap'],
        'Transport': ['Good', 'Medium', 'Bad'],
        'Air quality level': ['Good', 'Medium', 'Bad', 'Unknown']
    }

    # define a list of class names
    category_vectors = {}
    for category, names in categories.items():
        category_vectors[category] = model.encode(names)

    def get_phrase_vector(phrase):
        # use SentenceTransformer to encode the entire phrase
        return model.encode(phrase)

    def match_category(input_phrases, category_names, category_vector_list):
        import re
        negation_words = ['not', 'no', 'never', "don't", "doesn't", "didn't", "won't", 'cannot', "can't"]
        # concatenate all input phrases into a single string
        full_phrase = ' '.join(input_phrases)
        # split words using regular expressions by spaces, hyphens, and underscores
        words = re.split(r'\s+|-|_', full_phrase.lower())
        has_negation = any(neg_word in words for neg_word in negation_words)
        target_words = [w for w in words if w not in negation_words]
        if not target_words:
            # return a default value if there is no valid target word
            return None, [0.0] * len(category_names)
        if has_negation:
            # attempt to obtain the antonym of the target word
            antonym_words = []
            for w in target_words:
                antonyms = get_antonym(w)
                if antonyms:
                    # use the first antonym
                    antonym_words.append(list(antonyms)[0])
                else:
                    # retain the original word if there is no antonym
                    antonym_words.append(w)
            target_phrase = ' '.join(antonym_words)
        else:
            target_phrase = ' '.join(target_words)
        input_vec = get_phrase_vector(target_phrase)
        category_similarities = []
        for category_vector in category_vector_list:
            sim = cosine_similarity([input_vec], [category_vector])[0][0]
            category_similarities.append(sim)
        # find the best matching category
        max_similarity = max(category_similarities)
        best_category_index = category_similarities.index(max_similarity)
        best_category = category_names[best_category_index]
        return best_category, category_similarities

    # used to store the similarity of each feature
    x1_similarities = []

    # city type analysis
    if 'city' in user_input:
        category, sims = match_category(user_input['city'], categories['City_type'], category_vectors['City_type'])
        if category:
            if category in ['Nature', 'Humanities']:
                analyzed_input['City_type'] = [category, 'Balanced']
            else:
                analyzed_input['City_type'] = [category]
            x1_similarities.append(max(sims))
        else:
            analyzed_input['City_type'] = ['Balanced']  # default
            x1_similarities.append(0)

    # temperature analysis
    if 'temp' in user_input:
        category, sims = match_category(user_input['temp'], categories['Climate'], category_vectors['Climate'])
        if category:
            analyzed_input['Climate'] = category
            x1_similarities.append(max(sims))
            if category == 'Cold':
                # select the 25th percentile temperature
                avg_temp = df['AvgTemp'].quantile(0.25)
            elif category == 'Warm':
                # select the 75th percentile temperature
                avg_temp = df['AvgTemp'].quantile(0.75)
            else:
                # select median temperature
                avg_temp = df['AvgTemp'].median()
            analyzed_input['AvgTemp'] = avg_temp
        else:
            analyzed_input['Climate'] = 'Temperate'  # default
            analyzed_input['AvgTemp'] = df['AvgTemp'].median()
            x1_similarities.append(0)

    # cost of living analysis
    if 'cost' in user_input:
        category, sims = match_category(user_input['cost'], categories['Living Cost Type'],
                                        category_vectors['Living Cost Type'])
        if category:
            analyzed_input['Living Cost Type'] = category
            x1_similarities.append(max(sims))
            if category == 'Cheap':
                cost_index = df['Cost of Living Index'].quantile(0.25)
            elif category == 'Expensive':
                cost_index = df['Cost of Living Index'].quantile(0.75)
            else:
                cost_index = df['Cost of Living Index'].median()
            analyzed_input['Cost of Living Index'] = cost_index
        else:
            analyzed_input['Living Cost Type'] = 'Medium'  # default
            analyzed_input['Cost of Living Index'] = df['Cost of Living Index'].median()
            x1_similarities.append(0)

    # transportation analysis
    if 'transportation' in user_input:
        category, sims = match_category(user_input['transportation'], categories['Transport'],
                                        category_vectors['Transport'])
        if category:
            analyzed_input['Transport'] = category
            x1_similarities.append(max(sims))
        else:
            analyzed_input['Transport'] = 'Medium'  # default
            x1_similarities.append(0)

    # air quality analysis
    if 'air quality' in user_input:
        category, sims = match_category(user_input['air quality'], categories['Air quality level'],
                                        category_vectors['Air quality level'])
        if category:
            analyzed_input['Air quality level'] = category
            x1_similarities.append(max(sims))
        else:
            analyzed_input['Air quality level'] = df['Air quality level'].mode()[0]  # default
            x1_similarities.append(0)

    # calculate x1 and normalize it to [0, 1]
    # treat negative similarity as 0
    x1_total = sum([max(0, sim) for sim in x1_similarities])
    # sum of the maximum possible similarity values
    max_x1 = len(x1_similarities)
    x1_norm = x1_total / max_x1 if max_x1 > 0 else 0

    return analyzed_input, x1_norm


def vectorize_input(analyzed_input):
    vector_dict = {}

    # city type vectorization
    city_types = analyzed_input.get('City_type', ['Balanced'])
    city_type_vectors = []
    for ct in city_types:
        vec = city_type_encoder.transform(pd.DataFrame({'City_type': [ct]}))
        city_type_vectors.append(vec)
    # take the maximum value of multiple vectors to form a multi-hot encoding
    city_type_vector = np.maximum.reduce(city_type_vectors)
    vector_dict['City_type'] = city_type_vector

    # cost of living index
    cost_index = analyzed_input.get('Cost of Living Index', df['Cost of Living Index'].median())
    vector_dict['Cost of Living Index'] = cost_index_scaler.transform(
        pd.DataFrame({'Cost of Living Index': [cost_index]}))

    # cost of Living Type vectorization
    cost_type = analyzed_input.get('Living Cost Type', 'Medium')
    vector_dict['Living Cost Type'] = cost_type_encoder.transform(pd.DataFrame({'Living Cost Type': [cost_type]}))

    # transportation vectorization
    transport = analyzed_input.get('Transport', 'Medium')
    vector_dict['Transport'] = transport_encoder.transform(pd.DataFrame({'Transport': [transport]}))

    # average temperature vectorization
    avg_temp = analyzed_input.get('AvgTemp', df['AvgTemp'].median())
    vector_dict['AvgTemp'] = temp_scaler.transform(pd.DataFrame({'AvgTemp': [avg_temp]}))

    # climate vectorization
    climate = analyzed_input.get('Climate', 'Temperate')
    vector_dict['Climate'] = climate_encoder.transform(pd.DataFrame({'Climate': [climate]}))

    # air quality vectorization
    air_quality = analyzed_input.get('Air quality level', df['Air quality level'].mode()[0])
    vector_dict['Air quality level'] = air_quality_encoder.transform(pd.DataFrame({'Air quality level': [air_quality]}))

    # merge all vectors
    vector = np.concatenate(list(vector_dict.values()), axis=1)
    return vector.flatten()


def vectorize_cities(df):
    city_type_vectors = city_type_encoder.transform(df[['City_type']])
    cost_index_normalized = cost_index_scaler.transform(df[['Cost of Living Index']])
    cost_type_vectors = cost_type_encoder.transform(df[['Living Cost Type']])
    transport_vectors = transport_encoder.transform(df[['Transport']])
    avg_temp_normalized = temp_scaler.transform(df[['AvgTemp']])
    climate_vectors = climate_encoder.transform(df[['Climate']])
    air_quality_vectors = air_quality_encoder.transform(df[['Air quality level']])

    vectors = np.concatenate([
        city_type_vectors,
        cost_index_normalized,
        cost_type_vectors,
        transport_vectors,
        avg_temp_normalized,
        climate_vectors,
        air_quality_vectors
    ], axis=1)

    return vectors


def get_similar_cities(user_vector, city_vectors, df, x1_norm, top_n=5, alpha=0.5):
    # calculate x2 and normalize it to [0, 1]
    similarities = cosine_similarity(user_vector.reshape(1, -1), city_vectors)
    x2 = similarities[0]
    # map cosine similarity from [-1, 1] to [0, 1]
    x2_norm = (x2 + 1) / 2

    # calculate final similarity
    final_similarities = alpha * x1_norm + (1 - alpha) * x2_norm

    similar_indices = final_similarities.argsort()[::-1][:top_n]
    similar_cities = df.iloc[similar_indices]
    similar_scores = final_similarities[similar_indices]

    return list(zip(similar_cities['City'], similar_scores))


def recommend_cities(user_input, df, alpha=0.5):
    analyzed_input, x1_norm = semantic_analysis(user_input)
    user_vector = vectorize_input(analyzed_input)
    city_vectors = vectorize_cities(df)
    similar_cities = get_similar_cities(user_vector, city_vectors, df, x1_norm, alpha=alpha)

    return similar_cities
