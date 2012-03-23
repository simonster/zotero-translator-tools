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

"""Sets compatibility on Zotero translators by fetching the latest test results. Currently only
adds compatibility."""

import calendar, gzip, io, json, os, re, sets, sys, time, urllib

TRANSLATORS_DIRECTORY = "/Users/simon/Desktop/Development/FS/zotero/translators"
TEST_URL = "http://zotero-translator-tests.s3-website-us-east-1.amazonaws.com/"
UPDATE_LASTUPDATED = False

gt = time.gmtime()
if len(sys.argv) > 1:
	date = sys.argv[1]
else:
	date = time.strftime("%Y-%m-%d", gt)
timestamp = time.strftime("%Y-%m-%d %H:%M:%S", gt)

def fetch_json(file, gzipped=False):
	"""Fetches a JSON file from the given test URL"""
	fp = urllib.urlopen(TEST_URL+date+"/"+file)
	response = fp.getcode()
	if response != 200:
		raise Exception('Server returned an error: '+str(response));
	if gzipped:
		data = json.load(gzip.GzipFile(fileobj=io.BytesIO(fp.read())))
	else:
		data = json.load(fp)
	fp.close()
	return data

# Load index
index = fetch_json("index.json")

# Loop through test results to figure out compat
translator_compat = {}
for result_file in index:
	m = re.match(r'^testResults-([a-z]+)-(.*)\.json$', result_file)
	if not m:
		continue
	browser = m.group(1)
	if browser == 'g':
		# No need to load Gecko results
		continue
	
	results = fetch_json(result_file, True)
	for translator_results in results['results']:
		# Make sure translation succeeded
		succeeded = translator_results['succeeded'] and (not translator_results['pending']) \
			and (not translator_results['failed']) and (not translator_results['unknown'])
		if not succeeded:
			continue
		
		# Add to compat
		translatorID = translator_results['translatorID']
		if translatorID in translator_compat:
			[translator_compat[translatorID].add(char) for char in browser]
		else:
			translator_compat[translatorID] = sets.Set(browser)

# Loop through translators
for translator_file in os.listdir(TRANSLATORS_DIRECTORY):
	if translator_file.endswith('.js'):
		# Read existing translator
		fp = open(os.path.join(TRANSLATORS_DIRECTORY, translator_file), 'r+')
		try:
			translator = fp.read()
			
			# Parse JSON header
			m = re.match(r'^\s*{[\S\s]*?}\s*?[\r\n]', translator)
			info = json.loads(m.group(0))
			
			if info['translatorID'] in translator_compat:
				if 'browserSupport' in info:
					browserSupport = info['browserSupport']
				else:
					browserSupport = 'g'
				
				compat = translator_compat[info['translatorID']]
				diff = compat.difference(browserSupport)
				if diff:
					# Build new browserSupport string
					newBrowserSupport = ''
					for browser in 'gcsib':
						if browser in compat or browser in browserSupport:
							newBrowserSupport += browser
					
					print 'Updating '+info['label']+': '+browserSupport+' -> '+newBrowserSupport
					# Replace or add browserSupport
					if 'browserSupport' in info:
						newTranslator = re.sub(r'"browserSupport"(\s*):(\s*)"[^"]*"',
							r'"browserSupport"\1:\2"'+newBrowserSupport+'"',
							translator)
					else:
						newTranslator = re.sub(r's/(\s*)"priority"(\s*):(\s*)([0-9]+),',
							r'\11"priority"\2:\3\4,\1"browserSupport"\2:\3"'+newBrowserSupport+'",',
							translator)
					
					if newTranslator == translator:
						print "ERROR: Could not update browserSupport"
						continue;
						
					# Update lastUpdated
					if UPDATE_LASTUPDATED or "s" in diff or "c" in diff:
						newTranslator = re.sub(r'"lastUpdated"(\s*):(\s*)"[^"]*"',
							r'"lastUpdated"\1:\2"'+timestamp+'"', newTranslator)
					
					# Write out translator
					fp.seek(0)
					fp.truncate(0)
					fp.write(newTranslator)
		finally:
			fp.close()