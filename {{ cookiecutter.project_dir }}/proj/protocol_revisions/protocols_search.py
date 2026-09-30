import polars as pl
from pylbmisc.ctg import Protocols

filters1 = [
    pl.col("phases").cast(pl.String).str.contains("PHASE2"),
    pl.col("n_arms") == 1,
    pl.col("primary_test_type").cast(pl.String).str.contains("NON_INFERIORITY"),
]
phase2_1arm_ninf = Protocols(*filters1)
# phase2_1arm_ninf.dump("phase2_1arm_ninf", tg_results=False)
phase2_1arm_ninf.results["nct_number"]

filters2 = [
    pl.col("phases").cast(pl.String).str.contains("PHASE2"),
    pl.col("n_arms") == 1,
    (pl.col("title") + pl.col("summary"))
    .str.to_lowercase()
    .str.contains("de[- ]escalation"),
]
phase2_1arm_deescalation = Protocols(*filters2)
phase2_1arm_deescalation.results["nct_number"]
# phase2_1arm_deescalation.dump("phase2_1arm_deescalation", tg_results=False)

# # 1 solo su tempo all'evento?
# filters3 = filters2 + [
#     pl.col("primary_outcomes").str.to_lowercase().str.contains("time|survival")
# ]
# phas2_1arm_deescalation_time = Protocols(*filters3)
# view(phas2_1arm_deescalation_time.results)


(all_results := (phase2_1arm_ninf + phase2_1arm_deescalation)).dump(
    "all_results", tg_results=False
)
