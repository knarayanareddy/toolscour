"""
Unit tests for the AI ToolScour pipeline.

Run from the repository root:
    python3 -m unittest discover -s pipeline -p "test_*.py" -v

Network access is never required: GitHub tree lookups are stubbed.
"""

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import harvest_ai_tools as harvest  # noqa: E402
import taxonomy_ai as taxonomy  # noqa: E402
import validate_corpus as validator  # noqa: E402


def _hf_raw(**overrides):
    raw = {
        "id": "hf-acme--tiny-model",
        "name": "tiny-model",
        "owner": "acme",
        "description": "Hugging Face text-generation model: acme/tiny-model",
        "stars": 1200,
        "forks": 40,
        "language": "Python",
        "license": "apache-2.0",
        "topics": ["huggingface", "model-weights", "text-generation"],
        "pushed_at": "2026-01-01T00:00:00Z",
        "source": "huggingface",
        "url": "https://huggingface.co/acme/tiny-model",
    }
    raw.update(overrides)
    return raw


class EnrichmentTests(unittest.TestCase):
    def test_hf_record_keeps_hub_url_and_hub_quickstart(self):
        rec = harvest.enrich_huggingface_record(_hf_raw())
        self.assertEqual(rec["url"], "https://huggingface.co/acme/tiny-model")
        self.assertIn("hf download acme/tiny-model", rec["quickstart_code"])
        self.assertNotIn("git clone", rec["quickstart_code"])
        self.assertEqual(rec["source"], "huggingface")
        for field in validator.REQUIRED_ENRICHMENT:
            self.assertTrue(rec.get(field), field)

    def test_github_record_still_defaults_to_github_url(self):
        rec = taxonomy.enrich_repository_record({
            "id": 1, "name": "agent-kit", "owner": "acme", "description": "LLM agent toolkit",
            "stars": 900, "forks": 1, "language": "Python", "license": "MIT", "topics": ["llm"],
            "pushed_at": "2026-01-01T00:00:00Z",
        })
        self.assertEqual(rec["url"], "https://github.com/acme/agent-kit")
        self.assertEqual(rec["quickstart_code"], "git clone https://github.com/acme/agent-kit.git")

    def test_landmark_override_does_not_leak_onto_hub_record(self):
        landmark_key = next(iter(taxonomy.LANDMARK_INTEL))
        owner, name = landmark_key.split("/", 1)
        raw = _hf_raw(id=f"hf-{owner}--{name}", owner=owner, name=name,
                      url=f"https://huggingface.co/{owner}/{name}")
        rec = harvest.enrich_huggingface_record(raw)
        self.assertNotIn("git clone", rec["quickstart_code"])

    def test_ensure_enriched_backfills_legacy_hub_record(self):
        legacy = {k: v for k, v in _hf_raw().items()}  # no taxonomy fields, as in the old corpus
        fixed = harvest.ensure_enriched(legacy)
        self.assertEqual(fixed["domain"] in taxonomy.TAXONOMY_RULES, True)
        self.assertEqual(fixed["url"], legacy["url"])

    def test_ensure_enriched_leaves_github_records_alone(self):
        rec = {"id": 2, "name": "x", "owner": "y", "url": "https://github.com/y/x"}
        self.assertIs(harvest.ensure_enriched(rec), rec)


class ArchivedAndGateTests(unittest.TestCase):
    def _node(self, **overrides):
        node = {
            "databaseId": 7, "name": "lib", "owner": {"login": "org"}, "description": "LLM library",
            "stargazerCount": 800, "forkCount": 3, "primaryLanguage": {"name": "Python"},
            "licenseInfo": {"spdxId": "MIT"}, "repositoryTopics": {"nodes": []},
            "pushedAt": "2026-01-01T00:00:00Z", "isArchived": False,
        }
        node.update(overrides)
        return node

    def test_archived_repos_are_skipped(self):
        self.assertIsNone(harvest.parse_node(self._node(isArchived=True)))
        self.assertIsNotNone(harvest.parse_node(self._node()))

    def test_gate_requires_ai_signal_and_description(self):
        self.assertTrue(harvest.passes_new_record_gate(
            {"name": "mlx-examples", "description": "Examples in the MLX framework", "topics": []}))
        self.assertFalse(harvest.passes_new_record_gate(
            {"name": "Babylon.js", "description": "A game and rendering engine", "topics": []}))
        self.assertFalse(harvest.passes_new_record_gate(
            {"name": "llm-thing", "description": "", "topics": ["llm"]}))

    def test_gate_does_not_match_inside_words(self):
        self.assertFalse(harvest.passes_new_record_gate(
            {"name": "xmlparser", "description": "Fast XML parsing", "topics": []}))


class SkillVerificationTests(unittest.TestCase):
    def _tree_response(self, paths):
        body = mock.MagicMock()
        body.read.return_value = (
            '{"tree": [' + ",".join(f'{{"path": "{p}", "type": "blob"}}' for p in paths) + "]}"
        ).encode()
        ctx = mock.MagicMock()
        ctx.__enter__.return_value = body
        ctx.__exit__.return_value = False
        return ctx

    def test_detects_nested_skill_md(self):
        with mock.patch("urllib.request.urlopen",
                        return_value=self._tree_response(["README.md", "skills/review/SKILL.md"])):
            self.assertTrue(harvest.repo_ships_skill_md("o", "r", "t"))

    def test_rejects_repo_without_skill_md(self):
        with mock.patch("urllib.request.urlopen", return_value=self._tree_response(["src/main.py"])):
            self.assertFalse(harvest.repo_ships_skill_md("o", "r", "t"))

    def test_unreadable_tree_returns_none(self):
        with mock.patch("urllib.request.urlopen", side_effect=OSError("boom")):
            self.assertIsNone(harvest.repo_ships_skill_md("o", "r", "t"))

    def test_unverified_candidate_is_reclassified_not_dropped(self):
        rec = {"id": 9, "name": "awesome-agent-skills", "owner": "o",
               "description": "A curated list of agent skills", "topics": ["agent-skills"],
               "artifact": "Agent Skill Pack"}
        with mock.patch.object(harvest, "repo_ships_skill_md", return_value=False), \
                mock.patch.object(harvest.time, "sleep"):
            harvest.verify_skill_flags([rec], "token")
        self.assertIs(rec["skill_verified"], False)
        self.assertEqual(rec["artifact"], "Curated List / Docs")

    def test_prior_verdict_is_reused_without_api_call(self):
        rec = {"id": 9, "name": "skills", "owner": "o", "description": "", "topics": [],
               "artifact": "Agent Skill Pack"}
        with mock.patch.object(harvest, "repo_ships_skill_md") as api:
            harvest.verify_skill_flags([rec], "token", prior_by_id={"9": {"skill_verified": True}})
        api.assert_not_called()
        self.assertEqual(rec["artifact"], "Agent Skill Pack")

    def test_verified_skill_survives_truncated_refetch(self):
        # Re-fetch lost the 'agent-skills' topic, so the fresh classification is not a skill.
        fresh = {"id": 9, "name": "reactive-resume", "owner": "o", "description": "resume builder",
                 "topics": ["react"], "artifact": "UI / Application"}
        with mock.patch.object(harvest, "repo_ships_skill_md") as api:
            harvest.verify_skill_flags([fresh], "token", prior_by_id={"9": {"skill_verified": True}})
        api.assert_not_called()
        self.assertEqual(fresh["artifact"], "Agent Skill Pack")
        self.assertIs(fresh["skill_verified"], True)

    def test_no_token_never_demotes_skill_packs(self):
        rec = {"id": 9, "name": "skills", "owner": "o", "description": "", "topics": [],
               "artifact": "Agent Skill Pack"}
        harvest.verify_skill_flags([rec], None)
        self.assertEqual(rec["artifact"], "Agent Skill Pack")
        self.assertNotIn("skill_verified", rec)

    def test_new_skill_patterns_detected(self):
        self.assertTrue(taxonomy.is_skill_pack("stop-slop", "A skill file for removing AI tells from prose", []))
        self.assertTrue(taxonomy.is_skill_pack("design", "HTML-native design skill for Claude Code", []))
        # SDK for a voice platform that merely contains the word "skills": not an agent skill pack.
        self.assertFalse(taxonomy.is_skill_pack("alexa-skills-kit-sdk-for-python",
                                                "The Alexa Skills Kit SDK for Python helps you get a skill up and running", []))

    def test_classify_artifact_respects_allow_skill_flag(self):
        self.assertNotEqual(taxonomy.classify_artifact("x", "agent skills collection", [], allow_skill=False),
                            "Agent Skill Pack")
        self.assertNotEqual(taxonomy.classify_artifact("x", "skill pack for Claude Code", ["agent-skills"]),
                            taxonomy.classify_artifact("x", "skill pack for Claude Code", ["agent-skills"],
                                                       allow_skill=False))


class ValidatorTests(unittest.TestCase):
    def _good(self, **overrides):
        rec = taxonomy.enrich_repository_record({
            "id": 11, "name": "solid", "owner": "org", "description": "LLM inference server",
            "stars": 2000, "forks": 10, "language": "Python", "license": "MIT", "topics": ["llm"],
            "pushed_at": "2026-01-01T00:00:00Z",
        })
        rec.update(overrides)
        return rec

    def test_clean_record_has_no_findings(self):
        self.assertEqual(validator.check_record(self._good(), set(taxonomy.TAXONOMY_RULES)), [])

    def test_below_star_floor_is_error(self):
        findings = validator.check_record(self._good(stars=120), set(taxonomy.TAXONOMY_RULES))
        self.assertIn("ERROR", [f[0] for f in findings])

    def test_github_clone_on_hub_url_is_error(self):
        rec = self._good(url="https://huggingface.co/org/solid",
                         quickstart_code="git clone https://github.com/org/solid.git")
        msgs = [m for _, _, m in validator.check_record(rec, set(taxonomy.TAXONOMY_RULES))]
        self.assertTrue(any("GitHub clone" in m for m in msgs))

    def test_duplicate_github_pair_is_error(self):
        a, b = self._good(id=1), self._good(id=2)
        findings = validator.check_corpus([a, b])
        self.assertTrue(any(f[0] == "ERROR" and "duplicate owner/name" in f[2] for f in findings))

    def test_placeholder_intel_is_warning(self):
        rec = self._good()
        rec["beginner_intel"] = dict(rec["beginner_intel"],
                                     why_it_matters=validator.PLACEHOLDER_WHY)
        findings = validator.check_record(rec, set(taxonomy.TAXONOMY_RULES))
        self.assertIn(("WARNING", validator.record_key(rec), "placeholder intel (shard_builder fallback, not a real summary)"),
                      findings)

    def test_generated_template_text_is_not_flagged(self):
        # Generated intel legitimately mentions "Managed cloud APIs" among alternatives.
        findings = validator.check_record(self._good(), set(taxonomy.TAXONOMY_RULES))
        self.assertFalse(any("placeholder" in m for _, _, m in findings))


if __name__ == "__main__":
    unittest.main()
