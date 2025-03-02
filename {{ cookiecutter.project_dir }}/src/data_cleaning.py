import pylbmisc as lb
from pylbmisc.utils import table, dput
import pprint

# from pprint import pprint

# # Data import
# # -----------
dfs = lb.io.import_data("data/raw_dataset.xlsx")


# # Sanitize variable names, keeping as comment
# # -------------------------------------------
dfs, comments = lb.dm.sanitize_varnames(dfs)
type(dfs)  # single or dict of datasets?


# # Unique values inspection/monitoring
# # -----------------------------------
lb.dm.dump_unique_values(dfs)


# # Type coercions: help(lb.dm.Coercer)
# # -----------------------------------
# # dput variable names
if False:
    # single dataset
    pprint.pp(dfs.columns.to_list())
    # # multiple datasets
    # for k, df in dfs.items():
    #     print(k, "\n")
    #     pprint.pp(df.columns.to_list())


# prepare coercion
def to_variable(x):
    categs = ['IgG', 'IgA', 'LC', 'IgD', 'IgM', 'NS']
    rval = lb.dm.to_categorical(x, categories=categs)
    return rval


df_coercions = {
    lb.dm.to_sex: ["sex"],
    to_variable: ["variable"],
}


# # single dataset
df = lb.dm.Coercer(dfs, df_coercions).coerce()
# # multiple datasets
# df  = lb.dm.Coercer(dfs["df"], df_coercions).coerce()
# df2 = lb.dm.Coercer(dfs["df2"], df2_coercions).coerce()


# # Variabili derivate
# # ------------------


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
