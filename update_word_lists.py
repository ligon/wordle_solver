#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import bs4
import re

baseurl = "https://www.nytimes.com/games/wordle/"
page = requests.get(baseurl)

soup = BeautifulSoup(page.content,'html.parser')
src = soup.find_all('script')

jsfile = re.compile('/wordle.[a-z0-9]+.js')

src = [s for s in soup.find_all('script') if jsfile.search(str(s)) is not None]

fn = src[0].get_attribute_list('src')[0]

code = str(requests.get(fn).content)

Qstart = code.index("Q=[")
Qend = code[Qstart:].index(']')+1
Q = code[Qstart:Qstart+Qend]

Jstart = code.index("J=[")
Jend = code[Jstart:].index(']')+1
J = code[Jstart:Jstart+Jend]

Answers = eval(J[2:])
Guesses = eval(Q[2:])

assert len(Guesses) > len(Answers)

with open('.guesses','w') as f:
    f.writelines("%s\n" % s for s in Guesses)

with open('.answers','w') as f:
    f.writelines("%s\n" % s for s in Answers)
    
Guesses = Answers + Guesses
