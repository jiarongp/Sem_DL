import os
from nltk.corpus import words as eng

def buid_dict_file(file_list, dict_file, max_num):
    word_dict = {}
    for file in file_list:
        print("Now produce %s" % file)
        with open(file, 'r') as f:
            for ll in f:
                ll= ll.lower()
                words = ll.strip().split(' ')
                for word in words:
                    if word in eng.words(): #returns the lower case words.
                        if word in word_dict:
                            word_dict[word] += 1
                        else:
                            word_dict[word] = 1
    print("Get word_dict success: {} words".format(len(word_dict)))

    word_dict_list = sorted(word_dict.items(), key=lambda d: d[1], reverse=True)

    with open(dict_file, 'w') as f:
        f.write("<PAD>\n")
        f.write("<UNK>\n")
        f.write("<EOS>\n")
        f.write("<GO>\n")
        _num = 0
        for ii in word_dict_list:
            _num = int(ii[1])
            if _num < max_num:
                break
            # print(str(ii[0]))
            f.write("{}\n". format(str(ii[0])))
    print("build dict finished!")
    return

if __name__ == '__main__':
    file_list = ['D:/Coding/PYTHON/seqGAN2/legitimate_tweets.txt']
    dict_file= "tweets_Vocab.vocab"
    buid_dict_file(file_list, dict_file, max_num=5)



