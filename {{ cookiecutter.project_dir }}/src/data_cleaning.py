import pylbmisc as lb
from pylbmisc.utils import dput, interactive, table, view
import pprint
# from functools import reduce

# # Data import
# # -----------
dfs = lb.io.import_data("data/raw_dataset.xlsx")


# # Sanitize variable names, keeping as comment
# # -------------------------------------------
dfs, comments = lb.dm.fix_varnames(dfs, return_tfd=True)

if interactive():
    if isinstance(dfs, dict):
        print(list(dfs.keys()))


# # Unique values inspection/monitoring
# # -----------------------------------
lb.dm.dump_unique_values(dfs)


# # Type coercions: help(lb.dm.Coercer)
# # -----------------------------------
# # dput variable names
if interactive():
    # multiple datasets
    if isinstance(dfs, dict):
        for k, df in dfs.items():
            print(k, "\n")
            pprint.pp(df.columns.to_list())
    else:
        pprint.pp(dfs.columns.to_list())


# prepare coercion
def to_variable(x):
    levels = [0, 1, 2, 3, 4, 5]
    labels = ["IgG", "IgA", "LC", "IgD", "IgM", "NS"]
    return lb.dm.to_categorical(x, levels=levels, labels=labels)


# using mc function factory for quicker categoricals
livello_educativo = lb.dm.mc(["Media", "Superiore", "Laurea"])
stato_civile = lb.dm.mc(
    levels=[0, 1, 2, 3, 4],
    labels=["Sposata/Convivente",
            "Divorziata/Separata/Vedova",
            "Nubile",
            "Sposata/Convivente",
            "Divorziata/Separata/Vedova"]
)


df_coercions = {
    lb.dm.to_sex: ["sex"],
    to_variable: ["variable"],
    livello_educativo: ["titstu"],
    stato_civile: ["civstat"]
}


# # single dataset
dfs = dfs.set_index("sud_codpaz")
df = lb.dm.Coercer(dfs, df_coercions).coerce()
# # multiple datasets
# df  = lb.dm.Coercer(dfs["df"], df_coercions).coerce()
# df2 = lb.dm.Coercer(dfs["df2"], df2_coercions).coerce()


# # variable renaming for multiple dataset
# socio = socio.rename(columns={"cognome": "id"})
# mal = mal.rename(columns=lambda x: "mal_" + x if x != "cognome" else "id")
# lav = lav.rename(columns=lambda x: "lav_" + x if x != "cognome" else "id")
# sal = sal.rename(columns=lambda x: "sal_" + x if x != "cognome" else "id")
# bis = bis.rename(columns=lambda x: "bis_" + x if x != "cognome" else "id")


# # merging multiple dataset
# df = pd.merge(socio, mal,
#               left_on="id",
#               right_on="id",
#               suffixes=(None, None))


# def merger(x, y):
#     return pd.merge(x, y,
#                     left_on=["id", "time"],
#                     right_on=["id", "time"],
#                     suffixes=(None, None))


# df = reduce(merger, [df, lav, sal, bis])


# # Variabili derivate
# # ------------------
df = df.assign(
    x=lambda _df: (_df.whatever).astype(""),
    y=lambda _df: (_df.whatever).astype("")
)

# # Keep-rename for final datasets
# # ------------------------------
keep_rename = {
    # keep : rename_to
    "id_paziente": "id",
    "sesso": "sex",
}


keep = list(keep_rename.keys())
df = df[keep]  #.rename(columns=keep_rename)

# # Export for analysis
# # -------------------
lb.io.export_data(df, "tmp/clean_df")
# lb.io.export_data({"df": df, "df2": df2}, "tmp/clean")
