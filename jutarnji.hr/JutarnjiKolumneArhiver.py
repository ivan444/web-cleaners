#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2009.10.13

Wrapper za arhivu kolumna Jutarnjeg lista.

@author: Ivan Krišto

TODO:
	- Možda malo bolje formatirati datum unutar <date>?
'''

import sys
import re
import urllib
import codecs
import datetime
#from threading import Thread
from threading import Condition

# Multithread zastavica, staviti na True ako želite višedretveno skidanje
multithread = False

# Lista svih kolumni
arhiveLinks = []
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/rimovanje/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/on_the_record/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/sumnjivo_lice/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/jutarnja_propovijed/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/linija_zivota/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/vijesti_iz_liliputa/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/kontrapunkt/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/klasa_optimist/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/dnevnik_s_margine/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/iz_maksimirske_sume/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/subotnja_matineja/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/bivsi_kolumnisti/subotnje_fusnote/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/bivsi_kolumnisti/kolumna_tomislava_ivica/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/bivsi_kolumnisti/fakat/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/bivsi_kolumnisti/pobjednici_i_gubitnici/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/bivsi_kolumnisti/ispovjedaonica/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/bivsi_kolumnisti/ispod_tepiha/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/bivsi_kolumnisti/sabat_salom/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/bivsi_kolumnisti/trece_poluvrijeme/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/bivsi_kolumnisti/od_kantuna_do_kantuna/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/bivsi_kolumnisti/pod_rijeckom_urom/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/bivsi_kolumnisti/vodena_vrata/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/bivsi_kolumnisti/nogometno_ogledalo/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/bivsi_kolumnisti/time_out/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/bivsi_kolumnisti/kolumna_williama_montgomerya/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/bivsi_kolumnisti/dobro_vam_jutro/")
arhiveLinks.append("http://www.jutarnji.hr/komentari/kolumne/bivsi_kolumnisti/kolumna_radovana_stipetica/")


#logOut = sys.__stdout__ # stdout
logOut = codecs.open("log.txt", "w", "utf-8")

def logFull(type, msg):
	if multithread: logCondition.acquire()
	print >>logOut, u"[" + type + "][" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] " + msg
	if multithread: logCondition.release()

def log(msg):
	logFull("INFO", msg)

def logWarning(msg):
	logFull("WARNING", msg)

def logError(msg):
	logFull("ERROR", msg)


patternBRtoNL = re.compile('\s*<br>\s*', re.M|re.DOTALL|re.I|re.U)
patternPtoNL = re.compile('\s*<p[^>]*>\s*(.+?)</p>', re.M|re.DOTALL|re.I|re.U)

def brToNl(text):
	if text == None: return None
	return patternBRtoNL.sub("\n", text)

def doClean(pattern, text):
	clean = pattern.search(text)
	if clean == None: return None
	else: return brToNl(clean.group(1))

xml_escape_table = {
	"&": "&amp;",
 	'"': "&quot;",
 	"'": "&apos;",
 	">": "&gt;",
 	"<": "&lt;",
}

def xmlEscape(text):
	"""Produce entities within text."""
	if text == None or text == "": return ""
	L=[]
	for c in text:
		L.append(xml_escape_table.get(c,c))
	return "".join(L)

#class DownloadThread(Thread):
#	def __init__ (self, id, startDay, startMonth, startYear, endDay, endMonth, endYear):
#		Thread.__init__(self)
#		self.id = id
#		self.startDay = startDay
#		self.startMonth = startMonth
#		self.startYear = startYear
#		self.endDay = endDay
#		self.endMonth = endMonth
#		self.endYear = endYear
#		
#	def run(self):
#		downloader(self.startDay, self.startMonth, self.startYear, self.endDay, self.endMonth, self.endYear)

def downloadPage(url):
	trys = 3
	downloaded = False
	while trys > 0 and not downloaded:
		try:
			page = urllib.urlopen(url).read()
			downloaded = True
		except:
			logError("Skidanje stranice " + url + " nije uspjelo!")
			downloaded = False
			trys-=1
			
	return (page, downloaded)

def extractTextLinks():
	firstTextPattern = re.compile(u'<a class="arhiva" href="(.+?)"', re.U|re.M|re.I|re.DOTALL)
	rawTextPattern = re.compile(u'<div id="arhiva-kolumna"(.+?)<div class="span-2">', re.U|re.M|re.I|re.DOTALL)
	onlyLinksPattern = re.compile(u'<a href="(.+?)"', re.U|re.M|re.I|re.DOTALL)
	linkRootPattern = re.compile(u'http://www.jutarnji.hr/(.+?)/', re.U|re.M|re.I|re.DOTALL)
	
	textLinks = []
	for l in arhiveLinks:
		log("Pobiranje URL-ova kolumni sa " + l)
		
		(page, downloaded) = downloadPage(l)
	
		if downloaded:
			try:
				firstText = firstTextPattern.search(page)
				rawText = rawTextPattern.search(page)
				if firstText == None and rawText == None:
					logWarning(u"Na stranici " + l + " nema URL-ova!")
					continue
				
				if firstText != None:
					textLinks.append(firstText.group(1))
				
				if rawText != None:
					onlyLinks = onlyLinksPattern.findall(rawText.group(1))
					extractedLinks = []
					
					for link in onlyLinks:
						linkRootMG = linkRootPattern.match(link)
						if linkRootMG == None: continue
						linkRoot = linkRootMG.group(1)
						if linkRoot in extractedLinks: continue
						if linkRoot == "": continue
	
						extractedLinks.append(linkRoot)
						textLinks.append(link)
				
				log(u"Završeno pobiranje URL-ova sa " + l)
			except:
				pass
	
	return textLinks

extractTitleDatePattern = re.compile(u'<p class="head">(.+?)</h1>', re.U|re.M|re.I|re.DOTALL)
extractTitlePattern = re.compile(u'<h1>(.+?)$', re.U|re.M|re.I|re.DOTALL)
extractDatePattern = re.compile(u'Objavljeno:&nbsp;\s*(.+?)\s*</p>', re.U|re.M|re.I|re.DOTALL)
extractAuthorPattern = re.compile(u'<div class="author.+?<a .+?>\s*(.+?)\s*</a>\s*</h2>', re.U|re.M|re.I|re.DOTALL)
extractColumnTitlePattern = re.compile(u'<div class="subsections">.+?<h1>\s*(.+?)\s*</h1>', re.U|re.M|re.I|re.DOTALL)
patternNbspToSpace = re.compile('\s*&nbsp;\s*', re.M|re.DOTALL|re.I|re.U)
patternAmpNbspToSpace = re.compile('\s*&amp;nbsp;\s*', re.M|re.DOTALL|re.I|re.U)
patternRawContent = re.compile('<p class="lead">(.+?)<div class="rate span-3">', re.M|re.DOTALL|re.I|re.U)
patternFindScript = re.compile('\s*<script.+</script>\s*', re.M|re.DOTALL|re.I|re.U)
patternFindTag = re.compile('<.+?>', re.M|re.DOTALL|re.I|re.U)
patternExtraNl = re.compile('\n{2,}', re.M|re.DOTALL|re.I|re.U)

def nbspToSpace(text):
	if text == None: return ""
	text = patternNbspToSpace.sub(" ", text)
	text = patternAmpNbspToSpace.sub(" ", text)
	return text

def bigReplace(text):
	text = text.replace("&apos;", "'").replace("&quot;", "\"").replace(u"‘", "'").replace(u"’", "'")
	text = text.replace(u"„", "&quot;").replace(u"…", "...").replace(u"#8225;", "").replace(u"#8226;", "")
	return text.replace(u"“", "\"").replace(u"”", "\"").replace("&amp;", "&").replace("&amp;#8226;", "").replace("&amp;amp;", "&amp;")

def cleanContent(page):
	rawMG = patternRawContent.search(page)
	rawContent = brToNl(rawMG.group(1))
	rawContent = nbspToSpace(rawContent)
	rawContent = patternFindScript.sub("", rawContent)
	rawContent = patternFindTag.sub("", rawContent)
	rawContent = patternExtraNl.sub("\n", rawContent)
	content = bigReplace(rawContent)
	
	return content.strip()

def wrapClean(text):
	return bigReplace(nbspToSpace(text))

def cleanPage(url):
	try:
		(page, downloaded) = downloadPage(url)
		page = page.decode("utf_8")

		cleaned = {}
		if downloaded:
			log(u"Obrađujem: " + url)
			titleDateMG = extractTitleDatePattern.search(page)
			title = extractTitlePattern.search(titleDateMG.group(1)).group(1)
			date = extractDatePattern.search(titleDateMG.group(1)).group(1)
			
			authorMG = extractAuthorPattern.search(page)
			author = authorMG.group(1)
			
			columnTitleMG = extractColumnTitlePattern.search(page)
			columnTitle = columnTitleMG.group(1)
			
			cleaned["title"] = wrapClean(title)
			cleaned["date"] = date
			cleaned["author"] = wrapClean(author)
			cleaned["columnTitle"] = wrapClean(columnTitle)
			cleaned["content"] = cleanContent(page)
			
			#cleaning("".group(1).decode("cp1250"), "")
			
			return cleaned
	except:
		logError("Greska pri obradi! URL: " + url)
		return None

def downloader():
	textLinks = extractTextLinks()
#	textLinks = []
#	textLinks.append("http://www.jutarnji.hr/inicijativa-za-referendum-u-rs-u-nova-je-sablast-nad-bosnom-i-hercegovinom/222127/")
#	textLinks.append("http://www.jutarnji.hr/premijerka-je--nazalost--obmanula-javnost/325149/")
#	textLinks.append("http://www.jutarnji.hr/ivan-mu-je-ime/300968/")
#	textLinks.append("http://www.jutarnji.hr/dubrovacki-knez-razvlastio-bi-gospare/311949/")
#	textLinks.append("http://www.jutarnji.hr/mafiji-je-ime-sotona--a-kako-zvati-one-koji-toj-sotoni-novace-vojsku-/346239/")
	
	id = 1
	linksLen = len(textLinks)
#	linkNum = 0

	# Prethodni naslov (za potrebe izbacivanja duplikata)
	prevTitle = None
	for l in textLinks:
		cleaned = cleanPage(l)
#		linkNum += 1
#		if linkNum % 10 == 0:
#			log("Dovršeno: " + str("%02f" % linkNum*1.0/linksLen) + "%")
		if cleaned == None: continue
		if prevTitle == cleaned["title"]:
			# Preskačemo duplikat
			logWarning(u"Preskačem: " + l)
			continue
		
		if multithread: writeCondition.acquire()
		print >>cleaningOut, u'\t<doc name="jutarnji-kolumne-'+str(id)+'">'
		id += 1
		print >>cleaningOut, u'\t\t<content language="hr">'
		print >>cleaningOut, u'\t\t\t<title>'+xmlEscape(cleaned["title"])+'</title>'
		print >>cleaningOut, u'\t\t\t<body>'
		print >>cleaningOut, xmlEscape(cleaned["content"])
		print >>cleaningOut, u'\t\t\t</body>'
		print >>cleaningOut, u'\t\t</content>\n'
		
		#print >>cleaningOut, u'\t\t<categories scheme="jutarnji-kolmune" version="1.0">'
		#print >>cleaningOut, u'\t\t\t<category id="'+col+'">'+xmlEscape("blah!")+'</category>'
		#print >>cleaningOut, u'\t\t</categories>\n'
		
		print >>cleaningOut, u'\t\t<extraInfo>'
		print >>cleaningOut, u'\t\t\t<author>'+xmlEscape(cleaned["author"])+'</author>'
		print >>cleaningOut, u'\t\t\t<date>'+cleaned["date"]+'</date>'
		print >>cleaningOut, u'\t\t\t<url>'+xmlEscape(l)+'</url>'
		print >>cleaningOut, u'\t\t\t<columntitle>'+xmlEscape(cleaned["columnTitle"])+'</columntitle>'
		print >>cleaningOut, u'\t\t\t<creation-date>'+str(datetime.datetime.now().date())+'</creation-date>'
		print >>cleaningOut, u'\t\t</extraInfo>\n'
		
		print >>cleaningOut, u'\t</doc>\n'
		
		prevTitle = cleaned["title"]
		# sync end
		if multithread: writeCondition.release()
		
		log(u"Obrađeno (" + str(id-1) + "/" + str(linksLen) + ") stranica - " + ("%2.2f" % ((id-1)*100.0/linksLen)) + "%")
						
if __name__ == '__main__':
	
	# Monitori za sinkronizaciju
	if multithread: 
		writeCondition = Condition()
		logCondition = Condition()
	
	# Ispis - start
	# Izlazna datoteka
	#cleaningOut = sys.__stdout__ # stdout
	now = datetime.datetime.now()
	year = now.year
	month = now.month
	day = now.day
	cleaningOut = codecs.open("jutarnji-kolumne-arhiva-"+str(year)+"-"+('%02d' % month)+"-"+('%02d' % day)+".xml", "w", "utf-8")
	
	print >>cleaningOut, u'<?xml version="1.0" encoding="utf-8"?>'
	print >>cleaningOut, u'<documentSet name="jutarnji-kolumne-arhiva-'+str(year)+'-'+("%02d" % month)+'-'+("%02d" % day)+'" type="" description="Arhiva kolumni Jutarnjeg lista do '+str(year)+'-'+("%02d" % month)+'-'+("%02d" % day)+'" xmlns="http://ktlab.fer.hr" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://ktlab.fer.hr http://ktlab.fer.hr/download/documentSet.xsd">'
	# Ispis - end
	
	if not multithread:
		downloader()
		
#	else:
#		# Podjela posla na 10 djelova
#		# Podjela se mogla izvesti nad samim dokumentima, no tu nastaju komplikacije radi nepoznatog
#		# broja članaka u kategoriji (koji je sad stavljen na 1000 i iteriranje se prekida pri prvom koji nije nađen
#		workers = []
#		jobsNum = dDiff.days / 10
#		jobsDate = datetime.timedelta(jobsNum-1)
#		roundErr =  dDiff.days % 10 # Pogreška pri int djeljenju, ove poslove dobiva prvi
#		oneDay = datetime.timedelta(1)
#		zeroDay = datetime.timedelta(0)
#		
#		workerStart = dStart
#		workerEnd = dStart + jobsDate + datetime.timedelta(roundErr) + oneDay
#		for i in xrange(0,10):
#			if workerEnd - workerStart < zeroDay: break
#			workers.append(DownloadThread(i, workerStart.day, workerStart.month, workerStart.year, workerEnd.day, workerEnd.month, workerEnd.year))
#			workerStart = workerEnd + oneDay
#			workerEnd = workerStart+jobsDate
#		
#		for w in workers:
#			w.start()
#			log("Worker " + str(w.id) + " started")
#			
#		for w in workers:
#			w.join()
#			log("Worker " + str(w.id) + " joined")
	
	# Ispis - start
	print >>cleaningOut, u'</documentSet>'
	cleaningOut.close()
	# Ispis - end
	log(u"Gotovo!")

