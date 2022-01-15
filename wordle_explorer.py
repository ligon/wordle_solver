from wordle_words import Ta, La
import re

def apply_regex(ex,l,method='match'):
    if method == 'match':
        p = re.compile(ex)
        return [w for w in l if p.match(w)]
    elif method=='search':
        p = re.compile(ex)
        return [w for w in l if p.search(w)]

def doesnt_have_letters(letters,l):
    return apply_regex('[^%s]{5}' % letters,l)

def has_letter_in_some_position(letter,l):
    return apply_regex('[%c]' % letter,l,method='search')

def has_letters_in_some_position(letters,l):
    myl = l.copy()
    for letter in letters:
        myl = has_letter_in_some_position(letter,myl)

    return myl

def has_letter_not_in_some_position(letter,position,l):
    ex = [r'[\w]']*5
    ex[position] = '[^%c]' % letter
    ex = "".join(ex)
    return apply_regex(ex,l,method='search')

def has_letter_in_known_position(letter,position,l):
    ex = [r'[\w]']*5
    ex[position] = '[%c]' % letter.lower()
    ex = "".join(ex)
    return apply_regex(ex,l)

def refine(doesnt_have,has_in_known_position,has_not_in_position,l):
    if len(doesnt_have):
        myl = doesnt_have_letters(doesnt_have,l) # Eliminate words that have verboten letters
    else:
        myl = l.copy()

    for letter,position in has_not_in_position:
        myl = has_letter_not_in_some_position(letter,position,myl)
        myl = has_letter_in_some_position(letter,myl)

    for letter,position in has_in_known_position:
        myl = has_letter_in_known_position(letter,position,myl)

    return myl

def interpret_response(guess,response,L):
    #if guess==response.lower() and response==response.upper(): return []
        
    doesnt_have = "".join(set(guess).difference(set(response.lower())))

    has_in_known_position = []
    has_not_in_position = []
    for i,letter in enumerate(response):
        if letter in 'abcdefghijklmnopqrstuvwxyz':
            has_not_in_position.append((letter,i))
        elif letter in 'abcdefghijklmnopqrstuvwxyz'.upper():
            has_in_known_position.append((letter,i))

    return refine(doesnt_have,has_in_known_position,has_not_in_position,L)

    
def main():
    """Input response from wordle.  Letters in correct position are
    capitalized, letters *not* in correct position lowercase, letters
    not in word represented with a "_".`
    """
    L = La
    while True:
        guess = input('What is new guess?')
        response = input('What is wordle response to "%s"?' % guess)
        L = interpret_response(guess,response,L)
        print(L)
        
if __name__=='__main__':
    main()
