#######################################
# filename: wiki.py
# author: Shaun Rasmusen
# 

import getopt
import sys

import define as d
import pronounce as p

optstring = "w:l:s:dph"
longopts = ["word=", "language=", "sentence=", "define", "pronounce", "help"]

###############################################################################
# usage prints usage information about the script and exists with a return code.
#
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

if __name__ == "__main__":
    word = ''
    lang = 'russian'
    doSentence = False
    pronounce = False
    define = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], optstring, longopts)
    except getopt.GetoptError:
        usage()

    # The last of `-w` and `-s` will be acted on.
    # One of `-p` or `-d` is required.
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-w', '--word'):
            doSentence = False
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
        p.processPronounce(word, lang, doSentence)
    elif define:
        d.processDefine(word, lang)
    else:
        usage()