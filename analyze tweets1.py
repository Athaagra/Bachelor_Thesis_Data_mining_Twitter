#!/usr/bin/env python
# -*- coding: utf-8 -*-

import operator
import json
from nltk import bigrams
from collections import Counter
import re
from collections import defaultdict
from nltk.corpus import stopwords
import string
import vincent
import pandas
import arrow

start = arrow.now()

punctuation = list(string.punctuation)
stop = stopwords.words('french') + stopwords.words('german') + stopwords.words('italian') + stopwords.words('english') + punctuation + ["l'a", "amp", "ter", "les", "c'est", 'de', 'en', 'el', 'https', 'rt', 'via', 'RT']

print stop
emoticons_str = r"""
    (?:
        [:=;]  # Eyes
        [oO\-]?  # Nose (optional)
        [D\)\]\(\]/\\OpP]  # Mouth
    )"""

regex_str = [
    emoticons_str,
    r'<[^>]+>',  # HTML tags
    r'(?:@[\w_]+)',  # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',

    r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])",  # words with - and '
    r'(?:[\w_]+)',  # other words
    r'(?:\S)'  # anything else
]

tokens_re = re.compile(r'('+'|'.join(regex_str)+')',
                       re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^'+emoticons_str+'$',
                         re.VERBOSE | re.IGNORECASE)


def tokenize(s):
    return tokens_re.findall(s)


def preprocess(s, lowercase=True):
    tokens = tokenize(s)
    if lowercase:
        tokens = [token if emoticon_re.search(token)
                  else token.lower() for token in tokens]
    return tokens

fname = 'news.json'

pr = 0
err = 0
dates_news = []
dates_tech = []
with open(fname, 'r') as f:
    count_stop = Counter()
    count_langs = Counter()
    count_hashtags = Counter()
    count_https = Counter()
    count_mentions = Counter()
    count_bigram = Counter()
    geo_data = {
        "type": "FeatureCollection",
        "features": []
    }
    for line in f:
        tweet = json.loads(line)
        if tweet['coordinates']:
            geo_json_feature = {
                "type": "Feature",
                "geometry": tweet['coordinates'],
                "properties": {
                    "text": tweet['text'],
                    "created_at": tweet['created_at']
                }
            }
            geo_data['features'].append(geo_json_feature)
        try:
            pr += 1
            print str(tweet['created_at']) + " ok: " + str(pr)
            
            terms_stop = [term for term in preprocess(tweet['text'])
                          if term not in stop and
                          not term.startswith(('#', '@', 'http')) and
                          len(term) > 2]
            langs_only = preprocess(tweet['lang'])
            hashtags_only = [term for term in preprocess(tweet['text'])
                             if term.startswith(('#')) and
                             len(term) > 2]
            https_only = [term for term in preprocess(tweet['text'])
                             if term.startswith(('https:')) and
                             len(term) > 2]
            mentions_only = [term for term in preprocess(tweet['text'])
                             if term.startswith(('@'))]
            terms_bigram = bigrams(terms_stop)
            terms = [term for term in preprocess(tweet['text'])
                     if term not in stop and len(term) != 1]
            # track when the hashtag is mentioned
            if 'news' in terms:
                dates_isis.append(tweet['created_at'])
            if 'tech' in terms:
                dates_peace.append(tweet['created_at'])
            
        except:
            err += 1
        count_stop.update(terms_stop)
        count_langs.update(langs_only)
        count_hashtags.update(hashtags_only)
        count_https.update(https_only)
        count_mentions.update(mentions_only)
        count_bigram.update(terms_bigram)
        # if pr == 1000:
        #     break

nElements = 50

print "----------------------------"

print "count_bigram"

word_freq = count_bigram.most_common(nElements)
labels, freq = zip(*word_freq)
data = {'data': freq, 'x': labels}
bar = vincent.Bar(data, iter_idx='x', height=500, width=900)
bar.x_axis_properties(label_angle=-45, label_align="right")
bar.legend(title="Most frequent bigram")
bar.to_json('WEB/bigram.json')


print "----------------------------"
print "Active: " + str(pr)
print "error: " + str(err)

print "generating geo data"
with open('WEB/geo_data.json', 'w') as fout:
    fout.write(json.dumps(geo_data, indent=4))

print "generating most common terms json"

word_freq = count_stop.most_common(nElements)
labels, freq = zip(*word_freq)
data = {'data': freq, 'x': labels}
bar = vincent.Bar(data, iter_idx='x', height=500, width=900)
bar.x_axis_properties(label_angle=-45, label_align="right")
bar.legend(title="Most frequent terms")
bar.to_json('WEB/freq_terms.json')

print "generating most common Langs"

word_freq = count_langs.most_common(nElements)
labels, freq = zip(*word_freq)
data = {'data': freq, 'x': labels}
bar = vincent.Bar(data, iter_idx='x', height=500, width=900)
bar.x_axis_properties(label_angle=-45, label_align="right")
bar.legend(title="Most frequent langs")
bar.to_json('WEB/freq_langs.json')

print "generating most common https json"

word_freq = count_https.most_common(nElements)
labels, freq = zip(*word_freq)
data = {'data': freq, 'x': labels}
bar = vincent.Bar(data, iter_idx='x', height=500, width=900)
bar.x_axis_properties(label_angle=-45, label_align="right")
bar.legend(title="Most frequent https")
bar.to_json('WEB/freq_https.json')

print "generating most common hashtags json"

word_freq = count_hashtags.most_common(nElements)
labels, freq = zip(*word_freq)
data = {'data': freq, 'x': labels}
bar = vincent.Bar(data, iter_idx='x', height=500, width=900)
bar.x_axis_properties(label_angle=-45, label_align="right")
bar.legend(title="Most frequent hashtags")
bar.to_json('WEB/freq_hashtags.json')

print "generating most common mentions json"

word_freq = count_mentions.most_common(nElements)
labels, freq = zip(*word_freq)
data = {'data': freq, 'x': labels}
bar = vincent.Bar(data, iter_idx='x', height=500, width=900)
bar.x_axis_properties(label_angle=-45, label_align="right")
bar.legend(title="Most frequent mentions")
bar.to_json('WEB/freq_mentions.json')

print "time charting now"

# 1 time charting
print '1'
ones = [1]*len(dates_news)
twos = [1]*len(dates_tech)
# 2 the index of the series
print '2'
idxn = pandas.DatetimeIndex(dates_news)
idxp = pandas.DatetimeIndex(dates_tech)
# 3 the actual series (at series of 1s for the moment)
print '3'
news = pandas.Series(ones, index=idxn)
tech = pandas.Series(twos, index=idxp)
# 4 Resampling / bucketing
print '4'
per_minute_i = news.resample('1Min', how='sum').fillna(0)
per_minute_p = tech.resample('1Min', how='sum').fillna(0)


# 5 all the data together
print '5'
match_data = dict(news=per_minute_i, tech=per_minute_p)
# 6 we need a DataFrame, to accommodate multiple series
print '6'
all_matches = pandas.DataFrame(data=match_data,
                               index=per_minute_i.index)
# 7 Resampling as above
print '7'
all_matches = all_matches.resample('1Min', how='sum').fillna(0)

# 8 and now the plotting
print '8'
time_chart = vincent.Line(all_matches[['news', 'tech']])
time_chart.axis_titles(x='Time', y='Freq')
time_chart.legend(title='Matches')
time_chart.to_json('WEB/time_chart.json')

print "started at: " + str(start)
print ''

stop = arrow.now()
print "stopped at: " + str(stop)

print ''

print "total time: " + str(stop - start)
