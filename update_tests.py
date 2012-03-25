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

import os, re, time, argparse
from common import *

TRANSLATORS_DIRECTORY = "/Users/simon/Desktop/Development/FS/zotero/translators"
UPDATE_LASTUPDATED = False

parser = argparse.ArgumentParser(description='Updates items to correspond with the most recent '
	+'test run')
parser.add_argument('translator', help='path to translator to update')
parser.add_argument('-d', '--date', help='use test runs from DATE')
args = parser.parse_args()
date = args.date or time.strftime("%Y-%m-%d", time.gmtime())

# Load translator file
fp = open(args.translator, 'r+')
translator = fp.read()
# Read info
m = re.match(r'^\s*{[\S\s]*?}\s*?[\r\n]', translator)
info = json.loads(m.group(0))
# Read tests
m = re.search(r'(/\*\* BEGIN TEST CASES \*\*/\s*var testCases =\s*)([\s\S]*?)(\s*/\*\* END TEST CASES \*\*/)',
	translator)
tests = json.loads(m.group(2))

# Load index
index = fetch_json(date+"/index.json")

# Find Gecko testResults file
gecko_testResults = [file for file in index if re.match(r'^testResults-g-(.*)\.json$', file)]
if not gecko_testResults:
	raise Exception('No test results for '+date+' available')
gecko_testResults = fetch_json(date+"/"+gecko_testResults[0], True)

# Find translator
translator_results = [translator_results for translator_results in gecko_testResults['results']
	if translator_results['translatorID'] == info['translatorID']];
if not gecko_testResults:
	raise Exception('Translator '+info['translatorID']+' not found in test results')
translator_results = translator_results[0]

# Update unknown tests
if not translator_results['unknown']:
	raise Exception('Translator has no data mismatches to update')
for testResult in translator_results['unknown']:
	for test in tests:
		if test['url'] == testResult['url']:
			test['items'] = testResult['itemsReturned']

# Save
newTranslator = translator.replace(m.group(0),
	m.group(1)+json.dumps(tests, indent=64).replace(' ' * 64, '\t')+m.group(3))
if newTranslator == translator:
	raise Exception('Could not update tests')

# Write out translator
fp.seek(0)
fp.truncate(0)
fp.write(newTranslator)