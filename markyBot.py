import tweepy
import markovify

class TwitterBot(object):

    def __init__(self,consumer_key, consumer_secret,
                 access_token, access_token_secret,screen_name,markov_model=None):

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.markov_model = markov_model
        self.made_tweets = []
        self.screen_name = screen_name
        self.replied_to_tweets = []

    def authorise(self):
        '''Handles authorisation of the Twitter APP in use'''
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        api = tweepy.API(auth)
        return api

    def make_markov_model(self, text_file):
        '''Makes a markov model from given new line textfile and overwrites any existing markov model'''
        with open(text_file, encoding='utf-8') as corpus:
            training_text = corpus.read()
            markov_model = markovify.NewlineText(training_text)
            self.markov_model = markov_model

    def make_markov(self,length):
        return self.markov_model.make_short_sentence(length)

    def make_markov_tweet(self):
        """Makes a tweet out of our created markov model"""
        attempts = 0
        while attempts < 5:
            new_tweet = self.markov_model.make_short_sentence(140)
            if new_tweet not in self.made_tweets:
                api = self.authorise()
                s = api.update_status(new_tweet)
                break
            else:
                attempts += 1

    def update_already_tweeted(self):
        """Checks to see whether the given account """
        api = self.authorise()
        new_tweets = api.user_timeline(screen_name=self.screen_name,count=200)
        for tweet in new_tweets:
            text = tweet.text
            if text not in self.made_tweets:
                self.made_tweets.append(text)

    def reply_to_mentions(self):
        '''Replys to mentions - makes five attempts to create unique markov reply before failing silently'''
        api = self.authorise()
        attempts = 0
        tweets_to_me = api.search('@{}'.format(self.screen_name))
        for tweet in tweets_to_me:
            if tweet.id not in self.replied_to_tweets:
                while attempts < 5:
                    screen_name = '@{}'.format(tweet.user.screen_name)
                    new_tweet = self.make_markov((140 - len(screen_name) - 2))
                    if new_tweet not in self.made_tweets:
                        s = format('{} {}'.format(screen_name, new_tweet))
                        do = api.update_status(s)
                        self.replied_to_tweets.append(tweet.id)
                        self.made_tweets.append(s)
                        break
                    else:
                        attempts += 1
