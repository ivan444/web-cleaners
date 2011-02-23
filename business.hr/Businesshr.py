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
	baseUrl = "http://www.business.hr"
	sufix = "/hr/Naslovnica/Sve-vijesti"
	
	pNext = re.compile(u'<li class="next"><a href="(.+?)" rel', re.U|re.I|re.M|re.DOTALL)

	pArticles = re.compile(u'<dt><a href="(.+?)">.+?dt>\s+<dd class="related-category">', re.U|re.I|re.M|re.DOTALL)
	
	while True:
		(page, dl) = downloadPage(baseUrl+sufix)
		if not dl:
			logging.error("Crawling has failed! Resulting archive may be incomplete!!")
			break	

		# Get article urls
#		page = page.decode("cp1250")
		articles = pArticles.findall(page)
		for a in articles: articleUrls.append(baseUrl + a)

		# Get link for next page
		lnext = pNext.findall(page)
		if len(lnext) == 0: break
		else: sufix = lnext[0]

	return articleUrls

# Cleaning patterns
dateP = re.compile('<p class="date">\s*(.+?)\s*</p>', re.I|re.M|re.U|re.DOTALL)
authorP = re.compile('<p class="author">\s*(.+?)\s*</p>', re.I|re.M|re.U|re.DOTALL)
summaryP = re.compile('<p class="lead">\s*(.+?)\s*</p>', re.I|re.M|re.U|re.DOTALL)
titleP = re.compile('<h1 style="display:block;padding-bottom:10px;">(.+?)</h1>', re.I|re.M|re.U|re.DOTALL)
def cleanPage(page):
	#page = page.decode("cp1250")
	
	soup = BeautifulSoup(page)

	result = soup.find('div', {"id":"article-text"}).findAll(name='p', recursive=False)
	body = "".join(["%s" % k for k in result])
	body = unicode(body, "utf-8")

	resultTitle = soup.find('div', {"id":"article-head"}).findAll(name='h1', recursive=False)
	title = resultTitle[0].contents[0]

	extras = {}
	try:
		date = dateP.findall(page)
		extras["date"] = date[0]
	except Exception as e:
		logging.error("Error parsing date! Exception: " + str(e))

	try:
		author = authorP.findall(page)
		extras["author"] = unicode(author[0], "utf-8")
	except Exception as e:
		logging.error("Error parsing author! Exception: " + str(e))

	try:
		summary = summaryP.findall(page)
		extras["summary"] = unicode(summary[0], "utf-8")
	except Exception as e:
		logging.error("Error parsing summary! Exception: " + str(e))

	return (body, title, extras)
	
