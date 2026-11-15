from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor,as_completed
import pyvo

CATALOG_QUERIES={
"allwise":"""SELECT TOP 5000 designation, ra, dec, w1mpro, w1sigmpro, w2mpro, w2sigmpro, w3mpro, w3sigmpro, w4mpro, w4sigmpro, ext_flg FROM fp_psc WHERE 1=CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{ra},{dec},{radius}))""",
"catwise":"""SELECT TOP 5000 source_name, ra, dec, pmra, pmdec, w1mpro, w1sigmpro, w2mpro, w2sigmpro FROM catwise_2020 WHERE 1=CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{ra},{dec},{radius}))""",
"gaia":"""SELECT TOP 5000 source_id, ra, dec, phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag, pmra, pmdec, parallax FROM gaia_dr3_source WHERE 1=CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{ra},{dec},{radius}))"""
}

def query_catalogs(tap_url:str,ra:float,dec:float,radius_deg:float):
    if not 0<=ra<360 or not -90<=dec<=90 or not 0<radius_deg<=1:raise ValueError("Invalid ICRS coordinates or radius.")
    def query_one(name,adql):
        service=pyvo.dal.TAPService(tap_url)
        return name,service.search(adql.format(ra=f"{ra:.8f}",dec=f"{dec:.8f}",radius=f"{radius_deg:.6f}"),maxrec=5000).to_table()
    tables={};failures=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures={pool.submit(query_one,name,sql):name for name,sql in CATALOG_QUERIES.items()}
        for future in as_completed(futures):
            name=futures[future]
            try:_,tables[name]=future.result()
            except Exception as exc:failures.append({"catalog":name,"error":type(exc).__name__})
    return tables,failures
