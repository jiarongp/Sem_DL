import json
import nltk.data
import nltk

data = json.load(open("data.json"))

print("Load json file length: %d" % len(data))

# print(data[0])


"""
"rating": 
"title": 
"movie": 
"review": 
"link": 
"user":
"""


def produce_document(_doc):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    _sens = sent_detector.tokenize(_doc)
    return _sens


def produce_line(_line):
    _line = _line.strip()
    _line = _line.lower()
    _token = nltk.word_tokenize(_line)
    return _token


sentences_review_list = []
sentences_title_list = []

for i, item in enumerate(data):
    review = item['review']

    sentences = produce_document(item['review'])
    for sen in sentences:
        eachLine = sen.lower()
        tokens = nltk.word_tokenize(eachLine)
        l = len(tokens)
        if l <= 15 and l > 1:
            sentences_review_list.append(tokens)
            # print(tokens)
            # input()

    sentences = produce_document(item['title'])
    for sen in sentences:
        eachLine = sen.lower()
        tokens = nltk.word_tokenize(eachLine)
        l = len(tokens)
        if l <= 15 and l > 1:
            sentences_title_list.append(tokens)

    if i % 10000 == 0:
        print(i)


print("collect review sentences from review, we have %d " % len(sentences_review_list))
print("collect title sentences from review, we have %d " % len(sentences_title_list))
input("pause!")

with open("imdb_sentences.txt", 'w') as f:
    for sen in sentences_title_list:
        f.write(' '.join([str(i) for i in sen])+'\n')
    for sen in sentences_review_list:
        f.write(' '.join([str(i) for i in sen])+'\n')
print("finished! write %d num sen" % (len(sentences_review_list) + len(sentences_title_list)))
