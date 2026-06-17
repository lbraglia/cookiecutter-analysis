import pylbmisc as lb
from pylbmisc.r import *
import pprint
import prjlib as prj   # prj specific common code
import os
testing = interactive = lb.utils.is_interactive()

# # Data import
# # -----------
# # standard/old import
# try:
#     raw_dfs
# except NameError:
#     raw_dfs = lb.io.import_data("data/raw_dataset.xlsx.gpg")
#     dfs, comments = lb.dm.fix_varnames(raw_dfs, return_tfd=True)

# # redcap import
# try:
#     raw_df
# except NameError:
#     raw_df, vd = lb.io.import_redcap()

# if False:
#     lb.io.export_data(raw_dfs, "/tmp/rawdata.xlsx")
#     os.system("libreoffice /tmp/rawdata.xlsx &")
#     os.system("make view-crf &")
#     os.system("make view-protocol &")
#     pprint.pp(vd)


# # Rimozione variabili, eventuale renaming per pulizia codice a valle
# # ------------------------------------------------------------------
# rm = ["scanner_y", "outcome_finale_y","aace_ace_ame", "eu_tirads", "suv_max"]
# ft = {
#     "categoria_ecografica_finale": "eco",
#     "eta": "age",
#     "sesso_0_f_1_m": "sex",
#     "anno": "year",
#     "fumo_0_attivo_1_pregresso_2_mai": "smoke",
# }
# dfs = dfs.drop(columns = rm).rename(columns=ft)


# Coercions/recoding
# ------------------
lb.dm.dump_unique_values(dfs)
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
    lb.dm.to_integer: [
        
    ],
    lb.dm.to_numeric: [
        
    ],
    lb.dm.to_noyes: [
        
    ],
    lb.dm.to_categorical: [
        
    ],
    lb.dm.to_date: [
        
    ],
    lb.dm.mr_split: [
        
    ],
    # livello_educativo: ["titstu"],
    # stato_civile: ["civstat"]
}


# # single dataset
dfs = dfs.set_index("sud_codpaz")
df = lb.dm.Coercer(dfs, df_coercions).coerce()
# # multiple datasets
# clean_df  = lb.dm.Coercer(dfs["df"], df_coercions).coerce()
# clean_df2 = lb.dm.Coercer(dfs["df2"], df2_coercions).coerce()

# stringhe rimanenti
df.select_dtypes("string[pyarrow]").columns.to_list()



# # variable renaming and merging for multiple dataset
# # --------------------------------------------------
# socio = socio.rename(columns={"cognome": "id"})
# mal = mal.rename(columns=lambda x: "mal_" + x if x != "cognome" else "patient_id")
# lav = lav.rename(columns=lambda x: "lav_" + x if x != "cognome" else "patient_id")
# sal = sal.rename(columns=lambda x: "sal_" + x if x != "cognome" else "patient_id")
# bis = bis.rename(columns=lambda x: "bis_" + x if x != "cognome" else "patient_id")
#
# df = functools.reduce(
#     lambda x,y: pd.merge(x, y, on="patient_id", how="left", validate="1:1"),
#     [socio, mal, lav, sal, bis]
# )


# Data validation
# ---------------


# # Variabili derivate
# # ------------------
df = df.assign(
    x=lambda _df: (_df.whatever).astype(""),
    y=lambda _df: (_df.whatever).astype("")
)

# # Keep-rename for final datasets
# # ------------------------------
# keep_rename = {
#     # keep : rename_to
#     "id_paziente": "id",
#     "sesso": "sex",
# }
# df = lb.dm.dfkeeprn(df, keep_rename)

# # Export for analysis
# # -------------------
export_dict = {"db": df, "db_des": df[prj.des_vars]}
lb.io.export_data(export_dict, "tmp/clean", ext=".R")

if False:
    lb.io.export_data(export_dict, "/tmp/final_dbs.xlsx")
    os.system("libreoffice /tmp/final_dbs.xlsx &")
