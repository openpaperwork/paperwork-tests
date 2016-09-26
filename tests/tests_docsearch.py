import unittest

from paperwork_backend.config import PaperworkConfig
from paperwork_backend import docsearch


class DocSearchInit(object):
    def init_docsearch(self):
        new_docs = set()
        upd_docs = set()
        missing_docs = set()

        config = PaperworkConfig()
        config.read()

        # start from scratch
        dsearch = docsearch.DocSearch(config['workdir'].value)
        dsearch.destroy_index()

        dsearch = docsearch.DocSearch(config['workdir'].value)
        dsearch.reload_index()

        doc_examiner = dsearch.get_doc_examiner()
        doc_examiner.examine_rootdir(
            lambda x: new_docs.add(x),
            lambda x: upd_docs.add(x),
            lambda x: missing_docs.add(x),
            lambda x: None,
        )

        assert(len(upd_docs) <= 0)
        assert(len(missing_docs) <= 0)

        index_updater = dsearch.get_index_updater()
        for doc in new_docs:
            index_updater.add_doc(doc)
        index_updater.commit()

        return dsearch


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.docsearch = DocSearchInit().init_docsearch()

    def test_all_docs_in(self):
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
        self.assertIn("20121213_1946_26", docids)
        self.assertIn("weird name", docids)
        self.assertNotIn("20090215_1952_46", docids)

        docs = self.docsearch.find_documents(u"gratuitem")
        docids = [doc.docid for doc in docs]
        self.assertIn("20121213_1946_26", docids)
        self.assertIn("weird name", docids)
        self.assertNotIn("20090215_1952_46", docids)

        # unicode
        txt = b'\xc3\xa9ligibilit\xc3\xa9'.decode('utf-8')
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

    def test_negation(self):
        docs = self.docsearch.find_documents(
            u"installation AND NOT gratuitement"
        )
        docids = [doc.docid for doc in docs]
        self.assertIn("20090215_1952_46", docids)
        self.assertNotIn("20121213_1946_26", docids)

    def test_negation2(self):
        # order shouldn't matter
        docs = self.docsearch.find_documents(
            u"NOT gratuitement AND installation"
        )
        docids = [doc.docid for doc in docs]
        self.assertIn("20090215_1952_46", docids)
        self.assertNotIn("20121213_1946_26", docids)

    def test_negation3(self):
        docs = self.docsearch.find_documents(
            "NOT arcep AND NOT FIA-NET"
        )
        docids = [doc.docid for doc in docs]
        self.assertIn("20121213_1946_26", docids)
        self.assertIn("20090215_1952_46", docids)
        self.assertNotIn("weird name", docids)
        self.assertNotIn("20130126_1833_26", docids)

    def test_label(self):
        docs = self.docsearch.find_documents(u"basiclabel")
        docids = [doc.docid for doc in docs]
        self.assertEqual(len(docids), 1)
        self.assertIn("20090215_1952_46", docids)

        docs = self.docsearch.find_documents(u"\"annoyingly complex label\"")
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
        self.docsearch = DocSearchInit().init_docsearch()

    def test_single_keyword(self):
        sugges = self.docsearch.find_suggestions(u"installation")
        self.assertIn("installations", sugges)

    def test_multiple_keywords(self):
        sugges = self.docsearch.find_suggestions(u"installatio gratuitement")
        self.assertIn("installation gratuitement", sugges)
        self.assertIn("installations gratuitement", sugges)

    def test_labels(self):
        sugges = self.docsearch.find_suggestions(u"basiclabe")
        self.assertIn("basiclabel", sugges)

        sugges = self.docsearch.find_suggestions(u"annoyingl")
        self.assertIn("annoyingly", sugges)

    def test_negation(self):
        sugges = self.docsearch.find_suggestions(u"NOT installatio")
        self.assertIn("NOT installations", sugges)
