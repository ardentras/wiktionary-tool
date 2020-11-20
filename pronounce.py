#######################################
# filename: pronounce.py
# author: Shaun Rasmusen
# 

import json
import string
import sys
import textwrap
from html.parser import HTMLParser

###############################################################################
# PronunciationHTMLParser overrides HTMLParser to try and pull all IPA 
# pronunciation information from a Wiktionary Pronunciation HTML block
#
class PronunciationHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ipas = []
        self.foundIPA = False

    def handle_starttag(self, tag, attrs):
        if tag == 'span':
            for attr, val in attrs:
                if attr == 'class':
                    if val == 'IPA':
                        self.foundIPA = True

    def handle_data(self, data):
        if self.foundIPA:
            if '[' in data or '/' in data:
                self.ipas.append(data)
                self.foundIPA = False

    def getIPAs(self):
        return self.ipas

###############################################################################
# punc_clean cleans the punctuation from a word and returns it
#
def punc_clean(word):
    return word.strip(string.punctuation)

###############################################################################
# pronounce_it retrieves all page sections for the desired word from Wiktionary,
# attempts to locate the desired language and if found, returns a list of all
# found IPA pronunciation guides for that entry
#
def pronounce_it(word, lang="russian"):
    try:
        import requests
    except Exception:
        print('Cannot use this function without \'requests\' installed.')
        print('Run \'python -m pip install requests\' and try again.')
        sys.exit(2)
    
    htmlParser = PronunciationHTMLParser()
    r = requests.get("https://en.wiktionary.org/api/rest_v1/page/mobile-sections/%s" % (word))
    
    thetree = json.loads(r.text)
    
    languageFound = False
    level = 0

    if 'lead' in thetree and 'sections' in thetree['lead']:
        for section in thetree['lead']['sections']:
            if 'toclevel' in section:
                if section['toclevel'] == 1:
                    if section['line'] == lang.title():
                        languageFound = True
                    else:
                        languageFound = False
                if section['line'] == 'Pronunciation' and languageFound:
                    thehtml = htmlParser.feed(thetree['remaining']['sections'][section['id'] - 1]['text'])

    return htmlParser.getIPAs()

###############################################################################
# processPronounce preprocesses the input to be handled by pronounce_it,
# particularly when reading sentences. It also does its best to pretty print
# the output.
#
def processPronounce(word, lang = "russian", doSentence = False):
    ipaNotFound = '[!!!]'
    
    print("Trying to pronounce '%s'\n" % word)
    
    if doSentence:
        words = word.split(' ')
        sentence = ''
        ipaSentence = ''
        for word in words:
            ipas = pronounce_it(punc_clean(word.lower()), lang)
            if len(ipas) > 0:
                sentence = sentence + word.ljust(len(ipas[0]), ' ') + ' '
                ipaSentence = ipaSentence + ipas[0].ljust(len(word), ' ') + ' '
            else:
                sentence = sentence + word.ljust(len(ipaNotFound), ' ') + ' '
                ipaSentence = ipaSentence + ipaNotFound.ljust(len(word), ' ') + ' '
        
        sentenceLines = textwrap.wrap(sentence, 80)
        ipaSentenceLines = []
        count = 0
        for sentenceLine in sentenceLines:
            ipaSentenceLines.append(ipaSentence[count:ipaSentence.find(' ', count + len(sentenceLine))])
            count = count + len(ipaSentence[count:ipaSentence.find(' ', count + len(sentenceLine))]) + 1

        for i in range(len(sentenceLines)):
            print(sentenceLines[i])
            print(ipaSentenceLines[i])
            print()
    
    else:
        ipas = pronounce_it(punc_clean(word.lower()), lang)
        if len(ipas) > 0:
            print('Found', len(ipas), 'option' + ('s' if len(ipas) > 1 else '') + ':')
            for ipa in ipas:
                print('\t- %s' % (ipa))
        else:
            print('Found no pronunciation guide.')
        
        print("\nSee 'https://en.wiktionary.org/wiki/%s' for more details" % (word))