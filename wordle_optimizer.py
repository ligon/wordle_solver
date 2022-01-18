from wordle_words import La as Answers, Ta 
from wordle_explorer import interpret_response
from collections import defaultdict
import numpy as np
import pandas as pd
import datetime
import time

Guesses = Answers + Ta

# Get rid of obsolete answers
days_elapsed = (datetime.datetime.now().date() - datetime.date(2021, 6, 19)).days
Answers = Answers[days_elapsed:]

def quantile_criterion(q):
    """
    Return 
    """
    def foo(x):
        return np.percentile(x,q)

    return foo

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

    answer_soltns = list(set(df.loc[df==df.min()].index.tolist()).intersection(answers))

    if len(answer_soltns):      # If multiple words shrink the set similarly, and some are answers...
        return answer_soltns[0] # ...then take a chance at getting it in one.
    else:
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

def initial_guess(rho=None,fn='first_round_reductions.csv.gz'):
    """Choose "optimal" initial guess.  By default this is (one of) the
    guesses that reduces list size the most *on average*.

    If risk_aversion is supplied (a float in (0,1)), then when the
    parameter is low this chooses riskier guesses---a riskier guess
    increases the probability of completing the puzzle in fewer moves,
    but at cost of possibly failing badly.
    """

    df = pd.read_csv(fn,index_col=0)

    # Drop answers to old puzzles
    df = df.iloc[:,days_elapsed:]

    if rho is None:
        df = df.mean(axis=1)
    else:
        df = df.quantile(rho,axis=1)
        
    answer_soltns = list(set(df.loc[df==df.min()].index.tolist()).intersection(Answers))

    if len(answer_soltns):      # If multiple words shrink the set similarly, and some are answers...
        return answer_soltns[0] # ...then take a chance at getting it in one.
    else:
        return df.idxmin()
    
def autoplay(guesses,answers,answer,guess='roate',criterion=np.mean):
    """
    Conduct play in ignorance of answer, return number of rounds.
    """
    i=0
    while len(answers)>1:
        print(len(answers))
        response = wordle(guess,answer)
        answers = interpret_response(guess,response,answers)
        print(sorted(answers))
        print(guess,end='')
        guess = suggestion(guesses,answers,criterion=criterion)
        i += 1

    return i


def main():
    return scoring(Guesses,Answers)

if __name__=='__main__':
    #S = main()
    #df = pd.DataFrame(zip(*[(s,np.mean(list(S[s].values()))) for s in Guesses])).T.set_index(0).squeeze().astype(float)
    #print(df.idxmin())
    rho = 0.3
    guess = initial_guess(rho=rho,fn='first_round_reductions.csv.gz')
    autoplay(Guesses,Answers,Answers[0],guess=guess,criterion=quantile_criterion(rho))
    #play_manually(Guesses,Answers)
    
