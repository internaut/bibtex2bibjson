# BibTeX2BibJSON - Convert BibTeX files to BibJSON

BibTeX2BibJSON is a Python script and set of functions to convert BibTeX files / BibTeX strings to BibJSON. It is based on the [BibtexParser](https://bibtexparser.readthedocs.org/) library.

## Usage

You can either use the `bibtex2bibjson.py` script directly or use the functions from `bibjson.py` in your existing code.

### `bibtex2bibjson.py` script

`bibtex2bibjson.py` will output the resulting BibJSON directly to _stdout_, while errors that might occur during conversion are printed to _stderr_. So in order to save the output to a file you need to call `./bibtex2bibjson.py MY_FILE.bib 1> MY_FILE.json`. This will save the BibJSON data to _MY_FILE.json_ and error messages will be printed to the console.

### `bibjson.py` functions

If you want to use the BibJSON functions in your existing code, you will probably need to import one of the following functions and use them according to what you want to do:

* `collection_from_bibtex_str(bib_str, **kwargs)` -- create a complete BibJSON collection from a BibTeX string (which came from a BibTeX file, for example). This uses [BibtexParser](https://bibtexparser.readthedocs.org/) to parse the BibTeX string. You will need to pass a _collection_ parameter which denotes the name of the BibJSON collection.
* `collection_from_dict(entries, **kwargs)` -- create a complete BibJSON collection from a BibtexParser-like dictionary. You will need to pass a _collection_ parameter which denotes the name of the BibJSON collection.
* `record_from_entry(key, entry, collection)` -- create a single BibJSON record from a single BibtexParser-like entry. Identify the record by _key_ (this will become the _id_ and _cite_key_).

### Conversion errors

The implementation follows the official [list of allowed entry types and fields](https://en.wikipedia.org/wiki/BibTeX#Entry_types) and prints errors via `logging.error()` if required fields are missing or entry types cannot be handled.

## Requirements

* it has only been tested on Python 3.4 but should work on lower Python versions down to 2.7 without (major) modifications
* [BibtexParser](https://bibtexparser.readthedocs.org/) must be installed (for example via `pip`)

## BibJSON

BibJSON is still a draft (as of Feb. 2016) and the final format is not yet defined. Hence I followed the examples from the following resources to for the structure of the BibJSON output:

* http://wiki.okfn.org/Projects/openbibliography/bibjson/common
* http://okfnlabs.org/bibjson/

## License

The source-code is provided under [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0) (see `LICENSE` file).
