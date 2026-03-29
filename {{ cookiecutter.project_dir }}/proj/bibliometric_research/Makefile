search:
	pubmed_search '"method comparison studies[tiab]"'

biblio_citations:
	biblio_citations search_results.csv

top_biblio:
	head -n 100 search_results_bibliocitations.csv > top100biblio.csv

top_biblio_info:
	doi2info top100biblio.csv && libreoffice top100biblio_info.xlsx

tg_results:
	winston_sends top100biblio_info.xlsx group::lavoro
