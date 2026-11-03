EDITOR=emacs
PDF_VIEWER=okular
RM=rm -rf
RUNPY=python
RUNR=R CMD BATCH --no-save --no-restore
UVRUNPY=uv run python
DOC_VIEWER=libreoffice --write --view

define tg
	winston_sends $1 group::lavoro
endef

define utils
	uv run utils/$1 $2
endef

.PHONY: *

# default targets
edit: edit-src
compile: report
report: report-rnw
# report: report-docx
view: view-report
default: clean


# -----------------------------
# Project setup and mantainance
# -----------------------------
init:
	@ # when nixos only: direnv allow && $(call utils,project_init)
	# @ direnv allow
	@ $(call utils,project_init)

add-data:
	# @ # if you use uv, nixos will require tkinter in each dir
	@ echo "Need to choose if using redcap or generic imports"
	# @ ${UVRUNPY} utils/add_data_generic
	# @ ${UVRUNPY} utils/add_data_redcap

add-protocol:
	@ # do not use uv here, assume the user has tkinter lib (which is std)
	@ # $(call utils,add_protocol)	
	${RUNPY} utils/add_protocol

add-crf:
	${RUNPY} utils/add_crf


add-plugins:
	@ $(call utils,add_plugins)

venv-repl:
	@ ${UVRUNPY}

venv-sync:
	@ uv sync

venv-freeze:
	@ $(call utils,venv_freeze)

# ----------------
# Edit/run/compile
# ----------------
# last file as default open
edit-src:
	@ ${EDITOR} src/* src/prjlib/src/prjlib/*.py src/data_cleaning.py & # src/report.Rnw &

data-cleaning:
	@ echo "======================="
	@ echo "Data cleaning"          
	@ echo "======================="
	@ ${UVRUNPY} src/data_cleaning.py

estimates-validation:
	@ echo "======================="
	@ echo "Estimates validation"          
	@ echo "======================="
	@ ${RUNR} src/estimates_validation.R

report-rnw:
	@ echo "======================="
	@ echo "Compiling report.Rnw"          
	@ echo "======================="
	@ $(call utils,compile_rnw,src/report.Rnw) &

report-docx:
	@ echo "======================="
	@ echo "Compiling report.qmd"          
	@ echo "======================="
	@ $(call utils,compile_qmd,src/report.qmd) && make view-report-docx &

article:
	@ echo "======================="
	@ echo "Compiling article.qmd"          
	@ echo "======================="
	@ $(call utils,compile_qmd,src/article.qmd) && make view-article &

appendices:
	@ echo "======================="
	@ echo "Compiling appendices.qmd"          
	@ echo "======================="
	@ $(call utils,compile_qmd,src/appendices.qmd) && make view-appendices &

slides:
	@ echo "======================="
	@ echo "Compiling slides.Rnw"          
	@ echo "======================="
	@ $(call utils,compile_rnw,src/slides.Rnw)

# ----------
# View stuff
# ----------
view-protocol:
	@ ${PDF_VIEWER} proj/protocol/protocol.pdf &

view-crf:
	@ ${PDF_VIEWER} proj/crf/*.pdf &

view-literature:
	@ ${PDF_VIEWER} proj/literature/*.pdf &

view-report: view-report-pdf
view-report-pdf:
	@ ${PDF_VIEWER} report.pdf

view-report-docx:
	@ ${DOC_VIEWER} report.docx

view-article:
	@ ${DOC_VIEWER} article.docx &

view-appendices:
	@ ${DOC_VIEWER} appendices.docx &

view-slides:
	@ ${PDF_VIEWER} slides.pdf &

# ---------------
# Outputs sending
# ---------------
tg-report-docx:
	@ $(call tg,report.docx) &

tg-report-pdf:
	@ $(call tg,report.pdf) &

tg-article:
	@ $(call tg,article.docx) &

tg-appendices:
	@ $(call tg,appendices.docx) &

tg-slides:
	@ $(call tg,slides.pdf) &

zip-results:
	@ $(call utils,zip_results)

# ---------------
# Utils
# ---------------
clean:
	@ ${RM} \
	*.tex *.aux *.pytxcode *.toc *.log pythontex-files-* \
	*.bbl *.bcf *.blg *.run.xml *.out *.qmd *.Rnw *.md \
	*.nav *.snm *.Rout *_files *.docx *.pdf

cleanall: clean
	${RM} tmp/*

sysinfo:
	@ echo "System informations"
	@ echo "==================="
	@ echo
	@ echo "Standard install:"
	@ echo
	@ ${RUNPY} utils/sysinfo
	@ echo
	@ echo "UV install:"
	@ echo	
	@ ${UVRUNPY} utils/sysinfo
