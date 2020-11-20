#######################################
# filename: define.py
# author: Shaun Rasmusen
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
def define_it(word, lang="russian"):
    try:
        import requests
    except Exception:
        print('Cannot use this function without \'requests\' installed.')
        print('Run \'python -m pip install requests\' and try again.')
        sys.exit(2)

    try:
        import pycountry
    except Exception:
        print('Cannot use this function without \'pycountry\' installed.')
        print('Run \'python -m pip install pycountry\' and try again.')
        sys.exit(2)

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

###############################################################################
# processDefine preprocesses the input to be handled by define_it. It also does
# some pretty printing around the definition.
#
def processDefine(word, lang = "russian"):
    print("Trying to define '%s'\n" % word)
    definition = define_it(word, lang)
    if len(definition) > 0:
        print(definition)
    else:
        print('Found no definition.')

    print("\nSee 'https://en.wiktionary.org/wiki/%s' for more details" % (word))