from pathlib import Path
import pylbmisc as lb
outdir = Path("randomization/")

# Parameters
the_seed = None
n = None
# i centri DEBBONO essere il PRIMO criterio di stratificazione
strata = {"centres": ["ausl_re"],
          # "agecl": ["<18", "18-65", ">65"]
          }

# list generation
randlist = lb.rand.List(seed = the_seed, n = n, strata = strata)
randlist
randlist.stats()

# export
if not outdir.exists():
    outdir.mkdir()
randlist.to_txt(outdir / "all_lists.txt")
randlist.to_csv(outdir)
