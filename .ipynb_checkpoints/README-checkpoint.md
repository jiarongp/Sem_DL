```
.
├── data (storing data from tweets)
├── dataloader.py
├── discriminator.py
├── generator.py
├── README (storing README.md material)
├── README.md
├── references (literatures)
├── save (log, saved models and generated texts)
└── train.py
```


## Data Preparation

- Extract a dataset in .txt file, each tweet has one line
- Generate a .vocab file from dataset in a frequency descending sequence, by counting the appearances of each word. The first four words are ``<PAD>, <UNK>, <EOS>, <GO>``
- Replace each word in the dataset using the corresponding number token from .vocab file.

## Model

<p align="center">
<img width="80%" src="./README/encdec.jpg" />
<br>
Figure 1. <b>Encoder-decoder architecture</b> – An encoder converts a source sentence into a "meaning" vector which is passed through a <i>decoder</i> to produce a translation.
</p>


<p align="center">
<img width="48%" src="./README/seq2seq.jpg" />
<br>
Figure 2. <b>Seq2Seq Model</b> – example of a deep recurrent
architecture proposed by for translating a source sentence "I am a student" into a target sentence "Je suis étudiant".
</p>

## Training

For training, we will feed the system with the following tensors, which are in time-major format and contain word indices:

- ``encoder_inputs [max_encoder_time, batch_size]``: source input words.
- ``decoder_inputs [max_decoder_time, batch_size]``: target input words.
- ``decoder_outputs [max_decoder_time, batch_size]``: target output words, these are decoder_inputs shifted to the left by one time step with an end-of-sentence tag appended on the right.

### Embedding

Given the categorical nature of words, the model must first look up the source and target embeddings to retrieve the corresponding word representations. 
> The words in sentence would be translated into combination of vectors of corresponding words with lookup function


> For this embedding layer to work, a vocabulary is first chosen for each language. Usually, a vocabulary size V is selected, and only the most frequent V words are treated as unique. All other words are converted to an "unknown" token and all get the same embedding. The embedding weights, one set per language, are usually learned during training.

> Similarly, we can build embedding_decoder and decoder_emb_inp. Note that one can choose to initialize embedding weights with pretrained word representations such as word2vec or Glove vectors. In general, given a large amount of training data we can learn these embeddings from scratch.

Once retrieved, the word embeddings are then fed as input into the main network, which consists of two multi-layer RNNs – an encoder for the source language and a decoder for the target language. These two RNNs, in principle, can share the same weights; however, in practice, we often use two different RNN parameters (such models do a better job when fitting large training datasets). The encoder RNN uses zero vectors as its starting states and is built as follows:

``` python
# Build RNN cell
encoder_cell = tf.nn.rnn_cell.BasicLSTMCell(num_units)

# Run Dynamic RNN
#   encoder_outputs: [max_time, batch_size, num_units]
#   encoder_state: [batch_size, num_units]
encoder_outputs, encoder_state = tf.nn.dynamic_rnn(
    encoder_cell, encoder_emb_inp,
    sequence_length=source_sequence_length, time_major=True)
```

Note that sentences have different lengths to avoid wasting computation, we tell
*dynamic_rnn* the exact source sentence lengths through
*source_sequence_length*. Since our input is time major, we set
*time_major=True*. Here, we build only a single layer LSTM, *encoder_cell*. We
will describe how to build multi-layer LSTMs, add dropout, and use attention in
a later section.

### Decoder

The *decoder* also needs to have access to the source information, and one
simple way to achieve that is to initialize it with the last hidden state of the
encoder, *encoder_state*. In Figure 2, we pass the hidden state at the source
word "student" to the decoder side.

``` python
# Build RNN cell
decoder_cell = tf.nn.rnn_cell.BasicLSTMCell(num_units)
```

``` python
# Helper
helper = tf.contrib.seq2seq.TrainingHelper(
    decoder_emb_inp, decoder_lengths, time_major=True)
# Decoder
decoder = tf.contrib.seq2seq.BasicDecoder(
    decoder_cell, helper, encoder_state,
    output_layer=projection_layer)
# Dynamic decoding
outputs, _ = tf.contrib.seq2seq.dynamic_decode(decoder, ...)
logits = outputs.rnn_output
```

Here, the core part of this code is the *BasicDecoder* object, *decoder*, which
receives *decoder_cell* (similar to encoder_cell), a *helper*, and the previous
*encoder_state* as inputs. By separating out decoders and helpers, we can reuse
different codebases, e.g., *TrainingHelper* can be substituted with
*GreedyEmbeddingHelper* to do greedy decoding. See more
in
[helper.py](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/contrib/seq2seq/python/ops/helper.py).

Lastly, we haven't mentioned *projection_layer* which is a dense matrix to turn
the top hidden states to logit vectors of dimension V. We illustrate this
process at the top of Figure 2.

``` python
projection_layer = layers_core.Dense(
    tgt_vocab_size, use_bias=False)
```

### Loss

Given the *logits* above, we are now ready to compute our training loss:

``` python
crossent = tf.nn.sparse_softmax_cross_entropy_with_logits(
    labels=decoder_outputs, logits=logits)
train_loss = (tf.reduce_sum(crossent * target_weights) /
    batch_size)
```

Here, *target_weights* is a zero-one matrix of the same size as
*decoder_outputs*. It masks padding positions outside of the target sequence
lengths with values 0.

***Important note***: It's worth pointing out that we divide the loss by
*batch_size*, so our hyperparameters are "invariant" to batch_size. Some people
divide the loss by (*batch_size* * *num_time_steps*), which plays down the
errors made on short sentences. More subtly, our hyperparameters (applied to the
former way) can't be used for the latter way. For example, if both approaches
use SGD with a learning of 1.0, the latter approach effectively uses a much
smaller learning rate of 1 / *num_time_steps*.

### Gradient computation & optimization

We have now defined the forward pass of our NMT model. Computing the
backpropagation pass is just a matter of a few lines of code:

``` python
# Calculate and clip gradients
params = tf.trainable_variables()
gradients = tf.gradients(train_loss, params)
clipped_gradients, _ = tf.clip_by_global_norm(
    gradients, max_gradient_norm)
```

One of the important steps in training RNNs is gradient clipping. Here, we clip
by the global norm.  The max value, *max_gradient_norm*, is often set to a value
like 5 or 1. The last step is selecting the optimizer.  The Adam optimizer is a
common choice.  We also select a learning rate.  The value of *learning_rate*
can is usually in the range 0.0001 to 0.001; and can be set to decrease as
training progresses.

``` python
# Optimization
optimizer = tf.train.AdamOptimizer(learning_rate)
update_step = optimizer.apply_gradients(
    zip(clipped_gradients, params))
```

In our own experiments, we use standard SGD (tf.train.GradientDescentOptimizer)
with a decreasing learning rate schedule, which yields better performance. See
the [benchmarks](#benchmarks).

## Discriminator
<p align="center">
<img width="80%" src="./README/cnn.png" />
</p>