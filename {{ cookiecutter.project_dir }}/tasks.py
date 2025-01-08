import configparser
import os
import shutil
import subprocess

import pylbmisc as lb

from pathlib import Path
from zipfile import ZipFile
from invoke import task
from tkinter.filedialog import askopenfilename

# ----------------------------------------------- Parameters
# external programs
editor = "emacs --no-splash -r -fh"
pdf_viewer = "okular --unique"
clean_cmd = "rm -rf *.tex *.aux *.pytxcode *.toc *.log pythontex-files-* *.bbl *.bcf *.blg *.run.xml *.out *.Rnw"

# libraries needed for any project
default_prj_requirements = ["pandas", "file:///home/l/.src/pypkg/pylbmisc"]

# Directories/PATHS
prj = Path(".")
prj_src_dir         = prj / "src"
prj_tmp_dir         = prj / "tmp"
prj_data_dir        = prj / "data"
prj_outputs_dir     = prj / "outputs"
prj_proj_dir        = prj / "proj"
prj_ini             = prj / "proj" / "info.ini"
prj_docs_dir        = prj / "proj" / "docs"
prj_biblio_common   = prj / "proj" / "biblio" / "common_biblio.bib"
prj_biblio_specific = prj / "proj" / "biblio" / "prj_biblio.bib"

prj_report          = prj / "report.pdf"
prj_readme          = prj / "README.md"

def prj_dataset(data):
    return prj / "data" / f"dataset_{data}.xlsx"

def prj_protocol(data):
    return prj / "proj" / "docs" / f"protocol_{data}.pdf"

prj_dataset_link    =  prj / "data" / "dataset.xlsx"
prj_protocol_link   =  prj / "proj" / "docs" / "protocol.pdf"


def import_data():
    """
    Import latest dataset and set up proper symlinks.
    """
    dataset_date = input(
        "Insert date of the data extraction (YYYY-MM-DD) or leave blank to skip: "
    ).replace("-", "_")
    if dataset_date != "":
        outfile = prj_dataset(dataset_date)
        symlink = prj_dataset_link
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
            symlink.unlink()
        symlink.symlink_to(outfile.absolute())


def import_protocol():
    """
    Import latest protocol and set up proper symlinks
    """
    msg = "Insert date of the study protocol (YYYY-MM-DD) or leave blank to skip: "
    protocol_date = input(msg).replace("-", "_")
    if protocol_date != "":
        outfile = prj_protocol(protocol_date)
        symlink = prj_protocol_link
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
               prj_biblio_common.absolute())
    subprocess.run(["touch", str(prj_biblio_specific)])
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
    metadata = configparser.ConfigParser()
    metadata.read(prj_ini)
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
    # prj_src_py  = prj_src_dir.glob("*.py")
    # prj_src_r   = prj_src_dir.glob("*.R")
    # prj_src_qmd = prj_src_dir.glob("*.qmd")
    # prj_src_rnw = prj_src_dir.glob("*.Rnw")
    # py   = list(prj_src_py)
    # r    = list(prj_src_r)
    # qmd  = list(prj_src_qmd)
    # rnw  = list(prj_src_rnw)
    # all_files = [str(f) for f in py + r + qmd + rnw]
    # ignore = [str(prj_src_dir / f) for f in ["src/__init__.py", "src/_region_.tex"]]
    # edit_files = [f for f in all_files if f not in ignore]
    # paths_str = " ".join(edit_files)
    paths_str  = str(prj_src_dir / "*")
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
    # pys = prj_srcpys(prj)
    pys = prj_src_dir.glob("*.py")
    if pys:
        for py in pys:
            print(f"-- Executing {py} --")
            c.run(f"uv run python {py}")
    else:
        print("No *.py in src")



@task
def runrs(c):
    """
    Esegue i file src/*.R nella directory radice del progetto e ne salva l'output in
    tmp
    """
    rs = prj_src_dir.glob("*.R")
    # rs = prj_srcrs(prj)
    if rs:
        for r in rs:
            infile = r
            outfile = prj_tmp_dir / (str(r.stem) + ".txt")
            print(f"Executing {infile} (output in {outfile})")
            cmd = f"R CMD BATCH --no-save --no-restore {infile} {outfile}"
            c.run(cmd)
    else:
        print("No *.R in src")



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
def zip(c):
    """
    Zippa il report.pdf e i file in prj/outputs per l'invio.
    """
    outputs = list(prj_outputs_dir(prj).iterdir()) + [prj_report(prj)]
    outpaths = [f.resolve() for f in outputs]
    zip_fpath = Path("/tmp/{0}.zip".format(prj))
    if zip_fpath.exists():
        zip_fpath.unlink()
    with ZipFile(zip_fpath, "w") as zip:
        for f in outpaths:
            arcn = prj / f.name if f.name == 'report.pdf' else prj / "allegati" / f.name
            zip.write(f, arcname = arcn)

   
@task
def tgrep(c):
    """
    Invia il report.pdf via telegram nella chat lavoro.
    """
    the_report = prj_report(prj).resolve()
    if not the_report.exists():
        raise ValueError("Non esiste {}.".format(the_report))
    c.run("winston_sends {} group::lavoro".format(the_report))


@task
def tgout(c):
    """
    Invia gli allegati nella cartella outputs via telegram nella chat lavoro.
    """
    outputs = list(prj_outputs_dir(prj).iterdir())
    outpaths = [f.resolve() for f in outputs]
    if outpaths:
        for f in outpaths:
            c.run("winston_sends {} group::lavoro &".format(f))
    else:
        raise ValueError("Non vi sono file in {}.".format(prj_outputs_dir(prj)))


@task
def tgzip(c):
    """
    Invia il malloppone zippato via telegram nella chat lavoro
    """
    zip = Path("/tmp/{0}.zip".format(prj))
    if not zip.exists():
        raise ValueError("Non esiste {}.".format(zip))
    c.run(f"winston_sends {zip} group::lavoro")

# @task
# def lint(c):
#     """
#     Esegue il linter (flake8) nella cartella src.
#     """
#     c.run("cd {0} && flake8 src".format(prj))


# @task
# def mypy(c):
#     """
#     Esegue mypy nella cartella src del progetto.
#     """
#     c.run("cd {0} && mypy src".format(prj))


# @task
# def format(c):
#     """
#     Esegue il formatter (black) nella cartella src.
#     """
#     c.run("cd {0} && black src".format(prj))


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
