from pattern.vector import GA, chngrams
# from pattern.en import lexicon
import json
from random import choice
from random import randint as ri
from collections import Counter
from math import log

with open('words.json', 'r') as infile:
    words = json.load(infile)

allgrams = list()
for w in words:
    char3grams = chngrams(w, 3).items()
    char4grams = chngrams(w, 4).items()
    allgrams.extend(char3grams + char4grams)

lexicon = Counter()
for gram in allgrams:
    lexicon[gram[0]] += gram[1]

# print 'lexicon length:', len(lexicon)

mostCommon = max(lexicon.keys(), key=lambda k: lexicon[k])
# print mostCommon, lexicon[mostCommon]

def chseq(length=4, chars='abcdefghijklmnopqrstuvwxyz'):
    # Returns a string of random characters. 
    return ''.join(choice(chars) for i in range(length))

class Jabberwocky(GA):
    
    def fitness(self, w):
        #*log(lexicon[ch])/log(lexicon[mostCommon])
        return sum(0.2*log(lexicon[ch])/log(lexicon[mostCommon]) for ch in chngrams(w, 4) if ch in lexicon)*8/len(w) + \
               sum(0.1*log(lexicon[ch])/log(lexicon[mostCommon]) for ch in chngrams(w, 3) if ch in lexicon)*8/len(w)
               # sum(0.05*log(lexicon[ch])/log(lexicon[mostCommon]) for ch in chngrams(w, 2) if ch in lexicon)
    
    def combine(self, w1, w2):
        return w1[:len(w1)/2] + w2[len(w2)/2:] # cut-and-splice

    def mutate(self, w):
        return w.replace(choice(w), chseq(1), 1)   

def invent_word():
    candidates = list()
    for _ in range(64):
        candidates.append(''.join(chseq(ri(6,12))))

    ga = Jabberwocky(candidates)
    i = 0
    # ga.avg < 1.0 and 
    while i < 1000:
        ga.update(top=0.125, mutation=0.2)
        i += 1

    return max(ga.population, key=lambda x: ga.population.count(x))
    # print ga.generation
    # print ga.avg