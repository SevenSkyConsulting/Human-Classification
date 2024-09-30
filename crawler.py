import json
import requests
from collections import Counter
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.corpus import stopwords

UNRELATED_WORDS = ['url', 'logo', 'image', 'id', 'context', 'domain', 'image', 'height', 'weight']
RELATED_WORDS = ['title', 'description', 'price', 'category', 'type', 'brand', 'keywords', 'keywords', 'author']
STOP_WORDS = set(stopwords.words('english'))


def check_unrelated_words(word):
    for stop_word in UNRELATED_WORDS:
        if (stop_word in word) or (word in stop_word):
            return False
    return True


def check_related_words(word):
    for stop_word in RELATED_WORDS:
        if (stop_word in word) or (word in stop_word):
            return True
    return False


def ignore_http(text):
    if isinstance(text, str):
        if text.startswith('http'):
            return False
    return True


def modify_sentences(text: str):
    if len(text.split()) > 5:
        words = word_tokenize(text)
        tokenised_words = [word.lower() for word in words]
        keywords = [word for word in tokenised_words if word.isalpha() and word not in STOP_WORDS]
        listed_keywords = Counter(keywords).most_common(5)
        return [keyword[0] for keyword in listed_keywords]
    else:
        return text


def modify_value(key, value, outs: dict):
    if not check_unrelated_words(key):
        return outs

    if isinstance(value, str):
        if check_unrelated_words(key) and ignore_http(value):
            outs[key] = modify_sentences(value)

    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                for inner_key, inner_value in item.items():
                    if check_unrelated_words(inner_key) and ignore_http(inner_value):
                        outs[f'{key}-{inner_key}'] = modify_sentences(inner_value) if isinstance(inner_value, str) else inner_value

    elif isinstance(value, dict):
        for inner_key, inner_value in value.items():
            if check_unrelated_words(inner_key) and ignore_http(inner_value):
                outs[f'{key}-{inner_key}'] = modify_sentences(inner_value) if isinstance(inner_value, str) else inner_value

    else:
        if check_unrelated_words(key):
            outs[key] = value
    return outs


def find_keywords(soup):
    metas = soup.find_all('meta')
    outs = {}
    for meta in metas:
        try:
            if meta.get('name'):
                if 'twitter' in meta['name']:
                    outs = modify_value(meta['name'], meta['content'], outs)
            elif meta.get('property'):
                if 'twitter' in meta['property']:
                    outs = modify_value(meta['property'], meta['content'], outs)
            else:
                print('Not Related!')
        except Exception as e:
            raise Exception(e)

    lds = soup.find_all("script", {"type": "application/ld+json"})
    for idx, ld in enumerate(lds):
        temp_ld = json.loads(ld.get_text())
        for data_key, data_value in temp_ld.items():
            outs = modify_value(data_key, data_value, outs)

    print(outs)
    return outs


def purify_data(url):
    # Send a GET request to the website
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code != 200:
        return {"error": f"Failed to retrieve content, status code: {response.status_code}"}

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    titles_h1s = {
        'title': modify_sentences(soup.title.string) if soup.title else "No title found",
        'h1_tags': [modify_sentences(h1.get_text().strip()) for h1 in soup.find_all('h1')]
    }

    outs = find_keywords(soup=soup) or 'feature not found'

    return {**titles_h1s, **outs}
    