import polars as pl
from pylbmisc.ctg import Protocols
from pylbmisc.r import view
from pylbmisc.utils import is_interactive

filters2 = [
    pl.col("n_arms") == 1,
    pl.col("phases").cast(pl.String).str.contains("PHASE2"),
    pl.col("primary_test_type").cast(pl.String).str.contains("NON_INFERIORITY"),
]
nodert = Protocols(*filters2)
if is_interactive():
    view(nodert.results)
nodert.dump("protocols_search_results", tg_results=False)
