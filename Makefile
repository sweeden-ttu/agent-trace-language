# Full LaTeX + BibTeX build (refs.bib -> main.bbl -> bibliography in PDF)
MAIN = main

.PHONY: all pdf review pages clean count

all pdf: paper/$(MAIN).pdf

paper/$(MAIN).pdf: paper/$(MAIN).tex paper/refs.bib paper/sec/*.tex
	pdflatex -interaction=nonstopmode -output-directory=paper paper/$(MAIN).tex
	cd paper && bibtex $(MAIN)
	pdflatex -interaction=nonstopmode -output-directory=paper paper/$(MAIN).tex
	pdflatex -interaction=nonstopmode -output-directory=paper paper/$(MAIN).tex

# Review build: camera-ready false (no acknowledgments)
review:
	@echo "Building review version (\\camerareadyfalse)..."
	@pdflatex -interaction=nonstopmode -output-directory=paper "\def\camerareadyfalse{}\input{paper/$(MAIN).tex}" || true
	@(cd paper && bibtex $(MAIN)) || true
	@pdflatex -interaction=nonstopmode -output-directory=paper "\def\camerareadyfalse{}\input{paper/$(MAIN).tex}" || true
	@pdflatex -interaction=nonstopmode -output-directory=paper "\def\camerareadyfalse{}\input{paper/$(MAIN).tex}" || true
	@echo "Review PDF built: paper/$(MAIN).pdf"

# Report PDF page count and warn if content pages exceed target
pages: paper/$(MAIN).pdf
	@echo "--- Page count ---"
	@pdfinfo paper/$(MAIN).pdf 2>/dev/null | grep Pages || mdls -name kMDItemNumberOfPages paper/$(MAIN).pdf 2>/dev/null
	@echo "Target: <= 7 content pages before bibliography"

# Word count for abstract
count:
	@echo "Abstract word count:"
	@detex paper/sec/00_abstract.tex | wc -w

clean:
	rm -f paper/$(MAIN).aux paper/$(MAIN).bbl paper/$(MAIN).blg paper/$(MAIN).log paper/$(MAIN).out paper/$(MAIN).pdf
