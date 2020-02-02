MacSpell is a spell checker designed on Cocoa's spell-checking facilities.

## Features

 * Pure command line utility
 * Interactive spelling checker capability
 * Can act as Ispell replacement (ispell -a)
 * All dictionaries included, it uses the dictionaries provided by macOS.

## Installation
```
$ pip install macspell
```

## Usage
```
$ macspell --check README.txt
$ macspell --encoding=latin1 --check LEIAME.txt
```

## Emacs
```elisp
;; MacSpell
(setq ispell-program-name "macspell")
(setq ispell-extra-args '("--encoding=latin1" "--auto-lang=no"))
;(setq ispell-dictionary "english")
```

## Nano
```
set speller "macspell -x -c"
```
