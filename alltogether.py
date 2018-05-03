
import sys
import json
from collections import Counter
import re
from nltk.corpus import stopwords
import string
import vincent
import pandas
import time
 
punctuation = list(string.punctuation)
stop = stopwords.words('english') + punctuation + ['rt', 'via']
 
emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""
 
regex_str = [
    emoticons_str,
    r'<[^>]+>', # HTML tags
    r'(?:@[\w_]+)', # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs
 
    r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
    r'(?:[\w_]+)', # other words
    r'(?:\S)' # anything else
]
    
tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE)
 
def tokenize(s):
    return tokens_re.findall(s)
 
def preprocess(s, lowercase=False):
    tokens = tokenize(s)
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens


if __name__ == '__main__':
    fname = 'news.json'

    with open(fname, 'r') as f:
        #'#news''science'
        dates_tech = []
        dates_news = []
        dates_science = []
        # f is the file pointer to the JSON data set
        for line in f:
            tweet = json.loads(line)
            # let's focus on hashtags only at the moment
            terms_hash = [term for term in preprocess(tweet['text']) if term.startswith('#')]
            # track when the hashtag is mentioned
            if '#tech' in terms_hash:
                dates_tech.append(tweet['created_at'])
            # a list of "1" to count the hashtags
            ones = [1]*len(dates_tech)
            # the index of the series
            idx = pandas.DatetimeIndex(dates_tech)
            # the actual series (at series of 1s for the moment)
            tech = pandas.Series(ones, index=idx)
            per_minute_i = tech.resample('1min', how='sum').fillna(0)

            if '#news' in terms_hash:
                dates_news.append(tweet['created_at'])
            # a list of "1" to count the hashtags
            ones = [1]*len(dates_news)
            # the index of the series
            idx = pandas.DatetimeIndex(dates_news)
            # the actual series (at series of 1s for the moment)
            news = pandas.Series(ones, index=idx)
            per_minute_s = news.resample('1min', how='sum').fillna(0)

            if '#science' in terms_hash:
                dates_science.append(tweet['created_at'])
            # a list of "1" to count the hashtags
            ones = [1]*len(dates_science)
            # the index of the series
            idx = pandas.DatetimeIndex(dates_science)
            # the actual series (at series of 1s for the moment)
            science = pandas.Series(ones, index=idx)
            per_minute_e = science.resample('1min', how='sum').fillna(0)
            
            # all the data together
            match_data = dict(tech=per_minute_i, news=per_minute_s, science=per_minute_e)
            # we need a DataFrame, to accommodate multiple series
            all_matches = pandas.DataFrame(data=match_data,
                                           index=per_minute_i.index)
             
            # Resampling / bucketing
            all_matches = all_matches.resample('1Min', how='sum').fillna(0)
            time_chart = vincent.Line(all_matches[['tech', 'news', 'science']])
            time_chart.axis_titles(x='Time', y='Freq')
            time_chart.legend(title='Reports')
            time_chart.to_json('WEB/time_chart.json')
