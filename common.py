#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    ***** BEGIN LICENSE BLOCK *****
    
    Copyright © 2012 Center for History and New Media
                     George Mason University, Fairfax, Virginia, USA
                     http://zotero.org
    
    This file is part of Zotero.
    
    Zotero is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    Zotero is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.
    
    You should have received a copy of the GNU Affero General Public License
    along with Zotero.  If not, see <http://www.gnu.org/licenses/>.
    
    ***** END LICENSE BLOCK *****
"""

"""Updates tests to fix data mismatches."""

import sys, time, gzip, json, urllib, io

TEST_URL = "http://zotero-translator-tests.s3-website-us-east-1.amazonaws.com/"

def fetch_json(path, gzipped=False):
	"""Fetches a given JSON file from TEST_URL, and returns the contained JSON data"""
	fp = urllib.urlopen(TEST_URL+path)
	response = fp.getcode()
	if response != 200:
		raise Exception('Server returned an error: '+str(response));
	if gzipped:
		data = json.load(gzip.GzipFile(fileobj=io.BytesIO(fp.read())))
	else:
		data = json.load(fp)
	fp.close()
	return data