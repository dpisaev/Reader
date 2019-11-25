from bs4 import BeautifulSoup
import requests
import string
import langdetect
import pymorphy2
import nltk
from nltk.corpus import wordnet as wn
from nltk import word_tokenize, FreqDist
import codecs
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from collections import Counter
from gensim.models import KeyedVectors
from gensim.test.utils import datapath
import numpy as np
import re

nltk.download('wordnet')

# количество вытаскиваемых слов
K = 5


def get_stop_words(fname):
    with codecs.open("reader/"+fname, "r", "utf-8") as file:
        return [line.strip() for line in file]


def clean_html(soup):
    bad_html = ['a', 'script', 'meta', 'img',  'style']
    for bad in bad_html:
        for script in soup.find_all(bad, src=False):
            script.decompose()

    texts = ''

    for item in soup.find_all():
        if item.string != None:
            texts +=  ' ' + item.string
    return texts

def clean_text(texts):
    morph = pymorphy2.MorphAnalyzer()
    lang = langdetect.detect(texts)
    texts = texts.split()
    ru_stopwords = set(get_stop_words("Ru.txt"))
    en_stopwords = set(get_stop_words("En.txt"))
    stop_words = ru_stopwords | en_stopwords
    texts = [i.strip(string.punctuation) for i in texts]
    return_words = []
    for word in texts:

        if word.lower() != '' and word.lower() not in stop_words:
            if lang == 'ru':
                return_words.append(morph.parse(word)[0].normal_form)
            elif lang == 'en':
                if wn.morphy(word) is None:
                    return_words.append(word)
                elif word != '':
                    return_words.append(wn.morphy(word))
            else:
                return_words.append(word)
    return return_words

def get_word2vec_result(words, model, top_n=10):
    words = list(filter(lambda x: x in model.vocab, words))
    words = list(set(words))
    print(words)
    common = model.most_similar_cosmul(positive=words)
    print(common)
    vectors = np.array([model.get_vector(x[0]) for x in common])
    mean = sum(vectors) / len(vectors)
    distances = model.distances(mean, words)
    result = list(zip(distances, words))
    result.sort(reverse=True)
    return result[:top_n]


def parse(url):
    # model = KeyedVectors.load_word2vec_format(datapath('/home/yndx36/PycharmProjects/reader/reader/glove.6B.100.w2v'), binary=False)
    resp = requests.get(url)

    soup = BeautifulSoup(resp.text, 'html.parser')
    title = soup.title.string
    clear_html = clean_html(soup)
    real_text = clean_text(clear_html)
    count = FreqDist(real_text)
    k = count.most_common(K)
    # ml_k = get_word2vec_result(real_text, model)

    return title, [x[0] for x in k]
