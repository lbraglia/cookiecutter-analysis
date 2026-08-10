import polars as pl
from pylbmisc.ctg import Protocols

search = "length of stay"

# primary outcome search
primary_search = Protocols(
    pl.col("primary_outcome_measures").str.contains(search)
).dump("po_" + search.lower().replace(" ", "_"))

# # any outcome search: if previous fails...
# any_search = Protocols(
#     pl.col("all_outcomes").str.contains(search)
# ).dump("ao_" + search.lower().replace(" ", "_"))





