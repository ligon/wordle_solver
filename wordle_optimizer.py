from wordle_words import La as Answers, Ta 
from wordle_explorer import interpret_response
from collections import defaultdict
import numpy as np
import pandas as pd
import time 

Guesses = Answers + Ta

def wordle(guess, answer):
    res = ''
    for i,letter in enumerate(guess):
        if letter == answer[i]:
            res+=letter.upper()
        elif letter in answer:
            res+=letter
        else:
            res+=' '
    return res

def scoring(guesses,answers):
    start = time.process_time()
    
    Scores = defaultdict(dict)

    for i,word in enumerate(guesses):
        #print(i,word,time.process_time() - start)
        for answer in answers:
            response = wordle(word,answer)
            L = interpret_response(word,response,answers)
            Scores[word][answer] = len(L)

    return Scores

def suggestion(guesses,answers,criterion=np.mean):
    """Given a list of possible guesses and answers, return the guess
    which, on /average/ eliminates the largest number of answers
    (assuming each answer to be equally probable).

    """
    S = scoring(guesses,answers)
    
    df = pd.DataFrame(zip(*[(s,criterion(list(S[s].values()))) for s in guesses])).T.set_index(0).squeeze().astype(float)
    return df.idxmin()

def play_manually(guesses,answers,answer=None):
    i=0
    while len(answers)>1:
        guess = input('What is next guess? ')
        if answer is None:
            response = input('What is response to "%s"? ' % guess)
        else:
            response = wordle(guess,answer)
        answers = interpret_response(guess,response,answers)
        print(len(answers),answers)
        i += 1

    return answers,i

def play_against_web(guesses,answers,guess='roate',criterion=np.mean):
    i=0
    while len(answers)>1:
        response = input('What is response to "%s"? ' % guess)
        answers = interpret_response(guess,response,answers)
        print(answers)
        guess = suggestion(guesses,answers,criterion=criterion)
        i += 1

    return answers,i

def autoplay(guesses,answers,answer,guess='roate',criterion=np.mean):
    """
    Conduct play in ignorance of answer, return number of rounds.
    """
    i=0
    while len(answers)>1:
        print(guess,len(answers))
        response = wordle(guess,answer)
        answers = interpret_response(guess,response,answers)
        print(sorted(answers))
        guess = suggestion(guesses,answers,criterion=criterion)
        i += 1

    return i


def main():
    return scoring(Guesses,Answers)

if __name__=='__main__':
    #S = main()
    #df = pd.DataFrame(zip(*[(s,np.mean(list(S[s].values()))) for s in Guesses])).T.set_index(0).squeeze().astype(float)
    #print(df.idxmin())
    #autoplay(Guesses,Answers,'tangy',guess='roate')
    play_manually(Guesses,Answers)
