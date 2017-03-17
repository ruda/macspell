### About ###

MacSpell is a spell checker designed on Cocoa's spell-checking facilities.

Features:
* Pure command line utility
* Interactive spelling checker capability
* Can act as Ispell replacement (ispell -a)
* All dictionaries included, it uses the dictionaries provided by macOS

### Installation ###

The quick and easy way to install is:

    curl -RO https://raw.githubusercontent.com/ruda/macspell/2017/macspell.py
    chmod +x macspell.py

Another alternative is to install with Python's `easy_install` or `pip` tool:

    sudo easy_install macspell
    sudo pip install macspell

The utility will be found at `/usr/local/bin/macspell.py`.

### Usage ###

List all possible misspelled words from file README.

    macspell.py --list < README

Interactively check spelling of file README.

    macspell.py --check README

Learning new words.

    macspell.py --learn
    Rudá
    Sumé
    foobar
    ^D

Forgetting learned words:

    macspell.py --unlearn
    Rudá
    Sumé
    foobar
    ^D

### MacSpell and Emacs ###

On Emacs, you can run the spell checker with `M-x ispell-buffer`. Also, you can change to any dictionary, like “Brazilian Portuguese”, with `M-x ispell-change-dictionary RET brasileiro RET`.

To use MacSpell in Emacs, just include the following lines in your Emacs initialization file:

    ;; MacSpell
    (setq ispell-program-name "/path/to/macspell.py"
          ispell-extra-args '("--encoding=latin1" "--auto-lang=no")
          ispell-dictionary "english")

Why the options above?
* `--encoding=latin1` Emacs expects latin1 (iso8859-1) ending when running ispell.
* `--auto-lang=no` Do not use automatic language selection.

### MacSpell and Nano ###

Put in your `.nanorc` the following line:

    set speller "/path/to/macspell.py -x -c"

Use `Control+t` to start the spell checker. It will run MacSpell in interactive mode and after that, return to the editor.

### Manual ###
<pre>
Usage: macspell.py [options] [command]

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
</pre>
