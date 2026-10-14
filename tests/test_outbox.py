"""Offline tests for the outbox CLI: no key, no network."""
import io
import importlib.machinery
import importlib.util
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "outbox")


def load():
    loader = importlib.machinery.SourceFileLoader("outbox_cli", SCRIPT)
    spec = importlib.util.spec_from_loader("outbox_cli", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


outbox = load()


def gemini_response(text, finish="STOP", usage=None, version=None):
    r = {
        "candidates": [{"content": {"parts": [{"text": text}]}, "finishReason": finish}],
        "usageMetadata": usage or {"promptTokenCount": 10, "candidatesTokenCount": 5},
    }
    if version:
        r["modelVersion"] = version
    return r


class FakeHTTP:
    """Stands in for urllib.request.urlopen: replays a scripted list of outcomes."""

    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.requests = []
        self.timeouts = []

    def __call__(self, req, timeout=None):
        self.requests.append(req)
        self.timeouts.append(timeout)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        body = json.dumps(outcome).encode()
        resp = io.BytesIO(body)
        resp.__enter__ = lambda s=resp: s
        resp.__exit__ = lambda s, *a: None
        return resp


def http_error(code, body=b"", retry_after=None):
    headers = {"Retry-After": retry_after} if retry_after else {}
    return urllib.error.HTTPError("u", code, "err", headers, io.BytesIO(body))


class PromptObeysItsOwnRules(unittest.TestCase):
    """`rules.md` is edited, not shipped verbatim, so it is ours to lint along with the
    text written here (the additions and the audience notes): all of it has to pass the
    rules it carries."""

    def test_no_em_dashes_anywhere(self):
        self.assertNotIn("\u2014", outbox.RULES + "".join(outbox.AUDIENCES.values())
                         + outbox.DESCRIBED_READER)

    def test_rules_file_ends_with_the_change_list_format(self):
        self.assertTrue(outbox.RULES.startswith("Translate the input from"))
        self.assertNotIn("Output only the rewritten text.", outbox.RULES)
        self.assertIn(outbox.SEPARATOR, outbox.RULES.split("\n\n")[-1])

    def test_no_contrast_framing_in_the_audience_notes(self):
        import re
        text = re.sub(r"""["'][^"']*["']""", "",
                      "\n\n".join([*outbox.AUDIENCES.values(), outbox.DESCRIBED_READER])).lower()
        for pattern in ("not just", "isn't about", "rather than", "is not x"):
            self.assertNotIn(pattern, text, pattern)


class SplitChanges(unittest.TestCase):
    def test_splits_on_separator_line(self):
        out, changes = outbox.split_changes("Hello.\n\n--- changes ---\n- cut a hedge\n")
        self.assertEqual(out, "Hello.")
        self.assertEqual(changes, "- cut a hedge")

    def test_separator_with_surrounding_spaces(self):
        out, changes = outbox.split_changes("A.\n  --- changes ---  \nB")
        self.assertEqual((out, changes), ("A.", "B"))

    def test_no_separator_means_no_changes(self):
        out, changes = outbox.split_changes("Just text")
        self.assertEqual(out, "Just text")
        self.assertIsNone(changes)

    def test_separator_inside_a_sentence_does_not_split(self):
        text = "The line --- changes --- is not alone here."
        out, changes = outbox.split_changes(text)
        self.assertEqual(out, text)
        self.assertIsNone(changes)


class PostCheck(unittest.TestCase):
    def test_clean_text_has_no_warnings(self):
        self.assertEqual(outbox.post_check("We shipped it on Monday."), [])

    def test_em_dash_is_reported(self):
        w = outbox.post_check("Genuinely — it works.")
        self.assertEqual(len(w), 1)
        self.assertIn("1 em dash", w[0])


class BuildSystem(unittest.TestCase):
    def test_audience_leads_and_the_rules_close(self):
        s = outbox.build_system("funder", None)
        self.assertTrue(s.startswith("Audience for the text below"))
        self.assertNotIn("\n\n\n", s)
        self.assertIn("program officer", s)
        self.assertNotIn("Samples of how the sender", s)
        self.assertTrue(s.endswith(outbox.RULES))

    def test_voice_sits_between_audience_and_rules(self):
        s = outbox.build_system("engineer", "Hi all, quick one.\n")
        self.assertLess(s.index("Audience"), s.index("Samples of how the sender"))
        self.assertLess(s.index("Hi all, quick one."), s.index(outbox.RULES))
        self.assertTrue(s.endswith(outbox.RULES))


class DescribedReader(unittest.TestCase):
    """--for takes a name or a description of the reader. A description replaces the
    named note: it opens the audience block verbatim, so whatever the caller said
    about the reader, the register or the length sits under the precedence line,
    and a fixed tail supplies what the caller did not say (keep the content and the
    structure, change the register and the wording)."""

    def test_a_description_opens_the_audience_block_and_the_tail_follows(self):
        s = outbox.build_system("Sam and the operations team", None)
        self.assertTrue(s.startswith(
            "Audience for the text below (where this conflicts with a rule that follows, "
            "this takes precedence): Sam and the operations team. " + outbox.DESCRIBED_READER))
        self.assertTrue(s.endswith(outbox.RULES))
        for note in outbox.AUDIENCES.values():
            self.assertNotIn(note, s)

    def test_a_description_ending_in_punctuation_is_not_doubled(self):
        s = outbox.build_system("The reader is Sam. She has read the previous report.", None)
        self.assertIn("previous report. " + outbox.DESCRIBED_READER, s)
        self.assertNotIn("report.. ", s)

    def test_a_name_still_gets_its_note_and_no_tail(self):
        for name, note in outbox.AUDIENCES.items():
            s = outbox.build_system(name, None)
            self.assertIn(note, s, name)
            self.assertNotIn(outbox.DESCRIBED_READER, s, name)

    def test_the_tail_sits_between_the_description_and_any_voice(self):
        s = outbox.build_system("a partner org's ops lead", "Hi all, quick one.\n")
        self.assertLess(s.index(outbox.DESCRIBED_READER), s.index("Samples of how the sender"))

    def test_one_unknown_word_is_refused_with_the_names(self):
        with self.assertRaises(outbox.argparse.ArgumentTypeError) as cm:
            outbox.audience_arg("enginer")
        for name in outbox.AUDIENCES:
            self.assertIn(name, str(cm.exception))
        self.assertIn("enginer", str(cm.exception))

    def test_a_name_and_a_phrase_pass_through(self):
        self.assertEqual(outbox.audience_arg("funder"), "funder")
        self.assertEqual(outbox.audience_arg("  a partner org's ops lead "), "a partner org's ops lead")

    def test_blank_is_refused(self):
        with self.assertRaises(outbox.argparse.ArgumentTypeError):
            outbox.audience_arg("   ")


class PerCallInstructions(unittest.TestCase):
    """outbox is shared: the skill's outward-draft use must not shift because one
    caller needed a rule. So the flag is additive and off by default, and these
    pin both halves of that."""

    def test_no_instruction_leaves_the_prompt_byte_identical(self):
        for audience in outbox.AUDIENCES:
            for voice in (None, "Hi all, quick one.\n"):
                self.assertEqual(outbox.build_system(audience, voice, None),
                                 outbox.build_system(audience, voice),
                                 f"{audience}/{'voice' if voice else 'no voice'}")

    def test_an_empty_or_blank_list_is_the_same_as_none(self):
        base = outbox.build_system("manager", None)
        for empty in ([], [""], ["   \n"], [None]):
            self.assertEqual(outbox.build_system("manager", None, empty), base, empty)

    def test_an_instruction_lands_after_the_rules_as_a_rule(self):
        s = outbox.build_system("manager", None, ["Do not state the due date."])
        self.assertGreater(s.index("Do not state the due date."), s.index(outbox.RULES))
        self.assertIn(outbox.INSTRUCTION_PREFACE, s)
        self.assertIn("- Do not state the due date.", s)

    def test_it_is_not_framed_as_prose_to_imitate(self):
        """The whole reason for the flag: --voice would make a directive a sample."""
        s = outbox.build_system("manager", None, ["Do not state the due date."])
        preface = s[s.index(outbox.INSTRUCTION_PREFACE):]
        self.assertNotIn("Samples of how the sender", preface)
        self.assertIn("not text to rewrite", preface)

    def test_several_instructions_each_get_a_line(self):
        s = outbox.build_system("team", None, ["First rule.", "Second rule."])
        self.assertIn("- First rule.\n- Second rule.", s)

    def test_the_preface_obeys_the_rules_it_carries(self):
        """It joins the system prompt, so it is held to the no-em-dash rule the
        audience notes and rules.md are held to."""
        self.assertNotIn("—", outbox.INSTRUCTION_PREFACE)


class RequestBody(unittest.TestCase):
    def test_shape(self):
        b = outbox.request_body("SYS", "DRAFT", 0.2, "high")
        self.assertEqual(b["systemInstruction"]["parts"][0]["text"], "SYS")
        self.assertEqual(b["contents"][0]["parts"][0]["text"], "Input:\n\nDRAFT")
        self.assertEqual(b["generationConfig"]["thinkingConfig"]["thinkingLevel"], "high")
        self.assertEqual(b["generationConfig"]["temperature"], 0.2)


class Call(unittest.TestCase):
    def test_sends_key_header_and_model_path(self):
        http = FakeHTTP([gemini_response("ok")])
        out = outbox.call("gemini-x", {"a": 1}, "KEY", 5, urlopen=http)
        self.assertEqual(out["candidates"][0]["content"]["parts"][0]["text"], "ok")
        req = http.requests[0]
        self.assertTrue(req.full_url.endswith("/models/gemini-x:generateContent"))
        self.assertEqual(req.get_header("X-goog-api-key"), "KEY")
        self.assertNotIn("KEY", req.full_url)

    def test_retries_on_429_then_succeeds(self):
        http = FakeHTTP([http_error(429, retry_after="0"), gemini_response("ok")])
        with mock.patch.object(outbox.time, "sleep"):
            out = outbox.call("m", {}, "K", 5, urlopen=http)
        self.assertEqual(len(http.requests), 2)
        self.assertEqual(out["candidates"][0]["content"]["parts"][0]["text"], "ok")

    def test_400_exits_with_the_body(self):
        http = FakeHTTP([http_error(400, b'{"error": "bad model"}')])
        with self.assertRaises(SystemExit) as cm:
            outbox.call("m", {}, "K", 5, urlopen=http)
        self.assertIn("HTTP 400", str(cm.exception))
        self.assertIn("bad model", str(cm.exception))

    def test_read_timeout_exits_with_a_message_without_retrying(self):
        # urllib wraps only send errors in URLError; a slow response raises TimeoutError.
        http = FakeHTTP([TimeoutError("The read operation timed out"), gemini_response("ok")])
        with self.assertRaises(SystemExit) as cm:
            outbox.call("m", {}, "K", 5, urlopen=http)
        self.assertIn("5 s", str(cm.exception))
        self.assertIn("--timeout", str(cm.exception))
        self.assertEqual(len(http.requests), 1)

    def test_gives_up_after_four_5xx(self):
        http = FakeHTTP([http_error(503)] * 4)
        with mock.patch.object(outbox.time, "sleep"), self.assertRaises(SystemExit):
            outbox.call("m", {}, "K", 5, urlopen=http)
        self.assertEqual(len(http.requests), 4)


class ExtractText(unittest.TestCase):
    def test_joins_parts_and_skips_thoughts(self):
        r = {"candidates": [{"content": {"parts": [
            {"text": "secret", "thought": True}, {"text": "a"}, {"text": "b"}]}, "finishReason": "STOP"}]}
        self.assertEqual(outbox.extract_text(r), "ab")

    def test_no_candidate_names_the_block_reason(self):
        with self.assertRaises(SystemExit) as cm:
            outbox.extract_text({"promptFeedback": {"blockReason": "SAFETY"}})
        self.assertIn("SAFETY", str(cm.exception))

    def test_empty_text_exits(self):
        with self.assertRaises(SystemExit):
            outbox.extract_text(gemini_response("   ", finish="MAX_TOKENS"))

    def test_truncation_is_reported_on_stderr(self):
        err = io.StringIO()
        with mock.patch.object(sys, "stderr", err):
            self.assertEqual(outbox.extract_text(gemini_response("cut", finish="MAX_TOKENS")), "cut")
        self.assertIn("MAX_TOKENS", err.getvalue())


class ReadKey(unittest.TestCase):
    def test_env_wins(self):
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": " k1 "}):
            self.assertEqual(outbox.read_key(), "k1")

    def test_missing_file_names_the_path(self):
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": ""}), \
                mock.patch.object(outbox, "KEYFILE", "/nonexistent/key"):
            with self.assertRaises(SystemExit) as cm:
                outbox.read_key()
        self.assertIn("/nonexistent/key", str(cm.exception))


class Main(unittest.TestCase):
    def run_main(self, argv, stdin="", response=None):
        http = FakeHTTP([response or gemini_response("Plain text.\n--- changes ---\n- one")])
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "K", "OUTBOX_MODEL": "gemini-flash-latest"}), \
                mock.patch.object(outbox, "VOICEFILE", "/nonexistent/voice.md"), \
                mock.patch.object(outbox.urllib.request, "urlopen", http), \
                mock.patch.object(sys, "stdin", io.StringIO(stdin)), \
                mock.patch.object(sys, "stdout", out), \
                mock.patch.object(sys, "stderr", err):
            rc = outbox.main(argv)
        return rc, out.getvalue(), err.getvalue(), http

    def test_stdout_is_the_rewrite_only_and_stderr_has_the_changes(self):
        rc, out, err, http = self.run_main([], stdin="Here's the thing — done.")
        self.assertEqual(rc, 0)
        self.assertEqual(out, "Plain text.\n")
        self.assertIn("changes:\n- one", err)
        self.assertIn("gemini-flash-latest", err)
        body = json.loads(http.requests[0].data)
        self.assertIn("Here's the thing", body["contents"][0]["parts"][0]["text"])
        self.assertIn("competent engineer explaining it to another engineer", body["systemInstruction"]["parts"][0]["text"])

    def test_gemini_defaults_have_no_clock(self):
        response = io.BytesIO(json.dumps(gemini_response("Plain.")).encode())
        with mock.patch.object(outbox.urllib.request, "urlopen", return_value=response) as request:
            outbox.call("gemini-x", {}, "K", None)
        self.assertIsNone(request.call_args.kwargs["timeout"])
        _, _, _, http = self.run_main([], stdin="A draft.")
        self.assertEqual(http.timeouts, [None])
        config = json.loads(http.requests[0].data)["generationConfig"]
        self.assertEqual(config, {"temperature": 1.0, "thinkingConfig": {"thinkingLevel": "high"}})

    def test_audience_and_model_flags_reach_the_request(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("draft body")
        try:
            rc, out, err, http = self.run_main(["--for", "participant", "--model", "gemini-z", f.name])
        finally:
            os.unlink(f.name)
        self.assertEqual(rc, 0)
        self.assertTrue(http.requests[0].full_url.endswith("gemini-z:generateContent"))
        self.assertIn("hackathon participant", json.loads(http.requests[0].data)["systemInstruction"]["parts"][0]["text"])

    def test_empty_draft_refuses_before_any_request(self):
        with self.assertRaises(SystemExit) as cm:
            self.run_main([], stdin="  \n")
        self.assertIn("empty", str(cm.exception))

    def test_show_prompt_makes_no_request(self):
        rc, out, err, http = self.run_main(["--show-prompt", "--for", "team"])
        self.assertEqual(rc, 0)
        self.assertEqual(http.requests, [])
        self.assertIn("runs programs and operations", out)

    def test_a_described_reader_reaches_the_request(self):
        rc, out, err, http = self.run_main(
            ["--for", "the post's author and the other programme leads"], stdin="a draft")
        self.assertEqual(rc, 0)
        sent = json.loads(http.requests[0].data)["systemInstruction"]["parts"][0]["text"]
        self.assertIn("this takes precedence): the post's author and the other programme leads. ", sent)
        self.assertIn(outbox.DESCRIBED_READER, sent)

    def test_show_prompt_prints_a_described_reader(self):
        rc, out, err, http = self.run_main(["--show-prompt", "--for", "Sam, who runs operations"])
        self.assertEqual(rc, 0)
        self.assertEqual(http.requests, [])
        self.assertIn("Sam, who runs operations. " + outbox.DESCRIBED_READER, out)

    def test_an_unknown_single_word_exits_before_any_request(self):
        http = FakeHTTP([])  # any request would raise IndexError, not SystemExit
        err = io.StringIO()
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "K", "OUTBOX_MODEL": "gemini-flash-latest"}), \
                mock.patch.object(outbox.urllib.request, "urlopen", http), \
                mock.patch.object(sys, "stdin", io.StringIO("a draft")), \
                mock.patch.object(sys, "stderr", err):
            with self.assertRaises(SystemExit) as cm:
                outbox.main(["--for", "enginer"])
        self.assertEqual(cm.exception.code, 2)
        self.assertEqual(http.requests, [])
        self.assertIn("engineer", err.getvalue())
        self.assertIn("enginer", err.getvalue())

    def test_instruction_flags_reach_the_system_prompt(self):
        rc, out, err, http = self.run_main(
            ["--instruction", "Rule one.", "--instruction", "Rule two."],
            stdin="a draft")
        self.assertEqual(rc, 0)
        sent = json.loads(http.requests[0].data)["systemInstruction"]["parts"][0]["text"]
        self.assertIn("- Rule one.\n- Rule two.", sent)

    def test_without_the_flag_the_prompt_carries_no_instruction_block(self):
        rc, out, err, http = self.run_main([], stdin="a draft")
        sent = json.loads(http.requests[0].data)["systemInstruction"]["parts"][0]["text"]
        self.assertNotIn(outbox.INSTRUCTION_PREFACE, sent)
        self.assertTrue(sent.endswith(outbox.RULES))


class ServedModel(Main):
    """The default model is an alias Google hot-swaps to each new Flash release,
    including previews. The usage line names what actually served the call, so a
    swap is visible on the run it first happens, not discovered from a drift."""

    def test_an_alias_resolving_elsewhere_is_named_on_the_usage_line(self):
        rc, out, err, http = self.run_main(
            [], stdin="a draft",
            response=gemini_response("Plain.\n--- changes ---\n- one", version="gemini-served"))
        self.assertIn("outbox: gemini-flash-latest served by gemini-served,", err)

    def test_a_model_serving_itself_is_named_once(self):
        rc, out, err, http = self.run_main(
            ["--model", "gemini-z"], stdin="a draft",
            response=gemini_response("Plain.\n--- changes ---\n- one", version="gemini-z"))
        self.assertIn("outbox: gemini-z,", err)
        self.assertNotIn("served by", err)

    def test_a_response_without_a_version_still_prints_the_usage_line(self):
        rc, out, err, http = self.run_main(["--model", "gemini-z"], stdin="a draft")
        self.assertIn("outbox: gemini-z,", err)
        self.assertNotIn("served by", err)
        self.assertNotIn("None", err)


class ClaudeMain(unittest.TestCase):
    def run_main(self, argv=(), envelope=None, returncode=0, stderr="", model="sonnet"):
        with open(os.path.join(HERE, "fixtures", "claude-success.json")) as f:
            captured = json.load(f)
        stdout = json.dumps(captured if envelope is None else envelope)
        result = mock.Mock(stdout=stdout, stderr=stderr, returncode=returncode)
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch.object(outbox, "VOICEFILE", "/nonexistent/voice.md"), \
                mock.patch.object(outbox.urllib.request, "urlopen", side_effect=AssertionError("unexpected HTTP call")), \
                mock.patch("subprocess.run", return_value=result) as run, \
                mock.patch.object(sys, "stdin", io.StringIO("A draft.")), \
                mock.patch.object(sys, "stdout", out), \
                mock.patch.object(sys, "stderr", err):
            if model is not None:
                os.environ["OUTBOX_MODEL"] = model
            rc = outbox.main(list(argv))
        return rc, out.getvalue(), err.getvalue(), run.call_args

    def test_capture_rewrites_in_an_isolated_context_without_a_timeout(self):
        rc, out, err, call = self.run_main()
        self.assertEqual(rc, 0)
        self.assertEqual(out, "We used the new dashboard to get the team on the same page. The team saved two hours each week.\n")
        self.assertIn("no claims changed", err)
        self.assertIn("claude-sonnet-5-5, 2 in / 75 out / 0 thinking tokens", err)
        self.assertEqual(call.args[0], ["claude", "-p", "--safe-mode", "--system-prompt",
                         outbox.build_system("engineer", None), "--model", "sonnet",
                         "--effort", "xhigh", "--output-format", "json", "--max-turns", "1",
                         "--disallowed-tools", "*", "--strict-mcp-config", "--no-session-persistence"])
        self.assertEqual(call.kwargs["input"], "Input:\n\nA draft.")
        self.assertEqual(call.kwargs["cwd"], tempfile.gettempdir())
        self.assertNotIn("timeout", call.kwargs)

    def test_unset_model_uses_sonnet(self):
        _, _, _, call = self.run_main(model=None)
        argv = call.args[0]
        self.assertEqual(argv[argv.index("--model") + 1], "sonnet")

    def test_explicit_model_effort_and_instruction(self):
        _, _, _, call = self.run_main(["--model", "opus", "--effort", "low", "--instruction", "Keep the date."])
        argv = call.args[0]
        self.assertEqual(argv[argv.index("--model") + 1], "opus")
        self.assertEqual(argv[argv.index("--effort") + 1], "low")
        self.assertEqual(argv[argv.index("--system-prompt") + 1],
                         outbox.build_system("engineer", None, ["Keep the date."]))

    def test_error_envelope_exits_with_its_message(self):
        with self.assertRaisesRegex(SystemExit, "request failed"):
            self.run_main(envelope={"is_error": True, "subtype": "test_error", "result": "request failed"})

    def test_nonzero_exit_preserves_cli_error(self):
        with self.assertRaisesRegex(SystemExit, "login required"):
            self.run_main(returncode=1, stderr="login required")

    def test_empty_result_exits(self):
        with self.assertRaisesRegex(SystemExit, "empty.*success"):
            self.run_main(envelope={"is_error": False, "subtype": "success", "result": " "})

    def test_malformed_stdout_exits_with_raw_message(self):
        with mock.patch("json.dumps", return_value="broken output"):
            with self.assertRaisesRegex(SystemExit, "broken output"):
                self.run_main()

    def test_post_check_runs_on_claude_rewrites(self):
        _, out, err, _ = self.run_main(envelope={"result": "Done — today.\n--- changes ---\nno claims changed"})
        self.assertEqual(out, "Done — today.\n")
        self.assertIn("1 em dash left in", err)

    def test_missing_cli_exits_with_a_message(self):
        with mock.patch("subprocess.run", side_effect=FileNotFoundError("claude missing")):
            with self.assertRaisesRegex(SystemExit, "could not run claude"):
                outbox.call_claude("sonnet", "rules", "draft", "xhigh")

    def test_backend_specific_flags_are_refused(self):
        for argv in (["--thinking", "high"], ["--temperature", "1"],
                     ["--model", "gemini-x", "--effort", "xhigh"]):
            with self.subTest(argv=argv), self.assertRaises(SystemExit):
                self.run_main(argv)


if __name__ == "__main__":
    unittest.main()
