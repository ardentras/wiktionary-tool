from html.parser import HTMLParser
import json
import requests
import getopt
import sys
import string
import textwrap
import pycountry

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

class DefinitionHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sentence = ""

    def handle_data(self, data):
        self.sentence = self.sentence + data
    
    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.sentence = self.sentence + '\n'

    def getSentence(self):
        return self.sentence
    
    def clear(self):
        self.sentence = ''

def usage(retvalue = 1):
    print('''
Usage: %s -[pdh][w word][s sentence][l language]

Arguments
    -d/--define     get definition
    -h/--help       print this dialogue
    -l/--language   the language. defaults to russian
    -p/--pronounce  get pronunciation
    -s/--sentence   a sentence to pronounce, wrapped in quotes
    -w/--word       the word to look up
''' % (sys.argv[0]))

    sys.exit(retvalue)

def punc_clean(word):
    return word.strip(string.punctuation)

def pronounce_it(word, lang="russian"):
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

def define_it(word, lang="russian"):
    htmlParser = DefinitionHTMLParser()
    r = requests.get("https://en.wiktionary.org/api/rest_v1/page/definition/%s" % (word))

    thetree = json.loads(r.text)
    block = ''
    country_code = ''

    language = pycountry.languages.get(name=lang)
    
    try:
        if hasattr(language, 'alpha_2'):
            country_code = language.alpha_2 
        else:
            country_code = language.alpha_3
    except Exception:
        return ''

    if country_code in thetree:
        for item in thetree[country_code]:
            block = block + item['partOfSpeech'] + ": \n"
            count = 1
            for definition in item['definitions']:
                htmlParser.feed(definition['definition'])
                block = block + (' ' * 4) + str(count) + '. ' + htmlParser.getSentence() + '\n'
                count = count + 1
                htmlParser.clear()

                if 'parsedExamples' in definition:
                    for example in definition['parsedExamples']:
                        htmlParser.feed(example['example'])
                        for sentence in htmlParser.getSentence().split('\n'):
                            block = block + (' ' * 6) + sentence + '\n'
                        htmlParser.clear()

    return block

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

def processDefine(word, lang = "russian"):
    print("Trying to define '%s'\n" % word)
    definition = define_it(word, lang)
    if len(definition) > 0:
        print(definition)
    else:
        print('Found no definition.')

    print("\nSee 'https://en.wiktionary.org/wiki/%s' for more details" % (word))

################
## Code start ##
################

word = ''
lang = 'russian'
doSentence = False
pronounce = False
define = False

try:
    opts, args = getopt.getopt(sys.argv[1:], "w:l:s:dph", ["word=", "language=", "sentence=", "define", "pronounce", "help"])
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
    elif opt in ('-d', '--define'):
        define = True
    elif opt in ('-l', '--language'):
        lang = arg
    else:
        usage()

if pronounce:
    processPronounce(word, lang, doSentence)
elif define:
    processDefine(word, lang)
else:
    usage()