from collections import defaultdict
import random
import sys
import numpy as np

import etl

START="^"
END="$"

EOSENTENCE = set(["?",".","...","!","!!"])
IGNORE = set([",","-","(",")",""])
IGNORE_PARTS = set(["http://","https://"])
MAX_SENTENCE_LENGTH = 1000

class Ngram:
    def __init__(self, text, start, end, isStart, isEnd, len):
        self.text =text
        self.start = start
        self.end = end
        self.isStart = isStart
        self.isEnd = isEnd
        self.len =len

    def __str__(self):
        return ("^" if self.isStart else "") + self.text + ("$" if self.isEnd else "")

class Brain:

    ends = set()
    starts = set()
    ngrams = defaultdict(list)

    def __init__(self):
        pass

    def load(self, ngrams):
        for ngram in ngrams:
            if ngram.isStart:
                self.starts.add(ngram)
            if ngram.isEnd:
                self.ends.add(ngram)
            if not ngram.isStart:
                self.ngrams[ngram.start].append(ngram)

    
    def getNextNgram(self, ngram, first=False):
        if first==True or ngram.isEnd:
            return random.sample(self.starts,1)[0]

        choices =  self.ngrams[ngram.end]
        if len(choices) == 0:
            return None
        else:
            res = random.sample(choices,1)[0]
            return res
            

    def generate(self,wordHint=15):
        sentenceSize = 0
        ngrams = []
        prevNgram = None
        first = True
        while(True):
            newNgram = self.getNextNgram(prevNgram, first=first)
            first = False
            if newNgram is not None :
                ngrams.append(newNgram)
                sentenceSize+=newNgram.len
                prevNgram = newNgram
                if (sentenceSize>=wordHint and newNgram.isEnd) or (sentenceSize>=MAX_SENTENCE_LENGTH):
                    for i,n in enumerate(ngrams):
                        if i>0 and ngrams[i-1].end == ngrams[i].start:
                            ngrams[i].text = ngrams[i].text[len(ngrams[i].start)+1:]
                    return " ".join(map(lambda x:x.text,ngrams)),ngrams
            else:
                #import ipdb; ipdb.set_trace()
                self.getNextNgram(ngrams[-1])
                return None, ngrams# could backtrack for more advanced logic!


def isEndOfSentence(word):
    for ending in EOSENTENCE:
        if len(word) >= len(ending) and word[-len(ending):] == ending:
            return True
    return False


def load(text, brain, n=2):
    text = text.replace("\n"," ")
    words = filter(lambda x: x not in IGNORE,map(lambda x:x.strip(),text.split(" ")))
    words = filter(lambda x: np.array([not p in x for p in IGNORE_PARTS]).all(), words)
    ngrams = []
    for i in range(n,len(words)):
        lb = max(i-n,0) # get the lower bound for the ngram
        curr_words = words[lb:i]
        currNgramIsStart = lb ==0  or isEndOfSentence(words[lb-1]) 
        currNgramIsEnd = False
        # break the ngram if the sentence ends
        for j,_ in enumerate(curr_words):
            if isEndOfSentence(curr_words[j]):
                curr_words = curr_words[:j+1]
                currNgramIsEnd = True
                break
        try:
            ngram = Ngram(" ".join(curr_words),curr_words[0], curr_words[-1], currNgramIsStart, currNgramIsEnd,len(curr_words))
        except Exception,e:
            print e
            print words[lb:i], curr_words
        ngrams.append(ngram)
        #if ngram.text=="our person.":
            #import ipdb; ipdb.set_trace()
    brain.load(ngrams)

def main(args):
    brain = Brain()
    #text = open(args[0]).read() # for plain text file
    lines = etl.get_statuses_as_lines(args[0])
    for line in lines:
        if not isEndOfSentence(line):
            line = line + "."
        load(line, brain, n=int(args[1]))
    for i in range(50):
        #print "generating:"
        sentence, details = brain.generate()
        if sentence is not None:
            print sentence
            print "------"
            #print details
        else:
            #print "--- generation failed---"
            continue


if __name__ == '__main__':
    main(sys.argv[1:])
