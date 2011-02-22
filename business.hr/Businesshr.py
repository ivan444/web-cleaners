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
		logging.debug("Found " + str(len(articles)) + " articles!")
		for a in articles: articleUrls.append(baseUrl + a)

		# Get link for next page
		lnext = pNext.findall(page)
		if len(lnext) == 0: break
		else: sufix = lnext[0]
		
	return articleUrls

# Cleaning patterns
dateP = re.compile('<h5>\((.+?)\)</h5>\s+<h1 style="display:block;padding-bottom:10px;">', re.I|re.M|re.U|re.DOTALL)
titleP = re.compile('<h1 style="display:block;padding-bottom:10px;">(.+?)</h1>', re.I|re.M|re.U|re.DOTALL)
bodyP = re.compile('<h4 style="display:block;">(.+?)</h4>', re.I|re.M|re.U|re.DOTALL)

def cleanPage(page):
	page = page.decode("cp1250")
	
	date = dateP.findall(page)
	title = titleP.findall(page)
	body = bodyP.findall(page)
	
	return (body[0], title[0], {"date": date[0]})
	
