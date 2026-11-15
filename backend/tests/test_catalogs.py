from astropy.table import Table
from app.services.catalogs import match_catalog,classify_candidate,MatchResult

def test_catalog_match_within_two_arcseconds():
 table=Table({"ra":[10.0],"dec":[20.0]})
 result=match_catalog(10.0001,20.0,table,"test")
 assert result.matched and result.catalog_index==0

def test_missing_catalog_match_is_not_proof_of_discovery():
 no=MatchResult(False,None,None,None)
 assert classify_candidate(8,no,no,no)=="NEW_CANDIDATE"

def test_proper_motion_label_requires_catalog_match():
 no=MatchResult(False,None,None,None)
 assert classify_candidate(8,no,no,no,motion_significance=5)=="NEW_CANDIDATE"
 yes=MatchResult(True,0.4,"Gaia",0)
 assert classify_candidate(8,yes,no,no,motion_significance=5)=="PROPER_MOTION_SHIFT"
