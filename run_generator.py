import tensorflow as tf
from generator import Generator
from tensorflow.python.util import deprecation
deprecation._PRINT_DEPRECATION_WARNINGS = False

#########################################################################################
#  Generator  Hyper-parameters
######################################################################################
EMB_DIM = 200 # embedding dimension
HIDDEN_DIM = 200 # hidden state dimension of lstm cell
MAX_SEQ_LENGTH = 25  # max sequence length
BATCH_SIZE = 64

dataset_path = "./data/tweets/"
emb_dict_file = dataset_path + "tweets.vocab"

def generate_samples(sess, trainable_model, generated_num, output_file, vocab_list, if_log=False, epoch=0):
    # Generate Samples
    generated_samples = []
    for _ in range(int(generated_num)):
        generated_samples.extend(trainable_model.generate(sess))

    with open(output_file, 'w', encoding='utf-8') as fout:
        for poem in generated_samples:
            poem = list(poem)
            if 2 in poem:
                poem = poem[:poem.index(2)]
            buffer = ' '.join([str(x) for x in poem]) + '\n'
            fout.write(buffer)

    if if_log:
        # open for writing, appending to the end of the file if it exists
        mode = 'a'
        if epoch == 0:
            # open for writing, truncating the file first
            mode = 'w'

        with open(output_file, mode,encoding='utf-8') as fout:
            # id_str = 'epoch:%d ' % epoch
            for poem in generated_samples:
                poem = list(poem)
                if 2 in poem:
                    poem = poem[:poem.index(2)]
                buffer = ' '.join([vocab_list[x] for x in poem]) + '\n'
                fout.write(buffer)

def load_emb_data(emb_dict_file):
    word_dict = {}
    word_list = []
    item = 0
    with open(emb_dict_file, 'r',encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            # remove /n
            word = line.strip()
            word_dict[word] = item
            item += 1
            word_list.append(word)
    length = len(word_dict)
    print("Load embedding success! Num: %d" % length)
    return word_dict, length, word_list

def main():
    # load embedding info
    vocab_dict, vocab_size, vocab_list = load_emb_data(emb_dict_file)

    # build model
    # num_emb, vocab_dict, batch_size, emb_dim, num_units, sequence_length
    generator = Generator(vocab_size, vocab_dict, BATCH_SIZE, EMB_DIM, HIDDEN_DIM, MAX_SEQ_LENGTH)
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    sess = tf.Session(config=config)
    sess.run(tf.global_variables_initializer())

    generator.load_model(sess,'./save/ckpt/model.ckpt')
    generate_samples(sess, generator, 1, './result.txt', vocab_list, if_log=True, epoch=0)
    
if __name__=='__main__':
    main()