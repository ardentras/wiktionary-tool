#######################################
# filename: define.py
# author: Shaun Rasmusen
# last modified: 12/18/2020
# 

import json
import sys
from html.parser import HTMLParser

###############################################################################
# DefinitionHTMLParser overrides HTMLParser to clear all HTML tags from a
# definition from the Wiktionary API for easier readability.
#
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

###############################################################################
# define_it retrieves all definitions for the desired word from Wiktionary,
# attempts to locate the desired language by trying to translate it to a
# country code and if found, returns a newline delimited string containing each
# part of speech, its definition(s), and example(s)
#
def define_it(word, language):
    try:
        import requests
    except Exception:
        print('Cannot use this function without \'requests\' installed.')
        print('Run \'python -m pip install requests\' and try again.')
        sys.exit(2)

    r = requests.get("https://en.wiktionary.org/api/rest_v1/page/definition/%s" % (word))
    block = parseDefinitionResponse(json.loads(r.text), language)

    # not yet supported
    #if len(block) == 0:
    #    r = requests.get("https://%s.wiktionary.org/api/rest_v1/page/definition/%s" % (language, word))
    #    block = parseDefinitionResponse(json.loads(r.text), language)

    return block

###############################################################################
# parseDefinitionResponse parses the response from the Wiktionary API to find a
# valid definition for the desired language. If not found on English Wiktionary,
# it will attempt to find the in language definition instead.
#
# block is returned with the definition if found, else empty.
#
def parseDefinitionResponse(thetree, language):
    htmlParser = DefinitionHTMLParser()
    block = ''
    country_code = ''

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

###############################################################################
# processDefine preprocesses the input to be handled by define_it. It also does
# some pretty printing around the definition.
#
def processDefine(word, lang = "russian"):
    try:
        import pycountry
    except Exception:
        print('Cannot use this function without \'pycountry\' installed.')
        print('Run \'python -m pip install pycountry\' and try again.')
        sys.exit(2)

    extra = ''

    language = pycountry.languages.get(name=lang)

    print("Trying to define '%s'\n" % word)
    definition = define_it(word, language)
    if len(definition) > 0:
        print(definition)
        print("\nSee 'https://en.wiktionary.org/wiki/%s#%s' for more details" % (word, lang.title()))
    else:
        print('Found no definition.')
        print("\nPerhaps try 'https://%s.wiktionary.org/wiki/%s#%s' instead" % (language.alpha_2 if hasattr(language, 'alpha_2') else language.alpha_3, word, lang.title()))
