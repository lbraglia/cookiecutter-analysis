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
#     raw_dfs = lb.io2.import_data("data/raw_dataset.xlsx.gpg")
#     dfs, comments = lb.dm2.fix_varnames(raw_dfs, return_tfd=True)

# # redcap import
# try:
#     raw_df
# except NameError:
#     raw_df, vd = lb.io2.import_redcap()

# if False:
#     lb.r.view(raw_dfs)
#     os.system("make view-crf &")
#     os.system("make view-protocol &")
#     pprint.pp(vd)


# # Rimozione variabili, eventuale renaming per pulizia codice a valle
# # ------------------------------------------------------------------
# ft = {
#     "categoria_ecografica_finale": "eco",
#     "eta": "age",
#     "sesso_0_f_1_m": "sex",
#     "anno": "year",
#     "fumo_0_attivo_1_pregresso_2_mai": "smoke",
# }
# dfs = dfs.select(ft.keys()).rename(ft)


# Coercions/recoding
# ------------------
lb.dm2.dump_unique_values(dfs)
lb.dm2.names_list(dfs)


# using mc function factory for quicker categoricals
livello_educativo = lb.dm2.enum_parser(["Media", "Superiore", "Laurea"])
stato_civile = lb.dm2.enum_parser(
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
    # lb.dm2.identity: [],
    lb.dm2.to_integer: [
        
    ],
    lb.dm2.to_numeric: [
        
    ],
    lb.dm2.to_noyes: [
        
    ],
    lb.dm2.to_sex: [
        
    ],
    lb.dm2.to_date: [
        
    ],
    # livello_educativo: ["titstu"],
    # stato_civile: ["civstat"]
}

mc = {
    lb.dm2.to_multiple_choices: [
        
    ],
}

# # single dataset
df = lb.dm2.Coercer(dfs, df_coercions, mc).coerce()
# # multiple datasets
# clean_df  = lb.dm2.Coercer(dfs["df"], df_coercions).coerce()
# clean_df2 = lb.dm2.Coercer(dfs["df2"], df2_coercions).coerce()



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
# krn = {
#     # keep : rename_to
#     "id_paziente": "id",
#     "sesso": "sex",
# }
# df = df.select(krn.keys()).rename(krn)

# # Export for analysis
# # -------------------
export_dict = {"db": df, "db_des": df[prj.des_vars]}
lb.io2.export_data(export_dict, "tmp/clean", ext=".R")

if False:
    lb.r.view(export_dict)
