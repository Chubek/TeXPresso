MULL ?= mull
ENGINE ?= cpp
MULL_ENGINES ?= cpp,d
TEX ?= tex
TEXPRESSO := bin/texpresso
.PHONY: example modules test check clean
example:
	MULL=$(MULL) $(TEXPRESSO) --engine=$(ENGINE) examples/hello.txp -o examples/hello.tex --run --tex-engine=$(TEX)
modules:
	MULL=$(MULL) $(TEXPRESSO) --engine=$(ENGINE) examples/modules/math.txp examples/modules/app.txp -o examples/modules/app.tex --run --tex-engine=$(TEX)
check:
	MULL=$(MULL) $(TEXPRESSO) --engine=$(ENGINE) --check-mull examples/hello.txp

test:
	MULL=$(MULL) MULL_ENGINES=$(MULL_ENGINES) python3 -m unittest discover -s tests -p 'test_*.py' -v
clean:
	find examples -name '*.tex' -delete
	find examples -name '*.log' -delete
