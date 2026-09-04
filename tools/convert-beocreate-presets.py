#!/usr/bin/env python3
"""
Convert Beocreate 2 speaker presets to the HiFiBerryOS schema-2 format.

The Beocreate 2 presets (hifiberry/create, Beocreate2/beo-speaker-presets,
MIT, (c) 2017 Bang & Olufsen) keep the equaliser and the channel settings in
two parallel maps keyed a-d, store 'level' tri-modally and leave a0 implicit.
Schema 2 merges the maps, makes level a plain linear gain and writes a0 out,
which is the shape sigmatcpserver's POST /filters/bank already accepts.

    ./convert-beocreate-presets.py \
        --source ~/localdev/beocreate/Beocreate2/beo-speaker-presets \
        --dest ../speaker-presets
"""

import argparse
import json
import os
import sys

CHANNELS = ("a", "b", "c", "d")
DEFAULT_SAMPLE_RATE = 48000
DEFAULT_MIN_PROFILE_VERSION = 11
SOURCE_CREDIT = "Bang & Olufsen, Beocreate 2 (MIT)"


def level_to_gain(level):
    """
    Convert a Beocreate 2 channel level to a linear gain.

    The old field meant three different things depending on its value
    (beo-extensions/channels/index.js, applyChannelLevelFromSettings):
    0 or 100 is unity, 1..99 is a percentage, negative is attenuation in dB.
    """
    if level is None:
        return 1.0
    if level == 0 or level == 100:
        return 1.0
    if level < 0:
        return 10 ** (level / 20.0)
    return level / 100.0


def convert_filter(old_filter):
    """
    Convert one biquad. a0 was implicit at 1; a1/a2 keep their signs -- both
    Beocreate 2 and Adau145x.write_biquad negate them when writing to the DSP,
    so negating here would apply it twice.
    """
    return {
        "a0": 1.0,
        "a1": float(old_filter["a1"]),
        "a2": float(old_filter["a2"]),
        "b0": float(old_filter["b0"]),
        "b1": float(old_filter["b1"]),
        "b2": float(old_filter["b2"]),
    }


def convert(old, preset_id):
    """Convert a whole Beocreate 2 preset document to schema 2."""
    meta = old["speaker-preset"]
    equaliser = old.get("equaliser", {})
    channels = old.get("channels", {})

    new = {
        "schemaVersion": 2,
        "id": preset_id,
        "name": meta["presetName"],
        "source": SOURCE_CREDIT,
        "requiredProfile": meta.get("fallbackDSP", "beocreate-universal"),
        "minProfileVersion": DEFAULT_MIN_PROFILE_VERSION,
        "sampleRate": int(meta.get("samplingRate") or DEFAULT_SAMPLE_RATE),
        "channels": {},
    }
    if meta.get("description"):
        new["description"] = meta["description"]

    for channel in CHANNELS:
        settings = channels.get(channel, {})
        new["channels"][channel] = {
            "role": settings.get("role", "mono"),
            "level": level_to_gain(settings.get("level")),
            "delayMs": float(settings.get("delay") or 0),
            "invert": bool(settings.get("invert", False)),
            "enabled": bool(settings.get("enabled", True)),
            "filters": [convert_filter(f) for f in equaliser.get(channel, [])],
        }

    return new


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True,
                        help="Beocreate2/beo-speaker-presets directory")
    parser.add_argument("--dest", required=True,
                        help="directory to write schema-2 presets into")
    args = parser.parse_args(argv)

    os.makedirs(args.dest, exist_ok=True)
    count = 0
    for name in sorted(os.listdir(args.source)):
        if not name.endswith(".json"):
            continue
        preset_id = name[:-len(".json")]
        with open(os.path.join(args.source, name)) as handle:
            old = json.load(handle)
        new = convert(old, preset_id)
        with open(os.path.join(args.dest, name), "w") as handle:
            json.dump(new, handle, indent=2)
            handle.write("\n")
        print("converted %s (%s)" % (preset_id, new["name"]))
        count += 1

    print("%d presets written to %s" % (count, args.dest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
