# -*- coding: utf-8 -*-

import sys
import platform

import CONFIG


def ConvertExtsStringToSortedList(cat: str):
    cat = cat.strip()
    category_exts = [ext.lower() for ext in cat.split()] # some spaces is equal to one
    category_exts = list(set(category_exts)) # removing duplicates without saving order
    # Sorting is needed in aim to recognize ".tar.gz" before ".gz"
    category_exts = [ext[::-1] for ext in category_exts] # reverse extension symbols order
    category_exts.sort(reverse = True)
    category_exts = [ext[::-1] for ext in category_exts] # restore symbols order
    return category_exts


def LoadDefaultCategories():
    """ Converting CONFIG.CATEGORIES to useful inner representation"""
    global categories
    for cat in CONFIG.CATEGORIES:
        ix = cat.find('.')
        if ix < 0:
            continue
        category_name = cat[:ix]
        category_name = category_name.strip()
        cat = cat[ix:]
        categories[category_name] = ConvertExtsStringToSortedList(cat)


def LoadDefaultFilenameTranslationTable():
    """Converting CONFIG.FILENAME_TRANSLATION_TABLE to useful inner representation"""
    global filename_translation_table
    for pair in CONFIG.FILENAME_TRANSLATION_TABLE.split(','):
        (key, val) = (pair[:1], pair[1:])
        filename_translation_table[ord(key)] = val
        filename_translation_table[ord(key.upper())] = val.upper()

def init():

    # gettext defines this value
    global _
    _ = lambda _: _ # by default i18n is absent

    global filename_translation_table
    filename_translation_table = {}
    LoadDefaultFilenameTranslationTable()

    global categories
    categories = {}
    LoadDefaultCategories()

    # Option '-d' value
    global option_base_dir
    option_base_dir = ""

    # Command line <INSPECTED_DIR> value
    global option_inspected_dir
    option_inspected_dir = ""

    # Option '-G' value
    global option_no_gui
    option_no_gui = False

    # Option '-l' value
    global option_make_links
    option_make_links = False

    global is_win
    is_win = False
    if platform.system().lower().find("windows") != -1:
        is_win = True
