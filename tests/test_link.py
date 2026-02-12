from agentskills.link import parse_harness_list


class TestParseHarnessList:
    def test_empty(self):
        assert parse_harness_list([]) == []

    def test_single(self):
        assert parse_harness_list(["anthropic"]) == ["anthropic"]

    def test_comma_separated(self):
        assert parse_harness_list(["anthropic,amp"]) == ["anthropic", "amp"]

    def test_deduplicates(self):
        assert parse_harness_list(["amp,amp", "amp"]) == ["amp"]

    def test_strips_whitespace(self):
        assert parse_harness_list([" anthropic , amp "]) == ["anthropic", "amp"]
