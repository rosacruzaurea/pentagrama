"""Author typing, omissions and the published Book contract."""
import json
import re
import unittest
from seo import metadata, structured_authors


class AuthorTests(unittest.TestCase):
    def test_person(self):
        self.assertEqual(structured_authors({'authors': ['Jan van Rijckenborgh']}),
                         [{'@type': 'Person', 'name': 'Jan van Rijckenborgh'}])

    def test_institution(self):
        self.assertEqual(structured_authors({'authors': ['Lectorium Rosicrucianum']}),
                         [{'@type': 'Organization', 'name': 'Lectorium Rosicrucianum'}])

    def test_coauthors_preserved(self):
        names = ['Catharose de Petri', 'Jan van Rijckenborgh']
        self.assertEqual([a['name'] for a in structured_authors({'authors': names})], names)

    def test_missing_and_traditional_not_asserted(self):
        for entry in [{}, {'authors': []}, {'authors': ['Hermes trimegisto']}]:
            self.assertEqual(structured_authors(entry), [])

    def test_unknown_coauthor_does_not_create_partial_attribution(self):
        self.assertEqual(structured_authors({'authors': ['Jan van Rijckenborgh', 'Unknown']}), [])

    def test_book_only_and_safe_json(self):
        for kind in ['livro', 'revista']:
            for names in [[], ['Hermes trimegisto'], ['Lectorium Rosicrucianum']]:
                entry = {'type': kind, 'title': 'A < B', 'authors': names, 'html': '', 'cover': ''}
                output = metadata(entry['title'], '', '/livros/example/', '/livros/example/', entry, '/logo.png', False)
                raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', output).group(1)
                self.assertNotIn('<', raw)
                work = json.loads(raw)['@graph'][-1]
                expected = kind == 'livro' and names == ['Lectorium Rosicrucianum']
                self.assertEqual('author' in work, expected)
                for field in ['isbn', 'datePublished', 'publisher']:
                    self.assertNotIn(field, work)


if __name__ == '__main__':
    unittest.main()
