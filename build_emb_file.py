import os


def load_dic(dic_file):
    word_dict = {}
    item = 0
    with open(dic_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            word = line.strip()
            word_dict[word] = item
            item += 1
    print("Load embedding success! Num: %d" % len(word_dict))
    return word_dict


def build_id_file(word_dict, file_list):
    for file in file_list:
        print("produce %s " % file)
        id_file = file.split('.')[0] + '.id'
        with open(id_file, 'w') as f_o:
            with open(file, 'r') as f_i:
                for line_text in f_i:
                    line_o = []
                    line_list = line_text.strip().split(' ')
                    for word in line_list:
                        if word in word_dict:
                            line_o.append(word_dict[word])
                        else:
                            line_o.append(word_dict['<UNK>'])
                    line_o = ' '.join([str(ii) for ii in line_o]) + '\n'
                    f_o.write(line_o)
        print("build file %s success!" % str(id_file))
    print("build id file finished!")


if __name__ == '__main__':
    dic_file = "D:/Coding/PYTHON/seqGAN2/data/movie/tweets_Vocab.vocab"
    word_dict = load_dic(dic_file)
    build_id_file(word_dict, ['D:/Coding/PYTHON/seqGAN2/legitimate_tweets.txt'])


