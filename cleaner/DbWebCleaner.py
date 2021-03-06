#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Web page cleaner.

@author: Ivan Krišto

TODO:
  - multithreaded download.
  - reading log file path from script arguments
'''

import sys
import re
import urllib
import chardet
import codecs
import datetime
import logging
import os
import getopt
import dbwriter
import json

logging.basicConfig(filename="web_cleaner.log", filemode="w", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

patternBRtoNL = re.compile('\s*<br>\s*', re.M|re.DOTALL|re.I|re.U)
patternPtoNL = re.compile('\s*</p>\s*', re.M|re.DOTALL|re.I|re.U)
patternExtraNl = re.compile('\n{2,}', re.M|re.DOTALL|re.I|re.U)
patternNbspToSpace = re.compile('\s*&nbsp;\s*', re.M|re.DOTALL|re.I|re.U)
patternAmpNbspToSpace = re.compile('\s*&amp;nbsp;\s*', re.M|re.DOTALL|re.I|re.U)
patternFindScript = re.compile('\s*<script.+</script>\s*', re.M|re.DOTALL|re.I|re.U)
patternFindTag = re.compile('<.+?>', re.M|re.DOTALL|re.I|re.U)

# Options
siteName = "untitled"
urlsNum = 1 # 1 to avoid division by zero
dbpath = None
output = None
impl = None
createdb = False
continueDl = False
writeOnly = False

# Database
db = None

def sstr(s):
  """ASCII safe str()"""
  safes = []
  for c in s:
    if ord(c) < 128: safes.append(c)
    else: safes.append(c)
  return "".join([c for c in safes])

def produceNewlines(text):
  """Convert BR and P elements to newline char."""
  if text == None: return ""
  text = patternBRtoNL.sub("\n", text)
  text = patternPtoNL.sub("\n", text)
  return patternExtraNl.sub("\n", text)

def nbspToSpace(text):
  """Convert &nbsp; entity to whitespace char."""
  if text == None: return ""
  text = patternNbspToSpace.sub(" ", text)
  text = patternAmpNbspToSpace.sub(" ", text)
  return text

def removeTags(text):
  """Remove HTML tags from text."""
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
  """Page downloader.
  Returns web page content (html) and
  True/False flag indicating is page succesfully downloaded."""

  trys = 3
  downloaded = False
  logging.info("Download: " + sstr(url) + ".")
  page = None
  while trys > 0 and not downloaded:
    try:
      page = urllib.urlopen(url).read()
      #enc = chardet.detect(page)
      #page = page.decode(enc["encoding"])
      downloaded = True
    except Exception as e:
      logging.error("Download of " + sstr(url) + " has failed! Exception: " + str(e))
      downloaded = False
      trys-=1
      if trys == 0: db.execCm("insert into fails values (?,?)", (url, datetime.datetime.now()))
  return (page, downloaded)


def commonCleaner(content):
  """Common HTML cleaner applied after specific web site cleaner."""
  content = nbspToSpace(content)
  content = produceNewlines(content)
  content = removeTags(content)
  content = bigReplace(content)
  content = xmlEscape(content)
  return content.strip()
 

def writePage(content, title, url, extras):
  """Write processed web page data into database."""
  db.insertArticle(content, title, url, extras, "hr")
  

def webCleaner():
  """Master part of script.
  Initiates crawling for article URLs,
  downloads article,
  cleans it and
  writes it to database."""

  global urlsNum
  if not continueDl:
    urls = crawlUrls()
    
    qurls = []
    now = datetime.datetime.now()
    [qurls.append((u, now)) for u in urls]
    db.executeMany("insert into article_urls values(?,?)", qurls)
    
    dlqueue = []
    [dlqueue.append((u,)) for u in urls]
    db.executeMany("insert into dl_queue values(?)", dlqueue)
    urlsNum = len(urls)
  else:
    urlsNum = db.execSel1("select count(url) from dl_queue")[0]

  logging.info("Number of URLs: " + str(urlsNum))

  curId = 0
  while True:
    url = db.dequeue()
    if url == None: break

    curId += 1
    try:
      (page, downloaded) = downloadPage(url)
      if downloaded:
        (content, title, extras) = cleanPage(page)
        #content = unicode(content, "utf-8")
        #title = unicode(title, "utf-8")
        #extras = unicode(extras, "utf-8")
        logging.info("Page: " + sstr(url) + " cleaned!")
        writePage(content, title, url, extras)
    except Exception as e:
      logging.error("Failed to process url " + sstr(url) + ". Exception: " + str(e))
      db.execCm("insert into fails values (?,?)", (url, datetime.datetime.now()))

    logging.info(u"Processed (" + str(curId) + "/" + str(urlsNum) + ") pages - " + ("%2.2f" % ((curId)*100.0/urlsNum)) + "%")


def writeExtraInfo(fOut, extras, nt):
  """Write unlimited depth extras hash (map)."""

  for tag, val in extras.items():
    try:
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
        fOut.write(commonCleaner(unicode(val)))

      fOut.write(u'</'+tag+'>\n')
    except Exception as e:
      logging.error("Failed to write tag " + tag + "! Exception: " + str(e))


def dbToXml():
  """Transfer database data to XML file."""

  curId = 0
  while True:
    db.execute("""select
    url, title, body, lang,
    extra_info, creation_time
    from articles
    limit 500
    offset ?""", (curId,))
    rows = db.fetchall()
    if rows == None or len(rows) == 0: break

    for r in rows:
      curId += 1

      print >>cleaningOut, u'\t<doc name="'+siteName+'-'+str(curId)+'">'
      print >>cleaningOut, u'\t\t<content language="'+r[3]+'">'
      print >>cleaningOut, u'\t\t\t<title>'+commonCleaner(r[1])+'</title>'
      print >>cleaningOut, u'\t\t\t<body>'
      print >>cleaningOut, commonCleaner(r[2])
      print >>cleaningOut, u'\t\t\t</body>'
      print >>cleaningOut, u'\t\t</content>\n'
      
      print >>cleaningOut, u'\t\t<extraInfo>'
      print >>cleaningOut, u'\t\t\t<url>'+xmlEscape(r[0])+'</url>'
      print >>cleaningOut, u'\t\t\t<creation-date>'+str(datetime.datetime.now().date())+'</creation-date>'

      #extras = json.loads(r["e"])
      extras = eval(r[4])
      writeExtraInfo(cleaningOut, extras, 3)

      print >>cleaningOut, u'\t\t</extraInfo>\n'
      
      print >>cleaningOut, u'\t</doc>\n'


def usage():
  print """Web page cleaner v0.1

Usage: python """ + sys.argv[0] + """ -s <siteName> -i <implementation>

Options
-------
Mandatory:
  -s SITE, --site=SITE		Site name.
  -i PATH, --impl=PATH		Path to crawler&cleaner implementation.

Optional:
  -d PATH, --dbpath=PATH	Path to database [<site_name>.db].
  -c, --createdb		Set if you are not using existing database (will be ignored if used with --write-only or --continue).
  -o PATH, --output=PATH	Path to output xml file [<site_name>-archive-<year>-<month>-<day>.xml].
  -h, --help			Print this message.
  --write-only			Only transfer database data to XML.
  --continue			Continue downloading process.
"""

def processOptions():
  """Process command line arguments."""

  global siteName, dbpath, output, impl, createdb, continueDl, writeOnly
  setSite = False
  setImpl = False
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hs:ci:d:o:", ["help", "site=", "createdb", "impl=", "dbpath=", "output=", "write-only", "continue"])
    len(args) # remove pydev warning...
  except getopt.GetoptError, err:
    print str(err)
    usage()
    sys.exit(2)
  
  for o, a in opts:
    if o in ("-s", "--site"):
      siteName = a
      setSite = True
    elif o in ("-i", "--impl"):
      impl = a
      setImpl = True
    elif o in ("-d", "--dbpath"):
      dbpath = a
    elif o in ("-o", "--output"):
      output = a
    elif o in ("-h", "--help"):
      usage()
      sys.exit()
    elif o in ("-c", "--createdb"):
      createdb = True
    elif o == "--write-only":
      writeOnly = True
    elif o == "--continue":
      continueDl = True
    else:
      print "Invalid argument " + o + "!"
      usage()
      sys.exit(2)
  
  if not setSite or not setImpl:
    usage()
    sys.exit(2)
  
  if dbpath == None:
    dbpath = siteName + ".db"
  if output == None:
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    output = siteName+"-archive-"+str(year)+"-"+('%02d' % month)+"-"+('%02d' % day)+".xml"
  

def initDb(dbpath, createdb):
  """Initialize database and create tables if needed."""

  global db
  db = dbwriter.Db(dbpath)

  if createdb == True and (writeOnly or continueDl):
    logging.warning("--createdb flag will be ignored! (see help)")

  if createdb:
    db.createTables()

if __name__ == '__main__':
  processOptions()    

  execfile(impl)

  initDb(dbpath, createdb and not writeOnly and not continueDl)
    
  if not writeOnly:
    webCleaner()

  # Izlazna datoteka
  now = datetime.datetime.now()
  year = now.year
  month = now.month
  day = now.day
  cleaningOut = codecs.open(output, "w", "utf-8")
  
  print >>cleaningOut, u'<?xml version="1.0" encoding="utf-8"?>'
  print >>cleaningOut, u'<documentSet name="'+siteName+'-archive-'+str(year)+'-'+("%02d" % month)+'-'+("%02d" % day)+'" type="" description=" " xmlns="http://ktlab.fer.hr" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://ktlab.fer.hr http://ktlab.fer.hr/download/documentSet.xsd">'
  
  dbToXml()
    
  print >>cleaningOut, u'</documentSet>'
  cleaningOut.close()
  
  logging.info(u"Done!")


