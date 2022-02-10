#!/usr/bin/env python
# -*- coding: utf-8 -*-

from wordle_words import La as Answers, Ta 
from wordle_explorer import interpret_response
from collections import defaultdict
import numpy as np
import pandas as pd
import datetime
import time
import argparse
from string import ascii_lowercase, ascii_uppercase

Guesses = Answers + Ta

# Get rid of obsolete answers
days_elapsed = (datetime.datetime.now().date() - datetime.date(2021, 6, 19)).days
Answers = Answers[days_elapsed:]

#########################
# Some possible criteria

def quantile_criterion(q):
    """
    Return 
    """
    def foo(x):
        return np.percentile(x,q)

    return foo

mse = lambda x: np.mean(np.array(x)**2)

mean = lambda x: np.mean(np.array(x))

crra = lambda gamma=1 : lambda x: np.log(np.array(x)) if gamma==1 else (np.mean(np.array(x)**(1-gamma))/(1-gamma))

##########################

def wordle(guess, answer):
    # default to no occurences
    response="     "
    response=list(response)
    # give precedence to perfect matches
    for i,letter in enumerate(guess):
        if answer[i] is letter:
            response[i] = letter.upper()
    # precedence from left to right of imperfect matches
    for i,letter in enumerate(guess):
        if letter in answer:
            if answer.count(letter) > response.count(letter):
                response[i] = letter
    return ''.join(response)
                
        
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

def initial_guess(criterion=mean,fn='first_round_reductions.csv.gz'):
    """Choose "optimal" initial guess.  By default this is (one of) the
    guesses that reduces list size the most *on average*, but
    alternative criteria can be supplied.
    """

    df = pd.read_csv(fn,index_col=0)

    # Drop answers to old puzzles
    df = df.iloc[:,days_elapsed:]

    df = df.apply(criterion,axis=1)
        
    answer_soltns = list(set(df.loc[df==df.min()].index.tolist()).intersection(Answers))

    if len(answer_soltns):      # If multiple words shrink the set similarly, and some are answers...
        return answer_soltns[0] # ...then take a chance at getting it in one.
    else:
        return df.idxmin()
    
def autoplay(guesses=Guesses,answers=Answers,answer=Answers[0],guess='roate',criterion=mean,verbose=False,show_progress=True):
    """
    Conduct play in ignorance of answer, return number of rounds.
    """
    i=0

    Sequence = []
    
    if guess is None:
        guess = initial_guess(criterion=criterion,fn='first_round_reductions.csv.gz')

    while len(answers)>1:
        round = {}
        if verbose and i>0 and show_progress:
            print(sorted(answers))
        print('Number of possible answers: %d' % len(answers))
        round['guess'] = guess.upper()
        response = wordle(guess,answer)
        round['response'] = response
        answers = interpret_response(guess,response,answers)
        round['answers'] = sorted(answers)
        if show_progress:
            print(guess,end=' ')
        guess = suggestion(guesses,answers,criterion=criterion)
        Sequence.append(round)
        i += 1

    if len(answers):
        soltn = answers[0]
    else:
        soltn = guess

    round = {'guess':soltn.upper(),
             'response':soltn.upper(),
             'answers':[soltn]}

    if show_progress:
        print('\nAnswer is %s' % soltn)

    Sequence.append(round)
            
    return Sequence

def show_play_no_spoilers(Sequence):
    """
    "No spoiler" version of play.
    """
    def redact_response(response):
        redaction = ''
        for c in response:
            if c in ascii_uppercase:
                redaction += "🟩"
            elif c in ascii_lowercase:
                redaction += '🟨'
            else:
                redaction += '⬛'

        return redaction
                
    S = []            
    for i,round in enumerate(Sequence):
        redaction = redact_response(round['response'])
        s = "{}. {} ({})".format(i+1,redaction,len(round['answers']))
        S.append(s)

    return S

        
if __name__=='__main__':
    parser = argparse.ArgumentParser('Find optimal solution to wordle.')
    parser.add_argument('--risk_aversion',type=float,
                        help="Number in (0,1) to choose how conservatively to play, using quantile criterion.",
                        default=None)

    parser.add_argument('--guess',type=str,
                        help="Provide initial guess (five letters).",
                        default=None)

    parser.add_argument('--criterion',type=str,
                        help="Use alternative criterion",
                        default=None)

    parser.add_argument('--verbose','-v',action='store_true',
                        help="Show possible remaining answers")


    args = parser.parse_args()
    
    rho = args.risk_aversion
    guess = args.guess

    if args.criterion is not None:
        Sequence = autoplay(Guesses,Answers,Answers[0],guess=guess,verbose=args.verbose,criterion=eval(args.criterion))
    
    elif rho is None:
        Sequence = autoplay(Guesses,Answers,Answers[0],guess=guess,verbose=args.verbose)
    else:
        Sequence = autoplay(Guesses,Answers,Answers[0],guess=guess,criterion=quantile_criterion(rho),verbose=args.verbose)

    S = show_play_no_spoilers(Sequence)
    print("\n".join(S))
