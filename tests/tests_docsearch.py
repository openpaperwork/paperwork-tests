import os

import unittest

from paperwork_backend import docsearch


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.docsearch = docsearch.DocSearch(os.path.join(os.getcwd(), "data"))
        self.docsearch.reload_index()

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
        docs = self.docsearch.find_documents(
            u"l'installation ' [) #####  gratuitement"
        )
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 2)
        self.assertIn("20121213_1946_26", docids)
        self.assertIn("weird name", docids)

    def test_negation(self):
        docs = self.docsearch.find_documents(
            u"installation AND NOT gratuitement"
        )
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 1)
        self.assertIn("20090215_1952_46", docids)

        # order shouldn't matter
        docs = self.docsearch.find_documents(
            u"NOT gratuitement AND installation"
        )
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 1)
        self.assertIn("20090215_1952_46", docids)

        docs = self.docsearch.find_documents(
            u"NOT gratuitement AND NOT installation"
        )
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 2)
        self.assertIn("20130126_1833_26", docids)
        self.assertIn("20130126_1902_26", docids)

    def test_label(self):
        docs = self.docsearch.find_documents(u"basiclabel")
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 1)
        self.assertIn("20090215_1952_46", docids)

        docs = self.docsearch.find_documents(u"annoyingly complex label")
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 1)
        self.assertIn("20090215_1952_46", docids)

        docs = self.docsearch.find_documents(u"NOT basiclabel")
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 4)
        self.assertIn("20121213_1946_26", docids)
        self.assertIn("20130126_1833_26", docids)
        self.assertIn("20130126_1902_26", docids)
        self.assertIn("weird name", docids)


class TestSuggestions(unittest.TestCase):
    def setUp(self):
        self.docsearch = docsearch.DocSearch(os.path.join(os.getcwd(), "data"))
        self.docsearch.reload_index()

    def test_single_keyword(self):
        sugges = self.docsearch.find_suggestions(u"installa")
        self.assertEqual(len(sugges), 1)
        self.assertIn("install", sugges)

    def test_multiple_keywords(self):
        sugges = self.docsearch.find_suggestions(u"installatio gratuitement")
        self.assertEqual(len(sugges), 2)
        self.assertIn("installation gratuitement", sugges)
        self.assertIn("installations gratuitement", sugges)

    def test_labels(self):
        sugges = self.docsearch.find_suggestions(u"basiclabe")
        self.assertEqual(len(sugges), 1)
        self.assertIn("basiclabel", sugges)

        sugges = self.docsearch.find_suggestions(u"annoyingl")
        self.assertEqual(len(sugges), 1)
        self.assertIn("annoyingly", sugges)

        sugges = self.docsearch.find_suggestions(u"annoyingl comple")
        self.assertEqual(len(sugges), 2)
        self.assertIn("annoyingly comple", sugges)
        self.assertIn("annoyingl complex", sugges)

    def test_negation(self):
        sugges = self.docsearch.find_suggestions(u"NOT installatio")
        self.assertEqual(len(sugges), 2)
        self.assertIn("NOT installation", sugges)
        self.assertIn("NOT installations", sugges)

    def tearDown(self):
        print("- Test done")
