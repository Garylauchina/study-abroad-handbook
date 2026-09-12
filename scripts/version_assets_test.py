"""Regression checks for fresh HTML being paired with cached, obsolete assets."""
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
import subprocess

from version_assets import on_post_build, retain_previous_assets


class VersionAssetsTest(unittest.TestCase):
    def test_cached_html_assets_survive_a_clean_release_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory) / 'repo'
            repo.mkdir()
            def git(*args):
                subprocess.run(['git', *args], cwd=repo, check=True, capture_output=True)
            git('init')
            name = 'assets/data/catalog-index.json'
            source = repo / 'docs' / name
            source.parent.mkdir(parents=True)
            old = b'[{"id":"old-program"}]'
            source.write_bytes(old)
            git('add', 'docs')
            git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'old release')
            source.write_bytes(b'{"universities":[],"programs":[]}')
            git('add', 'docs')
            git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'new release')
            built = Path(directory) / 'site'
            retain_previous_assets(built, [name, 'assets/new.css'], repo)
            old_url = f'assets/data/catalog-index.{hashlib.sha256(old).hexdigest()[:12]}.json'
            self.assertEqual((built / old_url).read_bytes(), old)
            self.assertFalse((built / 'assets/new.css').exists())

    def test_versioned_references_on_home_and_nested_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            contents = {
                'assets/stylesheets/handbook.css': '.country-grid{display:grid}',
                'assets/javascripts/catalog.mjs': 'export const catalog = true;',
                'assets/data/catalog-index.json': '[{"name":"计算机"}]',
            }
            for name, content in contents.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            nested = root / 'catalog/uk/index.html'
            nested.parent.mkdir(parents=True)
            home_html = '<link href="assets/stylesheets/handbook.css"><div data-catalog-url="assets/data/catalog-index.json"></div>'
            nested_html = ('<script type="module" src="../../assets/javascripts/catalog.mjs"></script>'
                           '<link href="/study-abroad-handbook/assets/stylesheets/handbook.css">'
                           '<a href="https://other.example/assets/stylesheets/handbook.css">external</a>')
            (root / 'index.html').write_text(home_html)
            nested.write_text(nested_html)
            config = SimpleNamespace(site_dir=root, site_url='https://example.test/study-abroad-handbook/',
                                     extra_css=['assets/stylesheets/handbook.css'],
                                     extra_javascript=['assets/javascripts/catalog.mjs'])
            on_post_build(config)
            manifest = json.loads((root / 'assets/asset-manifest.json').read_text())
            for source, destination in manifest.items():
                content = (root / source).read_bytes()
                self.assertEqual((root / destination).read_bytes(), content)
                self.assertIn(hashlib.sha256(content).hexdigest()[:12], destination)
            self.assertIn(manifest['assets/stylesheets/handbook.css'], (root / 'index.html').read_text())
            self.assertIn(manifest['assets/data/catalog-index.json'], (root / 'index.html').read_text())
            self.assertIn('../../' + manifest['assets/javascripts/catalog.mjs'], nested.read_text())
            self.assertIn('/study-abroad-handbook/' + manifest['assets/stylesheets/handbook.css'], nested.read_text())
            self.assertIn('type="module"', nested.read_text())
            self.assertIn('https://other.example/assets/stylesheets/handbook.css', nested.read_text())
            # A later data update must get a new URL even when its JavaScript stays unchanged.
            (root / 'assets/data/catalog-index.json').write_text('[{"name":"经济学"}]')
            (root / 'index.html').write_text(home_html)
            nested.write_text(nested_html)
            on_post_build(config)
            updated = json.loads((root / 'assets/asset-manifest.json').read_text())
            self.assertNotEqual(updated['assets/data/catalog-index.json'], manifest['assets/data/catalog-index.json'])
            self.assertEqual(updated['assets/javascripts/catalog.mjs'], manifest['assets/javascripts/catalog.mjs'])
            self.assertIn(updated['assets/data/catalog-index.json'], (root / 'index.html').read_text())


if __name__ == '__main__':
    unittest.main()
