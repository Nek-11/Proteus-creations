import json
import unittest
from pathlib import Path

from app import build_summary, load_jobs, render_page


class CockpitTests(unittest.TestCase):
    def setUp(self):
        self.data_path = Path(__file__).parents[1] / "data" / "jobs.json"
        self.jobs = load_jobs(self.data_path)

    def test_sample_data_has_bordeaux_pipeline(self):
        self.assertGreaterEqual(len(self.jobs), 8)
        self.assertTrue(any(job["company"] == "Synapse Medicine" for job in self.jobs))

    def test_summary_counts_and_priority(self):
        summary = build_summary(self.jobs)
        self.assertEqual(summary["total"], len(self.jobs))
        self.assertGreaterEqual(summary["active"], 1)
        self.assertGreaterEqual(summary["top_priority"].get("priority", 0), 5)

    def test_page_contains_local_first_dashboard_hooks(self):
        page = render_page(self.jobs)
        self.assertIn("Bordeaux Job Cockpit", page)
        self.assertIn("data-job-id=\"synapse-ml\"", page)
        self.assertIn("localStorage", page)


if __name__ == "__main__":
    unittest.main()
