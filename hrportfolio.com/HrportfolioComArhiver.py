#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2011.01.13

Wrapper za arhivu hrportfolio.com sitea.

@author: Ivan Krišto

'''

import sys
import re
import urllib

def crawlUrls():
	articleUrls = []
	baseUrl = "http://hrportfolio.com"
	arhiveUrls = ["/hr/fondovi/fondovi_4_4_0_2/|Vijesti|Arhiva_vijesti|Ostale_vijesti|0/",
				"/hr/fondovi/fondovi_4_2_0_2/|Vijesti|Arhiva_vijesti|Fondovi|1",
				"/hr/fondovi/fondovi_4_3_0_2/|Vijesti|Arhiva_vijesti|Tr-zhi-shte_kapitala|2"]
	
	pattern = re.compile('<small><a href="(.+?)" title', re.U|re.I|re.M|re.DOTALL)
	
	for u in arhiveUrls:
		(page, dl) = downloadPage(baseUrl+u)
		if dl:
			page = page.decode("cp1250")
			articles = pattern.findall(page)
			for a in articles: articleUrls.append(baseUrl + a)
		
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
	
#if __name__ == '__main__':
#	url = "http://hrportfolio.com/hr/fondovi/fondovi_4_3_0_2/|Vijesti|Tr-zhi-shte_kapitala|Novost|Dnevni_pregled_ZSE_za_11-cot-01-cot-2011-cot-|15951"
#	page = urllib.urlopen(url).read()
#	(body, title, extras) = cleanPage(page)
#	print "TITLE: " + title
#	print extras
#	print "BODY: " + body
