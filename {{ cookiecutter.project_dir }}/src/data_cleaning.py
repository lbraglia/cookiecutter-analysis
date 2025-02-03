import pylbmisc as lb
# from pprint import pprint

# Data import
# -----------
dfs = lb.io.import_data("data/raw_dataset.xlsx")

# Sanitize variable names, keeping as comment
# -------------------------------------------
dfs, comments = lb.dm.sanitize_varnames(dfs)

# Unique values inspection/monitoring
# -----------------------------------
lb.dm.dump_unique_values(dfs)

    
# Type coercions: help(lb.dm.Coercer)
# -----------------------------------
# # dput variable names
# for k, df in dfs.items():
#     print(k)
#     pprint(df.columns.to_list())

# # custom coercers
# def _sano(x):
#     return lb.dm.to_categorical(x, ["Sano", "Paziente"])

# def _numeric_insight(x):
#     ft = {"Male": 1,
#           "Non saprei": 2,
#           "Bene":  3}
#     return x.map(ft)
#
# df_coercions = {
#     lb.dm.to_sex    : ["sex"],
#     _sano           : ["sano"]: ,
#     _numeric_insight: ["insight_punteggi_1"]
# }
# 
# df2_coercions = {
#     lb.dm.to_sex    : ["sex"],
#     _sano           : ["sano"]: ,
#     _numeric_insight: ["insight_punteggi_1"]
# }
#
# # prima di questo passaggio impostare gli indici in dfs per il report dei NA?
# df  = lb.dm.Coercer(dfs["df"], df_coercions).coerce()
# df2 = lb.dm.Coercer(dfs["df2"], df2_coercions).coerce()


# # Export for analysis
# # -------------------
# dfs2 = {"df": df, "df2": df2}
# lb.io.export_data(dfs2, "tmp/clean", ext = "pkl")
