import sys
import logging

from collections import OrderedDict

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser import customization as bib_custom


CONVERT_TO_UNICODE = True


def collection_from_bibtex_str(bib_str, **kwargs):
    """
    Transform a Bibtex string (e.g. from a .bib-file) to a BibJSON collection.
    :param bib_str: input bibtex string
    :param kwargs: metadata for the BibJSON collection. "collection" parameter must be set.
    :return BibJSON collection dictionary
    """
    bib_parser = BibTexParser()
    bib_parser.ignore_nonstandard_types = False     # this is flipped. this seems to be an error in the library
    bib_parser.customization = _parse_bib_entry

    bib_obj = bibtexparser.loads(bib_str, parser=bib_parser)

    return collection_from_dict(bib_obj.entries_dict, **kwargs)


def collection_from_dict(entries, **kwargs):
    """
    Create collection from a dictionary of bibtex entries from bibtexparser.
    :param entries: bibtex entries from bibtexparser.
    :param kwargs: metadata for the BibJSON collection. "collection" parameter must be set.
    :return BibJSON collection dictionary
    """
    c = OrderedDict()
    c['metadata'] = OrderedDict()
    c['records'] = []

    # set metadata from kwargs
    assert 'collection' in kwargs
    for k, v in kwargs.items():
        if k != 'ignore_exceptions':
            c['metadata'][k] = v

    # set records
    for key, entry in entries.items():
        c['records'].append(record_from_entry(key, entry, kwargs['collection']))

    c['metadata']['records'] = len(c['records'])

    return c


def record_from_entry(key, entry, collection):
    """
    Create a single BibJSON record from a BibTeX entry dictionary.
    :param key: entry key (citekey)
    :param entry: BibTeX entry dictionary
    :param collection: collection name
    :return BibJSON record
    """
    # create new record
    r = OrderedDict()
    r['type'] = entry['ENTRYTYPE']
    r['id'] = key
    r['citekey'] = key
    r['collection'] = collection

    # call fill_record_<type> to convert entry of specific type to BibJSON dict
    fill_func = 'fill_record_%s' % r['type']
    call_fn = getattr(sys.modules[__name__], fill_func, None)
    if call_fn:
        call_fn(r, entry)
    else:
        logging.error("entry '%s': no conversion function for record type '%s'" % (key, r['type']))

    return r


def fill_record_article(r, entry):
    """
    handle 'article' type
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    _require_keys_in_entry(entry, ('title', 'year', 'author', 'journal'), req_all=True)

    _simple_fill(r, entry, ('title', 'year', 'note', 'key'))

    _fill_author(r, entry)
    _fill_journal(r, entry)


def fill_record_book(r, entry):
    """
    handle 'book' type
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    _require_keys_in_entry(entry, ('title', 'year', 'publisher'), req_all=True)
    _require_keys_in_entry(entry, ('author', 'editor'), req_all=False)

    _simple_fill(r, entry, ('title', 'year', 'note', 'key', 'volume', 'number', 'series', 'edition', 'month'))

    _fill_author(r, entry)
    _fill_editor(r, entry)
    _fill_publisher(r, entry)


def fill_record_booklet(r, entry):
    """
    handle 'booklet' type
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    _require_keys_in_entry(entry, ('title', ), req_all=True)
    _simple_fill(r, entry, ('title', 'howpublished', 'address', 'month', 'year', 'note', 'key'))

    _fill_author(r, entry)


def fill_record_conference(r, entry):
    """
    handle 'conference' type
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    fill_record_inproceedings(r, entry)


def fill_record_electronic(r, entry):
    """
    handle 'electronic' type
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    _require_keys_in_entry(entry, ('author', 'title', 'howpublished'), req_all=True)

    _simple_fill(r, entry, ('title', 'howpublished', 'month', 'year', 'note', 'key'))

    _fill_author(r, entry)


def fill_record_inbook(r, entry):
    """
    handle 'inbook' type
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    _require_keys_in_entry(entry, ('author', 'editor'), req_all=False)
    _require_keys_in_entry(entry, ('title', 'year', 'publisher'), req_all=True)

    _simple_fill(r, entry, ('title', 'year', 'note', 'key', 'volume', 'number', 'series', 'edition', 'month'))

    _simple_fill_one_of(r, entry, ('chapter', 'pages'))

    _fill_author(r, entry)
    _fill_editor(r, entry)
    _fill_publisher(r, entry)


def fill_record_incollection(r, entry):
    """
    handle 'incollection' type
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    _require_keys_in_entry(entry, ('author', 'publisher', 'title', 'year', 'booktitle'), req_all=True)

    _simple_fill(r, entry, ('title', 'year', 'booktitle', 'note', 'key', 'volume', 'number', 'series', 'chapter',
                 'pages', 'address', 'edition', 'month'))

    _fill_author(r, entry)
    _fill_publisher(r, entry)
    _fill_editor(r, entry)


def fill_record_inproceedings(r, entry):
    """
    handle 'inproceedings' type
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    _require_keys_in_entry(entry, ('author', 'title', 'year', 'booktitle'), req_all=True)

    _simple_fill(r, entry, ('title', 'year', 'booktitle', 'note', 'key', 'volume', 'number', 'series', 'organization',
                 'pages', 'address', 'edition', 'month'))

    _fill_author(r, entry)
    _fill_editor(r, entry)
    _fill_publisher(r, entry)


def fill_record_manual(r, entry):
    """
    handle 'manual' type
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    _require_keys_in_entry(entry, ('author', 'title'), req_all=True)
    _simple_fill(r, entry, ('title', 'address', 'organization', 'edition', 'month', 'year', 'note', 'key'))

    _fill_author(r, entry)


def fill_record_mastersthesis(r, entry):
    """
    handle 'mastersthesis' type
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    fill_record_phdthesis(r, entry)


def fill_record_misc(r, entry):
    """
    handle 'misc' type
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    _simple_fill(r, entry, ('title', 'howpublished', 'month', 'year', 'note', 'key'))

    _fill_author(r, entry)


def fill_record_periodical(r, entry):
    """
    handle 'periodical' type
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    _require_keys_in_entry(entry, ('title', 'year', 'number'), req_all=True)

    _simple_fill(r, entry, ('title', 'year', 'number', 'organization', 'note', 'key'))

    _fill_author(r, entry)
    _fill_publisher(r, entry)
    _fill_journal(r, entry)


def fill_record_phdthesis(r, entry):
    """
    handle 'phdthesis' type
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    _require_keys_in_entry(entry, ('author', 'title', 'school', 'year'), req_all=True)

    _simple_fill(r, entry, ('title', 'school', 'year', 'address', 'month', 'note', 'key'))

    _fill_author(r, entry)


def fill_record_proceedings(r, entry):
    """
    handle 'proceedings' type
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    _require_keys_in_entry(entry, ('title', 'year'), req_all=True)
    _simple_fill(r, entry, ('title', 'year', 'volume', 'number', 'series', 'address', 'month', 'organization',
                 'note', 'key'))

    _fill_editor(r, entry)
    _fill_publisher(r, entry)


def fill_record_techreport(r, entry):
    """
    handle 'techreport' type
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    _require_keys_in_entry(entry, ('author', 'title', 'institution', 'year'), req_all=True)

    _simple_fill(r, entry, ('title', 'institution', 'year', 'number', 'address', 'month', 'note', 'key'))

    _fill_author(r, entry)
    _fill_editor(r, entry)


def fill_record_unpublished(r, entry):
    """
    handle 'unpublished' type
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    _require_keys_in_entry(entry, ('author', 'title', 'note'), req_all=True)

    _simple_fill(r, entry, ('title', 'note' 'month', 'year', 'key'))

    _fill_author(r, entry)


def _simple_fill(r, entry, keys):
    """
    For each key in keys that exists in <entry>, assign its data to the record <r>
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :param keys: data keys to use
    :return None
    """
    for k in keys:
        if k in entry:
            r[k] = entry[k]


def _simple_fill_one_of(r, entry, keys):
    """
    Do _simple_fill but require that at least one of the keys in <keys> exists in entry.
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :param keys: data keys to use
    :return None
    """
    _require_keys_in_entry(entry, keys, req_all=False)

    for k in keys:
        if k in entry:
            r[k] = entry[k]


def _fill_author(r, entry):
    """
    Make a "named entry" dict with an author field
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    if 'author' not in entry:
        return

    _fill_named_entry(r, entry, 'author')


def _fill_editor(r, entry):
    """
    Make a "named entry" dict with an editor field
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    if 'editor' not in entry:
        return

    _fill_named_entry(r, entry, 'editor')


def _fill_publisher(r, entry):
    """
    Make a "named entry" dict with a publisher field
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    if 'publisher' not in entry:
        return

    r['publisher'] = {
        'name': entry['publisher']
    }

    if 'address' in entry:
        r['publisher']['address'] = entry['address']


def _fill_named_entry(r, entry, k):
    """
    Make a "named entry" dict with the name from the field with key <k>
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :param k: field to use for the name
    :return None
    """
    r[k] = [{'name': n} for n in entry[k]]


def _fill_journal(r, entry):
    """
    Make a "journal" dict
    :param r: BibJSON record dict that will be filled
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :return None
    """
    if 'journal' not in entry or 'volume' not in entry:
        return

    # fill with required fields
    r['journal'] = {
        'name': entry['journal'],
        'volume': entry['volume']
    }

    # fill optional fields
    opt_keys = ('number', 'pages', 'month')
    for k in opt_keys:
        if k in entry:
            r['journal'][k] = entry[k]


def _require_keys_in_entry(entry, keys, req_all):
    """
    Require at least one or all keys in <keys> to be found in <entry>. If not, call logging.error().
    :param entry: bibtexparser entry that will be used to fill the BibJSON record
    :param keys: keys to check
    :param req_all: True: require all keys to be in <entry>, False: require at least one key to be in <entry>
    :return None
    """
    keys_in_entry = [k in entry for k in keys]
    if (req_all and not all(keys_in_entry)) or (not req_all and not any(keys_in_entry)):
        logging.error("entry '%s': %s of the required keys '%s' not found in record"
                      % (entry.get('ID'), 'All' if not req_all else 'At least one', ', '.join(keys)))


def _parse_bib_entry(entry):
    """
    Customization function for bibtexparser.
    :param entry: bibtex record to modify
    :return bibtex record
    """
    if CONVERT_TO_UNICODE:
        entry = bib_custom.convert_to_unicode(entry)

    entry = bib_custom.author(entry)
    entry = bib_custom.editor(entry)
    entry = bib_custom.keyword(entry)
    entry = bib_custom.page_double_hyphen(entry)

    return entry
