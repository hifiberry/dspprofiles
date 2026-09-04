#!/usr/bin/env python3
"""
Tests for tools/convert-beocreate-presets.py.

Run:  python3 -m unittest test_convert_beocreate_presets -v   (from tools/)
"""

import importlib.util
import os
import unittest

_SPEC = importlib.util.spec_from_file_location(
    "convert_beocreate_presets",
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "convert-beocreate-presets.py"))
convert_module = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(convert_module)


OLD_CX100 = {
    "speaker-preset": {
        "presetName": "Beovox CX 100",
        "presetVersion": 1,
        "readOnly": True,
        "productIdentity": "beovox-cx100",
        "fallbackDSP": "beocreate-universal",
        "samplingRate": 48000,
    },
    "equaliser": {
        "a": [{"b0": 0.88, "b1": -1.58, "b2": 0.79, "a1": -1.82, "a2": 0.92}],
        "b": [], "c": [], "d": [],
    },
    "channels": {
        "a": {"level": 100, "enabled": True, "delay": 0,
              "role": "mono", "invert": False},
        "b": {"level": 100, "enabled": True, "delay": 0,
              "role": "mono", "invert": False},
        "c": {"level": 100, "enabled": True, "delay": 0,
              "role": "mono", "invert": False},
        "d": {"level": 100, "enabled": True, "delay": 0,
              "role": "mono", "invert": False},
    },
}


class TestLevelConversion(unittest.TestCase):
    """Beocreate 2's 'level' was tri-modal; 0 and 100 both meant unity."""

    def test_100_is_unity(self):
        self.assertEqual(convert_module.level_to_gain(100), 1.0)

    def test_zero_is_unity_not_silence(self):
        self.assertEqual(convert_module.level_to_gain(0), 1.0)

    def test_missing_is_unity(self):
        self.assertEqual(convert_module.level_to_gain(None), 1.0)

    def test_percentage(self):
        self.assertAlmostEqual(convert_module.level_to_gain(50), 0.5)

    def test_negative_is_decibels(self):
        self.assertAlmostEqual(convert_module.level_to_gain(-6), 0.501187, places=5)


class TestFilterConversion(unittest.TestCase):

    def test_adds_explicit_a0_and_keeps_signs(self):
        """The old format left a0 implicit at 1 and used RBJ-cookbook signs.
        Both the DSP toolkit and Beocreate 2 negate a1/a2 on the wire, so the
        conversion must not do it a second time."""
        result = convert_module.convert_filter(
            {"b0": 0.88, "b1": -1.58, "b2": 0.79, "a1": -1.82, "a2": 0.92})
        self.assertEqual(result, {"a0": 1.0, "a1": -1.82, "a2": 0.92,
                                  "b0": 0.88, "b1": -1.58, "b2": 0.79})


class TestPresetConversion(unittest.TestCase):

    def setUp(self):
        self.new = convert_module.convert(OLD_CX100, "beovox-cx100")

    def test_header(self):
        self.assertEqual(self.new["schemaVersion"], 2)
        self.assertEqual(self.new["id"], "beovox-cx100")
        self.assertEqual(self.new["name"], "Beovox CX 100")
        self.assertEqual(self.new["requiredProfile"], "beocreate-universal")
        self.assertEqual(self.new["minProfileVersion"], 11)
        self.assertEqual(self.new["sampleRate"], 48000)

    def test_channels_merge_equaliser_and_settings(self):
        channel_a = self.new["channels"]["a"]
        self.assertEqual(channel_a["role"], "mono")
        self.assertEqual(channel_a["level"], 1.0)
        self.assertEqual(channel_a["delayMs"], 0.0)
        self.assertFalse(channel_a["invert"])
        self.assertTrue(channel_a["enabled"])
        self.assertEqual(len(channel_a["filters"]), 1)

    def test_all_four_channels_present_even_when_empty(self):
        for channel in ("a", "b", "c", "d"):
            self.assertIn(channel, self.new["channels"])
        self.assertEqual(self.new["channels"]["b"]["filters"], [])

    def test_defaults_for_a_sparse_preset(self):
        """other-speaker.json omits samplingRate, delay and invert."""
        sparse = {
            "speaker-preset": {"presetName": "Other Speaker",
                               "fallbackDSP": "beocreate-universal",
                               "description": "Four full-range channels."},
            "equaliser": {"a": [], "b": [], "c": [], "d": []},
            "channels": {"a": {"level": 100, "enabled": True, "role": "left"},
                         "b": {"level": 100, "enabled": True, "role": "right"},
                         "c": {"level": 100, "enabled": True, "role": "left"},
                         "d": {"level": 100, "enabled": True, "role": "right"}},
        }
        new = convert_module.convert(sparse, "other-speaker")
        self.assertEqual(new["sampleRate"], 48000)
        self.assertEqual(new["description"], "Four full-range channels.")
        self.assertEqual(new["channels"]["a"]["delayMs"], 0.0)
        self.assertFalse(new["channels"]["a"]["invert"])


if __name__ == "__main__":
    unittest.main()
