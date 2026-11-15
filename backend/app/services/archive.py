from __future__ import annotations
import json
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib.parse import urlparse
import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
DEFAULT_COLLECTIONS=("spherex_dr1","spherex_qr3","spherex_dr1_deep","spherex_qr3_deep")
ALLOWED_HOSTS={"irsa.ipac.caltech.edu","nasa-irsa-spherex.s3.us-east-1.amazonaws.com"}
def parse_cloud_access(value):
    if value is None:return []
    try:payload=json.loads(value) if isinstance(value,str) else value
    except (TypeError,json.JSONDecodeError):return []
    found=[]
    def walk(node):
        if isinstance(node,dict):
            for key,item in node.items():
                if key.lower() in {"uri","url","access_url","s3_uri","href"} and isinstance(item,str):found.append(item)
                else:walk(item)
        elif isinstance(node,list):
            for item in node:walk(item)
        elif isinstance(node,str) and node.startswith(("s3://","https://")):found.append(node)
    walk(payload);return list(dict.fromkeys(found))
def validate_archive_url(url):
    p=urlparse(url)
    if p.scheme not in {"https","s3"}:raise ValueError("Archive URL must use HTTPS or S3.")
    if p.scheme=="https" and p.hostname not in ALLOWED_HOSTS:raise ValueError("Archive URL host is not allow-listed.")
    if p.scheme=="s3" and p.netloc!="nasa-irsa-spherex":raise ValueError("Unapproved SPHEREx S3 bucket.")
    return url
def _query_collection(ra,dec,radius_deg,collection):
    from astroquery.ipac.irsa import Irsa
    coord=SkyCoord(ra=ra*u.deg,dec=dec*u.deg,frame="icrs")
    table=Irsa.query_sia(pos=(coord,radius_deg*u.deg),collection=collection)
    records=[]
    for row in table:
        item={}
        for key in table.colnames:
            value=row[key];item[str(key).lower()]=None if np.ma.is_masked(value) else str(value)
        item["collection"]=collection;item["cloud_urls"]=parse_cloud_access(item.get("cloud_access"))
        if item.get("access_url"):validate_archive_url(item["access_url"])
        records.append(item)
    return records
def search_spherex_sia(ra,dec,radius_deg,collections=DEFAULT_COLLECTIONS):
    if not 0<=ra<360 or not -90<=dec<=90 or not 0<radius_deg<=1:raise ValueError("Invalid ICRS coordinates or radius.")
    records=[];failures=[]
    with ThreadPoolExecutor(max_workers=max(1,min(4,len(collections)))) as pool:
        futures={pool.submit(_query_collection,ra,dec,radius_deg,c):c for c in collections}
        for future in as_completed(futures):
            collection=futures[future]
            try:records.extend(future.result())
            except Exception as exc:failures.append({"collection":collection,"error":type(exc).__name__})
    records.sort(key=lambda r:r.get("t_min") or r.get("date_obs") or "")
    return {"observations":records,"partial":bool(failures),"collection_failures":failures}
