#!/usr/bin/python
#
# Bugzilla client
#
# Copyright, (C) Eugeni Dodonov <eugeni@dodonov.net>, 2011
#
# Distributed according to GPLv2 license, please see COPYING for details
#
# encoding: utf-8

import os
import sys
import urllib
import urllib2
import xml.etree.cElementTree as ET

# this comes from python-bugz
from bugz import bugzilla

import pygtk
import gtk
import gobject
import pango
import glob

import gettext
import __builtin__
__builtin__._ = gettext.gettext

BUGZILLA_URL="https://qa.mandriva.com/"

class UI:
    (COLUMN_ID, COLUMN_STATUS, COLUMN_DESCR) = range(3)
    def __init__(self, bugz=None):
        """Initializes web UI for bugzilla"""

        self.bugz = bugz
        self.window = gtk.Window()
        self.window.set_title(_("Support client"))
        self.window.set_default_size(640, 480)
        self.window.connect('delete-event', lambda *w: gtk.main_quit())

        self.main_vbox = gtk.VBox()
        self.window.add(self.main_vbox)

        self.notebook = gtk.Notebook()
        self.main_vbox.pack_start(self.notebook)

        self.notebook.append_page(self.create_report_window(), gtk.Label(_("Report a problem")))
#        self.notebook.append_page(self.create_my_reports(), gtk.Label(_("My reported issues")))
        self.window.show_all()


    def create_report_window(self):
        vbox = gtk.VBox()

        label = gtk.Label(_("Please describe your problem"))
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
        buffer.insert(buffer.get_end_iter(), _("Please describe your problem in details"))
        vbox.pack_start(sw, False, False)

        hbox = gtk.HBox()
        # button
        button = gtk.Button(_("Search for similar bugs"))
        button.connect('clicked', self.search, textview)
        hbox.pack_start(button)

        # button
        button = gtk.Button(_("Report a new problem"))
        button.set_sensitive(False)
        button.connect('clicked', self.report)
        hbox.pack_start(button)

        vbox.pack_start(hbox, False, False)

        hbox = gtk.HBox()
        vbox.pack_start(gtk.Label("The following matches were found for your bug description:"), False, False)

        sw, lstore = self.create_bugs_view()
        self.bugs_lstore = lstore
        self.bugs_map = {}

        vbox.pack_start(sw)
        return vbox

    def create_bugs_view(self):
        """Creates a view for list of bugs"""

        # create the list of bugs view
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        # list of levels
        lstore = gtk.ListStore(
                gobject.TYPE_STRING,
                gobject.TYPE_STRING,
                gobject.TYPE_STRING)

        # bugs treeview
        treeview = gtk.TreeView(lstore)
        treeview.set_rules_hint(True)
        treeview.set_search_column(self.COLUMN_ID)
        treeview.connect('row-activated', self.bug_selected, lstore)

        renderer = gtk.CellRendererText()

        # column for bug id
        column = gtk.TreeViewColumn(_("Bug id"), renderer, text=self.COLUMN_ID)
        column.set_sort_column_id(self.COLUMN_ID)
        column.set_resizable(True)
        column.set_expand(False)
        treeview.append_column(column)

        # column for status
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Status"), renderer, text=self.COLUMN_STATUS)
        column.set_sort_column_id(self.COLUMN_STATUS)
        column.set_resizable(False)
        column.set_expand(True)
        treeview.append_column(column)

        # column for description
        renderer = gtk.CellRendererText()
        renderer.set_property('wrap-width', 400)
        renderer.set_property('wrap-mode', pango.WRAP_WORD_CHAR)
        column = gtk.TreeViewColumn(_("Description"), renderer, text=self.COLUMN_DESCR)
        column.set_sort_column_id(self.COLUMN_DESCR)
        column.set_resizable(True)
        column.set_expand(False)
        treeview.append_column(column)

        sw.add(treeview)

        return sw, lstore

    def bug_selected(self, treeview, path, col, model):
        """A bug was selected"""
        iter = model.get_iter(path)
        bug_id = model.get_value(iter, self.COLUMN_ID)
        if bug_id not in self.bugs:
            print "Error: no info on bug %s!" % bug_id
        bug = self.bugs[bug_id]

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

    def report(self, widget):
        """Report a new issue"""
        print "Reporting a new issue"

    def search(self, widget, textview):
        """Search for existing bugs"""
        print "Searching for bugs data"
        if not self.bugz:
            # TODO: show error message
            return
        buffer = textview.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        bugs = []
        # TODO: background and inteligent search
        for word in text.split(" "):
            results = self.bugz.search(text)
            print "Searching for %s" % word
            for bug in results:
                id = bug['bugid']
                status = bug['status']
                desc = bug['desc']
                bugs.append((id, status, desc))
                self.bugs_map[id] = bug
        # update bugs view
        lstore = self.bugs_lstore
        lstore.clear()
        for id, status, desc in bugs:
            iter = lstore.append()
            lstore.set(iter,
                    self.COLUMN_ID, id,
                    self.COLUMN_STATUS, status,
                    self.COLUMN_DESCR, desc
                    )


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
    bugz = bugzilla.Bugz(BUGZILLA_URL)
    ui = UI(bugz=bugz)
    gtk.main()
