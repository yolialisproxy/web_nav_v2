#!/usr/bin/env python3
"""
HTTP-level E2E smoke tests for web_nav_v2.
Runs against a live localhost:8080 server — no browser needed.

Run: python3 -m pytest tests/test_http_e2e.py -v --tb=short
"""

import json
import re
from pathlib import Path

import pytest
import urllib.request

BASE_URL = "http://localhost:8080"
PROJECT_ROOT = Path(__file__).parent.parent


def http_get(path, timeout=10):
    url = BASE_URL + (path if path.startswith("/") else f"/{path}")
    return urllib.request.urlopen(url, timeout=timeout)


class TestHttpE2E:
    """HTTP-level end-to-end smoke tests."""

    # ── Homepage ───────────────────────────────────────

    def test_01_homepage_returns_200(self):
        resp = http_get("/")
        assert resp.status == 200

    def test_02_homepage_has_critical_elements(self):
        resp = http_get("/")
        body = resp.read().decode("utf-8", errors="replace")
        # sites-grid is dynamically injected by JS; check static DOM only
        checks = {
            "header": 'id="header"',
            "sidebar": 'id="sidebar"',
            "main_content": 'id="main-content"',
            "search_input": 'id="search-input"',
            "view_switcher": 'id="view-switcher"',
            "view_grid": 'id="view-grid"',
            "view_list": 'id="view-list"',
        }
        missing = [n for n, s in checks.items() if s not in body]
        assert not missing, f"Homepage missing elements: {missing}"

    def test_03_homepage_no_unbalanced_js_braces(self):
        resp = http_get("/")
        body = resp.read().decode("utf-8", errors="replace")
        scripts = re.findall(r"<script[^>]*>(.*?)</script>", body, re.DOTALL)
        for i, s in enumerate(scripts):
            if 'src="' in s:
                continue
            opens, closes = s.count("{"), s.count("}")
            assert opens == closes, f"Script block {i}: {opens} open vs {closes} close braces"

    def test_04_homepage_has_view_grid_button(self):
        resp = http_get("/")
        body = resp.read().decode("utf-8", errors="replace")
        assert 'id="view-grid"', "Grid view button missing"
        assert 'id="view-list"', "List view button missing"

    # ── Data integrity ─────────────────────────────────

    def test_10_data_websites_json_loads(self):
        resp = http_get("/data/websites.json")
        assert resp.status == 200
        data = json.loads(resp.read())
        assert isinstance(data, list)
        assert len(data) > 3000

    def test_11_data_all_sites_have_required_fields(self):
        resp = http_get("/data/websites.json")
        data = json.loads(resp.read())
        for idx, site in enumerate(data):
            for field in ("name", "url", "category"):
                assert field in site, f"Site #{idx} missing '{field}': {site}"

    def test_12_data_all_urls_valid(self):
        resp = http_get("/data/websites.json")
        data = json.loads(resp.read())
        bad = [s for s in data if not s.get("url", "").startswith("http")]
        assert not bad, f"Sites with non-HTTP(S) URLs: {[s['name'] for s in bad[:5]]}"

    def test_13_data_no_literal_placeholder_urls_in_name_field(self):
        """Flag sites whose name field starts with http:// or https:// (URL used as name)."""
        resp = http_get("/data/websites.json")
        data = json.loads(resp.read())
        bad = [s for s in data if s.get("name", "").startswith(("http://","https://"))]
        assert not bad, f"Name field starts with a URL protocol: {[s['name'] for s in bad[:5]]}"

    def test_14_data_tag_index_valid(self):
        resp = http_get("/data/tag_index.json")
        assert resp.status == 200
        data = json.loads(resp.read())
        assert isinstance(data, list) and len(data) > 0
        for entry in data[:5]:
            assert "tag" in entry and "count" in entry

    # ── API / endpoints ────────────────────────────────

    def test_20_api_games_json_exists(self):
        resp = http_get("/api/games.json")
        assert resp.status == 200
        data = json.loads(resp.read())
        assert isinstance(data, list) and len(data) > 0

    def test_21_robots_txt_exists(self):
        resp = http_get("/robots.txt")
        assert resp.status == 200

    def test_22_sitemap_xml_exists(self):
        resp = http_get("/sitemap.xml")
        assert resp.status == 200
        body = resp.read().decode("utf-8", errors="replace")
        assert "<urlset" in body

    def test_23_manifest_json_valid(self):
        resp = http_get("/manifest.json")
        assert resp.status == 200
        data = json.loads(resp.read())
        assert "name" in data or "short_name" in data

    def test_24_sw_service_worker_exists(self):
        resp = http_get("/sw.js")
        assert resp.status == 200

    # ── Static assets ─────────────────────────────────

    def test_30_core_js_modules_exist(self):
        for mod in [
            "assets/js/state.js",
            "assets/js/data.js",
            "assets/js/search.js",
            "assets/js/render.js",
            "assets/js/app.js",
            "assets/js/game-hub.js",
        ]:
            r = http_get(f"/{mod}")
            assert r.status == 200, f"Missing JS module: /{mod}"

    def test_31_core_css_files_exist(self):
        for css in [
            "assets/css/core.css",
            "assets/css/app.css",
            "assets/css/game-hub.css",
        ]:
            r = http_get(f"/{css}")
            assert r.status == 200, f"Missing CSS file: /{css}"

    # ── Games ──────────────────────────────────────────

    def test_40_games_directory_has_nine_games(self):
        games_dir = PROJECT_ROOT / "assets/js/games"
        if not games_dir.exists():
            pytest.skip("games directory not found")
        game_files = sorted(games_dir.glob("*.js"))
        assert len(game_files) >= 8, f"Expected >=8 game files, got {len(game_files)}"
        names = {f.stem for f in game_files}
        expected = {"tetris", "gomoku", "2048", "chess", "solitaire"}
        missing = expected - names
        assert not missing, f"Missing expected games: {missing}"
