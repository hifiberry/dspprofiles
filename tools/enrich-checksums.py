#!/usr/bin/env python3
"""
enrich-checksums.py — annotate DSP profile XMLs with a length-based SHA-1.

Each bundled profile XML already carries a signature-based MD5 under
<metadata type="checksum">. This tool adds a complementary length-based
SHA-1 under <metadata type="checksum_sha1"> so sigmatcpserver (and
anything else identifying a running profile) can match against either
algorithm.

How it works for each profile:
  1. POST the XML to a live sigmatcpserver REST endpoint (default
     http://localhost:13141/dspprofile). sigmatcpserver flashes it
     via the standard kill_dsp -> writeXbytes -> start_dsp path.
  2. GET /checksum on the live DSP, which returns both
     signature.{md5,sha1} and length.{md5,sha1}.
  3. Verify the XML's stored <metadata type="checksum"> matches the
     live signature.md5. If it doesn't, the XML is inconsistent and
     this profile is skipped.
  4. Take the live length.sha1 and write it into the XML next to the
     existing checksum metadata.

The script is idempotent (existing checksum_sha1 entries are skipped
unless --force is given) and always re-flashes a recovery profile in a
try/finally so the device is left in a working state, even if a profile
fails or the script is interrupted.

Audio output during the run will be unpredictable — flashing the
DAC+DSP / DSP Addon profiles to a Beocreate routes I2S to outputs that
don't drive the speakers. That's fine for measurement; the DSP runs
the program and we read the checksums regardless.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import time
from pathlib import Path
from typing import Optional

import requests


# Match the existing checksum metadata line so we can splice the new one
# in immediately after it. Whitespace inside the tag is preserved by the
# replacement so manual diffs read cleanly.
#
# We operate on the file as bytes (the bundled XMLs are CRLF-terminated
# and we don't want write-back to convert them to LF), so the patterns
# are byte patterns too.
_CHECKSUM_LINE_RE = re.compile(
    rb'(?P<indent>[ \t]*)<metadata type="checksum"(?:\s+[^>]*)?>'
    rb'(?P<value>[0-9A-Fa-f]+)</metadata>'
)

_LINE_END_AFTER_CHECKSUM_RE = re.compile(rb'(\r\n|\n|\r)')

_CHECKSUM_SHA1_RE = re.compile(
    rb'<metadata\s+type="checksum_sha1"', re.IGNORECASE
)


class EnrichError(RuntimeError):
    """Anything that should abort processing of one profile but keep the run going."""


def post_profile(session: requests.Session, base_url: str, xml_path: Path, timeout: float) -> None:
    """Flash the XML at `xml_path` to the DSP. Raises on failure.

    The XML content is sent inline so the script can run from any host
    against a remote sigmatcpserver — the server doesn't need the file
    to exist on its own filesystem. Reading in binary mode preserves
    the original line endings (the bundled XMLs are CRLF) so any later
    write-back doesn't churn every line in git.
    """
    logging.info("Flashing %s ...", xml_path.name)
    xml_body = xml_path.read_bytes()
    r = session.post(
        f"{base_url.rstrip('/')}/dspprofile",
        data=xml_body,
        headers={"Content-Type": "application/xml"},
        timeout=timeout,
    )
    # The endpoint may return 200 with a JSON status, or it may return
    # an empty body if it took longer than its own response deadline.
    # As long as the HTTP layer succeeded, defer to the post-flash
    # checksum read for the actual verdict.
    if r.status_code >= 400:
        raise EnrichError(
            f"POST /dspprofile failed for {xml_path}: HTTP {r.status_code} {r.text[:200]}"
        )


def read_checksums(session: requests.Session, base_url: str, timeout: float) -> dict:
    """Return both signature and length checksums for the live DSP."""
    r = session.get(f"{base_url.rstrip('/')}/checksum", timeout=timeout)
    r.raise_for_status()
    data = r.json()
    if "signature" not in data or "length" not in data:
        raise EnrichError(f"/checksum response missing signature/length: {data}")
    return data


def stored_signature_md5(xml_bytes: bytes) -> Optional[str]:
    m = _CHECKSUM_LINE_RE.search(xml_bytes)
    return m.group("value").decode("ascii").upper() if m else None


def _detect_line_ending(xml_bytes: bytes, anchor: re.Match) -> bytes:
    """Pick the line terminator already used right after the checksum line."""
    tail = xml_bytes[anchor.end():anchor.end() + 2]
    m = _LINE_END_AFTER_CHECKSUM_RE.match(tail)
    return m.group(1) if m else b"\n"


def insert_length_sha1(xml_bytes: bytes, length_sha1: str) -> bytes:
    """Insert a checksum_sha1 metadata line directly after the checksum line.

    Preserves the file's existing line-ending convention by reusing
    whatever terminator follows the checksum line.
    """
    if _CHECKSUM_SHA1_RE.search(xml_bytes):
        raise EnrichError("XML already has checksum_sha1; refusing to duplicate")

    anchor = _CHECKSUM_LINE_RE.search(xml_bytes)
    if not anchor:
        raise EnrichError('Could not find a <metadata type="checksum"> line to anchor against')

    eol = _detect_line_ending(xml_bytes, anchor)
    indent = anchor.group("indent")
    new_line = (
        eol + indent + b'<metadata type="checksum_sha1">'
        + length_sha1.upper().encode("ascii") + b'</metadata>'
    )
    return xml_bytes[:anchor.end()] + new_line + xml_bytes[anchor.end():]


def process_profile(
    xml_path: Path,
    session: requests.Session,
    base_url: str,
    flash_timeout: float,
    force: bool,
    dry_run: bool,
) -> bool:
    """Returns True if the XML was modified (or would be in dry-run)."""
    xml_bytes = xml_path.read_bytes()

    if _CHECKSUM_SHA1_RE.search(xml_bytes) and not force:
        logging.info("%s: already has checksum_sha1, skipping (use --force to re-do)", xml_path.name)
        return False

    declared_md5 = stored_signature_md5(xml_bytes)
    if not declared_md5:
        raise EnrichError(f"{xml_path.name}: no <metadata type=\"checksum\"> found in XML")

    if dry_run:
        logging.info("%s: would flash + measure (declared signature MD5 = %s)", xml_path.name, declared_md5)
        return True

    post_profile(session, base_url, xml_path, timeout=flash_timeout)
    cs = read_checksums(session, base_url, timeout=10.0)

    live_sig_md5 = cs["signature"].get("md5", "").upper()
    live_len_sha1 = cs["length"].get("sha1", "").upper()

    if not live_sig_md5 or not live_len_sha1:
        raise EnrichError(f"{xml_path.name}: /checksum did not return both md5+sha1 (got {cs})")

    if live_sig_md5 != declared_md5:
        raise EnrichError(
            f"{xml_path.name}: declared signature MD5 ({declared_md5}) does not match "
            f"live DSP signature MD5 ({live_sig_md5}) after flash — refusing to bake in a checksum"
        )

    logging.info("%s: signature MD5 verified, length SHA-1 = %s", xml_path.name, live_len_sha1)
    new_bytes = insert_length_sha1(xml_bytes, live_len_sha1)
    xml_path.write_bytes(new_bytes)
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("profiles", nargs="+", type=Path, help="XML profile files to enrich")
    ap.add_argument(
        "--device", default="http://localhost:13141",
        help="Base URL of a sigmatcpserver REST endpoint (default: %(default)s).",
    )
    ap.add_argument(
        "--recovery-profile", type=Path, required=True,
        help="Path to a profile that should be re-flashed at the end of the run "
             "to leave the device in a working state. Typically the one matching "
             "the device's actual hardware (e.g. beocreate-universal-11.xml).",
    )
    ap.add_argument(
        "--flash-timeout", type=float, default=180.0,
        help="HTTP timeout for the flash POST in seconds (default: %(default)s). "
             "Flashes can run 60-120 s due to mandatory erase/write delays.",
    )
    ap.add_argument(
        "--force", action="store_true",
        help="Re-do XMLs that already have checksum_sha1.",
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="Show what would happen without flashing or modifying files.",
    )
    ap.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose logging.",
    )
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    for p in args.profiles + [args.recovery_profile]:
        if not p.is_file():
            logging.error("not a file: %s", p)
            return 2

    session = requests.Session()

    failures: list[str] = []
    modified: list[Path] = []

    try:
        for xml_path in args.profiles:
            try:
                if process_profile(
                    xml_path=xml_path,
                    session=session,
                    base_url=args.device,
                    flash_timeout=args.flash_timeout,
                    force=args.force,
                    dry_run=args.dry_run,
                ):
                    modified.append(xml_path)
            except EnrichError as e:
                logging.error("Skipping %s: %s", xml_path.name, e)
                failures.append(f"{xml_path}: {e}")
            except requests.RequestException as e:
                logging.error("HTTP error on %s: %s", xml_path.name, e)
                failures.append(f"{xml_path}: HTTP {e}")
                # If a transport failure happens we don't know whether the
                # device is in a good state — bail out so the recovery flash
                # runs before anything else hits the device.
                break
            # Small breather so sigmatcpserver finishes reloading state
            # before the next request.
            time.sleep(2.0)
    finally:
        if not args.dry_run:
            logging.info("Re-flashing recovery profile %s ...", args.recovery_profile.name)
            try:
                post_profile(session, args.device, args.recovery_profile, timeout=args.flash_timeout)
                logging.info("Recovery flash complete.")
            except Exception as e:
                logging.error(
                    "RECOVERY FLASH FAILED — device is left with whatever the last "
                    "successful flash put on the DSP. Manual recovery may be needed. "
                    "Error: %s", e,
                )
                failures.append(f"recovery flash: {e}")

    logging.info(
        "Done. %d profile(s) %s; %d failure(s).",
        len(modified),
        "would have been modified" if args.dry_run else "modified",
        len(failures),
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
