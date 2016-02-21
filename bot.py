
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
from tumblr_post import post_to_tumblr


# In[29]:

BOTNAME = 'lexiconjure'
CHARRNN_PATH = '/home/ubuntu/char-rnn'
SCRIPT_PATH = '/home/ubuntu/lexiconjure'

# ADD RNN MODEL PATH!!!
RNN_MODEL_PATH = '/home/ubuntu/models/lm_oed_epoch33.57_0.7451.t7_cpu.t7'


# In[30]:

with open('badwords.json', 'r') as infile:
    badwords = json.load(infile)

with open('seed.txt', 'r') as infile:
    seed = infile.read().strip().decode('utf8')

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

    gen_seed = '%s\n%s | %s | ' % (seed, word, word)

    # print "DEFINING:\t", repr(gen_seed)
    
    rnn_cmd_list = [
        'th',
        'sample.lua',
        RNN_MODEL_PATH,
        '-length',
        '1024',
        '-verbose',
        '0',
        '-temperature',
        '0.5',
        '-primetext',
        gen_seed.encode('utf8'),
        '-gpuid',
        '-1'
    ]

    rnn_proc = subprocess.Popen(
        rnn_cmd_list,
        stdout=subprocess.PIPE
    )
    raw_definition = rnn_proc.stdout.read().decode('utf8')

    print "RAW OUTPUT:"
    print repr(raw_definition)

    # Back to original working directory
    os.chdir(SCRIPT_PATH)

    # Take the 2nd paragraph, split training format into lines
    definition_grafs = filter(lambda y: y, map(lambda x: x.strip(), raw_definition.split(u'\n')))
    definition_lines = definition_grafs[1].split(u' | ')[2:]

    user_credit = u'<a href="https://twitter.com/%s">@%s</a>' % (screen_name, screen_name)
    tumblr_def = u'\n'.join(definition_lines)

    if len(definition_grafs) == 2:
        tumblr_def = tumblr_def.rsplit(u'\n', 1)[0]

    if screen_name:
        tumblr_def += u'\n%s' % user_credit

    post_to_tumblr(
        unicode(word).encode('utf8'),
        unicode(tumblr_def).encode('utf8'),
        source=screen_name
    )

    definition = unicode(word)
    for i, line in enumerate(definition_lines):
        definition += u'\n'+line
        chars_remaining -= len(u'\n'+line)
        # if not on the last line and next
        # line has too many characters,
        # stop adding lines...
        if len(definition_lines) > i+1 and chars_remaining < len(definition_lines[i+1]):
            break

    if chars_remaining < 0:
        definition = definition[:chars_remaining-3] + u'...'

    if screen_name:
        definition = u'%s\n@%s' % (definition, screen_name)

    return unicode(definition).encode('utf8')


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
    else:
        print "BANNED WORD DETECTED"


# In[34]:

class StreamResponder(StreamListener):
    
    def on_status(self, status):
        # try:
        if status.author.screen_name.lower() != BOTNAME and not status.text.startswith('RT'):
            process_status(status.author.screen_name, status.text)
        # except:
        #     print sys.exc_info()
            
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

bot_id = str(api.get_user(BOTNAME).id)


# In[37]:

stream.filter(follow=[bot_id], async=True)

while 1:
    api.update_status(
        make_definition_tweet(
            genetic.invent_word()
    ))
    time.sleep(5400)
