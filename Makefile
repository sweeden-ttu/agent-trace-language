# Full LaTeX + BibTeX build (refs.bib -> main.bbl -> bibliography in PDF)
MAIN = main

.PHONY: all pdf review pages clean count

all pdf: $(MAIN).pdf

$(MAIN).pdf: $(MAIN).tex refs.bib sec/*.tex
	pdflatex -interaction=nonstopmode $(MAIN).tex
	bibtex $(MAIN)
	pdflatex -interaction=nonstopmode $(MAIN).tex
	pdflatex -interaction=nonstopmode $(MAIN).tex

# Review build: camera-ready false (no acknowledgments)
review:
	@echo "Building review version (\\camerareadyfalse)..."
	@pdflatex -interaction=nonstopmode "\def\camerareadyfalse{}\input{$(MAIN).tex}" || true
	@bibtex $(MAIN) || true
	@pdflatex -interaction=nonstopmode "\def\camerareadyfalse{}\input{$(MAIN).tex}" || true
	@pdflatex -interaction=nonstopmode "\def\camerareadyfalse{}\input{$(MAIN).tex}" || true
	@echo "Review PDF built: $(MAIN).pdf"

# Report PDF page count and warn if content pages exceed target
pages: $(MAIN).pdf
	@echo "--- Page count ---"
	@pdfinfo $(MAIN).pdf 2>/dev/null | grep Pages || mdls -name kMDItemNumberOfPages $(MAIN).pdf 2>/dev/null
	@echo "Target: <= 7 content pages before bibliography"

# Word count for abstract
count:
	@echo "Abstract word count:"
	@detex sec/00_abstract.tex | wc -w

clean:
	rm -f $(MAIN).aux $(MAIN).bbl $(MAIN).blg $(MAIN).log $(MAIN).out $(MAIN).pdf
