DESTDIR?=/
PREFIX=/usr/local
BINDIR=$(PREFIX)/bin
PYTHON=python
PYTHON_SITE_PACKAGES=$(shell python -c 'from distutils.sysconfig import get_python_lib; print(get_python_lib())')

build:
	$(PYTHON) setup.py bdist_wheel

install:
	$(PYTHON) setup.py install \
		--root=$(DESTDIR) \
		--prefix=$(PREFIX) \
		--install-lib=$(PYTHON_SITE_PACKAGES)

uninstall:
	rm -f $(BINDIR)/macspell

clean:
	rm -f *~ *.pyc
	$(PYTHON) setup.py clean
	rm -rf build dist *.egg-info
