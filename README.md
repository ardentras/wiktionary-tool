# Wiktionary Tool

(c) 2020 Shaun Rasmusen

---

## Description

A tool for retreiving data from Wiktionary via its API in a simplified,
or more specific format.

---

## How to Run

```text
Usage: ./wiki.py -[pdh][w word][s sentence][l language]

Arguments
    -d/--define     get definition
    -h/--help       print this dialogue
    -l/--language   the language. defaults to russian
    -p/--pronounce  get pronunciation
    -s/--sentence   a sentence to pronounce, wrapped in quotes
    -w/--word       the word to look up
```

One of `-d/--define` or `-p/--pronounce` is required along with a `-w/--word`.

`--define` will return all definition and examples for the desired language.

`--pronounce` will return all IPA available from the API for the provided `--word`.
If given a `--sentence`, it will attempt to get the first IPA for each word and
print it. If no pronunciation is found, then it will output `[!!!]`.

`--language` allows you to specify the language to pick. This tool is defaulted to
Russian, but it will attempt to process any language provided. Note that not all
languages available in Wiktionary can be successfully queried by this tool, in
particular those categorized under `Other` by Wiktionary.