#!/usr/bin/env python3
"""
TTS synthesis script for 6pack.care
Usage: python3 scripts/tts_synth.py manifesto.md audio/manifesto.mp3

Reads a Markdown file, transforms it to clean spoken English,
then synthesises via ElevenLabs and writes an MP3.

Requires:
  ELEVENLABS_API_KEY   – API key
  ELEVENLABS_VOICE_ID  – voice ID (default: Audrey Tang 0YIItGwEClgeMtCdHyV1)
"""

import io, json, os, re, subprocess, sys, tempfile, time, requests

# ── Config ────────────────────────────────────────────────────────────────────

API_KEY  = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "0YIItGwEClgeMtCdHyV1")
MODEL    = "eleven_turbo_v2"
FORMAT   = "mp3_44100_128"

VOICE_SETTINGS = {
    "stability": 0.99,
    "similarity_boost": 0.99,
    "style": 0.0,
    "use_speaker_boost": True,
}

CHUNK_LIMIT = 20000  # stay under ElevenLabs 10k per-request limit

# ── Text transformation ───────────────────────────────────────────────────────

# Abbreviations: ordered longest-match first to avoid partial replacements.
ABBREVS = [
    # Latin phrases
    (r"\be\.g\.",          "for example"),
    (r"\bi\.e\.",          "that is"),
    (r"\betc\.",           "et cetera"),
    (r"\bviz\.",           "namely"),
    (r"\bcf\.",            "compare"),
    (r"\bvs?\.",           "versus"),
    (r"\bca\.",            "approximately"),
    # Titles
    (r"\bDr\.",            "Doctor"),
    (r"\bProf\.",          "Professor"),
    (r"\bkami\b",          "kaami"),
    (r"\bMr\.",            "Mister"),
    (r"\bMrs\.",           "Misses"),
    (r"\bMs\.",            "Ms"),
    (r"\bSt\.",            "Saint"),
    # Common spoken acronyms (keep as letters with hyphens so TTS spells them)
    (r"\bCSAM\b",          "C-S-A-M"),
    (r"\bPCA\b",           "P-C-A"),
    (r"\bCDN\b",           "C-D-N"),
    (r"\bSMS\b",           "S-M-S"),
    (r"\bKYC\b",           "K-Y-C"),
    (r"\bASI\b",           "A-S-I"),
    (r"\bRLCF\b",          "R-L-C-F"),
    (r"\bSSE\b",           "S-S-E"),
    (r"\bVBR\b",           "V-B-R"),
    (r"\bCBR\b",           "C-B-R"),
    # Slang / shorthand
    (r"\bd/acc\b",         "d slash a-c-c"),
    # Web
    (r"ROOST\.tools\b",    "ROOST tools"),
]

# Words for integers 0–19
_ONES = [
    "zero","one","two","three","four","five","six","seven","eight","nine",
    "ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen",
    "seventeen","eighteen","nineteen",
]
_TENS = ["","","twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"]

def _int_to_words(n: int) -> str:
    if n < 0:
        return "minus " + _int_to_words(-n)
    if n < 20:
        return _ONES[n]
    if n < 100:
        tens, ones = divmod(n, 10)
        return _TENS[tens] + ("-" + _ONES[ones] if ones else "")
    if n < 1000:
        hundreds, rest = divmod(n, 100)
        tail = (" and " + _int_to_words(rest)) if rest else ""
        return _ONES[hundreds] + " hundred" + tail
    if n < 1_000_000:
        thousands, rest = divmod(n, 1000)
        tail = (", " + _int_to_words(rest)) if rest else ""
        return _int_to_words(thousands) + " thousand" + tail
    if n < 1_000_000_000:
        millions, rest = divmod(n, 1_000_000)
        tail = (", " + _int_to_words(rest)) if rest else ""
        return _int_to_words(millions) + " million" + tail
    return str(n)  # fallback

def _year_to_words(n: int) -> str:
    """Convert a 4-digit year to spoken form: 2014 → 'twenty fourteen'."""
    if 1000 <= n <= 1999:
        hi, lo = divmod(n, 100)
        return _int_to_words(hi) + " " + (_int_to_words(lo) if lo else "hundred")
    if 2000 <= n <= 2099:
        if n == 2000:
            return "two thousand"
        lo = n - 2000
        return "twenty " + _int_to_words(lo) if lo < 100 else _int_to_words(n)
    return _int_to_words(n)

def _number_to_words(s: str) -> str:
    """Convert a numeric string (possibly with commas) to words."""
    s_clean = s.replace(",", "")
    if "." in s_clean:
        int_part, dec_part = s_clean.split(".", 1)
        left  = _int_to_words(int(int_part)) if int_part else "zero"
        right = " ".join(_ONES[int(d)] for d in dec_part if d.isdigit())
        return left + " point " + right
    return _int_to_words(int(s_clean))

def _expand_number(m: re.Match) -> str:
    raw = m.group(0).replace(",", "")
    n   = int(raw) if raw.isdigit() else None
    return _int_to_words(int(raw.replace(",", "")))

# Regex for a bare number (with optional thousands commas)
_NUM_RE = r"\d{1,3}(?:,\d{3})*|\d+"


def transform(text: str) -> str:
    """Convert Markdown + prose to clean spoken text suitable for TTS."""

    # 1. Strip YAML front matter
    text = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)

    # 2. Strip HTML block elements (including their text content)
    text = re.sub(r"<div[^>]*>.*?</div>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", "", text)

    # 3. Markdown links → label only
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # 4. Markdown headings → pause markers before and after for TTS prosody
    text = re.sub(r"^#{1,6}\s+(.+)$", r"\n...... \1 ...\n", text, flags=re.MULTILINE)

    # 5. Bold / italic → double-quoted for TTS emphasis (preserves stress cues)
    text = re.sub(r"\*{1,3}([^*\n]+)\*{1,3}", r'"\1"', text)
    text = re.sub(r"_{1,2}([^_\n]+)_{1,2}",   r'"\1"', text)
    # Collapse double-quotes from bold wrapping already-quoted text: ""word"" → "word"
    text = text.replace('""', '"')

    # 6. List markers
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*]\s+",  "", text, flags=re.MULTILINE)

    # 7. ⿻ and Unicode symbols
    # Consume ⿻ together with any immediately following whitespace so "⿻ Plurality" → "Plurality"
    text = re.sub(r"⿻\s*", "", text)
    text = text.replace("…", "...")
    text = text.replace("·", ", ")
    # Drop parenthetical CJK content entirely (e.g. (數位), (神))
    text = re.sub(r"\s*\([^)]*[\u3400-\u9fff][^)]*\)", "", text)

    # 8. Smart quotes → straight
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")

    # 9. Dashes
    #    Em dash used as parenthetical  → commas
    text = re.sub(r"\s*—\s*", ", ", text)
    #    En dash in ranges (e.g. 8–9)   → " to "
    text = re.sub(r"(\w)\u2013(\w)", r"\1 to \2", text)
    text = re.sub(r"\s*\u2013\s*", " to ", text)

    # 10. Slash in non-URL, non-path contexts → " or "
    #     (d/acc handled already in ABBREVS above before this runs — guard it here too)
    text = re.sub(r"(?<!\w)([A-Za-z]{2,})/([A-Za-z]{2,})(?!\w)", r"\1 or \2", text)

    # 11. Abbreviations (before number expansion so "vs." is caught first)
    for pattern, replacement in ABBREVS:
        text = re.sub(pattern, replacement, text)

    # 12. Percentages  →  "N percent"
    def pct_repl(m):
        num_str = m.group(1).replace(",", "")
        if "." in num_str:
            val = float(num_str)
            # e.g. 2.5 → "two point five"
            words = _number_to_words(num_str)
        else:
            words = _int_to_words(int(num_str))
        return words + " percent"
    text = re.sub(r"([\d,]+(?:\.\d+)?)\s*%", pct_repl, text)

    # 13. Currency
    def currency_repl(sym, singular, plural):
        def repl(m):
            num_str = m.group(1).replace(",", "")
            n = float(num_str)
            words = _number_to_words(num_str)
            unit = singular if n == 1 else plural
            return words + " " + unit
        return repl
    text = re.sub(r"\$([\d,]+(?:\.\d+)?)", currency_repl("$", "dollar",  "dollars"),  text)
    text = re.sub(r"£([\d,]+(?:\.\d+)?)", currency_repl("£", "pound",   "pounds"),   text)
    text = re.sub(r"€([\d,]+(?:\.\d+)?)", currency_repl("€", "euro",    "euros"),    text)

    # 14. Explicit +N time-zone or score notation
    text = re.sub(r"\+(\d+)\b", lambda m: "plus " + _int_to_words(int(m.group(1))), text)

    # 15. Ordinals  →  spoken form  (1st → first, 2nd → second …)
    _ORDINALS = {1:"first",2:"second",3:"third",4:"fourth",5:"fifth",
                 6:"sixth",7:"seventh",8:"eighth",9:"ninth",10:"tenth",
                 11:"eleventh",12:"twelfth"}
    def ord_repl(m):
        n = int(m.group(1))
        if n in _ORDINALS:
            return _ORDINALS[n]
        # fallback: "23rd" → "twenty-third"
        suffix_map = {1:"first",2:"second",3:"third"}
        base = _int_to_words(n)
        last = n % 10
        if last in suffix_map and n not in (11,12,13):
            # strip trailing "one"/"two"/"three" and add ordinal suffix
            if last == 1: base = base[:-3] + "first"  if base.endswith("one")   else base + "st"
            if last == 2: base = base[:-3] + "second" if base.endswith("two")   else base + "nd"
            if last == 3: base = base[:-5] + "third"  if base.endswith("three") else base + "rd"
        else:
            base = base + "th"
        return base
    text = re.sub(r"\b(\d+)(?:st|nd|rd|th)\b", ord_repl, text)

    # 16. 4-digit years (1800–2099) before general number expansion
    text = re.sub(r"\b(1[89]\d\d|20[0-9]\d)\b",
                  lambda m: _year_to_words(int(m.group(1))), text)

    # 17. Remaining numbers with commas  →  words
    text = re.sub(r"\b\d{1,3}(?:,\d{3})+\b",
                  lambda m: _number_to_words(m.group(0)), text)

    # 18. Standalone integers ≤ 9999 that TTS might mangle in context
    #     (leave larger bare integers for TTS—it handles them well)
    text = re.sub(r"\b(\d{1,4})\b",
                  lambda m: _int_to_words(int(m.group(1))), text)

    # 19. Remove emojis and other non-speech Unicode
    text = re.sub(r"[\U0001F000-\U0001FFFF\u2600-\u27FF\uFE00-\uFE0F]", "", text)

    # 20. Stray punctuation / symbols
    text = text.replace("@", " at ")
    text = text.replace("#",  "")
    text = text.replace("*",  "")
    text = text.replace("`",  "")
    text = text.replace("~",  "")
    text = text.replace("|",  ", ")
    text = text.replace("\\", "")

    # 21. Collapse whitespace
    text = re.sub(r"[ \t]+",  " ",  text)
    text = re.sub(r"\n{3,}",  "\n\n", text)
    text = "\n".join(l.rstrip() for l in text.splitlines())

    return text.strip()


# ── Synthesis ─────────────────────────────────────────────────────────────────

def synthesise(text: str, out_path: str) -> None:
    if not API_KEY:
        sys.exit("Error: ELEVENLABS_API_KEY not set")

    print(f"Characters: {len(text):,}  (limit 40,000)")
    if len(text) > 40_000:
        sys.exit(f"Error: text is {len(text):,} chars, exceeds 40,000 limit")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format={FORMAT}"
    t0 = time.time()
    r = requests.post(url,
        headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
        json={"text": text, "model_id": MODEL, "voice_settings": VOICE_SETTINGS},
        timeout=300,
    )
    if r.status_code != 200:
        sys.exit(f"ElevenLabs error {r.status_code}: {r.text[:400]}")

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(r.content)

    elapsed = time.time() - t0
    print(f"Wrote {out_path}  ({len(r.content)//1024} KB, {elapsed:.1f}s)")


# ── Loudness normalization ───────────────────────────────────────────────

TARGET_I   = -16    # integrated loudness (LUFS), broadcast standard for speech
TARGET_TP  = -1.5   # true peak (dBTP)
TARGET_LRA =  7     # loudness range (LU)

# dynaudnorm flattens frame-level dynamics (fixes files that start loud
# then trail off); two-pass loudnorm then hits the target LUFS precisely.
_DYNAUDNORM = "dynaudnorm=f=150:g=31:p=0.95:m=20"


def normalize_loudness(mp3_path: str) -> None:
    """Normalize MP3 to broadcast loudness using ffmpeg two-pass loudnorm."""
    loudnorm_base = f"loudnorm=I={TARGET_I}:TP={TARGET_TP}:LRA={TARGET_LRA}"

    # Pass 1: measure (dynaudnorm → loudnorm analysis)
    r = subprocess.run(
        ["ffmpeg", "-i", mp3_path,
         "-af", f"{_DYNAUDNORM},{loudnorm_base}:print_format=json",
         "-f", "null", "-"],
        capture_output=True, text=True,
    )
    stderr = r.stderr
    json_start = stderr.rfind("{")
    json_end = stderr.rfind("}") + 1
    if json_start < 0 or json_end <= json_start:
        print("Warning: could not parse loudnorm output, skipping normalization")
        return
    stats = json.loads(stderr[json_start:json_end])
    print(f"Measured loudness: {stats['input_i']} LUFS  "
          f"(range {stats['input_lra']} LU, peak {stats['input_tp']} dBTP)")

    # Pass 2: apply with measured values + linear gain
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(tmp_fd)
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", mp3_path,
             "-af", (
                 f"{_DYNAUDNORM},"
                 f"{loudnorm_base}"
                 f":measured_I={stats['input_i']}"
                 f":measured_TP={stats['input_tp']}"
                 f":measured_LRA={stats['input_lra']}"
                 f":measured_thresh={stats['input_thresh']}"
                 f":linear=true"
             ),
             "-ar", "44100", tmp_path],
            check=True, capture_output=True,
        )
        os.replace(tmp_path, mp3_path)
        print(f"Normalized → {TARGET_I} LUFS")
    except subprocess.CalledProcessError as e:
        print(f"Warning: loudness normalization failed: {e.stderr[:200] if e.stderr else e}")
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input.md> <output.mp3> [--dry-run]")
        sys.exit(1)

    in_path  = sys.argv[1]
    out_path = sys.argv[2]
    dry_run  = "--dry-run" in sys.argv

    with open(in_path) as f:
        raw = f.read()

    text = transform(raw)

    if dry_run:
        print(text)
        sys.exit(0)

    synthesise(text, out_path)
    normalize_loudness(out_path)
