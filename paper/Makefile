# Build the IEEE paper.
#
# The paper is not written yet. This Makefile exists so that `make paper` from
# the repository root fails with an explanation rather than
# "make: *** paper: No such file or directory", which tells the reader nothing.

MAIN := aegis

.PHONY: all
all:
ifeq ($(wildcard $(MAIN).tex),)
	@echo
	@echo "The paper has not been written yet."
	@echo
	@echo "  Intended contribution and the rules it must follow: paper/README.md"
	@echo "  Current project state:                              docs/STATE.md"
	@echo
	@exit 1
else
	latexmk -pdf -interaction=nonstopmode -halt-on-error $(MAIN).tex
endif

.PHONY: clean
clean:
	@latexmk -C 2>/dev/null || true
	@rm -f *.aux *.bbl *.blg *.log *.out *.synctex.gz
