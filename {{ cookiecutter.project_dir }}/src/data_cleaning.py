import os
import prjlib as prj
import pylbmisc as lb
from pylbmisc import dm2 as dm
from pylbmisc import io2 as io
from pprint import pp
from pylbmisc.r import *

testing = interactive = lb.utils.is_interactive()

# Data import
# -----------
# # standard/old import
# try:
#     raw_df
# except NameError:
#     raw_df = io.import_data("data/raw_dataset.xlsx.gpg")
#     raw_df, vd = dm.fix_varnames(raw_df, return_tfd=True)

# redcap import
try:
    raw_df
except NameError:
    df, raw_df, labels, vd = io.import_redcap(idvarprog=0)

if False:
    lb.r.view(df)
    os.system("make view-crf &")
    os.system("make view-protocol &")
    pp(vd)

    
# Coercions/recoding
# ------------------
dm.dump_unique_values(raw_df)
dm.names_list(raw_df)


# using mc function factory for quicker categoricals
livello_educativo = dm.enum_parser(["Media", "Superiore", "Laurea"])
stato_civile = dm.enum_parser(
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
    # dm.identity: [],
    dm.to_integer: [
        
    ],
    dm.to_numeric: [
        
    ],
    dm.to_noyes: [
        
    ],
    dm.to_sex: [
        
    ],
    dm.to_date: [
        
    ],
    # livello_educativo: ["titstu"],
    # stato_civile: ["civstat"]
}

mc = {
    dm.to_multiple_choices: [
        
    ],
}

# # single dataset
df = dm.Coercer(df, df_coercions, mc).coerce()
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
# df = df.with_columns(
#     date=lb.dm2.to_date("date"),
#     date_dmy=lb.dm2.to_date_dmy("date_dmy"),
#     date_dmy2=lb.dm2.date_parser("%d/%m/%Y")("date_dmy2"),
#     da_state=lb.dm2.enum_parser(levels=["Ohio", "Nevada"], labels=["aio", "gal"])(
#         "state"
#     ),
# )


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
io.export_data(export_dict, "tmp/clean", ext=[".R", ".pkl"])
if False:
    lb.r.view(export_dict)

