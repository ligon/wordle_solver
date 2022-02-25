#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import bs4
import re

baseurl = "https://www.nytimes.com/games/wordle/"
page = requests.get(baseurl)

soup = BeautifulSoup(page.content,'html.parser')
src = soup.find_all('script')

src = [s for s in soup.find_all('script') if 'src="main' in str(s)]

js = str(src).split('"')[1]

assert 'main' in js

code = requests.get(baseurl + js)

code = requests.get(baseurl + js)
csoup = BeautifulSoup(code.content,features="lxml")
vars = str(csoup).split('var ')

arrs = [v for v in vars if '["' in v[:5]]

s=re.compile(r"\[([^]]+)\]")

foo = s.findall(arrs[0])

Answers = eval('[' + foo[0] + ']')
Guesses = eval('[' + foo[1] + ']')

assert len(Guesses) > len(Answers)

Guesses = Answers + Guesses
