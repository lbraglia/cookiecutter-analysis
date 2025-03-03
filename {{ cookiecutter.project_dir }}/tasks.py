import configparser
import os
import shutil
import subprocess
import datetime as dt

import pylbmisc as lb

from pathlib import Path
from invoke import task
from tkinter.filedialog import askopenfilename

# -----------------------------------------------------------------------------------------------
# PARAMETERS
# -----------------------------------------------------------------------------------------------

# external programs
editor = "emacs --no-splash -r -fh"
pdf_viewer = "okular --unique"
clean_cmd = "rm -rf *.tex *.aux *.pytxcode *.toc *.log pythontex-files-*" \
    " *.bbl *.bcf *.blg *.run.xml *.out *.qmd *.Rnw *.md"

# libraries needed for any project
# default_prj_requirements = ["pandas", "openpyxl", "--editable", "file:///home/l/.src/pypkg/pylbmisc"]
default_prj_requirements = ["jupyter", "--editable", "file:///home/l/.src/pypkg/pylbmisc"]

# -----------------------------------------------------------------------------------------------
# PATHS
# -----------------------------------------------------------------------------------------------

# project
root = Path(".")
src_dir       = root / "src"
tmp_dir       = root / "tmp"
data_dir      = root / "data"
outputs_dir   = root / "outputs"
proj_dir      = root / "proj"
docs_dir      = root / "proj" / "docs"
common_biblio = root / "proj" / "biblio" / "common_biblio.bib"
prj_biblio    = root / "proj" / "biblio" / "prj_biblio.bib"
final_report  = root / "report.pdf"

# outside project
brain = Path("~/.brain/pages").expanduser()

# -----------------------------------------------------------------------------------------------
# UTILS
# -----------------------------------------------------------------------------------------------


def get_metadata():
    """Read/parse the project .ini file containing information inserted during
    project creation."""
    ini_path = proj_dir / "info.ini"
    metadata = configparser.ConfigParser()
    metadata.read(ini_path)
    return metadata


def addsomething(url, outfile, overwrite = False):
    """Function to downloa stuff (plugin or udpdated tasks.py)"""
    if outfile.exists() and not overwrite:
        msg = f"File {outfile} already exists, download aborted."
        print(msg)
        return None
    os.system(f"wget -O {outfile} {url}")


def import_data():
    """
    Import latest dataset and set up proper symlinks.
    """
    dataset_date = input(
        "Insert date of the data extraction (YYYY-MM-DD) or leave blank to skip: "
    ).replace("-", "_")
    if dataset_date != "":
        outfile = data_dir / f"raw_dataset_{dataset_date}.xlsx"
        symlink = data_dir / "raw_dataset.xlsx"
        title = "Select DATA FILES to be imported and anonymized"
        initialdir = "/tmp"
        filetypes = [("Formati", ".csv .xls .xlsx .zip")]
        fpaths = askopenfilename(
            title=title, initialdir=initialdir, filetypes=filetypes, multiple=True
        )
        # import data
        dfs = lb.io.import_data(fpaths)
        # save as a single excel file
        lb.io.export_data(x=dfs, path=outfile.absolute(), index=False)
        # add symlink
        if symlink.exists():
            symlink.rename(data_dir / "old_raw_dataset.xlsx")
        symlink.symlink_to(outfile.relative_to(data_dir))


def import_protocol():
    """
    Import latest protocol and set up proper symlinks
    """
    msg = "Insert date of the study protocol (YYYY-MM-DD) or leave blank to skip: "
    protocol_date = input(msg).replace("-", "_")
    if protocol_date != "":
        outfile = docs_dir / f"protocol_{protocol_date}.pdf"
        symlink = docs_dir / "protocol.pdf"
        title = "Select the study protocol file to be imported"
        initialdir = "/tmp"
        filetypes = [("Formati", ".docx .doc .pdf")]
        fpath = Path(
            askopenfilename(title=title, initialdir=initialdir, filetypes=filetypes)
        )
        if fpath.suffix == ".pdf":
            # just copy the .pdf file
            shutil.copy(fpath, outfile.absolute())
        else:
            # convert with libreoffice
            libreoffice_export = Path("/tmp") / (fpath.stem + '.pdf')
            if libreoffice_export.exists():
                libreoffice_export.unlink()
            os.system(f"libreoffice --headless --convert-to pdf {fpath} --outdir /tmp")
            shutil.copy(libreoffice_export, outfile.absolute())
        # smart symlinks
        if symlink.exists():
            symlink.unlink()
        symlink.symlink_to(outfile.relative_to(docs_dir))


def create_logseq_page(fpath, metadata):
    pi_surname = metadata["pi"]["surname"]
    pi_name = metadata["pi"]["name"]
    pi_uo = metadata["pi"]["uo"]
    prj_description = metadata["project"]["description"]
    prj_acronym = metadata["project"]["acronym"]
    prj_title = metadata["project"]["title"]
    prj_dir = metadata["project"]["dir"]
    prj_url = metadata["project"]["url"]
    prj_created = metadata["project"]["created"]
    prj_contatto = metadata["project"]["contatto"]
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = days[dt.date.fromisoformat(prj_created).weekday()]
    created = f"{prj_created} {dow}"
    logseq_template = f"""type:: [[project]]
area:: [[lavoro]]
priority:: A
description:: {prj_description}
tags:: fase1 | fase2 | fase3 | fase4, 1braccio | 2bracci | +2bracci, superiorità | non-inferiorità | equivalenza, coorte | caso-controllo | cross-sectional, eziologico | diagnostico | trattamento | prognostico, prospettico | retrospettivo
created:: [[{created}]]
project-title:: {prj_title}
project-acronym:: {prj_acronym}
project-PI:: {pi_surname} {pi_name}
project-contatto:: {prj_contatto}
pi-struttura:: {pi_uo}
project-directory:: [here](file:///home/l/projects/{prj_dir})
project-repo:: [here]({prj_url})
project-ndatasets:: 1
-
- ## Lore
	-
-
- ## Log
	-
-
- ## Appunti
	-
-
- ## Meetings
	-
-
- ## Mail
	-
"""
    with open(fpath, "w") as f:
        print(logseq_template, file = f)


def uv_init():
    os.system("rm -rf .venv uv.lock pyproject.toml")
    subprocess.run(["uv", "init", "."])
    subprocess.run(["rm", "-rf", "hello.py"])
    subprocess.run(["uv", "add"] + default_prj_requirements)


def compile_tex(tex):
    """Compile a single tex file in src"""
    link = Path(tex.name) # current directory
    if link.exists():
        link.unlink()
    link.symlink_to(tex)
    print(f"-- Compiling {tex} --")
    pdflatex = f"pdflatex {link.stem}"
    pythontex = f"uv run pythontex {link.stem}"
    biber = f"biber {link.stem}"
    pdf_view = f"{pdf_viewer} {link.stem}.pdf"
    cmd = f"{pdflatex} && {biber} && {pythontex} && {pdflatex} && {pdflatex} && {pdf_view} &"
    os.system(cmd)


def compile_rnw(rnw):
    """Compile a single Rnw file in src"""
    link = Path(rnw.name) # current directory
    tex = link.with_suffix(".tex")
    if link.exists():
        link.unlink()
    link.symlink_to(rnw)
    print(f"-- Compiling {rnw} --")
    knit = f"Rscript -e 'knitr::knit(input = \"{link}\", output = \"{tex}\", envir = new.env())'"
    pdflatex = f"pdflatex {link.stem}"
    biber = f"biber {link.stem}"
    pdf_view = f"{pdf_viewer} {link.stem}.pdf"
    cmd = f"{knit} && {pdflatex} && {biber} && {pdflatex} && {pdflatex} && {pdf_view} &"
    os.system(cmd)


def compile_qmd(qmd):
    """Compile a single qmd file in src"""
    link = Path(qmd.name)  # link of eg report.qmd to src/report.qmd
    if link.exists():
        link.unlink()
    link.symlink_to(qmd)
    # redirect quarto figures to output
    output_link = Path(link.stem + "_files")
    if output_link.exists():
        output_link.unlink()
    output_link.symlink_to("outputs")
    print(f"-- Compiling {qmd} --")
    os.system(f"uv run quarto render {link} --debug")
    if output_link.exists():
        output_link.unlink()


# -----------------------------------------------------------------------------------------------
# COMMON TASKS
# -----------------------------------------------------------------------------------------------


@task
def clean(c):
    """
    Pulisce la directory del progetto.
    """
    c.run(clean_cmd)


@task
def init(c):
    """
    Inizializza un nuovo progetto parzialmente creato da cookiecutter
    """
    metadata = get_metadata()
    # ------------------------------------------------------------
    print("Bibliography setup")
    if not common_biblio.exists():
        os.symlink("/home/l/texmf/tex/latex/biblio/biblio.bib",
                   common_biblio.absolute())
    subprocess.run(["touch", str(prj_biblio)])
    # -----------------------------------------------------------
    print("Importing protocol")
    import_protocol()
    # -----------------------------------------------------------
    print("Importing dataset")
    import_data()
    # -----------------------------------------------------------
    print("UV init")
    uv_init()
    # -----------------------------------------------------------
    print("Git init")
    url = metadata["project"]["url"]
    cmd = f"git init -b master && git remote add origin {url} && git add . && git commit -m 'Directory setup'"
    os.system(cmd)
    # -----------------------------------------------------------
    print("Logseq page")
    # -----------------------------------------------------------
    logseq_page = brain / (metadata["project"]["dir"] + ".md")
    if logseq_page.exists():
        print("logseq page already available, skipping.")
    else:
        create_logseq_page(fpath = logseq_page, metadata = metadata)
    return None


@task
def adddata(c):
    """
    Importa il dataset nella directory del progetto.
    """
    import_data()


@task
def addprot(c):
    """
    Importa il protocollo nella directory del progetto.
    """
    import_protocol()


@task
def viewdata(c):
    """
    Mostra il dataset ultima versione.
    """
    cmd = "libreoffice --calc --view data/raw_dataset.xlsx &"
    os.system(cmd)


@task
def viewprot(c):
    """
    Mostra il protocollo ultima versione.
    """
    cmd = f"{pdf_viewer} proj/docs/protocol.pdf &"
    os.system(cmd)


@task
def viewlit(c):
    """
    Mostra la letteratura del progetto.
    """
    cmd = f"{pdf_viewer} proj/docs/letteratura/*.pdf &"
    os.system(cmd)


@task
def viewcrf(c):
    """
    Mostra le crf del progetto.
    """
    cmd = f"{pdf_viewer} proj/docs/crf/*.pdf &"
    os.system(cmd)


@task
def edit(c):
    """
    Edita i file rilevanti del progetto con Emacs.
    """
    paths_str  = str(src_dir / "*")
    cmd = f"{editor}  {paths_str} & " 
    os.system(cmd)


@task
def venvrepl(c):
    """
    Esegue un interprete python nell'environment considerato
    """
    os.system("uv run python")


@task
def venvsync(c):
    """
    Sincronizza uv per far si che tutte le dipendenze siano soddisfatte
    """
    os.system("uv sync")


@task
def venvfreeze(c):
    """
    Freeza le dipendenze ad oggi aggiungendo eclude-newer al pyproject.toml.
    Prima di farlo fare l'update di tutti i pacchetti ed eseguire l'elaborazione
    per sicurezza
    """
    # today = date.today().isoformat()
    now = dt.datetime.now(dt.timezone.utc)
    string = f"\n\n[tool.uv]\nexclude-newer = '{now.isoformat()}'\n"
    with open("pyproject.toml", "a") as f:
        f.write(string)


@task
def runpys(c):
    """
    Esegue i file src/*.py nella directory radice del progetto.
    """
    # pys = srcpys(prj)
    pys = src_dir.glob("*.py")
    for py in sorted(pys):
        print(f"-- Executing {py} --")
        c.run(f"uv run python {py}")


@task
def runrs(c):
    """
    Esegue i file src/*.R nella directory radice del progetto e ne salva l'output in
    tmp
    """
    rs = src_dir.glob("*.R")
    for r in sorted(rs):
        infile = r
        outfile = tmp_dir / (str(r.stem) + ".txt")
        print(f"Executing {infile} (output in {outfile})")
        cmd = f"R CMD BATCH --no-save --no-restore {infile} {outfile}"
        c.run(cmd)


@task
def reportqmd(c):
    """
    Clean degli output e compila src/report.qmd
    """
    if outputs_dir.exists():
        shutil.rmtree(outputs_dir)
        outputs_dir.mkdir()
    compile_qmd(Path("src/report.qmd"))


@task
def compiletexs(c):
    """
    Compila i file src/*.qmd nella directory radice del progetto con quarto.
    """
    texs = src_dir.glob("*.tex")
    for tex in sorted(texs):
        compile_tex(tex)


@task
def compilernws(c):
    """
    Compila i file src/*.Rnw nella directory radice del progetto con quarto.
    """
    rnws = src_dir.glob("*.Rnw")
    for rnw in sorted(rnws):
        compile_rnw(rnw)


@task
def compileqmds(c):
    """
    Compila i file src/*.qmd nella directory radice del progetto con quarto.
    """
    qmds = src_dir.glob("*.qmd")
    for qmd in sorted(qmds):
        compile_qmd(qmd)


@task
def tgrep(c):
    """
    Invia il report.pdf via telegram nella chat lavoro.
    """
    if not final_report.exists():
        raise ValueError(f"Non esiste {final_report}.")
    c.run(f"winston_sends {final_report} group::lavoro")


@task
def zip(c):
    """
    Zippa il report.pdf e i file in prj/outputs per l'invio.
    """
    metadata = get_metadata()
    acronym = metadata["project"]["acronym"]
    pi = metadata["pi"]["surname"]
    paste = f"{pi}_{acronym}"
    zip_fpath = Path(f"/tmp/{paste}.zip")
    if zip_fpath.exists():
        zip_fpath.unlink()
    # copy reports in outputs
    report_pdf = Path("report.pdf")
    report_docx = Path("report.docx")
    if report_pdf.exists():
        shutil.copy(report_pdf, outputs_dir)
    if report_docx.exists():
        shutil.copy(report_docx, outputs_dir)
    shutil.make_archive(str(zip_fpath.with_suffix("")),
                        format = "zip",
                        base_dir = outputs_dir)


@task
def mypy(c):
    """
    Esegue mypy nella cartella src del progetto.
    """
    c.run("mypy src")


@task
def ruff(c):
    """
    Esegue ruff nella cartella src del progetto.
    """
    c.run("ruff check src")


@task
def list(c):
    """
    Lista i task di Invoke.
    """
    c.run("invoke -l")


@task
def help(c):
    """
    Help di Invoke.
    """
    c.run("invoke -h")


@task
def updatetasks(c):
    """Update tasks.py to latest version"""
    url = "https://raw.githubusercontent.com/lbraglia/cookiecutter-analysis/refs/heads/main/%7B%7B%20cookiecutter.project_dir%20%7D%7D/tasks.py"
    addsomething(url = url, outfile = Path("tasks.py"), overwrite = True)


@task
def addplugins(c):
    """
    Add plugins to current project
    """
    baseurl = "https://raw.githubusercontent.com/lbraglia/cookiecutter-analysis/refs/heads/main/plugins/"
    plugins = ["randomization.py",
               "estimates_validation.R",
               "report.Rnw",
               "report.tex"]
    choices = lb.utils.menu(title = "Specificare che plugin", choices = plugins)
    if choices:
        for f in choices:
            url = baseurl + f
            dest = src_dir / f
            addsomething(url = url, outfile = dest, overwrite = False)
