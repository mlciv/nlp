#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Copyright @ Jie Cao, jcao@cs.utah.edu
"""
import os,sys,math,random
from itertools import chain

class Viterbi:
    """ Viterbi Algorithm"""
    T = ('phi','noun','verb','inf','prep')
    T_map = {'phi':0,'noun':1,'verb':2,'inf':3,'prep':4}
    Pt_t = [{}] # for phi tag
    Pw_t = [{}] # for phi tag
    
    def __init__(self):
        pass

    def loadProbFile(self,probFile):
        for i in self.T:
            self.Pt_t.append({})
            self.Pw_t.append({})
        file = open(probFile)
        while 1:
            line = file.readline()
            if not line: 
                break
            # preprocess all line into lower case
            sequence = line.strip().lower().split(' ')
            tag_cond = sequence[1]
            key = sequence[0]
            probValue = float(sequence[2])
            if key in self.T:
                self.Pt_t[self.T_map[tag_cond]].setdefault(key,probValue)
                #print("tag="+key+",tag_cond="+tag_cond+", probValue="+str(probValue))
            else:
                self.Pw_t[self.T_map[tag_cond]].setdefault(key,probValue)
                #print("word="+key+",tag_cond="+tag_cond+", probValue="+str(probValue))

    def predict(self,probFile,sentenceFile):
        self.loadProbFile(probFile)
        file = open(sentenceFile)
        while 1:
            line = file.readline()
            if not line:
                break
            print("PROCESSING SENTENCE: "+line)
            # not to lower for sentence at first , to lower in the process
            W = line.strip().split(' ')
            self.doViterbi(W)

    def doViterbi(self,W):
        ## init score for every word
        # for begin word phi
        W.insert(0,'')
        Score = []
        BackPtr = []
        Seq = []
        SeqSum = []
        for word in W:
            Score.append([ 0.0 for x in range(len(self.T)) ])
            BackPtr.append([ 0 for x in range(len(self.T)) ])
            SeqSum.append([ 0.0 for x in range(len(self.T)) ])
            Seq.append('')
        for i in range(1,len(self.T)):
            Score[1][i] = self.Pw_t[i].setdefault(W[1].lower(),0.0001)*self.Pt_t[0].setdefault(self.T[i],0.0001)
            SeqSum[1][i] = self.Pw_t[i].setdefault(W[1].lower(),0.0001)*self.Pt_t[0].setdefault(self.T[i],0.0001)
            BackPtr[1][i] = 1
        
        ## iteration step
        for w_index in range(2,len(W)):
            for t_index in range(1,len(self.T)):
                max_p = -1.0
                max_index = -1
                sum_p = 0.0
                for j in range(1,len(self.T)):
                    tmp = Score[w_index-1][j]*self.Pt_t[j].setdefault(self.T[t_index],0.0001)
                    sum_p = sum_p + SeqSum[w_index-1][j]*self.Pt_t[j].setdefault(self.T[t_index],0.0001)
                    if tmp > max_p:
                        max_p = tmp
                        max_index = j
                Score[w_index][t_index] = self.Pw_t[t_index].setdefault(W[w_index].lower(),0.0001)*max_p
                BackPtr[w_index][t_index] = max_index
                SeqSum[w_index][t_index] = self.Pw_t[t_index].setdefault(W[w_index].lower(),0.0001)*sum_p

        ## trace
        print("FINAL VITERBI NETWORK")
        for w_index in range(1,len(W)):
            for t_index in range(1,len(self.T)):
                print("P(%s=%s) = %0.10f" % (W[w_index],self.T[t_index],Score[w_index][t_index]))
        print("")

        print("FINAL BACKPTR NETWORK")
        for w_index in range(2,len(W)):
            for t_index in range(1,len(self.T)):
                print("Backptr(%s=%s) = %s" % (W[w_index],self.T[t_index],self.T[BackPtr[w_index][t_index]]))
        print("")
        
        ## Sequence
        max_p = -1.0
        max_t = -1
        for t in range(1,len(self.T)):
            tmp = Score[len(W)-1][t]
            if tmp > max_p:
                max_p = tmp
                max_t = t
        Seq[len(W)-1] = max_t

        for w in range(len(W)-2,0,-1):
            Seq[w]= BackPtr[w+1][Seq[w+1]]
        
        print("BEST TAG SEQUENCE HAS PROBABILITY = %.10f" % max_p)
        for i in range(len(W)-1,0,-1):
            print(W[i]+" -> "+ self.T[Seq[i]])
        
        print("")
        print("FORWARD ALGORITHM RESULTS")
        for w_index in range(1,len(W)):
            sum_p = 0.0
            for t_index in range(1,len(self.T)):
                sum_p = sum_p + SeqSum[w_index][t_index]
            for k_index in range(1,len(self.T)):
                print("P(%s=%s) = %0.10f" % (W[w_index],self.T[k_index],SeqSum[w_index][k_index]/sum_p))
        

def main(argv):
    probFile = ""
    sentenceFile = ""
    if len(argv) < 3:
        print "too few arguments"
    else:
        probFile = argv[1]
        if os.path.isfile(probFile) == False:
            print "probFile[%s] does not exist" % probFile
            exit(-1)
        sentenceFile = argv[2]
        if os.path.isfile(sentenceFile) == False:
            print "sentenceFile[%s] does not exist" % sentenceFile
            exit(-1)
    """
    ['viterbi.py', 'probFile', 'sentenceFile']
    """
    viterbi = Viterbi()
    viterbi.predict(probFile,sentenceFile)

if __name__ == "__main__":
    main(sys.argv)

