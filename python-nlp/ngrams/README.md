# How to run
1. source env.sh
    In order to run "ngrams" command in the current directory with
    <code>ngrams <training file> <test file> <seeds file></code>
    I append the current directory befind the PATH environment, and then chmod
    a+x ngrams

2. ngrams training.txt test.txt > seqProbility.trace
3. ngrams training.txt test.txt seeds.txt > genSentenece.trace

# CADE Machine
lab1-1.eng.utah.edu

# Known issues
1. Padding Option 
Only when the 'pad_left' is True, 'pad_right' is False, the answer will be the same with the example.<code>ngrams = NGrams(2,True,False,None,'\n')¬</code>

Because this is related with the pading when caculating bigram.

By setting the NGrams class with different padding options, we can get different answer .

2. Generate Sentence
As the sentence are generated only by the probilities of bigram, not considering the
part-of-speech things. Hence bigrams with limited context info cannot grantee the correctness of every
setence.
