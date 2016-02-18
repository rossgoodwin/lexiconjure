
# coding: utf-8

# In[26]:

import sys
import os
import re
import json
import time
import subprocess


# In[27]:

import tweepy
from tweepy.streaming import StreamListener


# In[28]:

import twitter_credentials
import genetic


# In[29]:

BOTNAME = 'lexiconjure'
CHARRNN_PATH = '/home/ubuntu/char-rnn'
SCRIPT_PATH = '/home/ubuntu/lexiconjure'

# ADD RNN MODEL PATH!!!
RNN_MODEL_PATH = '/home/ubuntu/models/lm_oed_epoch33.57_0.7451.t7_cpu.t7'


# In[30]:

with open('badwords.json', 'r') as infile:
    badwords = json.load(infile)


# In[31]:

consumer_key = os.environ.get('TWITTER_CONSUMER_KEY', '-1')
consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET', '-1')
access_token = os.environ.get('TWITTER_ACCESS_TOKEN', '-1')
access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET', '-1')

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


# In[32]:

def make_definition_tweet(word, screen_name=''):
    if screen_name:
        chars_remaining = 140 - len(word) - len('\n@'+screen_name)
    else:
        chars_remaining = 140 - len(word)

    os.chdir(CHARRNN_PATH)

    gen_seed = '%s | %s | ' % (word, word)
    
    rnn_cmd_list = [
        'th',
        'sample.lua',
        RNN_MODEL_PATH,
        '-length',
        '256',
        '-verbose',
        '0',
        '-temperature',
        '0.5',
        '-primetext',
        gen_seed,
        '-gpuid',
        '-1'
    ]

    rnn_proc = subprocess.Popen(
        rnn_cmd_list,
        stdout=subprocess.PIPE
    )
    raw_definition = rnn_proc.stdout.read()

    # Back to original working directory
    os.chdir(SCRIPT_PATH)

    definition_lines = raw_definition.split('\n', 1)[0].split(' | ')[2:]

    definition = word
    for i, line in enumerate(definition_lines):
        definition += '\n'+line
        chars_remaining -= len('\n'+line)
        if len(definition_lines) > i+1 and chars_remaining < len(definition_lines[i+1]):
            break

    if chars_remaining < 0:
        definition = definition[:chars_remaining-3] + '...'

    if screen_name:
        return '%s\n@%s' % (definition, screen_name)
    else:
        return definition


# In[33]:

def process_status(author, text):
    tokens = filter(
        lambda t: not (t.startswith('@') or t.startswith('#') or t.startswith('http')),
        re.findall(r'[^\s]+', text)
    )
    to_define = ' '.join(tokens)
    if not any(w in to_define.lower() for w in badwords):
        tweet_text = make_definition_tweet(to_define, screen_name=author)
        api.update_status(tweet_text)


# In[34]:

class StreamResponder(StreamListener):
    
    def on_status(self, status):
        try:
            if status.author.screen_name.lower() != BOTNAME and not status.text.startswith('RT'):
                process_status(status.author.screen_name, status.text)
        except:
            print sys.exc_info()
            
        return True
    
    def on_error(self, status):
        print status
        if status == 420:
            #returning False in on_data disconnects the stream
            return False
        else:
            return True

    def on_limit(self, track):
        """Called when a limitation notice arrives"""
        print track
        return True

    def on_timeout(self):
        """Called when stream connection times out"""
        return True

    def on_disconnect(self, notice):
        """Called when twitter sends a disconnect notice
        Disconnect codes are listed here:
        https://dev.twitter.com/docs/streaming-apis/messages#Disconnect_messages_disconnect
        """
        print notice
        return False

    def on_warning(self, notice):
        """Called when a disconnection warning message arrives"""
        print notice
        return False


# In[35]:

stream = tweepy.Stream(auth, StreamResponder(), timeout=None)


# In[36]:

bot_id = str(tweepy.API(auth).get_user(BOTNAME).id)


# In[37]:

stream.filter(follow=[bot_id], async=True)

while 1:
    api.update_status(
        make_definition_tweet(
            genetic.invent_word()
    ))
    time.sleep(5400)
