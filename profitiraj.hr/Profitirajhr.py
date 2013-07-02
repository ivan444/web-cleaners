#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2011.02.22

Wrapper za arhivu business.hr sitea.

@author: Ivan Krišto

'''

import sys
import re
import urllib
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup

def crawlUrls():
	articleUrls = []
	baseUrls = ["http://www.profitiraj.hr/teme/novosti/", "http://www.profitiraj.hr/teme/profitirajtv/", "http://www.profitiraj.hr/teme/rijec-urednika/", "http://www.profitiraj.hr/teme/poduzetnici/", "http://www.profitiraj.hr/teme/marketing-i-prodaja/", "http://www.profitiraj.hr/teme/osobne-financije/", "http://www.profitiraj.hr/teme/poslovne-financije/", "http://www.profitiraj.hr/teme/slobodna-zanimanja-i-obrti/", "http://www.profitiraj.hr/teme/racunovodstvo-i-porezi/", "http://www.profitiraj.hr/teme/eu_fondovi/", "http://www.profitiraj.hr/teme/edukacija/", "http://www.profitiraj.hr/teme/poduzetnicke-price/"]

	pNext = re.compile(u'<a href="([^"]+)">&gt;</a>', re.U|re.I|re.M|re.DOTALL)

	pArticles = re.compile(u'<div class="item2">.+?<a href="(.+?)">', re.U|re.I|re.M|re.DOTALL)
	
	for url in baseUrls:
		currentUrl = url;
		while True:
			(page, dl) = downloadPage(currentUrl)
			if not dl:
				logging.error("Crawling has failed! Resulting archive may be incomplete!!")
				break	

			# Get article urls
	#		page = page.decode("cp1250")
			articles = pArticles.findall(page)
			logging.debug("Nasao " + str(len(articles)) + " clanaka")
			for a in articles: articleUrls.append(a)

			# Get link for next page
			lnext = pNext.findall(page)
			if len(lnext) == 0: break
			else: currentUrl = lnext[0]

	return articleUrls

# Cleaning patterns
authorP = re.compile('<p class="about">\s*(.+?)\s*</p>', re.I|re.M|re.U|re.DOTALL)
summaryP = re.compile('<p>\s*(.+?)\s*</p>\s*<div style="position: relative; height: 32px; clear: both;">', re.I|re.M|re.U|re.DOTALL)
bodyP = re.compile('<div id="__xclaimwords_wrapper">\s*(.+?)\s*<p id="tagovi">', re.I|re.M|re.U|re.DOTALL)
removeInner = re.compile(u'(<p>.+?[^>]</p>)', re.I|re.M|re.U|re.DOTALL)
def cleanPage(page):
	
	# Build parse tree
	soup = BeautifulSoup(page)

	# Body
	body = bodyP.findall(page)[0]
	body = unicode(body, "utf-8")
	body.replace("</div>", "")
	bodyParafs = removeInner.findall(body)
	body = "".join(["%s" % k for k in bodyParafs])

	# Title
	resultTitle = soup.find('div', {"id":"full"}).findAll(name='h2', recursive=False)
	title = "".join(["%s" % k for k in resultTitle])
	title = unicode(title, "utf-8")

	# Extras
	extras = {}

	try:
		author = authorP.findall(page)[0]
		author = unicode(author, "utf-8")
		if author[0:6] == u"Piše: ": author = author[6:]
		extras["author"] = author
	except Exception as e:
		logging.error("Error parsing author! Exception: " + str(e))

#	try:
#		summary = summaryP.findall(page)
#		extras["summary"] = unicode(summary[0], "utf-8")
#	except Exception as e:
#		logging.error("Error parsing summary! Exception: " + str(e))
	
	try:
		related = soup.find('ul', {"class":"related_post"}).findAll(name='a', recursive=True)
		connected = []
		for r in related:
			connected.append(r.get("href"))

		extras["connected"] = connected
	except Exception as e:
		logging.error("Error parsing connected! Exception: " + str(e))


	return (body, title, extras)

