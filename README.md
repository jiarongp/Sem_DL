Goal: generate text like real human tweeting

### To Do

- [ ] We need to find suitable dataset, real tweet and bot tweet.
    - [Botometer dataset](https://botometer.iuni.iu.edu/bot-repository/datasets.html) seems to be choice, but we need to look at it.

- [ ] use the [tweepy](https://www.tweepy.org/) library to get the text data, store them as the training data.
- [ ] Building the GANs model for text generation.
    - the [SentiGANs](https://github.com/Nrgeup/SentiGAN/tree/master/Toy_dataset) seems to be a good reference, because its also training a text generator.
    - train a state of the art discriminator focusing on tweet text content
        > Be careful, since we are training a text generator, so the discriminator should focus on the text content, because some social bot detector(classifier) is using other characteristics of the social bots to discriminate them.
        - to classify real data and bot data
        - maybe start with a single user tweet classification for experiment?
        
- We need to figure out what is our input of discrimminator and input of the generator
