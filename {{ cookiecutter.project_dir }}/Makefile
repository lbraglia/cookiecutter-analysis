DOCVIEWER=libreoffice
EDITOR=emacs
PDFVIEWER=okular
RM=rm -rf
RUNPY=uv run python
RUNR=R CMD BATCH --no-save --no-restore

define tg
	winston_sends $1 group::lavoro
endef

define utils
	uv run utils/$1 $2
endef

.PHONY: *

default: test

test:
	${RUNR} src/asd.R


init:
	direnv allow
	$(call utils,project_init)
	# # quando si sarà nix-only
	# direnv allow && $(call utils,project_init)

add-data-generic:
	@ python utils/add_data_generic

add-data-redcap:
	@ python utils/add_data_redcap

add-plugins:
	@ $(call utils,add_plugins)

zip-results:
	@ $(call utils,zip_results)

compile: report-pdf

view: view-report-pdf

edit:
	${EDITOR} src/*

venv-repl:
	${RUNPY}

venv-sync:
	uv sync

venv-freeze:
	$(call utils,venv_freeze)

add-protocol:
	@ # $(call utils,add_protocol)
	@ # do not use uv here, assume the user has tkinter lib (which is std)
	python utils/add_protocol

estimates-validation:
	${RUNR} src/estimates_validation.R


article:
	$(call utils,compile_qmd,src/article.qmd) && make view-article &

appendices:
	$(call utils,compile_qmd,src/appendices.qmd) && make view-appendices &

report-rnw:
	$(call utils,compile_rnw,src/report.Rnw) && make view-report-pdf &

view-report-pdf:
	${PDFVIEWER} report.pdf

report-docx:
	$(call utils,compile_qmd,src/report.qmd) && make view-report-docx &

view-report-docx:
	${DOCVIEWER} report.docx

slides:
	$(call utils,compile_rnw,src/slides.Rnw) && make view-slides &


tg-report-docx:
	$(call tg,report.docx) &

tg-report-pdf:
	$(call tg,report.pdf) &

tg-article:
	$(call tg,article.docx) &

tg-appendices:
	$(call tg,appendices.docx) &

tg-slides:
	$(call tg,slides.pdf) &


view-protocol:
	${PDFVIEWER} proj/protocol.pdf &

view-crf:
	${PDFVIEWER} proj/crf/*.pdf &

view-literature:
	${PDFVIEWER} proj/letteratura/*.pdf &

view-article:
	${DOCVIEWER} article.docx &

view-appendices:
	${DOCVIEWER} appendices.docx &

view-slides:
	${PDFVIEWER} slides.pdf &


clean:
	${RM} \
	*.tex *.aux *.pytxcode *.toc *.log pythontex-files-* \
	*.bbl *.bcf *.blg *.run.xml *.out *.qmd *.Rnw *.md \
	*.nav *.snm *.Rout *_files
