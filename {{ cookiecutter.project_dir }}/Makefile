edit:
	inv edit &

data-cleaning:
	inv run-py -f src/data_cleaning.py &

compile:
	[ -f src/report.Rnw ] && inv compile-rnw -f src/report.Rnw &
	[ -f src/report.qmd ] && inv compile-qmd -f src/report.qmd &

view:
	[ -f report.docx ] && ${DOCXVIEWER} report.docx &
	[ -f report.pdf ] && ${PDFVIEWER} report.pdf &

tg-report:
	[ -f report.docx ] && inv tg -f report.docx &
	[ -f report.pdf ] && inv tg -f report.pdf &

clean:
	inv clean
