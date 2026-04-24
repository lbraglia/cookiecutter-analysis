library(knitr)   # necessario per setup knitr
library(lbmisc)  # necessario per lbmisc::knitr_inline
knit_engines$set(python = reticulate::eng_python)
opts_chunk$set(
  fig.path    = 'outputs/',
  fig.align   = 'center',
  size        = 'small',
  strip.white = TRUE,
  tidy        = FALSE,
  echo        = FALSE,
  error       = TRUE,
  warning     = TRUE,
  message     = TRUE,
  dpi         = 600,
  dev         = c('png', 'tiff', 'cairo_ps', 'pdf')[c(1, 3, 4)],
  fig.width   = inches(cm = 8.5),  # dimensioni default journal
  fig.height  = inches(cm = 8.5),  # dimensioni default journal
  dev.args    = list(tiff = list(compression = 'lzw')))
knit_hooks$set(inline = lbmisc::knitr_inline)
wb <- openxlsx::createWorkbook() ## raw tables

## # pacchetti aggiuntivi
library(lbstat)
## library(lbagree)
## library(lbdiag)
## library(lbtrial)
## library(lbscorer)
## library(lbsurv)
## library(lme4)
## library(lmerTest)
## library(survival)
## library(telegram)
## library(xtable)

## -------------------------------------------------------------

# importazione dati
shut_up <- lapply(
  list.files(Sys.glob("tmp"), pattern = glob2rx("clean_*.R"), full.names = TRUE),
  function(x) source(x)
)
rm(shut_up)

# pretty printing of tableone for descriptives
if (exists("db_des")){
  names(db_des) <- pretty_text(names(db_des))
}
