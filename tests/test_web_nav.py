#!/usr/bin/env python3
"""
Test suite for web_nav_v2
"""

import json
import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "websites.json"

def load_sites():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

class TestDataIntegrity(unittest.TestCase):
    def test_data_file_exists(self):
        self.assertTrue(DATA_PATH.exists(), "Data file should exist")

    def test_data_is_valid_json(self):
        sites = load_sites()
        self.assertIsInstance(sites, list, "Data should be a list")

    def test_data_not_empty(self):
        sites = load_sites()
        self.assertGreater(len(sites), 0, "Data should not be empty")

    def test_each_site_has_required_fields(self):
        sites = load_sites()
        required_fields = ['name', 'url', 'category']
        for site in sites:
            for field in required_fields:
                self.assertIn(field, site, f"Site missing required field: {field}")
                self.assertTrue(site[field], f"Field '{field}' should not be empty")

    def test_url_format(self):
        sites = load_sites()
        for site in sites:
            url = site['url']
            self.assertTrue(
                url.startswith('http://') or url.startswith('https://'),
                f"URL should start with http:// or https://: {url}"
            )

    def test_category_count(self):
        sites = load_sites()
        categories = set(site['category'] for site in sites)
        self.assertGreater(len(categories), 10, "Should have more than 10 categories")
        self.assertLess(len(categories), 300, "Should have less than 300 categories")

    def test_tag_index_exists_and_valid(self):
        tag_path = PROJECT_ROOT / "data" / "tag_index.json"
        self.assertTrue(tag_path.exists(), "tag_index.json should exist")
        with open(tag_path, 'r', encoding='utf-8') as f:
            tag_data = json.load(f)
        self.assertIsInstance(tag_data, list, "tag_index should be a list")
        self.assertGreater(len(tag_data), 0, "tag_index should not be empty")
        for entry in tag_data[:10]:
            self.assertIn('tag', entry, "each entry must have 'tag'")
            self.assertIn('count', entry, "each entry must have 'count'")
            self.assertGreaterEqual(entry['count'], 0, "count must be >= 0")


class TestPerformance(unittest.TestCase):
    def test_json_load_time(self):
        import time
        start = time.time()
        sites = load_sites()
        load_time = time.time() - start
        self.assertLess(load_time, 2.0, f"JSON load time too high: {load_time:.2f}s")

    def test_data_size(self):
        size = DATA_PATH.stat().st_size
        self.assertLess(size, 10 * 1024 * 1024, f"Data size too large: {size / 1024 / 1024:.2f}MB")

class TestFileStructure(unittest.TestCase):
    def test_required_directories_exist(self):
        required_dirs = ['assets', 'assets/css', 'assets/js', 'pages', 'scripts', 'tests']
        for dir_path in required_dirs:
            full_path = PROJECT_ROOT / dir_path
            self.assertTrue(full_path.exists(), f"Directory should exist: {dir_path}")

    def test_key_files_exist(self):
        required_files = [
            'index.html',
            'assets/css/core.css',
            'assets/js/app.js',
            'pages/category.html',
            'pages/site-detail.html',
            'pages/search-results.html',
            'serve.py',
        ]
        for file_path in required_files:
            full_path = PROJECT_ROOT / file_path
            self.assertTrue(full_path.exists(), f"File should exist: {file_path}")

class TestFrontendIntegration(unittest.TestCase):
    def test_html_structure(self):
        index_path = PROJECT_ROOT / "index.html"
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('<html', content, "HTML should have <html> tag")
        self.assertIn('charset="UTF-8"', content, "HTML should have UTF-8 charset")

    def test_css_loaded(self):
        index_path = PROJECT_ROOT / "index.html"
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        css_files = ['core.css', 'app.css']
        for css_file in css_files:
            self.assertIn(css_file, content, f"HTML should link to {css_file}")

    def test_js_loaded(self):
        index_path = PROJECT_ROOT / "index.html"
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        js_files = ['state.js', 'data.js', 'app.js']
        for js_file in js_files:
            self.assertIn(js_file, content, f"HTML should include {js_file}")

class TestBackend(unittest.TestCase):
    def test_serve_py_exists(self):
        serve_path = PROJECT_ROOT / "serve.py"
        self.assertTrue(serve_path.exists(), "serve.py should exist")
        with open(serve_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('http.server', content, "serve.py should use http.server")

class TestPages(unittest.TestCase):
    def test_category_page_exists(self):
        page_path = PROJECT_ROOT / "pages" / "category.html"
        self.assertTrue(page_path.exists(), "category.html should exist")

    def test_site_detail_page_exists(self):
        page_path = PROJECT_ROOT / "pages" / "site-detail.html"
        self.assertTrue(page_path.exists(), "site-detail.html should exist")

    def test_search_results_page_exists(self):
        page_path = PROJECT_ROOT / "pages" / "search-results.html"
        self.assertTrue(page_path.exists(), "search-results.html should exist")

if __name__ == '__main__':
    unittest.main(verbosity=2)
