import functools
import string
import re
from nltk.corpus import words, stopwords
from nltk.stem import WordNetLemmatizer
import pandas as pd


def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)


def filter_printable(text: str) -> str:
    return ''.join(list(filter(lambda ch: ch in string.printable, text)))


def remove_links(text: str) -> str:
    return re.sub(r'https?://\S+|www\.\S+', '', text)


def remove_punctuations(text: str) -> str:
    return ''.join(list(filter(lambda ch: ch not in string.punctuation, text)))


def to_lowercase(text: str) -> str:
    return text.lower()


english_words = set(words.words())


def remove_nonwords(text: str) -> str:
    return ' '.join(list(filter(lambda word: word in english_words, text.split(' '))))


def lemmatize(text: str) -> str:
    lemmatizer = WordNetLemmatizer()
    ws = text.split(' ')
    for tag in ['a', 'r', 'n', 'v']:
        ws = list(map(lambda w: lemmatizer.lemmatize(w, tag), ws))
    return ' '.join(ws)


english_stopwords = set(stopwords.words('english'))


def remove_stop_words(text: str) -> str:
    return ' '.join(list(filter(lambda w: w not in english_stopwords, text.split(' '))))


def drop_unused_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=['id', 'location'], axis=1)


def process_text(df: pd.DataFrame) -> pd.DataFrame:
    transform_text = compose(
        remove_stop_words,
        lemmatize,
        remove_nonwords,
        to_lowercase,
        remove_punctuations,
        remove_links,
        filter_printable
    )
    df.text = df.text.apply(transform_text)
    return df


def clean_feature_keyword(df: pd.DataFrame) -> pd.DataFrame:
    # Blank line (nan) means there is not keyword
    df.keyword = df.keyword.fillna('none')
    # Rreplacing space character with '_'
    df.keyword = df.keyword.astype('str').apply(lambda x: x.replace('%20', '_'))
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns={
        'keyword': 'KEYWORD',
        'text': 'TEXT',
        'target': 'TARGET'
    })


transform = compose(
    rename_columns,
    clean_feature_keyword,
    process_text,
    drop_unused_columns
)
