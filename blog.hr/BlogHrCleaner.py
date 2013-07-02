#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

# Lista svih blogova. Ovdje dolazi blog s oznakom mjeseca (moze biti bilo koji mjesec)!
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

def crawlUrls():
  ptrnPrintLinks = re.compile(u'"(http://www.blog.hr/print/id/.+?)"', re.U|re.I|re.DOTALL)
  ptrnPrevMonth = re.compile(u'<td class="kalendar-strelica-natrag">(.+?)</td>', re.U|re.I|re.DOTALL)
  ptrnNextMonth = re.compile(u'<td class="kalendar-strelica-naprijed">(.+?)</td>', re.U|re.I|re.DOTALL)
  ptrnOnlyURL = re.compile(u'"(.+?)"', re.U|re.I|re.DOTALL)

  collectedLinks = []
  for l in arhiveLinks: collectedLinks.append(l)

  textLinks = []
  
  while len(arhiveLinks) > 0:
    l = arhiveLinks.pop()
    logging.debug("Pobiranje URL-ova blogova sa " + l)
    
    (page, downloaded) = downloadPage(l)
    if "<title>Blog.hr - HTTP 404 Not Found</title>" in page:
      logging.debug(u"URL " + l + " ne sadrzi blog!")
      continue
    
    if downloaded:
      try:
        # Spremanje print linkova
        printLinks = ptrnPrintLinks.findall(page)
        for p in printLinks:
          if not p in textLinks:
            textLinks.append(p)
        
        # Spremanje linka na sljedeći mjesec
        nextMonthContent = ptrnNextMonth.search(page).group(1)
        if nextMonthContent != "&nbsp;":
           nextMonthURL = ptrnOnlyURL.search(nextMonthContent).group(1)
           if not nextMonthURL in collectedLinks:
             arhiveLinks.append(nextMonthURL)
             collectedLinks.append(nextMonthURL)
        
        # Spremanje linka na prethodni mjesec     
        prevMonthContent = ptrnPrevMonth.search(page).group(1)
        if prevMonthContent != "&nbsp;":
           prevMonthURL = ptrnOnlyURL.search(prevMonthContent).group(1)
           if not prevMonthURL in collectedLinks:
             arhiveLinks.append(prevMonthURL)
             collectedLinks.append(prevMonthURL)
        
        logging.debug(u"Zavrseno pobiranje URL-ova sa " + l)
      except Exception as e:
        logging.error(u"Dogodila se iznimka prilikom obrade stranice " + l + ". " + str(e))
  
  return textLinks


ptrnTitle = re.compile(u'<h2>(.+?)</h2>', re.U|re.M|re.I|re.DOTALL)
ptrnDate = re.compile(u'<b>Post je objavljen (.+?) u .+? sati\.</b></p>', re.U|re.M|re.I|re.DOTALL)
ptrnAuthor = re.compile(u'<span><b>Adresa bloga: <a href="http://(.+?)\.blog\.hr/.+?html"', re.U|re.M|re.I|re.DOTALL)
ptrnPostUrl = re.compile(u'<span><b>Adresa bloga: <a href="(http://.+?\.blog\.hr/.+?html)"', re.U|re.M|re.I|re.DOTALL)
ptrnRawContent = re.compile('<p>(.+?)<b>Post je objavljen .+? u .+? sati\.</b></p>', re.M|re.DOTALL|re.I|re.U)

ptrnAllComments = re.compile(u'<ul class="komentari" id="komentari">(.+?)</ul>', re.U|re.M|re.I|re.DOTALL)
ptrnSingleComments = re.compile(u'<li>(.+?)</li>', re.U|re.M|re.I|re.DOTALL)
ptrnCommentAuthBlog = re.compile(u'<h2>\s*<a href="(.+?)"', re.U|re.M|re.I|re.DOTALL)
ptrnCommentNick = re.compile(u'<h2>\s*([^<>]+?)\s*<', re.U|re.M|re.I|re.DOTALL)
ptrnCommentContent = re.compile(u'</h2>(.+?)<img', re.U|re.M|re.I|re.DOTALL)
ptrnCommentDate = re.compile(u'<p class="ispodposta">(.+?)&', re.U|re.M|re.I|re.DOTALL)

def searchTxt(ptrn, txt):
  grps = ptrn.search(txt)
  if grps != None: return grps.group(1)
  else: return ""

def cleanPage(page):
  page = page.decode("cp1250")
  logging.debug("Encoding converted")
  extras = {}
  title = ptrnTitle.search(page).group(1)
  date = ptrnDate.search(page).group(1)
  author = ptrnAuthor.search(page).group(1)
  urlPost = ptrnPostUrl.search(page).group(1)
  content = ptrnRawContent.search(page).group(1)

  urlComments = urlPost.replace("print/id", "komentari/post")
  try:
    (pageCmts, downloaded) = downloadPage(urlComments)
    if downloaded:
      try:
        comments = []
        extras["comments"] = comments
        allCmts = searchTxt(ptrnAllComments, pageCmts)
        cmtsLst = ptrnSingleComments.findall(allCmts)
        for cmnt in cmtsLst:
          cmnt = {}

          cmnt["content"] = searchTxt(ptrnCommentContent, cmnt)
          cmnt["publish-datetime"] = searchTxt(ptrnCommentDate, cmnt)
          cmnt["author-nickname"] = searchTxt(ptrnCommentNick, cmnt)
          grpAuthBlog = ptrnCommentAuthBlog.search(cmnt)
          if grpAuthBlog != None:
            cmnt["author-blog"] = grpAuthBlog.group(1)
          comments.append({"comment": cmnt})
      except Exception as e:
        logging.error("Error parsing comments at URL " + urlComments + ". " + str(e))
  except Exception as e:
    logging.error("Error downloading URL: " + urlComments + ". " + str(e))
  
  extras["date"] = date
  extras["author"] = author
  
  return (content, title, extras)

