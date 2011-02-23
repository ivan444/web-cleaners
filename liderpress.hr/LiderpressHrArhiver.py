#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2011.01.13

Wrapper za arhivu liderpress.hr sitea.

@author: Ivan Krišto

'''

import sys
import re
import urllib
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup

#execfile("/home/ivan444/d/eclipse-workspace/WebPageCleaning/liderpress.hr/links.py")

def crawlUrls():
	#if True: return crawled

	articleUrls = []
	baseUrl = "http://www.liderpress.hr/Default.aspx?sid="
	arhiveUrl = baseUrl+"8"
	
	pattern = re.compile("href=\"Default.aspx\?sid=(\d+)\" title=\"[^\"]+\">Više&nbsp;\.\.\.</a>", re.U|re.I|re.M|re.DOTALL)
	
	# Get all years
	(yearsPage, dl) = downloadPage(arhiveUrl)
	yearsIds = pattern.findall(yearsPage)
	logging.debug("Years num: " + str(len(yearsIds)))
	
	for y in yearsIds:
		# Get all months
		(monthsPage, dl) = downloadPage(baseUrl+y)
		monthsIds = pattern.findall(str(monthsPage))
		logging.debug("Months num: " + str(len(monthsIds)))
		
		for m in monthsIds:
			if y == "987" or y == "340":
				(articlesPage, dl) = downloadPage(baseUrl+m)
				articlesIds = pattern.findall(articlesPage)
				logging.debug("Articles num: " + str(len(articlesIds)))
				for a in articlesIds: articleUrls.append(baseUrl + a)
				
			else:
				# Get all days
				(daysPage, dl) = downloadPage(baseUrl+m)
				daysIds = pattern.findall(daysPage)
				logging.debug("Days num: " + str(len(daysIds)))
				
				for d in daysIds:
					# Get all articles
					(articlesPage, dl) = downloadPage(baseUrl+d)
					articlesIds = pattern.findall(articlesPage)
					logging.debug("Articles num: " + str(len(articlesIds)))
					for a in articlesIds: articleUrls.append(baseUrl + a)
	
	return articleUrls

# Cleaning patterns
titleP = re.compile('<h2 class="itemTitle">(.+?)</h2>', re.I|re.M|re.U|re.DOTALL)
summaryP = re.compile('<div class="contentItemSummary"><p>(.+?)</p></div>', re.I|re.M|re.U|re.DOTALL)
majorP = re.compile('<h1 class="majorTitle">(.+?)</h1>', re.I|re.M|re.U|re.DOTALL)
bodyP = re.compile('<div class="tagLinked">.+?</div>\s*<p>(.+?)</p>\s*<div class="publishedDate">', re.I|re.M|re.U|re.DOTALL)                                                     
dateP = re.compile('<div class="publishedDate">(.+?)</div>', re.I|re.M|re.U|re.DOTALL)
conWrapP = re.compile('<h1>Vezani .lanci</h1>.*?<ul>(.+?)</ul>', re.I|re.M|re.U|re.DOTALL)
conelP = re.compile('.*?<li>.*?<a href="Default.aspx\?sid=(\d+)".+?</li>', re.I|re.M|re.U|re.DOTALL)

def cleanEntities(s):
	s = s.replace(u"&scaron;", u"š")
	s = s.replace(u"&Scaron;", u"Š")
	s = s.replace(u"&quot;", u"\"")
	return s

def getSoup(page, encoding):
	try:
		soup = BeautifulSoup(page, fromEncoding=encoding)
	except UnicodeEncodeError:
		soup = BeautifulSoup(page.decode(encoding), fromEncoding=encoding)
	return soup

def cleanPage(page):
	#page = page.decode("utf_8")
	page = unicode(page, "utf-8")
	
	logging.debug("Cleaning!")
	#soup = getSoup(page, "utf-8")
	soup = BeautifulSoup(page)
	result = soup.find('div', {"id":"__phlinews"}).findAll(name='p', recursive=False)
	body = "".join(["%s" % k for k in result])
	body = unicode(body, "utf-8")
	
	title = titleP.findall(page)
	summary = summaryP.findall(page)
	major = majorP.findall(page)
	#body = bodyP.findall(page)
	date = dateP.findall(page)
	
	extras = {"date": date[0], "major-title": cleanEntities(major[0]), "summary": cleanEntities(summary[0])}
	
	lis = conWrapP.findall(page)
	if len(lis) > 0:
		ids = conelP.findall(lis[0])
		if len(ids) > 0:
			extras["connected-sid"] = str(ids)
	
	logging.debug("Cleaned!")
	return (cleanEntities(body), cleanEntities(title[0]), extras)	

#if __name__ == '__main__':
#	url = "http://www.liderpress.hr/Default.aspx?sid=846"
#	page = urllib.urlopen(url).read()
#	(body, title, extras) = cleanPage(page)
#	print "TITLE: " + title
#	print extras
#	print "BODY: " + body
