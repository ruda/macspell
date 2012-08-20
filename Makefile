PREFIX=/usr/local
BINDIR=$(PREFIX)/bin

install:
	install -m 775 -d $(DESTDIR)/$(BINDIR)
	install -m 775 macspell.py $(DESTDIR)/$(BINDIR)/macspell

uninstall:
	rm -f $(BINDIR)/macspell

clean:
	rm -f *~ *.pyc
