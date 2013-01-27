import os
import sys

import unittest

from paperwork.backend import docsearch


class TestSearch(unittest.TestCase):
    def progress_cb(self, progression, total, step, doc=""):
        print ("%s : %d/%d : %s ..." % (step, progression, total, doc))

    def setUp(self):
        print ""
        print "- Initializing ..."
        self.docsearch = docsearch.DocSearch(os.path.join(os.getcwd(), "data"),
                                            self.progress_cb)
        print "- Testing ..."

    def test_all(self):
        docs = self.docsearch.find_documents(u"")
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 5)
        self.assertIn("20090215_1952_46", docids)
        self.assertIn("20121213_1946_26", docids)
        self.assertIn("20130126_1833_26", docids)
        self.assertIn("20130126_1902_26", docids)
        self.assertIn("weird name", docids)

    def test_single_keyword(self):
        docs = self.docsearch.find_documents(u"gratuitement")
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 2)
        self.assertIn("20121213_1946_26", docids)
        self.assertIn("weird name", docids)

        docs = self.docsearch.find_documents(u"gratuitem")
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 0)

        docs = self.docsearch.find_documents(u"l'installation")
        # "l'installation" is splited into 2 words: "l" and "installation"
        # "l" is too short, so it should be ignored
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 3)
        self.assertIn("20090215_1952_46", docids)  # contains "l'installation"
        self.assertIn("20121213_1946_26", docids)  # contains "installation" 
        self.assertIn("weird name", docids)  # contains "l'installation"

        # unicode
        txt = unicode('\xc3\xa9ligibilit\xc3\xa9', encoding='utf-8')
        docs = self.docsearch.find_documents(txt)
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 1)
        self.assertIn("weird name", docids)


    def test_multiple_keywords(self):
        docs = self.docsearch.find_documents(u"gratuitement l'installation")
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 2)
        self.assertIn("20121213_1946_26", docids)
        self.assertIn("weird name", docids)

        docs = self.docsearch.find_documents(u"gratuitement boucle")
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 1)
        self.assertIn("weird name", docids)

        # keyword order and extra spaces shouldn't matter
        docs = self.docsearch.find_documents(u"l'installation   gratuitement")
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 2)
        self.assertIn("20121213_1946_26", docids)
        self.assertIn("weird name", docids)

        # weird thingies should be ignored
        docs = self.docsearch.find_documents(u"l'installation ' [) #####  gratuitement")
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 2)
        self.assertIn("20121213_1946_26", docids)
        self.assertIn("weird name", docids)

    def test_negation(self):
        docs = self.docsearch.find_documents(u"installation !gratuitement")
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 1)
        self.assertIn("20090215_1952_46", docids)

        # order shouldn't matter
        docs = self.docsearch.find_documents(u"!gratuitement installation")
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 1)
        self.assertIn("20090215_1952_46", docids)

        # TOFIX(Jflesch)
        #docs = self.docsearch.find_documents(u"!gratuitement !installation")
        #docids = [doc.docid for doc in docs]
        #self.assertEqual(len(docids), 2)
        #self.assertIn("20130126_1833_26", docids)
        #self.assertIn("20130126_1902_26", docids)

    def test_label(self):
        # TOFIX(Jflesch)
        #docs = self.docsearch.find_documents(u"basiclabel")
        #docids = [doc.docid for doc in docs]
        #self.assertEqual(len(docids), 1)
        #self.assertIn("20090215_1952_46", docids)

        # TOFIX(Jflesch)
        #docs = self.docsearch.find_documents(u"annoyingly complex label")
        #docids = [doc.docid for doc in docs]
        #self.assertEqual(len(docids), 1)
        #self.assertIn("20090215_1952_46", docids)

        # TOFIX(Jflesch)
        #docs = self.docsearch.find_documents(u"!basiclabel")
        #docids = [doc.docid for doc in docs]
        #self.assertEqual(len(docids), 4)
        #self.assertIn("20121213_1946_26", docids)
        #self.assertIn("20130126_1833_26", docids)
        #self.assertIn("20130126_1902_26", docids)
        #self.assertIn("weird name", docids)
        pass


class TestSuggestions(unittest.TestCase):
    def progress_cb(self, progression, total, step, doc=""):
        print ("%s : %d/%d : %s ..." % (step, progression, total, doc))

    def setUp(self):
        print ""
        print "- Initializing ..."
        self.docsearch = docsearch.DocSearch(os.path.join(os.getcwd(), "data"),
                                            self.progress_cb)
        print "- Testing ..."

    def test_single_keyword(self):
        sugges = self.docsearch.find_suggestions(u"installa")
        self.assertEqual(len(sugges), 2)
        self.assertIn("installation", sugges)
        self.assertIn("installations", sugges)

    def test_multiple_keywords(self):
        sugges = self.docsearch.find_suggestions(u"installa gratuite")
        self.assertEqual(len(sugges), 2)
        self.assertIn("installation gratuitement", sugges)
        self.assertIn("installations gratuitement", sugges)

    def test_labels(self):
        # TOFIX(Jflesch)
        #sugges = self.docsearch.find_suggestions(u"basicl")
        #self.assertEqual(len(sugges), 1)
        #self.assertIn("basicl", sugges)

        # TOFIX(Jflesch)
        #sugges = self.docsearch.find_suggestions(u"annoyin")
        #self.assertEqual(len(sugges), 1)
        #self.assertIn("annoyingly", sugges)

        # TOFIX(Jflesch)
        #sugges = self.docsearch.find_suggestions(u"annoyin comple")
        #self.assertEqual(len(sugges), 1)
        #self.assertIn("annoyingly complex", sugges)
        pass

    def test_negation(self):
        sugges = self.docsearch.find_suggestions(u"!installa")
        self.assertEqual(len(sugges), 2)
        self.assertIn("!installation", sugges)
        self.assertIn("!installations", sugges)

    def tearDown(self):
        print "- Test done"


def get_all_tests():
    all_tests = unittest.TestSuite()

    tests = unittest.TestSuite([
            TestSearch("test_all"),
            TestSearch("test_single_keyword"),
            TestSearch("test_multiple_keywords"),
            TestSearch("test_negation"),
            TestSearch("test_label"),
        ])
    all_tests.addTest(tests)

    tests = unittest.TestSuite([
            TestSuggestions("test_single_keyword"),
            TestSuggestions("test_labels"),
            TestSuggestions("test_multiple_keywords"),
            TestSuggestions("test_negation"),
        ])
    all_tests.addTest(tests)

    return all_tests
