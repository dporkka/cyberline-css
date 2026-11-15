"""Keep release-audit counts precise without claiming incomplete checks pass."""
import unittest
from tests.axe_audit import summarize_findings


class AxeAuditSummaryTests(unittest.TestCase):
    def test_summarizes_nodes_and_rule_groups_separately(self):
        findings = [
            {"page": "index.html", "violations": [{"rule": "button-name"}],
             "incomplete": [{"rule": "color-contrast"}, {"rule": "color-contrast"},
                            {"rule": "aria-allowed-attr"}]},
            {"page": "docs/index.html", "violations": [],
             "incomplete": [{"rule": "color-contrast"}]},
            {"page": "examples/plain.html", "violations": [], "incomplete": []},
        ]
        report = summarize_findings(findings)
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["totals"], {
            "pages": 3, "confirmed_violation_nodes": 1,
            "incomplete_nodes": 4, "incomplete_page_rule_groups": 3,
            "incomplete_by_rule": {"aria-allowed-attr": 1, "color-contrast": 3}
        })
        self.assertEqual(report["pages"][0]["incomplete_by_rule"], {
            "aria-allowed-attr": 1, "color-contrast": 2})
        self.assertEqual(report["pages"][2]["incomplete_nodes"], 0)
        self.assertNotIn("passes", report["totals"])

    def test_empty_report_is_explicitly_empty(self):
        result = summarize_findings([])
        self.assertEqual(result["totals"]["pages"], 0)
        self.assertEqual(result["totals"]["incomplete_nodes"], 0)


if __name__ == "__main__":
    unittest.main()
