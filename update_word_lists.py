#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import bs4
import re
import git
import os

def commit_word_changes():
    answerdiff = None
    guessesdiff = None
    repo = git.Repo(os.getcwd())
    files = repo.git.diff(None, name_only=True).split('\n')
    if '.answers' in files:
        repo.git.add('.answers')
        answerdiff = repo.git.diff('.answers')
    if '.guesses' in files:
        repo.git.add('.guesses')
        guessesdiff = repo.git.diff('.guesses')
    if '.answers' in files or '.guesses' in files:
        repo.git.commit('-m','Update word lists.',author='ligon@berkeley.edu')

    return answerdiff,guessesdiff

baseurl = "https://www.nytimes.com/games/wordle/"
page = requests.get(baseurl)

soup = BeautifulSoup(page.content,'html.parser')
src = soup.find_all('script')

jsfile = re.compile('/wordle.[a-z0-9]+.js')

src = [s for s in soup.find_all('script') if jsfile.search(str(s)) is not None]

fn = src[0].get_attribute_list('src')[0]

code = str(requests.get(fn).content)

Qstart = code.index('["aa')
Qend = code[Qstart:].index(']')+1
Q = code[Qstart:Qstart+Qend]

Jstart = code.index('["cigar"')
Jend = code[Jstart:].index(']')+1
J = code[Jstart:Jstart+Jend]

Answers = eval(J)
Guesses = eval(Q)

assert len(Guesses) > len(Answers)

with open('.guesses','w') as f:
    f.writelines("%s\n" % s for s in Guesses)

with open('.answers','w') as f:
    f.writelines("%s\n" % s for s in Answers)
    
Guesses = Answers + Guesses

adiffs,gdiffs = commit_word_changes()

if adiffs is not None:
    print("Changes in Answers!")
    print(adiffs)


if gdiffs is not None:
    print("Changes in Answers!")
    print(gdiffs)
