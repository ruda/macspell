#!/usr/bin/python -u
# -*- coding: utf-8 -*-
#
# Spell checker designed on Cocoa's spell-checking facilities.
#
# Copyright (c) 2012-2017 Rudá Moura
# Licensed under the terms of BSD license
#

from __future__ import print_function
import os
import sys
import getopt
import logging
import shutil
import tempfile

MACSPELL = '@(#) International Ispell Version 3.1.20 (but really MacSpell 2017)'

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
# FIXME: czech, esperanto, esperanto-tex, norsk, norsk7-tex, polish,
# slovak, slovenian, svenska

Config = {
    'LOG_LEVEL': logging.INFO,
    'LOG_FILENAME': os.environ['HOME'] + '/Library/Logs/macspell.log',
    'TERSE_MODE': False,
    'AUTO_LANG': None,
    'LANG': 'en',
    'ENCODING': 'utf-8',
    'TERMINAL_ENCODING': sys.stdin.encoding,
}

if 'DEBUG' in os.environ:
    Config['LOG_LEVEL'] = logging.DEBUG

logging.basicConfig(filename=Config['LOG_FILENAME'],
                    level=Config['LOG_LEVEL'])
logger = logging.getLogger('MacSpell')

try:
    # Python 2
    input = raw_input
except NameError:
    pass


def get_line(stream=None):
    if stream is None:
        try:
            # Python 3
            stream = sys.stdin.buffer
        except AttributeError:
            stream = sys.stdin
    line = stream.readline().decode(Config['ENCODING'])
    logger.debug('Got line: %s', line)
    return line


def put_line(line, stream=None):
    if stream is None:
        try:
            # Python 3
            stream = sys.stdout.buffer
        except AttributeError:
            stream = sys.stdout
    logger.debug('Put line: %s', line)
    stream.write(line.encode(Config['ENCODING']))


def get_checker():
    from Cocoa import NSSpellChecker
    checker = NSSpellChecker.sharedSpellChecker()
    logger.debug('Got checker: %s', str(checker))
    return checker


def check_spelling(checker, string, start=0):
    from Cocoa import NSString
    _string = NSString.stringWithString_(string)
    _range, _count = checker.checkSpellingOfString_startingAt_language_wrap_inSpellDocumentWithTag_wordCount_(
        _string, start, None, False, 0, None)
    logger.debug('Check spelling: %s range: %s count: %d',
                 string, _range, _count)
    if _range.length == 0:
        return True, _count, None, None
    else:
        word = string[_range.location:_range.location + _range.length]
        logger.info('Misspelled word: %s', word)
        return False, _count, _range, word


def guesses(checker, string, _range):
    from Cocoa import NSString, NSRange
    _string = NSString.stringWithString_(string)
    _words = checker.guessesForWordRange_inString_language_inSpellDocumentWithTag_(
        _range, _string, None, 0)
    n = len(_words)
    words = u', '.join(_words)
    logger.info('Guesses: %s', words)
    return n, words


def dict2lang(dictionary):
    if dictionary in DICTIONARY_LIST:
        Config['LANG'] = DICTIONARY_LIST[dictionary]
    else:
        logger.debug('Invalid dictionary: %s', dictionary)
        print('Invalid dictionary ' + dictionary)
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
        print('Invalid language', language)
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
    checker.ignoreWord_inSpellDocumentWithTag_(_word, 0)


def remove_word(checker, word):
    from Cocoa import NSString
    _word = NSString.stringWithString_(word)
    if checker.hasLearnedWord_(_word):
        logger.info('Unlearning word: %s', word)
        checker.unlearnWord_(_word)


def check_mode(checker, original, temporary):
    logger.debug('Entered into Check Mode')
    while True:
        line = get_line(original)
        if not line:
            return True
        last = 0
        while True:
            ok, count, _range, word = check_spelling(checker, line, last)
            if ok:
                put_line(line[last:], temporary)
                break
            else:
                put_line(line[last:_range.location], temporary)
                last = _range.location + _range.length
                sys.stdout.write(line)
                print(' ' * _range.location + '^' * _range.length)
                print('Misspelled word:', word)
                n, words = guesses(checker, line, _range)
                words = words.split(', ')
                for i in range(n):
                    print('Action %d: Replace with word %s' % (i, words[i]))
                print('Action r: Replace with another word')
                print('Action l: Learn this word')
                print('Action i: Ignore this word')
                print('Action s: Skip to next word')
                print('Action x: Exit from MacSpell')
                while True:
                    new_word = None
                    try:
                        action = input('? ')
                    except KeyboardInterrupt:
                        return False
                    if not action:
                        continue
                    if action[0] in ('x', 'X', 'q', 'Q'):
                        return False
                    elif action[0] in ('r', 'R'):
                        try:
                            new_word = input('Replace with word? ').strip()
                            try:
                                # Python 2
                                new_word = unicode(
                                    new_word, Config['TERMINAL_ENCODING'])
                            except NameError:
                                pass
                        except KeyboardInterrupt:
                            print('Please, redo your action!')
                            continue
                        else:
                            break
                    elif action[0] in ('i', 'I'):
                        ignore_word(checker, word)
                        break
                    elif action[0] in ('l', 'L'):
                        add_word(checker, word)
                        break
                    elif action[0] in ('s', 'S', 'n', 'N'):
                        break
                    elif action[0] in "0123456789":
                        try:
                            i = int(action)
                        except ValueError:
                            print('Not a number!')
                            continue
                        else:
                            if i < n:
                                new_word = words[i]
                                print('Replacing with word %s' % new_word)
                                break
                            else:
                                print('Invalid number!')
                                continue
                    else:
                        print('Invalid action!')
                        continue
                if new_word:
                    put_line(new_word, temporary)
                else:
                    put_line(word, temporary)


def list_mode(checker):
    logger.debug('Entered into List Mode')
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
        print(word)


def pipe_mode(checker):
    logger.debug('Entered into Pipe Mode')
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
                        sys.stdout.write('*\n')
                break
            else:
                last = _range.location + _range.length
                n, words = guesses(checker, line, _range)
                if Config['TERSE_MODE'] == False:
                    for x in range(count - 1):
                        sys.stdout.write('*\n')
                try:
                    stdout = sys.stdout.buffer
                except AttributeError:
                    stdout = sys.stdout
                if n == 0:
                    stdout.write(b'# ' + word.encode(Config['ENCODING']) + b' '
                                 + str(_range.location).encode() + b'\n')
                else:
                    stdout.write(
                        b'& ' + word.encode(Config['ENCODING']) + b' %d %d:'
                        % (n, _range.location) + b' '
                        + words.encode(Config['ENCODING']) + b'\n')
        sys.stdout.write('\n')


def learn_mode(checker):
    logger.debug('Entered into Learn Mode')
    while True:
        line = get_line()
        if not line:
            break
        add_word(checker, line.strip())


def unlearn_mode(checker):
    logger.debug('Entered into Unlearn Mode')
    while True:
        line = get_line()
        if not line:
            break
        remove_word(checker, line.strip())


def usage(prog_name):
    print('''Usage: %s [options] [command]

Where [command] is one of:
  -h|--help		display this help
  -v|--version		display version
  -c|--check=<file>	check mode, spell check file and write to file
  -l|--list		list mode, "ispell -l" compatibility mode
  -a|--pipe		pipe mode, "ispell -a" compatibility mode
  --learn		learn mode, learn new words from pipe
  --unlearn		unlearn mode, forget words from pipe
  --list-dict		list all dictionaries available
  --list-lang		list all languages available
  --list-user-lang	list user preferred languages

and [options] is any of the following:
  -x|--dont-back	do not create backup file (see option --check)
  -d|--dict=|--master=<dict>	name of the dictionary to use
			(english, american, brasileiro, etc.)
  --lang=<code>		name of the language to use (en, en_US, pt_BR, etc.)
  --encoding=<enc>	text encoding to use (utf-8, latin1, etc.)
  --auto-lang=[yes|no]	automatically identify languages
''' % prog_name)


def main(argv=None):
    if argv == None:
        argv = sys.argv
    logger.debug('MacSpell started with arguments: %s', ', '.join(argv[1:]))
    if 'LANG' in os.environ:
        lang = os.environ['LANG']
        if '.' in lang:
            lang, enc = lang.split('.')
            Config['ENCODING'] = enc.lower()
        Config['LANG'] = lang
    if 'DICTIONARY' in os.environ:
        dict = os.environ['DICTIONARY']
        dict2lang(dict)
    try:
        opts, args = getopt.getopt(argv[1:],
                                   'vhalmBCd:Dc:x',
                                   ('version', 'help', 'check=', 'dont-backup', 'pipe', 'list', 'master=', 'dict=', 'lang=', 'encoding=', 'list-dict', 'list-lang', 'list-user-lang', 'auto-lang=', 'learn', 'unlearn'))
    except getopt.error as msg:
        print(msg[0], file=sys.stderr)
        return 2
    backup = True
    enter_check = enter_list = enter_pipe = enter_learn = enter_unlearn = False
    for opt, arg in opts:
        if opt == '-v' or opt == '--version':
            print(MACSPELL)
            return 0
        if opt == '-h' or opt == '--help':
            usage(sys.argv[0])
            return 0
        if opt == '-c' or opt == '--check':
            enter_check = True
            filename = arg
        if opt == '-x' or opt == '--dont-backup':
            backup = False
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
                print(d)
        if opt == '--list-user-lang':
            checker = get_checker()
            dicts = checker.userPreferredLanguages()
            for d in dicts:
                print(d)
        if opt == '--list-dict':
            dicts = list(DICTIONARY_LIST.keys())
            dicts.sort()
            for d in dicts:
                print('%s (%s)' % (d, DICTIONARY_LIST[d]))
            return 0
        if opt == '--encoding':
            logger.debug('Set encoding to: %s', arg)
            Config['ENCODING'] = arg

    if enter_check or enter_list or enter_pipe or enter_learn or enter_unlearn:
        checker = get_checker()
        set_language(checker, Config['LANG'])
        logger.debug('Current language: %s', checker.language())
        logger.debug('Current encoding: %s', Config['ENCODING'])

    if enter_check:
        if backup:
            shutil.copy2(filename, filename + ".bak")
        fd, tmpfile = tempfile.mkstemp(prefix='macspell')
        logger.debug('Temporary file: %s', tmpfile)
        os.close(fd)
        with open(tmpfile, 'wb') as tmpobj:
            with open(filename, 'rb') as fileobj:
                status = check_mode(checker, fileobj, tmpobj)
        if 'DEBUG' not in os.environ and status is True:
            shutil.move(tmpfile, filename)
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
