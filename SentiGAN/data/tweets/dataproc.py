import tweepy
import pandas as pd

def auth_api():
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler("6JBDj2M0D8yIvOG06fuFCGvMK", 
        "iEniBK2qIY4tUgRuDgdXYhAO5mZlkrpuknjpcUyK0gYGaXih6p")
    auth.set_access_token("760083289-jHl79xR2zNooAftuweWLfhMlHeE3iov3LnPaLWkB", 
        "Qg58KEbk9BzFLQovTcRQBnKfrbO9QJcM3IduwPsJsqVVZ")

    api = tweepy.API(auth)

    try:
        api.verify_credentials()
        print("Authentication OK")
    except:
        print("Error during authentication")
        
    return auth, api
        
def get_tweets(topic, date, tweet_num):
    # Create API object
    auth, api = auth_api()
    # Create API object
    api = tweepy.API(auth, wait_on_rate_limit=True,
    wait_on_rate_limit_notify=True)
    file_name = topic + '.csv'
    hash_tag = '#' + topic + " -filter:retweets"
    tweets_list = []

    for tweet in tweepy.Cursor(api.search, q=hash_tag, count=20,
                               lang="en",
                               since=date).items(tweet_num):
#         print (tweet.created_at, tweet.text)
        tweets_list.append(tweet.text)
    df = pd.DataFrame(dict([('text', tweets_list)]))
    df.to_csv(file_name, index=False)


def buid_dict_file(file_list, dict_file, max_num=5):
    word_dict = {}
    for file in file_list:
        print("Now produce %s" % file)
        with open(file, 'r') as f:
            for ll in f:
                words = ll.strip().split(' ')
                for word in words:
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
            # f.write("%s  %d\n" % (str(ii[0]), ii[1]))
            f.write(f"{str(ii[0])}\n")
    print("build dict finished!")
    return

def load_dic(dic_file):
    word_dict = {}
    item = 0
    with open(dic_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            word = line.strip()
            word_dict[word] = item
            item += 1
    print("Load embedding success! Num: {}".format(len(word_dict)))
    return word_dict

def build_id_file(word_dict, file_list):
    for file in file_list:
        print("produce {} ".format(file))
        id_file = '.' + file.split('.')[1] + '.id'
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
        print("build file {} success!".format(id_file))
    print("build id file finished!")