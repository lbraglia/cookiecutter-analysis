import pylbmisc as lb
from pylbmisc.r import *
testing = lb.utils.is_interactive()
# from functools import reduce

# # Data import
# # -----------
dfs = lb.io.import_data("data/raw_dataset.xlsx") # multiple custom dataset
df = lb.io.import_redcap()  # redcap export (data/DATA.csv, data/LABELS.csv)


# # Sanitize variable names, keeping as comment
# # -------------------------------------------
dfs, comments = lb.dm.fix_varnames(dfs, return_tfd=True)

if testing:
    if isinstance(dfs, dict):
        print(list(dfs.keys()))


# # Renaming eventuale per evitare che il codice a valle si sporchi
# # ---------------------------------------------------------------
# ft = {
#     "categoria_ecografica_finale": "eco",
#     "eta": "age",
#     "sesso_0_f_1_m": "sex",
#     "anno": "year",
#     "fumo_0_attivo_1_pregresso_2_mai": "smoke",
# }
# dfs = dfs.rename(columns=ft)

# rimozione variabili da non considerare
# --------------------------------------
# rm = ["scanner_y", "outcome_finale_y",
#       "aace_ace_ame", "eu_tirads",
#       "suv_max"
# ]
# dfs = dfs.drop(columns = rm)


# # Unique values inspection/monitoring
# # -----------------------------------
lb.dm.dump_unique_values(dfs)


# # Type coercions: help(lb.dm.Coercer)
# # -----------------------------------
# # dput variable names
lb.dm.names_list(dfs)


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
    # variabili che si vogliono tenere immodificate con keep_coerced_only in
    # Coercer.coerce sotto identity    
    # lb.dm.identity: [],
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

# stringhe rimanenti
df.select_dtypes("string[pyarrow]").columns.to_list()



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
