import configparser
import os
import shutil
import subprocess

import pylbmisc as lb

from pathlib import Path
from zipfile import ZipFile
from datetime import date
from invoke import task
from tkinter.filedialog import askopenfilename

TESTING = True

# ----------------------------------------------- Parameters
# sys infos
oggi = date.today()

# external programs
editor = "emacs --no-splash -r -fh"
pdf_viewer = "okular --unique"
clean_cmd = "rm -rf *.tex *.aux *.pytxcode *.toc *.log pythontex-files-* *.bbl *.bcf *.blg *.run.xml *.out *.Rnw"

# default lines for requirements.txt
default_requirements = [
    "# matplotlib",
    "# scipy",
    "# statsmodels",
    "# tableone",
    "pandas",
    "pylbmisc @ file:///home/l/.src/pypkg/pylbmisc",
]

# project snake paths
ini_file = Path("~/.project_snake.ini").expanduser()
psnake_dir = Path("project_snake")
psnake_template_dir = psnake_dir / "templates"
psnake_template_biblio = psnake_dir / "templates" / "biblio.bib"
psnake_template_gitignore = psnake_dir / "templates" / "gitignore"
psnake_template_texfiles = psnake_template_dir.glob("*.tex")
psnake_template_pyfiles = psnake_template_dir.glob("*.py")


# project standard directory and path generators
def prj_subdirs(prj):
    subdirs = (
        "tmp",
        "data",
        "outputs",
        "proj",
        "proj/biblio",
        "proj/docs",
        "proj/docs/revisione_protocollo",
        "proj/docs/revisione_articolo",
        "proj/docs/letteratura",
        "src",
    )
    return [prj.joinpath(sd) for sd in subdirs]



def prj_report(prj):
    return prj / "report.pdf"


def prj_gitignore(prj):
    return prj / ".gitignore"


def prj_tmp_dir(prj):
    return prj / "tmp"

def prj_data_dir(prj):
    return prj / "data"


def prj_dataset(prj, dataset_date):
    return prj / "data" / "dataset_{0}.xlsx".format(dataset_date)


def prj_dataset_link(prj):
    return prj / "data" / "dataset.xlsx"


def prj_outputs_dir(prj):
    return prj / "outputs"


def prj_proj_dir(prj):
    return prj / "proj"


def prj_metadata(prj):
    return prj / "proj" / "metadata.ini"


def prj_requirements(prj):
    return prj / "proj" / "requirements.txt"


def prj_biblio_dir(prj):
    return prj / "proj" / "biblio"


def prj_biblio_common(prj):
    return prj / "proj" / "biblio" / "common_biblio.bib"


def prj_biblio_specific(prj):
    return prj / "proj" / "biblio" / "prj_biblio.bib"


def prj_docs_dir(prj):
    return prj / "proj" / "docs"


def prj_protocol(prj, protocol_date):
    return prj / "proj" / "docs" / "protocol_{0}.pdf".format(protocol_date)


def prj_protocol_link(prj):
    return prj / "proj" / "docs" / "protocol.pdf"


def prj_src_dir(prj):
    return prj / "src"


def prj_srcfiles(prj):
    src_dir = prj_src_dir(prj)
    py = list(src_dir.glob("*.py"))
    tex = list(src_dir.glob("*.tex"))
    return py + tex


def prj_dontedit(prj):
    return [prj_src_dir(prj) / "__init__.py",
            prj_src_dir(prj) / "_region_.tex"] 


def prj_srcpys(prj):
    return prj_src_dir(prj).glob("*.py")


def prj_srcrs(prj):
    return prj_src_dir(prj).glob("*.R")


def prj_readme(prj):
    return prj / "README.md"


def prj_venv(prj):
    # virtual environment ~/.venv/prj
    return prj / ".venv"


def prj_python(prj):
    return prj_venv(prj) / "bin" / "python"



def freeze_venv(prj):
    """
    Fai il freeze del virtual environments e salvalo in requirements.txt
    """
    cmd = "{0} -m pip freeze > {1}".format(prj_python(prj), prj_requirements(prj))
    os.system(cmd)


def import_data(prj):
    """
    import dataset as a and set up useful symlinks
    """
    dataset_date = input(
        "Insert date of the data extraction (YYYY-MM-DD) or leave blank to skip: "
    ).replace("-", "_")
    if dataset_date != "":
        outfile = prj_dataset(prj, dataset_date)
        symlink = prj_dataset_link(prj)
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


def import_protocol(prj):
    """
    import protocol with date and set up useful symlinks
    """
    msg = "Insert date of the study protocol (YYYY-MM-DD) or leave blank to skip: "
    protocol_date = input(msg).replace("-", "_")
    if protocol_date != "":
        outfile = prj_protocol(prj, protocol_date)
        symlink = prj_protocol_link(prj)
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


# --------------------------------------------------------------------------------
# Project tasks
# --------------------------------------------------------------------------------
help_prj = "Directory da utilizzare per il task."
help_repo = "Repository bitbucket da clonare."


@task(help={"prj": help_prj})
def clean(c, prj="."):
    """
    Pulisce la directory del progetto.
    """
    c.run(f"{clean_cmd}")


@task
def init(c):
    """
    Inizializza un nuovo progetto parzialmente creato da cookiecutter
    """
    # ------------------------------------------------------------
    print("Bibliography setup")
    os.symlink("/home/l/texmf/tex/latex/biblio/biblio.bib",
               os.path.abspath("proj/biblio/common_biblio.bib"))
    subprocess.run(["touch", "proj/biblio/prj_biblio.bib"])
    # -----------------------------------------------------------
    print("Importing protocol")
    import_protocol(".")
    # -----------------------------------------------------------
    print("Importing dataset")
    import_data(".")
    # -----------------------------------------------------------
    print("UV init")
    subprocess.run(["uv", "init", "."])
    subprocess.run(["rm", "-rf", "hello.py"])
    # print("Metadata setup")
    # metadata = {
    #     "customer": customer,
    #     "acronym": acronym,
    #     "title": title,
    #     "created": created,
    #     "url": url,
    # }
    # metadata_file = prj_metadata(prj)
    # configs = configparser.ConfigParser()
    # configs["project"] = metadata
    # with open(metadata_file, "w") as f:
    #     configs.write(f)
    # # -----------------------------------------------------------
    # print("Git setup")
    # cmd = f"git init -b master && git remote add origin {url} && git add . && git commit -m 'Directory setup'"
    # os.system(cmd)
    # -----------------------------------------------------------
    return None


@task(help={"prj": help_prj})
def dataimp(c, prj="."):
    """
    Importa il dataset nella directory del progetto.
    """
    import_data(prj)


@task(help={"prj": help_prj})
def protimp(c, prj="."):
    """
    Importa il protocollo nella directory del progetto.
    """
    import_protocol(prj)


@task(help={"prj": help_prj})
def venvrepl(c, prj="."):
    """
    Usa l'environment del progetto in maniera interattiva.
    """
    os.system(prj_python(prj))


@task(help={"prj": help_prj})
def venvsetup(c, prj="."):
    """
    Crea (o azzera) il virtual environment e installa i requirements.txt
    """
    setup_venv(prj)


@task(help={"prj": help_prj})
def venvfreeze(c, prj="."):
    """
    A fine progetto fai il freeze dei requirements per riproducibilità.
    """
    freeze_venv(prj)


@task(help={"prj": help_prj})
def viewdoc(c, prj="."):
    """
    Mostra la documentazione del progetto (file proj/docs/*.pdf).
    """
    cmd = "{0} {1}/proj/docs/*.pdf".format(pdf_viewer, prj)
    c.run(cmd)


@task(default=True, help={"prj": help_prj})
def edit(c, prj="."):
    """
    Edita i file rilevanti del progetto con Emacs.
    """
    # evita __init__.py nel buffer di emacs
    dontedit = prj_dontedit(prj)
    src_edit = [f for f in prj_srcfiles(prj) if f not in dontedit]
    proj_files = [prj_readme(prj), prj_requirements(prj)]
    all_files = proj_files + src_edit
    relative_paths = " ".join([str(f.relative_to(prj)) for f in all_files])
    cmd = "cd {0} && {1} {2} &".format(prj, editor, relative_paths) # niente da fare
    c.run(cmd)
    # subprocess.Popen(cmd.split(" ")) # niente fixa

@task(help={"prj": help_prj})
def vscode(c, prj="."):
    """
    Edita la cartella con Codium (vscode).
    """
    c.run("codium {0}".format(prj))


@task(help={"prj": help_prj})
def runpys(c, prj="."):
    """
    Esegue i file src/*.py nella directory radice del progetto.
    """
    pys = prj_srcpys(prj)
    if pys:
        for py in pys:
            print("Executing {0}.".format(py))
            c.run("cd {0} && ./{1} {2}".format(prj,
                                               prj_python(prj).relative_to(prj),
                                               py.relative_to(prj)))

@task(help={"prj": help_prj})
def runrs(c, prj="."):
    """
    Esegue i file src/*.R nella directory radice del progetto e ne salva l'output in
    tmp
    """
    rs = prj_srcrs(prj)
    if rs:
        for r in rs:
            infile = r
            outfile = prj_tmp_dir(prj) / (str(r.stem) + ".txt")
            # outfile = Path("tmp") / (str(r.stem) + ".txt")
            print("Executing {0} (output in {1})".format(infile, outfile))
            cmd = "cd {0} && R CMD BATCH --no-save --no-restore {1} {2}".format(
                prj,
                infile.relative_to(prj),
                outfile.relative_to(prj)
            )
            c.run(cmd)


@task(help={"prj": help_prj})
def report(c, prj="."):
    """
    Esegue pdflatex/pythontex su src/report.tex nella directory radice del progetto e visualizza il pdf.
    """
    ln = "ln -s src/report.tex"
    pdflatex = "pdflatex report"
    pythontex = "pythontex --interpreter python:{0} report".format(
        prj_python(prj).expanduser().relative_to(prj)
    )
    biber = "biber report"
    pdf_view = "{0} report.pdf".format(pdf_viewer)
    c.run(
        "cd {0} && {1} && {2} && {3} && {4} && {5} && {6} && {7} && {8}".format(
            prj, ln, pdflatex, biber, pythontex, pdflatex, pdflatex, pdf_view, clean_cmd
        )
    )


   
@task(help={"prj": help_prj})
def zip(c, prj="."):
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

   
@task(help={"prj": help_prj})
def tgrep(c, prj="."):
    """
    Invia il report.pdf via telegram nella chat lavoro.
    """
    the_report = prj_report(prj).resolve()
    if not the_report.exists():
        raise ValueError("Non esiste {}.".format(the_report))
    c.run("winston_sends {} group::lavoro".format(the_report))


@task(help={"prj": help_prj})
def tgout(c, prj="."):
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


@task(help={"prj": help_prj})
def tgzip(c, prj="."):
    """
    Invia il malloppone zippato via telegram nella chat lavoro
    """
    zip = Path("/tmp/{0}.zip".format(prj))
    if not zip.exists():
        raise ValueError("Non esiste {}.".format(zip))
    c.run("winston_sends {} group::lavoro".format(zip))

# @task(help={"prj": help_prj})
# def lint(c, prj="."):
#     """
#     Esegue il linter (flake8) nella cartella src.
#     """
#     c.run("cd {0} && flake8 src".format(prj))


# @task(help={"prj": help_prj})
# def mypy(c, prj="."):
#     """
#     Esegue mypy nella cartella src del progetto.
#     """
#     c.run("cd {0} && mypy src".format(prj))


# @task(help={"prj": help_prj})
# def format(c, prj="."):
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
