#!/usr/bin/env python

import gtk
import gtk.gdk
import citationmapbuilder
import os
import StringIO
import re
import sys
import GuiListOfArticlesInGraph
import GuiOptionsWindow
import GuiArticleDetails

import xdot

class MyDotWindow(xdot.DotWindow):
	minNumberOfReferences = 1
	minNumberOfCitations = 3

	ui = '''
	<ui>
		<toolbar name="ToolBar">
			<toolitem action="Open"/>
			<toolitem action="Reload"/>
			<separator/>
			<toolitem action="ZoomIn"/>
			<toolitem action="ZoomOut"/>
			<toolitem action="ZoomFit"/>
			<toolitem action="Zoom100"/>
		</toolbar>
	</ui>
	'''


	def __init__(self):
		xdot.DotWindow.__init__(self)
		self.widget.connect('clicked', self.on_url_clicked)
		self.citationmap = citationmapbuilder.citationmapbuilder()

	def on_url_clicked(self, widget, url, event):
		self.articleDetailsWindow = GuiArticleDetails.GuiArticleDetails()
		try:
			article = self.citationmap.articles[url]
			graph = self.citationmap.graph
			self.articleDetailsWindow.updateArticleInformation(url, article, graph)
		except:
			self.articleDetailsWindow.updateArticleInformation(url)


	def updateMinNumberOfReferences(self, adj):
		self.minNumberOfReferences = adj.value

	def updateMinNumberOfCitations(self, adj):
		self.minNumberOfCitations = adj.value

	def showOptionsWindow(self):
		self.optionsWindow = GuiOptionsWindow.GuiOptionsWindow()
		self.optionsWindow.adjMinNumberOfReferences.connect("value_changed", self.updateMinNumberOfReferences)
		self.optionsWindow.adjMinNumberOfCitations.connect("value_changed", self.updateMinNumberOfCitations)
		self.optionsWindow.showgraphbutton.connect("clicked", self.filterAndShowCurrentCitationMap, None)
		self.optionsWindow.exportgraphbutton.connect("clicked", self.exportFilteredCitationMap, None)
		self.optionsWindow.listofnodesbutton.connect("clicked", self.getListOfNodes, None)

	def on_open(self, action):
		chooser = gtk.FileChooserDialog(title="Open directory with bibliography",
										action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
										buttons=(gtk.STOCK_CANCEL,
												 gtk.RESPONSE_CANCEL,
												 gtk.STOCK_OPEN,
												 gtk.RESPONSE_OK))
		chooser.set_default_response(gtk.RESPONSE_OK)
		if chooser.run() == gtk.RESPONSE_OK:
			filename = chooser.get_filename()
			chooser.destroy()
			self.open_directory(filename)
		else:
			chooser.destroy()

		self.showOptionsWindow()


	def on_reload(self, action):
		print("Reload pressed")
		if self.openfilename is not None:
			try:
				self.open_directory(self.openfilename)
			except IOError:
				pass


	def open_directory(self, directory):
		self.openfilename = directory
		self.citationmap.__init__()
		files = os.listdir(directory)
		patterntxtfile = re.compile('.*\.txt')
		for file in files:
			res = patterntxtfile.match(file)
			#if(res):
			self.citationmap.parsefile(os.path.join(directory, file))
		self.origNetwork = self.citationmap.graph.copy()

	def filterCurrentCitationMap(self):
		self.citationmap.graph = self.origNetwork.copy()
		self.citationmap.analyzeGraph()
		self.citationmap.cleanUpGraph(self.minNumberOfReferences, self.minNumberOfCitations)

	def filterAndExportCurrentCitationMap(self):
		self.filterCurrentCitationMap()
		output = StringIO.StringIO()
		self.citationmap.outputGraph(output)
		dotcode = output.getvalue()
		return dotcode

	def filterAndShowCurrentCitationMap(self, action, data):
		dotcode = self.filterAndExportCurrentCitationMap()
		self.set_dotcode(dotcode)

	def exportFilteredCitationMap(self, action, data):
		chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE,
						buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
		if chooser.run() == gtk.RESPONSE_OK:
			filename = chooser.get_filename()
			chooser.destroy()

			exportfile = open(filename, 'w')
			dotcode = self.filterAndExportCurrentCitationMap()
			exportfile.write(dotcode)
			exportfile.close()

		else:
			chooser.destroy()
		return False

	def getListOfNodes(self, action, data):
		listOfNodes = GuiListOfArticlesInGraph.GuiListOfArticlesInGraph()
		self.filterCurrentCitationMap()
		listOfNodes.nodesTreestore.clear()
		for key in self.citationmap.graphForAnalysis.nodes():
			try:
				article = self.citationmap.articles[key]
				year = int(article['PY'][0])
				TC = int(article['TC'][0])
				NR = int(article['NR'][0])
				piter = listOfNodes.nodesTreestore.append(None, [key, year, TC, NR])
			except:
				pass


dotcode = """
digraph G {
  Hello [URL="http://en.wikipedia.org/wiki/Hello"]
  World [URL="http://en.wikipedia.org/wiki/World"]
	Hello -> World
}
"""

def main():
	window = MyDotWindow()
	window.set_dotcode(dotcode)
	window.connect('destroy', gtk.main_quit)
	window.showOptionsWindow()
	if(len(sys.argv) > 1):
		window.open_directory(sys.argv[1])

	gtk.main()

if __name__ == '__main__':
	main()
