#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Web page cleaner.

@author: Ivan Krišto

'''

import sys
import re
import urllib
import chardet
import codecs
import datetime
import logging
import os

logging.basicConfig(filename="web_cleaner.log", filemode="w", level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

patternBRtoNL = re.compile('\s*<br>\s*', re.M|re.DOTALL|re.I|re.U)
patternPtoNL = re.compile('\s*</p>\s*', re.M|re.DOTALL|re.I|re.U)
patternExtraNl = re.compile('\n{2,}', re.M|re.DOTALL|re.I|re.U)
patternNbspToSpace = re.compile('\s*&nbsp;\s*', re.M|re.DOTALL|re.I|re.U)
patternAmpNbspToSpace = re.compile('\s*&amp;nbsp;\s*', re.M|re.DOTALL|re.I|re.U)
patternFindScript = re.compile('\s*<script.+</script>\s*', re.M|re.DOTALL|re.I|re.U)
patternFindTag = re.compile('<.+?>', re.M|re.DOTALL|re.I|re.U)

siteName = "untitled"
curId = 1
urlsNum = 1 # 1 to avoid division by zero

def produceNewlines(text):
  if text == None: return ""
  text = patternBRtoNL.sub("\n", text)
  text = patternPtoNL.sub("\n", text)
  return patternExtraNl.sub("\n", text)

def nbspToSpace(text):
  if text == None: return ""
  text = patternNbspToSpace.sub(" ", text)
  text = patternAmpNbspToSpace.sub(" ", text)
  return text

def removeTags(text):
  if text == None: return ""
  text = patternFindScript.sub(" ", text)
  return patternFindTag.sub(" ", text)

# TODO: Optimize!
def bigReplace(text):
  text = text.replace("&apos;", "'").replace("&quot;", "\"").replace(u"‘", "'").replace(u"’", "'")
  text = text.replace(u"„", "&quot;").replace(u"…", "...").replace(u"#8225;", "").replace(u"#8226;", "")
  return text.replace(u"“", "\"").replace(u"”", "\"").replace("&amp;#8226;", "").replace("&amp;amp;", "&amp;")

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
  logging.info("Download: " + url + ".")
  while trys > 0 and not downloaded:
    try:
      page = urllib.urlopen(url).read()
      #enc = chardet.detect(page)
      #page = page.decode(enc["encoding"])
      page = unicode(page, "utf-8")
      downloaded = True
    except:
      logging.error("Download of " + url + " has failed!")
      downloaded = False
      trys-=1
  return (page, downloaded)


def commonCleaner(content):
  """Common HTML cleaner applied after specific web site cleaner."""
  content = nbspToSpace(content)
  content = produceNewlines(content)
  content = removeTags(content)
  content = bigReplace(content)
  content = xmlEscape(content)
  return content.strip()

def writeExtraInfo(fOut, extras, nt):
  for tag, val in extras.items():
    fOut.write(u'\t'*nt+'<'+tag+'>')

    if isinstance(val, list):
      for v in val:
        if not isinstance(v, dict): logging.error("Invalid extras!")
        else:
          fOut.write("\n")
          writeExtraInfo(fOut, v, nt+1)
          fOut.write("\n" + "\t"*nt)

    elif isinstance(val, dict):
      fOut.write("\n")
      writeExtraInfo(fOut, val, nt+1)
      fOut.write("\n" + "\t"*nt)
      
    else:
      fOut.write(commonCleaner(val))

    fOut.write(u'</'+tag+'>\n')
  

def writePage(content, title, url, extras):
  global curId
  
  print >>cleaningOut, u'\t<doc name="'+siteName+'-'+str(curId)+'">'
  print >>cleaningOut, u'\t\t<content language="hr">'
  print >>cleaningOut, u'\t\t\t<title>'+commonCleaner(title)+'</title>'
  print >>cleaningOut, u'\t\t\t<body>'
  print >>cleaningOut, commonCleaner(content)
  print >>cleaningOut, u'\t\t\t</body>'
  print >>cleaningOut, u'\t\t</content>\n'
  
  print >>cleaningOut, u'\t\t<extraInfo>'
  print >>cleaningOut, u'\t\t\t<url>'+xmlEscape(url)+'</url>'
  print >>cleaningOut, u'\t\t\t<creation-date>'+str(datetime.datetime.now().date())+'</creation-date>'
  writeExtraInfo(cleaningOut, extras, 3)
  print >>cleaningOut, u'\t\t</extraInfo>\n'
  
  print >>cleaningOut, u'\t</doc>\n'
  
  logging.info(u"Processed (" + str(curId) + "/" + str(urlsNum) + ") pages - " + ("%2.2f" % ((curId)*100.0/urlsNum)) + "%")
  
  curId += 1

def webCleaner():
  global urlsNum
  urls = crawlUrls()
  urlsNum = len(urls)
  logging.info("Number of URLs: " + str(urlsNum))
  #logging.info(str(urls))
  
  for url in urls:
    try:
      (page, downloaded) = downloadPage(url)
      if downloaded:
        (content, title, extras) = cleanPage(page)
        #content = unicode(content, "utf-8")
        #title = unicode(title, "utf-8")
        #extras = unicode(extras, "utf-8")
        logging.info("Page: " + str(url) + " cleaned!")
        writePage(content, title, url, extras)
    except Exception as e:
      logging.error("Failed to process url " + str(url) + ". Exception: " + str(e))

    
if __name__ == '__main__':
  if len(sys.argv) < 3:
    print "Usage: WebCleaner.py <web_site_name> <implementation_py_script>"
    exit(-1)
    
  impPath = sys.argv[2]
  execfile(impPath)
    
  siteName = sys.argv[1]
  
  # Izlazna datoteka
  now = datetime.datetime.now()
  year = now.year
  month = now.month
  day = now.day
  cleaningOut = codecs.open(siteName+"-arhiva-"+str(year)+"-"+('%02d' % month)+"-"+('%02d' % day)+".xml", "w", "utf-8")
  
  print >>cleaningOut, u'<?xml version="1.0" encoding="utf-8"?>'
  print >>cleaningOut, u'<documentSet name="'+siteName+'-arhiva-'+str(year)+'-'+("%02d" % month)+'-'+("%02d" % day)+'" type="" description=" " xmlns="http://ktlab.fer.hr" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://ktlab.fer.hr http://ktlab.fer.hr/download/documentSet.xsd">'
  
  webCleaner()
    
  print >>cleaningOut, u'</documentSet>'
  cleaningOut.close()
  
  logging.info(u"Done!")

