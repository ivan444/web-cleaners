#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2010.04.01

Wrapper za arhivu blog.hr postova (bez komentara).

@author: Ivan Krišto

'''

import sys
import re
import urllib
import codecs
import datetime

# Lista svih blogova. Ovdje dolazi blog s oznakom mjeseca (može biti bilo koji mjesec)!
arhiveLinks = []
arhiveLinks.append("http://barba.blog.hr/2010/03/index.html")
arhiveLinks.append("http://astrodrom.blog.hr/2010/03/index.html")
arhiveLinks.append("http://marinjurjevic.blog.hr/2010/04/index.html")
arhiveLinks.append("http://hatzivelkos.blog.hr/2010/03/index.html")
arhiveLinks.append("http://fashion.blog.hr/2010/01/index.html")
arhiveLinks.append("http://civordnaratep.blog.hr/2010/03/index.html")
arhiveLinks.append("http://periodmuskesvinje.blog.hr/2010/02/index.html")
arhiveLinks.append("http://apatrida.blog.hr/2010/03/index.html")
arhiveLinks.append("http://kamena-kucica-na-skoju.blog.hr/2010/03/index.html")
arhiveLinks.append("http://xiola.blog.hr/2010/02/index.html")
arhiveLinks.append("http://motorobi.blog.hr/2010/01/index.html")
arhiveLinks.append("http://enhu.blog.hr/2009/12/index.html")
arhiveLinks.append("http://fearthepenguin.blog.hr/2007/08/index.html")
arhiveLinks.append("http://bushman.blog.hr/2008/02/index.html")
arhiveLinks.append("http://asboinu.blog.hr/2009/12/index.html")
arhiveLinks.append("http://redpen.blog.hr/2006/12/index.html")
arhiveLinks.append("http://anarhijaweekly.blog.hr/2009/04/index.html")
arhiveLinks.append("http://jesusquintana.blog.hr/2006/04/index.html")
arhiveLinks.append("http://domacica.blog.hr/2006/10/index.html")
arhiveLinks.append("http://novac.blog.hr/2009/12/index.html")
arhiveLinks.append("http://dritokonj.blog.hr/2010/02/index.html")
arhiveLinks.append("http://annie.blog.hr/2006/08/index.html")
arhiveLinks.append("http://sadisticoshy.blog.hr/2009/12/index.html")
arhiveLinks.append("http://blogomobil.blog.hr/2006/01/index.html")
arhiveLinks.append("http://tvkriticar.blog.hr/2008/03/index.html")
arhiveLinks.append("http://porto.blog.hr/2007/11/index.html")
arhiveLinks.append("http://trapula.blog.hr/2004/10/index.html")
arhiveLinks.append("http://gizmo.blog.hr/2004/06/index.html")
arhiveLinks.append("http://pametnizub888.blog.hr/2010/03/index.html")
arhiveLinks.append("http://nelinagustirna.blog.hr/2010/03/index.html")
arhiveLinks.append("http://broduboci.blog.hr/2010/02/index.html")
arhiveLinks.append("http://marole.blog.hr/2010/03/index.html")
arhiveLinks.append("http://zvoneradikal.blog.hr/2009/11/index.html")
arhiveLinks.append("http://uraljamanyc.blog.hr/2007/12/index.html")
arhiveLinks.append("http://washingtonrocks.blog.hr/2008/04/index.html")
arhiveLinks.append("http://ateizam.blog.hr/2009/10/index.html")




#logOut = sys.__stdout__ # stdout
logOut = codecs.open("log.txt", "w", "utf-8")

def logFull(type, msg):
	print >>logOut, u"[" + type + "][" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] " + msg

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
	printLinksPattern = re.compile(u'"(http://www.blog.hr/print/id/.+?)"', re.U|re.I|re.DOTALL)
	prevMonthPattern = re.compile(u'<td class="kalendar-strelica-natrag">(.+?)</td>', re.U|re.I|re.DOTALL)
	nextMonthPattern = re.compile(u'<td class="kalendar-strelica-naprijed">(.+?)</td>', re.U|re.I|re.DOTALL)
	onlyURLPattern = re.compile(u'"(.+?)"', re.U|re.I|re.DOTALL)

	collectedLinks = []
	for l in arhiveLinks: collectedLinks.append(l)

	textLinks = []
	
	while len(arhiveLinks) > 0:
		l = arhiveLinks.pop()
		log("Pobiranje URL-ova blogova sa " + l)
		
		(page, downloaded) = downloadPage(l)
		if "<title>Blog.hr - HTTP 404 Not Found</title>" in page:
			logWarning(u"URL " + l + " ne sadrži blog!")
			continue
		
		if downloaded:
			try:
				# Spremanje print linkova
				printLinks = printLinksPattern.findall(page)
				for p in printLinks:
					if not p in textLinks:
						textLinks.append(p)
				
				# Spremanje linka na sljedeći mjesec
				nextMonthContent = nextMonthPattern.search(page).group(1)
				if nextMonthContent != "&nbsp;":
					 nextMonthURL = onlyURLPattern.search(nextMonthContent).group(1)
					 if not nextMonthURL in collectedLinks:
					 	arhiveLinks.append(nextMonthURL)
					 	collectedLinks.append(nextMonthURL)
				
				# Spremanje linka na prethodni mjesec	 	
				prevMonthContent = prevMonthPattern.search(page).group(1)
				if prevMonthContent != "&nbsp;":
					 prevMonthURL = onlyURLPattern.search(prevMonthContent).group(1)
					 if not prevMonthURL in collectedLinks:
					 	arhiveLinks.append(prevMonthURL)
					 	collectedLinks.append(prevMonthURL)
				
				log(u"Završeno pobiranje URL-ova sa " + l)
			except:
				logError(u"Dogodila se iznimka prilikom obrade stranice " + l)
				pass
	
	return textLinks

extractTitlePattern = re.compile(u'<h2>(.+?)</h2>', re.U|re.M|re.I|re.DOTALL)
extractDatePattern = re.compile(u'<b>Post je objavljen (.+?) u .+? sati\.</b></p>', re.U|re.M|re.I|re.DOTALL)
extractAuthorPattern = re.compile(u'<span><b>Adresa bloga: <a href="http://(.+?)\.blog\.hr/.+?html"', re.U|re.M|re.I|re.DOTALL)

patternNbspToSpace = re.compile('\s*&nbsp;\s*', re.M|re.DOTALL|re.I|re.U)
patternAmpNbspToSpace = re.compile('\s*&amp;nbsp;\s*', re.M|re.DOTALL|re.I|re.U)
patternRawContent = re.compile('<p>(.+?)<b>Post je objavljen .+? u .+? sati\.</b></p>', re.M|re.DOTALL|re.I|re.U)
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

# TODO: This
def cleanPage(url):
	try:
		(page, downloaded) = downloadPage(url)
		page = page.decode("cp1250")

		cleaned = {}
		if downloaded:
			log(u"Obrađujem: " + url)
			title = extractTitlePattern.search(page).group(1)
			date = extractDatePattern.search(page).group(1)
			author = extractAuthorPattern.search(page).group(1)
			
			cleaned["title"] = wrapClean(title)
			cleaned["date"] = date
			cleaned["author"] = wrapClean(author)
			cleaned["content"] = cleanContent(page)
			
			#cleaning("".group(1).decode("cp1250"), "")
			
			return cleaned
	except:
		logError("Greska pri obradi! URL: " + url)
		return None

def downloader():
	textLinks = extractTextLinks()
	
	id = 1
	linksLen = len(textLinks)

	for l in textLinks:
		cleaned = cleanPage(l)
		if cleaned == None: continue
		
		print >>cleaningOut, u'\t<doc name="blog-hr-'+str(id)+'">'
		id += 1
		print >>cleaningOut, u'\t\t<content language="hr">'
		print >>cleaningOut, u'\t\t\t<title>'+xmlEscape(cleaned["title"])+'</title>'
		print >>cleaningOut, u'\t\t\t<body>'
		print >>cleaningOut, xmlEscape(cleaned["content"])
		print >>cleaningOut, u'\t\t\t</body>'
		print >>cleaningOut, u'\t\t</content>\n'
		
		print >>cleaningOut, u'\t\t<extraInfo>'
		print >>cleaningOut, u'\t\t\t<author>'+xmlEscape(cleaned["author"])+'</author>'
		print >>cleaningOut, u'\t\t\t<date>'+cleaned["date"]+'</date>'
		print >>cleaningOut, u'\t\t\t<url>'+xmlEscape(l)+'</url>'
		print >>cleaningOut, u'\t\t\t<creation-date>'+str(datetime.datetime.now().date())+'</creation-date>'
		print >>cleaningOut, u'\t\t</extraInfo>\n'
		
		print >>cleaningOut, u'\t</doc>\n'
		
		log(u"Obrađeno (" + str(id-1) + "/" + str(linksLen) + ") stranica - " + ("%2.2f" % ((id-1)*100.0/linksLen)) + "%")
						
if __name__ == '__main__':
	
	# Ispis - start
	# Izlazna datoteka
	#cleaningOut = sys.__stdout__ # stdout
	now = datetime.datetime.now()
	year = now.year
	month = now.month
	day = now.day
	cleaningOut = codecs.open("blog-hr-aa-arhiva-"+str(year)+"-"+('%02d' % month)+"-"+('%02d' % day)+".xml", "w", "utf-8")
	
	print >>cleaningOut, u'<?xml version="1.0" encoding="utf-8"?>'
	print >>cleaningOut, u'<documentSet name="blog-hr-aa-arhiva-'+str(year)+'-'+("%02d" % month)+'-'+("%02d" % day)+'" type="" description="Arhiva blog.hr blogova za prepoznavanje autora do '+str(year)+'-'+("%02d" % month)+'-'+("%02d" % day)+'" xmlns="http://ktlab.fer.hr" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://ktlab.fer.hr http://ktlab.fer.hr/download/documentSet.xsd">'
	# Ispis - end
	
	downloader()
		
	# Ispis - start
	print >>cleaningOut, u'</documentSet>'
	cleaningOut.close()
	# Ispis - end
	log(u"Gotovo!")

