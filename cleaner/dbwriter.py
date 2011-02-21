#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3
import datetime

class Db:
	def __init__(self, path):
		self.conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		self.cur = self.conn.cursor()
		
	def createTables(self):
		self.cur.executescript("""create table articles (
		url TEXT,
		title TEXT,
		body TEXT,
		lang TEXT,
		extra_info TEXT,
		creation_time TIMESTAMP);

		create table article_urls (
			url TEXT,
			t_added TIMESTAMP);

		create table fails (
			url TEXT,
			time TIMESTAMP);

		create table dl_queue (
			url TEXT);""")
		self.conn.commit()

	def insertArticle(self, content, title, url, extras, lang):
		self.cur.execute("""insert into articles
		values (?, ?, ?, ?, ?, ?)
		""", (url, title, content, lang, str(extras), datetime.datetime.now()))
		self.conn.commit()

	def dequeue(self):
		self.cur.execute("select url from dl_queue limit 1")
		row = self.cur.fetchone()

		url = None
		if row != None and row[0] != "": url = row[0]

		if url != None:
			self.cur.execute("delete from dl_queue where url = ?", (url,))
			self.conn.commit()

		return url
	
	def execute(self, query, vals):
		self.cur.execute(query, vals)

	def execCm(self, query, vals):
		self.cur.execute(query, vals)
		self.conn.commit()
	
	def execSel1(self, query):
		self.cur.execute(query)
		return self.cur.fetchone()
	
	def executeMany(self, query, vals):
		self.conn.executemany(query, vals)

	def execSelAll(self, query):
		self.cur.execute(query)
		return self.cur.fetchall()

	def executeSelect(self, query):
		self.cur.execute(query)
	
	def commit(self):
		self.conn.commit()

	def fetchone(self):
		return self.cur.fetchone()

	def fetchall(self):
		return self.cur.fetchall()

	def close(self):
		self.cur.close()

