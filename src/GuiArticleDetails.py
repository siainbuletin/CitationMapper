#-------------------------------------------------------------------------------
# Name:        GuiArticleDetails
# Purpose:     Article details window for the citation mapper program
#
# Author:      Henrik Skov Midtiby
#
# Created:     2011-02-25
# Copyright:   (c) Henrik Skov Midtiby 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python


import gtk
import pprint
import StringIO
import string
import webbrowser

def open_url(widget,url):
	webbrowser.open(url)

class GuiArticleDetails:
	def __init__(self):
		self.nodeinformationwindow = gtk.Window()
		self.nodeinformationwindow.set_title("Article details")
		self.nodeinformationwindow.set_size_request(500, 200)
		self.vbox = gtk.VBox(False, 0)
		self.linklabel = gtk.LinkButton("http://www.sdu.dk", label="Locate article on Web of Science")
		self.text = gtk.TextView()
		self.generateNodeScrolledWindow()
		self.nodescrolledwindow.show_all()
		self.vbox.pack_start(self.linklabel, False, False, 0)
		self.vbox.pack_start(self.nodescrolledwindow, True, True, 0)
		self.nodeinformationwindow.add(self.vbox)
		self.nodeinformationwindow.show_all()
        gtk.link_button_set_uri_hook(open_url)

	def generateNodeScrolledWindow(self):
		self.nodescrolledwindow = gtk.ScrolledWindow()
		self.nodescrolledwindow.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		self.nodescrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.nodescrolledwindow.add(self.text)

	def updateArticleInformation(self, url, article = None, graph = None):
		allKnowledgeAboutArticle = StringIO.StringIO()
		pp = pprint.PrettyPrinter(stream = allKnowledgeAboutArticle)
		pp.pprint(article)
		fullInfoAsText = allKnowledgeAboutArticle.getvalue()

		try:
			author = string.join(article["AU"], ' and ')
			year = article["PY"][0]
			title = string.join(article["TI"], " ")
			page = article["BP"][0]
			journal = article["SO"][0]
			nreferences = article["NR"][0]
			nreferencesInGraph = graph.in_degree(url)
			ncitations = article["TC"][0]
			ncitationsInGraph = graph.out_degree(url)
			self.text.get_buffer().insert_at_cursor('%s\n' % url)
			self.text.get_buffer().insert_at_cursor('\n')
			self.text.get_buffer().insert_at_cursor('%s\n' % title)
			self.text.get_buffer().insert_at_cursor('%s\n' % author)
			self.text.get_buffer().insert_at_cursor('%s\n' % journal)
			self.text.get_buffer().insert_at_cursor('\n')
			self.text.get_buffer().insert_at_cursor('Number of references: %s (%s)\n' % (nreferences, nreferencesInGraph))
			self.text.get_buffer().insert_at_cursor('Times cited: %s (%s)\n' % (ncitations, ncitationsInGraph))
			self.text.get_buffer().insert_at_cursor('\n')

			baseurl = "http://gateway.isiknowledge.com/gateway/Gateway.cgi?GWVersion=2&SrcApp=SFX&SrcAuth=SFX&DestApp=WOS&DestLinkType=GeneralSearchSummary"
			titlematch = "&title=%s" % title.replace(" ", "+")
			yearmatch = "&Period=Year+Selection&years=1985+1986+1987"
			searchurl = baseurl +  titlematch
			self.linklabel.set_uri(searchurl)

		except:
			try:
				self.text.get_buffer().insert_at_cursor('%s\n' % article["Journal"])
				nreferencesInGraph = graph.in_degree(url)
				ncitationsInGraph = graph.out_degree(url)
				self.text.get_buffer().insert_at_cursor('Number of references in graph: %s\n' % nreferencesInGraph)
				self.text.get_buffer().insert_at_cursor('Number of citations in graph: %s\n' % ncitationsInGraph)

			except:
				pass

		self.text.get_buffer().insert_at_cursor('\nAll available information:\n%s' % fullInfoAsText)

def main():
	gad = GuiArticleDetails()
	gtk.main()

if __name__ == "__main__":
	main()
