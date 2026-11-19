"""Contract for Vertigo-inspired, copyable, zero-JS SaaS resource composition."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "examples/vertigo-resource-workflow.html"

class Audit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags=[]; self.ids=set(); self.labels=set(); self.links=[]; self.inputs=[]; self.scripts=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs); self.tags.append((tag,a))
        if "id" in a: self.ids.add(a["id"])
        if tag=="label" and "for" in a: self.labels.add(a["for"])
        if tag=="a": self.links.append(a.get("href",""))
        if tag in ("input","select","textarea"): self.inputs.append(a)
        if tag=="script": self.scripts+=1

class VertigoResourceReference(unittest.TestCase):
    def test_reference_is_a_semantic_four_stage_resource_workflow(self):
        p=Audit(); html=PAGE.read_text(); p.feed(html)
        self.assertEqual(p.scripts,0)
        self.assertEqual(sum(tag=="main" for tag,_ in p.tags),1)
        self.assertEqual(sum(tag=="h1" for tag,_ in p.tags),1)
        self.assertTrue({"main","resources","resource-detail","resource-editor","workspace-settings"} <= p.ids)
        self.assertEqual(sum(tag=="table" for tag,_ in p.tags),1)
        self.assertEqual(sum(tag=="caption" for tag,_ in p.tags),1)
        self.assertIn('method="get"', html)
        self.assertIn('method="post"', html)
        self.assertIn('fieldset disabled', html)
        self.assertIn('aria-describedby="resource-error"', html)
        self.assertIn('aria-invalid="true"', html)
        self.assertIn('data-syn-theme="studio"', html)
        self.assertIn('syn-app-shell',html)
        self.assertIn('syn-table',html)
        self.assertIn('syn-field',html)
        self.assertIn('syn-detail-layout',html)
        self.assertIn('No backend',html)
        for i in p.inputs:
            if i.get("id"): self.assertIn(i["id"],p.labels)
        for href in p.links:
            if href.startswith("#") and href != "#":
                self.assertIn(href[1:],p.ids)

    def test_example_is_local_css_only_and_published_explicitly(self):
        page=PAGE.read_text()
        for path in ("../dist/syntyr.core.css","../dist/syntyr.recipes.css","vertigo-resource-workflow.css"):
            self.assertIn('href="'+path+'"',page)
            self.assertTrue((PAGE.parent / path).is_file())
        styles=(ROOT/"examples/vertigo-resource-workflow.css").read_text()
        self.assertIn(".vrw-",styles)
        self.assertNotIn("@import",styles)
        self.assertNotIn("@keyframes",styles)
        self.assertIn("vertigo-resource-workflow.html",(ROOT/"README.md").read_text())
        self.assertIn("vertigo-resource-workflow.html",(ROOT/"docs/index.html").read_text())
        self.assertIn("vertigo-resource-workflow.html",(ROOT/"llms.txt").read_text())
        site=(ROOT/"scripts/build_cloudflare_site.py").read_text()
        self.assertIn('"vertigo-resource-workflow.html"',site)
        self.assertIn('"vertigo-resource-workflow.css"',site)

        for test_path in ("tests/browser_matrix.py","tests/reflow_test.py","tests/axe_audit.py"):
            self.assertIn("vertigo-resource-workflow.html",(ROOT/test_path).read_text())

if __name__=="__main__": unittest.main()
