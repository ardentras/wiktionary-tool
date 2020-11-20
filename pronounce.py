from html.parser import HTMLParser
import json
import requests
import getopt
import sys
import string

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

def usage(retvalue = 1):
    print('''
Usage: %s -[ph][w word][s sentence][l language]

Arguments
    -w/--word       the word to look up
    -s/--sentence   a sentence to pronounce, wrapped in quotes
    -p/--pronounce  get pronunciation
    -l/--language   the language. defaults to russian
    -h/--help       print this dialogue
''' % (sys.argv[0]))

    sys.exit(retvalue)

def pronounce_it(word, lang="Russian"):
    htmlParser = PronunciationHTMLParser()
    r = requests.get("https://en.wiktionary.org/api/rest_v1/page/mobile-sections/%s" % (word))
    
    thetree = json.loads(r.text)
    
    russianFound = False
    level = 0

    if 'lead' in thetree and 'sections' in thetree['lead']:
        for section in thetree['lead']['sections']:
            if 'toclevel' in section:
                if section['toclevel'] == 1:
                    if section['line'] == lang.title():
                        russianFound = True
                    else:
                        russianFound = False
                if section['line'] == 'Pronunciation' and russianFound:
                    thehtml = htmlParser.feed(thetree['remaining']['sections'][section['id'] - 1]['text'])

    return htmlParser.getIPAs()

def punc_clean(word):
    return word.strip(string.punctuation)

################
## Code start ##
################

word = ''
lang = 'russian'
ipaNotFound = '[!!!]'
doSentence = False
pronounce = True

try:
    opts, args = getopt.getopt(sys.argv[1:], "w:l:s:ph", ["word=", "language=", "sentence=", "pronounce", "help"])
except getopt.GetoptError:
      usage()

for opt, arg in opts:
    if opt in ('-h', '--help'):
        usage(0)
    elif opt in ('-w', '--word'):
        word = arg
    elif opt in ('-s', '--sentence'):
        doSentence = True
        word = arg
    elif opt in ('-p', '--pronounce'):
        pronounce = True
    elif opt in ('-l', '--language'):
        lang = arg
    else:
        usage()

if pronounce:
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
        
        print(sentence)
        print(ipaSentence)
    
    else:
        ipas = pronounce_it(punc_clean(word.lower()), lang)
        if len(ipas) > 0:
            print('Found', len(ipas), 'options:')
            for ipa in ipas:
                print('\t- %s' % (ipa))
        else:
            print('Found no pronunciation guide.')
        
    print("\nSee 'https://en.wiktionary.org/wiki/%s' for more details" % (word))

else:
    usage()