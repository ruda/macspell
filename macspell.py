#!/usr/bin/python -u
# -*- coding: utf-8 -*-
#
# Spell checker designed on Cocoa's spell-checking facilities.
#
# Copyright (c) 2012, 2015 Rudá Moura
# Licensed under the terms of BSD license
#

import os, sys, getopt, logging

MACSPELL='@(#) International Ispell Version 3.1.20 (but really MacSpell 2015)'

DICTIONARY_LIST = {
    'american': 'en',
    'brasileiro': 'pt_BR',
    'british': 'en_GB',
    'castellano': 'es', 'castellano8': 'es',
    'dansk': 'da',
    'default': 'en',
    'deutsch': 'de', 'deutsch8': 'de',
    'english': 'en',
    'francais': 'fr', 'francais-tex': 'fr', 'francais7': 'fr',
    'german': 'de', 'german8': 'de',
    'italiano': 'it',
    'nederlands': 'nl', 'nederlands8': 'nl',
    'portugues': 'pt',
    'russian': 'ru', 'russianw': 'ru',
    'svenska': 'sv',
}
# FIXME: czech, esperanto, esperanto-tex, norsk, norsk7-tex, polish, slovak, slovenian, svenska

Config = {
    'LOG_LEVEL': logging.INFO,
    'LOG_FILENAME': os.environ['HOME'] + '/Library/Logs/macspell.log',
    'TERSE_MODE': False,
    'AUTO_LANG': None,
    'LANG': 'en',
    'ENCODING': 'utf-8',
}

if os.environ.has_key('DEBUG'):
    Config['LOG_LEVEL'] = logging.DEBUG

logging.basicConfig(filename=Config['LOG_FILENAME'],
                    level=Config['LOG_LEVEL'])
logger = logging.getLogger('MacSpell')

def get_line():
    line = sys.stdin.readline()
    logger.debug('Got line: %s', line)
    return unicode(line, Config['ENCODING'])

def get_checker():
    from Cocoa import NSSpellChecker
    checker = NSSpellChecker.sharedSpellChecker()
    logger.debug('Got checker: %s', str(checker))
    return checker

def check_spelling(checker, string, start=0):
    from Cocoa import NSString
    _string = NSString.stringWithString_(string)
    _range, _count = checker.checkSpellingOfString_startingAt_language_wrap_inSpellDocumentWithTag_wordCount_(_string, start, None, False, 0, None)
    logger.debug('Check spelling: %s range: %s count: %d', string.encode('utf-8'), _range, _count)
    if _range.length == 0:
        return True, _count, None, None
    else:
        word = string[_range.location:_range.location+_range.length]
        logger.info('Misspelled word: %s', word.encode('utf-8'))
        return False, _count, _range, word

def guesses(checker, string, _range):
    from Cocoa import NSString, NSRange
    _string = NSString.stringWithString_(string)
    _words = checker.guessesForWordRange_inString_language_inSpellDocumentWithTag_(_range, _string, None, 0)
    n = len(_words)
    words = u', '.join(_words)
    logger.info('Guesses: %s', words)
    return n, words

def dict2lang(dictionary):
    if DICTIONARY_LIST.has_key(dictionary):
        Config['LANG'] = DICTIONARY_LIST[dictionary]
    else:
        logger.debug('Invalid dictionary: %s', dictionary)
        print 'Invalid dictionary ' + dictionary
        sys.exit(1)

def set_language(checker, language):
    if Config['AUTO_LANG'] == None:
        Config['AUTO_LANG'] = checker.automaticallyIdentifiesLanguages()
    checker.setAutomaticallyIdentifiesLanguages_(Config['AUTO_LANG'])
    res = checker.setLanguage_(language)
    if res:
        logger.info('Selected language: %s', language)
    else:
        logger.error('Invalid language: %s', language)
        print 'Invalid language', language
        sys.exit(1)

def add_word(checker, word):
    from Cocoa import NSString
    _word = NSString.stringWithString_(word)
    if not checker.hasLearnedWord_(_word):
        logger.info('Learning word: %s', word)
        checker.learnWord_(_word)

def ignore_word(checker, word):
    from Cocoa import NSString
    _word = NSString.stringWithString_(word)
    logger.info('Ignoring word: %s', word)
    checker.ignoreWord_inSpellDocumentWithTag_(word, 0)

def remove_word(checker, word):
    from Cocoa import NSString
    _word = NSString.stringWithString_(word)
    if checker.hasLearnedWord_(_word):
        logger.info('Unlearning word: %s', word)
        checker.unlearnWord_(_word)

def list_mode(checker):
    logger.debug('Entered into List Mode')
    logger.debug('Current language: %s', checker.language())
    logger.debug('Current encoding: %s', Config['ENCODING'])
    words = []
    while True:
        line = get_line()
        if not line:
            break
        last = 0
        while True:
            ok, count, _range, word = check_spelling(checker, line, last)
            if ok:
                break
            else:
                last = _range.location + _range.length
                words.append(word)
    for word in words:
        print word

def pipe_mode(checker):
    logger.debug('Entered into Pipe Mode')
    logger.debug('Current language: %s', checker.language())
    logger.debug('Current encoding: %s', Config['ENCODING'])
    sys.stdout.write(MACSPELL + '\n')
    while True:
        line = get_line()
        if not line:
            break
        if line[0] == '!':
            logger.debug('Enter terse mode')
            Config['TERSE_MODE'] = True
            continue
        if line[0] == '%':
            logger.debug('Exit terse mode')
            Config['TERSE_MODE'] = False
            continue
        if line[0] == '+':
            logger.debug('Enter Tex mode')
            continue
        if line[0] == '-':
            logger.debug('Exit TeX mode')
            continue
        if line[0] == '*':
            logger.debug('Add to personal dictionary')
            add_word(checker, line[1:].strip())
            continue
        if line[0] == '@':
            logger.debug('Accept word, but leave out of dictionary')
            ignore_word(checker, line[1:].strip())
            continue
        if line.startswith('~nroff'):
            continue
        if line.startswith('~list'):
            continue
        if line.startswith('~tex'):
            continue
        if line.startswith('~plaintex'):
            continue
        if line.startswith('~latin1'):
            Config['ENCODING'] = 'latin1'
            continue
        if line.startswith('~latin3'):
            Config['ENCODING'] = 'latin3'
            continue
        if line[0] == '^':
            logger.debug('Spell-check rest of line')
        last = 0
        while True:
            ok, count, _range, word = check_spelling(checker, line, last)
            if ok:
                if Config['TERSE_MODE'] == False:
                    for x in range(count):
                        sys.stdout.write( '*\n' )
                break
            else:
                last = _range.location + _range.length
                n, words = guesses(checker, line, _range)
                if Config['TERSE_MODE'] == False:
                    for x in range(count-1):
                        sys.stdout.write( '*\n' )
                if n == 0:
                    sys.stdout.write( '# ' + word.encode(Config['ENCODING']) + ' ' + str(_range.location) + '\n' )
                else:
                    sys.stdout.write( '& ' + word.encode(Config['ENCODING']) + ' %d %d:' % (n, _range.location) + ' ' + words.encode(Config['ENCODING']) + '\n' )
        sys.stdout.write( '\n' )

def learn_mode(checker):
    logger.debug('Entered into Learn Mode')
    logger.debug('Current language: %s', checker.language())
    logger.debug('Current encoding: %S', Config['ENCODING'])
    while True:
        line = get_line()
        if not line:
            break
        add_word(checker, line.strip())

def unlearn_mode(checker):
    logger.debug('Entered into Unlearn Mode')
    logger.debug('Current language: %s', checker.language())
    logger.debug('Current encoding: %s', Config['ENCODING'])
    while True:
        line = get_line()
        if not line:
            break
        remove_word(checker, line.strip())

def usage(prog_name):
    print '''Usage: %s [options] [command]
Where [command] is one of:
  -h|--help	display this help
  -v|--version	display version
  -l|--list	list mode, "ispell -l" compatibility mode
  -a|--pipe	pipe mode, "ispell -a" compatibility mode
  --learn	learn mode, learn new words from pipe
  --unlearn	unlearn mode, forget words from pipe
  --list-dict	list all dictionaries available
  --list-lang	list all languages available
and [options] is any of the following:
  -d|--dict=|--master=<dict>	name of the dictionary to use (english, american, brasileiro, etc.)
  --lang=<code>		name of the language to use (en, en_US, pt_BR, etc.)
  --encoding=<enc>	text encoding to use (utf-8, latin1, etc.)
  --auto-lang=[yes|no]	automatically identify languages
''' % prog_name

def main(argv=None):
    if argv == None:
        argv = sys.argv
    logger.debug('MacSpell started with arguments: %s', ', '.join(argv[1:]))
    if os.environ.has_key('LANG'):
        lang = os.environ['LANG']
        if '.' in lang:
            lang, enc = lang.split('.')
            Config['ENCODING'] = enc.lower()
        Config['LANG'] = lang
    if os.environ.has_key('DICTIONARY'):
        dict = os.environ['DICTIONARY']
        dict2lang(dict)
    try:
        opts, args = getopt.getopt(argv[1:],
                                   'vhalmBCd:D',
                                   ('version', 'help', 'pipe', 'list', 'master=', 'dict=', 'lang=', 'encoding=', 'list-dict', 'list-lang', 'auto-lang=', 'learn', 'unlearn'))
    except getopt.error, msg:
        print >> sys.stderr, msg[0]
        return 2
    enter_list = enter_pipe = enter_learn = enter_unlearn = False
    for opt, arg in opts:
        if opt == '-v' or opt == '--version':
            print MACSPELL
            return 0
        if opt  == '-h' or opt == '--help':
            usage(sys.argv[0])
            return 0
        if opt == '-l' or opt == '--list':
            enter_list = True
        if opt == '-a' or opt == '--pipe':
            enter_pipe = True
        if opt == '--learn':
            enter_learn = True
        if opt == '--unlearn':
            enter_unlearn = True
        if opt in ('-m', '-B', '-C'):
            pass
        if opt == '-d' or opt == '--dict' or opt == '--master':
            dict2lang(arg)
        if opt == '--lang':
            Config['LANG'] = arg
        if opt == '--auto-lang':
            if arg.lower() == 'yes':
                Config['AUTO_LANG'] = True
            elif arg.lower() == 'no':
                Config['AUTO_LANG'] = False
            else:
                Config['AUTO_LANG'] = None
        if opt == '--list-lang':
            checker = get_checker()
            dicts = checker.availableLanguages()
            for d in dicts:
                print d
        if opt == '--list-dict':
            dicts = DICTIONARY_LIST.keys()
            dicts.sort()
            for d in dicts:
                print '%s (%s)' % (d, DICTIONARY_LIST[d])
            return 0
        if opt == '--encoding':
            logger.debug('Set encoding to: %s', arg)
            Config['ENCODING'] = arg

    if enter_list or enter_pipe or enter_learn or enter_unlearn:
        checker = get_checker()
        set_language(checker, Config['LANG'])

    if enter_list:
        list_mode(checker)
    if enter_pipe:
        pipe_mode(checker)
    if enter_learn:
        learn_mode(checker)
    if enter_unlearn:
        unlearn_mode(checker)

    logger.debug('Goodbye from MacSpell!')
    return 0

if __name__ == '__main__':
    sys.exit(main())
