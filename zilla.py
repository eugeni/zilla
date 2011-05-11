#!/usr/bin/python
# encoding: utf-8

import os
import sys
import urllib
import urllib2
import xml.etree.cElementTree as ET

import pygtk
import gtk
import gobject
import glob

class UI:
    def __init__(self):
        self.window = gtk.Window()
        self.window.set_title("Support client")
        self.window.set_default_size(640, 480)
        self.window.connect('delete-event', lambda *w: gtk.main_quit())

        self.main_vbox = gtk.VBox()
        self.window.add(self.main_vbox)

        self.notebook = gtk.Notebook()
        self.main_vbox.pack_start(self.notebook)

        self.notebook.append_page(self.create_report_window(), gtk.Label("Report a problem"))
        self.notebook.append_page(self.create_my_reports(), gtk.Label("My reported issues"))
        self.window.show_all()


    def create_report_window(self):
        vbox = gtk.VBox()

        label = gtk.Label("Please describe your problem")
        vbox.pack_start(label, False, False)
        # input text
        textview = gtk.TextView()
        textview.set_wrap_mode(gtk.WRAP_WORD)
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(textview)
        self.textview = textview

        buffer = textview.get_buffer()
        buffer.insert(buffer.get_end_iter(), "Кривые шрифты, ждем ебилдов (типа пример)...")
        vbox.pack_start(sw, False, False)

        # button
        button = gtk.Button("Search for existing bugs")
        button.set_sensitive(False)
        button.connect('clicked', self.search, textview)

        vbox.pack_start(button, False, False)

        hbox = gtk.HBox()
        vbox.pack_start(gtk.HSeparator(), True, False)
        vbox.pack_start(gtk.Label("The following matches were found for your bug description:"), False, False)
        vbox.pack_start(hbox, False, False)

        # hack hack hack - pregenerate list of reports
        for bug in ["40050", "62820", "62727"]:
            button = gtk.Button("Possible similar bug %s" % bug)
            button.connect('clicked', self.load_bug, bug, textview)
            hbox.pack_start(button)


        hbox = gtk.HBox()
        vbox.pack_start(gtk.HSeparator(), True, False)
        vbox.pack_start(gtk.Label("The following test-cases are available which could help you investigate the issue:"), False, False)
        vbox.pack_start(hbox, False, False)

        # hack hack hack - pregenerate list of reports
        for bug in ["test-fonts", "test-display-resolution", "test-kde-packages"]:
            button = gtk.Button("Testcase: %s" % bug)
            #button.connect('clicked', self.load_bug, bug, textview)
            hbox.pack_start(button)

        vbox.pack_start(gtk.VSeparator(), True, False)
        return vbox

    def create_my_reports(self):
        vbox = gtk.VBox()

        label = gtk.Label("My reported problems")
        vbox.pack_start(label, False, False)
        # input text
        hbox = gtk.HBox()
        vbox.pack_start(hbox, False, False)

        textview = gtk.TextView()
        textview.set_wrap_mode(gtk.WRAP_WORD)
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(textview)
        self.textview = textview

        vbox.pack_start(sw)

        # hack hack hack - pregenerate list of reports
        for bug in ["1235", "62820", "62727"]:
            button = gtk.Button("Issue %s" % bug)
            button.connect('clicked', self.load_bug, bug, textview)
            hbox.pack_start(button)

        return vbox

    def search(self, widget):
        print "Searching for bugs data"
        buffer = self.textview.get_buffer()

    def load_bug(self, widget, bug, view):
        print "Loading info for bug %s" % bug
        buffer = view.get_buffer()
        buffer.delete(buffer.get_start_iter(), buffer.get_end_iter())

        req = urllib2.Request("https://qa.mandriva.com/show_bug.cgi?id=%s&ctype=xml" % bug)
        resp = urllib2.urlopen(req).read()
        print resp

        try:
            res = ET.fromstring(resp)
        except SyntaxError:
            # looks like we found an invalid character
            print >>sys.stderr, "Invalid characters found, ignoring..",
            return

        for bug in res:
            for item in ["creation_ts", "short_desc", "product", "version", "bug_status", "resolution", "reporter", "assigned_to"]:
                val = bug.findtext("./%s" % item)
                buffer.insert(buffer.get_end_iter(), "%s: %s\n" % (item, val))

            buffer.insert(buffer.get_end_iter(), "\n\n")
            for comment in bug.findall("./long_desc/thetext"):
                buffer.insert(buffer.get_end_iter(), "-----\n%s\n" % comment.text)

if __name__ == "__main__":
    ui = UI()
    gtk.main()
