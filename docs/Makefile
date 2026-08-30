# Makefile for the plopm Sphinx documentation.

SPHINXOPTS  ?=
SPHINXBUILD ?= sphinx-build
SOURCEDIR    = text
BUILDDIR     = _build
APIDIR       = text/api

.PHONY: help clean api html linkcheck docs

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	rm -rf "$(BUILDDIR)"

api:
	@mkdir -p "$(APIDIR)"
	sphinx-apidoc -e -f -o "$(APIDIR)" ../src/plopm

html: api
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

linkcheck:
	@$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Preserve the repository's current publishing workflow when needed.
docs: html
	cp -a "$(BUILDDIR)/html/." .
