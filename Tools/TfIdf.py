#!/usr/bin/env python
# encoding: utf-8

"""
File: tfidfDE.py
Original author: Yasser Ebrahim
Release date: Oct 2012
Modified by: Julius Tens
E-Mail: mail@julius-tens.de
Web: https://github.com/juliuste
Date: 31.03.2016
Generate the TF-IDF ratings for a collection of documents.
"""

import math
import os
import sys

# error if python 2 is used
assert sys.version_info >= (3, 0)

scriptDir = os.path.dirname(__file__)


# 2018-05-01: Dac: turn off lemma and stopwords
# lemmaHandle = open(os.path.join(scriptDir, 'lemmata.csv'), 'r')
# stopwordHandle = open(os.path.join(scriptDir, 'stopwords.txt'), 'r')


# def importLemmata(handle):
#     lemmata = {}
#     # import lemmata from file
#     for line in handle:
#         if len(line) == 0 or line[0] == '#':
#             continue
#         words = line.split()
#         if len(words) != 2 or words[0] == words[1]:
#             continue
#         lemmata[words[0]] = words[1]
#     return lemmata
#
#
# def importStopwords(handle):
#     # import stopwords from file
#     stopwords = []
#     for line in handle:
#         if len(line.split()) == 0 or line[0] == '#':
#             continue
#         stopwords.append(line.split()[0])
#     return stopwords
#
#
# def lemmatize(text, lemmata):
#     # lemmatize text
#     for i in range(0, len(text)):
#         if text[i] in lemmata:
#             text[i] = lemmata[text[i]]
#
#     # don't return any single letters
#     text = [t for t in text if len(t) > 1]
#     return text
#
#
# def removeStopwords(text, stopwords):
#     # remove stopwords
#     content = [w for w in text if w not in stopwords]
#     return content


def tokenize(text):
    # remove punctuation, tokenize
    # 2018-05-01: Dac: keep alpha and '_'; lower case all word
    return "".join(c.lower() if (c.isalpha() or c == '_') else ' ' for c in text).split()


def isNoun(word):
    # pseudo check if given word is a noun (if it has a capital letter, so sometimes this method returns some garbage)
    return len(word) >= 1 and word[0].isupper()


def analyze(documents, resultsPerDocument=-1, preferNouns=False, ranking=True, files=False, verbose=False):
    """
    TF IFF
    :param documents:
    :param resultsPerDocument:
    :param preferNouns:
    :param ranking:
    :param files:
    :param verbose:
    :return: results = [{paper_id:, keywords:[[keyword, weight],]}]
    """
    if verbose:
        print('Initializing..')

    # 2018-05-01: Dac: turn off lemma and stopword
    # # load language data
    # lemmata = importLemmata(lemmaHandle)
    # stopwords = importStopwords(stopwordHandle)

    localWordFreqs = {}  # list words of a doc
    globalWordFreq = {}  # number of docs contain that word

    if verbose:
        print('Working through documents.. ')

    progress = 0

    for doc in documents:
        # calculate progress
        progress += 1
        if progress % math.ceil(float(len(documents)) / float(20)) == 0:
            if verbose:
                print(str(100 * progress / len(documents)) + '%')

        # local term frequency map
        localWordFreq = {}
        localWords = doc
        if files:
            # 2018-05-01: Dac: encoding UTF-8
            localWords = open(doc, 'r', encoding='UTF-8').read()
        localWords = tokenize(localWords)

        # 2018-05-01: Dac: turn off lemma and stopword
        # localWords = removeStopwords(localWords, stopwords)
        # localWords = lemmatize(localWords, lemmata)

        # increment local count
        for word in localWords:
            if word in localWordFreq:
                localWordFreq[word] += 1
            else:
                localWordFreq[word] = 1

        # increment global frequency (number of documents that contain this word)
        for (word, freq) in localWordFreq.items():
            if word in globalWordFreq:
                globalWordFreq[word] += 1
            else:
                globalWordFreq[word] = 1

        localWordFreqs[doc] = localWordFreq

    if verbose:
        print('Calculating.. ')

    results = []
    for doc in documents:
        # if files:
        #     # 2018-05-01: Dac: encoding UFT-8
        #     writer = open(doc + '_tfidf', 'w', encoding='UTF-8')

        # 2018-05-01: Dac: config result = {paper_id:, keyword:}
        result = {'paper_id': os.path.basename(doc), 'keywords': []}

        # 2018-05-01: Dac: fix code and comment out old code
        # max_freq = 0
        # for (term, freq) in localWordFreqs[doc].items():
        #     if freq > max_freq:
        #         max_freq = freq
        for (term, freq) in localWordFreqs[doc].items():
            # 2018-05-03: Dac: tf = frequency / max freq
            # tf = float(freq) / float(max_freq)
            # 2018-05-03: Dac: tf = frequency / total number of terms in a document
            tf = float(freq) / float(len(localWordFreqs[doc]))
            # idf = total
            idf = math.log(float(len(documents)) / float(1 + globalWordFreq[term]))
            tfidf = tf * idf
            result['keywords'].append([term, str(tfidf)])
        # iterate over terms in f, calculate their tf-idf, put in new list
        # for (term, freq) in localWordFreqs[doc].items():
        #     nounModifier = 1 + int(preferNouns) * int(isNoun(term)) * 0.3
        #     tf = bool(float(freq)) * (1 + math.log(float(freq)))
        #     idf = math.log(float(1 + len(documents)) / float(1 + globalWordFreq[term]))
        #     tfidf = float(tf) * float(idf) * nounModifier
        #     result['keywords'].append([term, str(tfidf)])

        # sort result on tfidf and write them in descending order
        result['keywords'] = sorted(result['keywords'], key=lambda x: (x[1], x[0]), reverse=True)
        # if files:
        #     print()
        # for (tfidf, term) in result[:resultsPerDocument]:
        #     if ranking:
        #         writer.write(term + '\t' + str(tfidf) + '\n')
        #     else:
        #         writer.write(term + '\n')

        if not ranking:
            res = []
            for re in result['keywords']:
                res.append(re[1])
            results.append(res[:resultsPerDocument])
        else:
            result['keywords'] = result['keywords'][:resultsPerDocument]
            results.append(result)

    if verbose:
        print('Success, with ' + str(len(documents)) + ' documents.')

    return results
