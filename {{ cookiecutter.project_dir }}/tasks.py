import configparser
import os
import shutil
import subprocess

import pylbmisc as lb

from pathlib import Path
from zipfile import ZipFile
from invoke import task
from tkinter.filedialog import askopenfilename

# -----------------------------------------------------------------------------------------------
# PARAMETERS
# -----------------------------------------------------------------------------------------------

# external programs
editor = "emacs --no-splash -r -fh"
pdf_viewer = "okular --unique"
clean_cmd = "rm -rf *.tex *.aux *.pytxcode *.toc *.log pythontex-files-* *.bbl *.bcf *.blg *.run.xml *.out *.Rnw"

# libraries needed for any project
default_prj_requirements = ["pandas", "file:///home/l/.src/pypkg/pylbmisc"]

# -----------------------------------------------------------------------------------------------
# PATHS
# -----------------------------------------------------------------------------------------------

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
        dfs = lb.io.data_import(fpaths)
        # save as a single excel file
        lb.io.data_export(x=dfs, path=outfile.absolute(), index=False)
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
        # pdf: copy, other convert it with pandoc
        if fpath.suffix == ".pdf":
            shutil.copy(fpath, outfile.absolute())
        else:
            subprocess.run(["pandoc", "-o", outfile.absolute(), fpath])
        # smart symlinks
        if symlink.exists():
            symlink.unlink()
        symlink.symlink_to(outfile.absolute())

# -----------------------------------------------------------------------------------------------
# TASKS
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
    # ------------------------------------------------------------
    print("Bibliography setup")
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
    subprocess.run(["uv", "init", "."])
    subprocess.run(["rm", "-rf", "hello.py"])
    subprocess.run(["uv", "add"] + default_prj_requirements)
    # adding the remote for git
    metadata = get_metadata()
    url = metadata["project"]["url"]
    cmd = f"git init -b master && git remote add origin {url} && git add . && git commit -m 'Directory setup'"
    os.system(cmd)
    # -----------------------------------------------------------
    return None



@task
def dataimp(c):
    """
    Importa il dataset nella directory del progetto.
    """
    import_data()


@task
def protimp(c):
    """
    Importa il protocollo nella directory del progetto.
    """
    import_protocol()


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
    # non so perché dia error invoke, da debuggare quando si ha piu tempo
    # src_py  = src_dir.glob("*.py")
    # src_r   = src_dir.glob("*.R")
    # src_qmd = src_dir.glob("*.qmd")
    # src_rnw = src_dir.glob("*.Rnw")
    # py   = list(src_py)
    # r    = list(src_r)
    # qmd  = list(src_qmd)
    # rnw  = list(src_rnw)
    # all_files = [str(f) for f in py + r + qmd + rnw]
    # ignore = [str(src_dir / f) for f in ["src/__init__.py", "src/_region_.tex"]]
    # edit_files = [f for f in all_files if f not in ignore]
    # paths_str = " ".join(edit_files)
    paths_str  = str(src_dir / "*")
    cmd = f"{editor}  {paths_str} & " 
    os.system(cmd)


@task
def repl(c):
    """
    Esegue un interprete python nell'environment considerato
    """
    os.system("uv run python")


@task
def runpys(c):
    """
    Esegue i file src/*.py nella directory radice del progetto.
    """
    # pys = srcpys(prj)
    pys = src_dir.glob("*.py")
    for py in pys:
        print(f"-- Executing {py} --")
        c.run(f"uv run python {py}")


@task
def runrs(c):
    """
    Esegue i file src/*.R nella directory radice del progetto e ne salva l'output in
    tmp
    """
    rs = src_dir.glob("*.R")
    for r in rs:
        infile = r
        outfile = tmp_dir / (str(r.stem) + ".txt")
        print(f"Executing {infile} (output in {outfile})")
        cmd = f"R CMD BATCH --no-save --no-restore {infile} {outfile}"
        c.run(cmd)



@task
def report(c):
    """
    Esegue pdflatex/pythontex su src/report.tex nella directory radice del progetto e visualizza il pdf.
    """
    rmln = "rm -rf report.tex"
    ln = "ln -s src/report.tex"
    pdflatex = "pdflatex report"
    pythontex = "uv run pythontex report"
    # pythontex = "pythontex --interpreter python:.venv/bin/python report"
    biber = "biber report"
    pdf_view = f"{pdf_viewer} report.pdf"
    c.run(
        "{0} && {1} && {2} && {3} && {4} && {5} && {6} && {7} && {8}".format(
            rmln, ln, pdflatex, biber, pythontex, pdflatex, pdflatex, pdf_view, clean_cmd
        )
    )


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

    with ZipFile(zip_fpath, "w") as zip:
        # report
        zip.write(final_report, f"{paste}/report.pdf")
        # allegati
        for a in outputs_dir.iterdir():
            if not a.name.startswith("."):
                zip.write(a, f"{paste}/allegati/{a.name}")



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
    List invoke tasks.
    """
    c.run("invoke -l")

@task
def help(c):
    """
    Invoke's help.
    """
    c.run("invoke -h") 
