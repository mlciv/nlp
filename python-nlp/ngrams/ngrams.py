#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Copyright @ Jie Cao, jcao@cs.utah.edu
"""
import os,sys,argparse,math,random
from itertools import chain

class NGrams:
    """ A simple ngrams class"""
    # record the ngrams from i=1 to N, every element is dict, which ngrame tuple as key, frequency as value
    n = 2
    pad_left= True
    #if the pad_right==false, the answer will be ok.
    pad_right = True
    
    symbol_begin = None
    symbol_end = '\n'
    ngramsFreq = []
    ngramsSumFreq = []
    vocabularySize = 0

    def __init__(self,n,pad_left,pad_right,symbol_begin,symbol_end):
        self.n = n
        self.pad_left = pad_left
        self.pad_right= pad_right
        self.symbol_begin = symbol_begin
        self.symbol_end = symbol_end


    # record the whole frequency of every ngram
    def train(self,trainingCorpus,splitToken=" "):
        #print 'traing with %s' % trainingCorpus
        # initialize the while Freq from i =1 to N
        i = 1
        n = self.n
        self.ngramsFreq.append(None)
        self.ngramsSumFreq.append(-1)
        while i < n + 1:
            self.ngramsFreq.append({})
            self.ngramsSumFreq.append(0)
            i+=1

        file = open(trainingCorpus)
        while 1:
            line = file.readline()
            if not line:
                break
            # preprocess all line into lower case
            sequence = line.strip().lower().split(splitToken)
            if sequence[-1]=='\n':
                sequence = sequence[:-1]
            x = 1
            while x< n+1:
                for item in self.ngrams(sequence,x,True,True,None,'\n'):
                    self.ngramsFreq[x][item] = self.ngramsFreq[x].setdefault(item,0)+1
                    #delete all invalid pading symbol, should count sos, eos in 
                    if item[-1] != None and item[0] != '\n':
                        self.ngramsSumFreq[x]+=1
                x += 1
        # delete the begin and end symbol
        self.vocabularySize = len(self.ngramsFreq[1]) - 2
        #print self.ngramsSumFreq
        #print self.ngramsFreq
        #print self.vocabularySize

    def getProbOfSequence(self,sequence,n,smooth=False):
        p = 1.0
        x = n
        if x == 1:
            # when test, delete the first n*symbol_begin and the last
            # n*symbol_end
            for item in list(self.ngrams(sequence,x,self.pad_left,self.pad_right,self.symbol_begin,self.symbol_end)):
                # delete invalid ngrams item
                if item[-1] == None or item[0] == '\n':
                    continue
                if p == 0:
                    break
                if self.ngramsFreq[x].setdefault(item,0) == 0:
                    p = 0
                    break 
                else:
                    p = p * (self.ngramsFreq[x].setdefault(item,0)/float(self.ngramsSumFreq[x]))
            if p==0:
                print 'Unigrams: logprob(S) = undefined' 
            else:
                print 'Unigrams: logprob(S) = %.4f' % math.log(p,2)
        elif x == 2:
            for item in list(self.ngrams(sequence,x,self.pad_left,self.pad_right,self.symbol_begin,self.symbol_end)):
                # delete invalid ngrams item
                if item[-1] == None or item[0] == '\n':
                    continue
                preItem = item[0:x-1]
                if smooth:
                    p = p *(self.ngramsFreq[x].setdefault(item,0)+1)/(self.ngramsFreq[x-1].setdefault(preItem,0)+self.vocabularySize)
                else:
                    if self.ngramsFreq[x-1].setdefault(preItem,0)==0 or self.ngramsFreq[x].setdefault(item,0) == 0:
                        #print 'Bigrams: preItem not exist'
                        p = 0
                        break
                    else:
                        p = p * self.ngramsFreq[x].setdefault(item,0)/float(self.ngramsFreq[x-1].setdefault(preItem,0))
            if smooth:
                print 'Smoothed Bigrams: logprob(S) = %.4f' % math.log(p,2)
            else:
                if p==0:
                    print 'Bigrams: logprob(S) = undefined' 
                else:
                    print 'Bigrams: logprob(S) = %.4f' % math.log(p,2)

    def getSeqAndTest(self,testSet,splitToken=" "):
        file = open(testSet)
        while 1:
            line = file.readline()
            if not line: 
                break
            # preprocess all line into lower case
            print 'S = %s' % line
            sequence = line.strip().lower().split(splitToken)
            if sequence[-1]=='\n':
                sequence = sequence[:-1]
            self.getProbOfSequence(sequence,1,smooth=False)
            self.getProbOfSequence(sequence,2,smooth=False)
            self.getProbOfSequence(sequence,2,smooth=True)
            print


    def generateBySeeds(self,seedsFile):
        print 'generate with %s' % seedsFile
        file = open(seedsFile)
        while 1:
            line = file.readline()
            if not line: 
                break
            # preprocess all line into lower case
            seed = line.strip()
            print 'Seed = %s\n' % seed
            i = 0
            while i<10: 
                i += 1
                self.generateBySeed(2,seed.strip().lower(),[seed,],i)
            print


    def generateBySeed(self,n,seed,seedSeq,number):
        dictSet = {}
        for item in self.ngramsFreq[n].keys():
            if item[0]!=seed:
                continue
            else:
                dictSet[item[-1]] = self.ngramsFreq[2][item]/(float)(self.ngramsFreq[1][(seed,)])
        # terminal 3:
        if len(dictSet)==0:
            print 'Sentence %d: %s' % (number,' '.join(seedSeq))
            return 
        while len(seedSeq) < 40:
            r = random.random()
            for i in dictSet.keys():
                r = r - dictSet[i]
                if r<=0:
                    seedSeq.append(i)
                    # terminal 1:
                    if i in ['.','?','!']:
                        print 'Sentence %d: %s' % (number,' '.join(seedSeq))
                        return 
                    else:
                        # terminal 2:
                        if len(seedSeq) == 40:
                            print 'Sentence %d: %s' % (number,' '.join(seedSeq))
                            return
                        else:
                            self.generateBySeed(n,i,seedSeq,number)
                            return 
                    break
                else:
                    continue
        return

    # given a sequence, generate all its ngrams tuple, include n*symbol_begin,
    # and n*symbol_end
    @staticmethod
    def ngrams(sequence,n,pad_left=True,pad_right=True,symbol_begin=None,symbol_end='\n'):
        sequence = iter(sequence)
        if pad_left:
            sequence = chain((symbol_begin,)*n,sequence)
        if pad_right:
            sequence = chain(sequence,(symbol_end,)*n)

        history = []
        #adding first n-1, and then roll over
        while n>1:
            history.append(next(sequence))
            n-=1
        for item in sequence:
            history.append(item)
            yield tuple(history)
            del history[0]
    
    @staticmethod
    def unigram(sequence, **args):
        for item in ngrams(sequence,1,**args):
            yield item
    
    @staticmethod
    def bigram(sequence, **args):
        for item in ngrams(sequence,2,**args):
            yield item
    

def main(argv):
    trainingCorpus = ""
    testSet = ""
    seedsFile = ""
    if len(argv) < 3:
        print "too few arguments"
    else:
        trainingCorpus = argv[1]
        if os.path.isfile(trainingCorpus) == False:
            print "trainingCorpus[%s] does not exist" % trainingCorpus
            exit(-1)
        testSet = argv[2]
        if os.path.isfile(testSet) == False:
            print "testSet[%s] does not exist" % testSet
            exit(-1)
        if len(argv) > 3:
            seedsFile = argv[3]
            if os.path.isfile(seedsFile) == False:
                print "seedsFile[%s] does not exist" % seedsFile
                exit(-1)
    """
    ['ngrams.py', 'traing.txt', 'test.txt', 'seeds.txt']
    """
    #Only when the 'pad_left' is True, 'pad_right' is False, the answer will be the same with the example.
    ngrams = NGrams(2,True,False,None,'\n')
    ngrams.train(trainingCorpus," ")
    ngrams.getSeqAndTest(testSet," ")
    if seedsFile!="":
        ngrams.generateBySeeds(seedsFile)
if __name__ == "__main__":
    main(sys.argv)

