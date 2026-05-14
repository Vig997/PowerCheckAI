import re

NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

QUANTITY_RE = re.compile(r"(?:(?P<count>\d+)\s*x|\(x(?P<paren>\d+)\)|(?P<prefix>\d+)\s+|(?P<word>one|two|three|four|five|six|seven|eight|nine|ten)\s+)", re.I)
VOLTAGE_RE = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s*v\b", re.I)
CURRENT_RE = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>ma|a)\b", re.I)
CAPACITY_RE = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s*mah\b", re.I)
LED_COUNT_RE = re.compile(r"(?P<count>\d+)\s*(?:leds?|pixels?|neopixels?)", re.I)
POWER_RE = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s*w\b", re.I)
RESISTANCE_RE = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>ohm|ohms|\u03a9|k\u03a9|kohm|kohms)\b", re.I)
CAPACITANCE_RE = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>uf|\u00b5f|mf|nf|pf|farad|farads)\b", re.I)
BUDGET_RE = re.compile(r"(?:budget|cost|under|less than|below)\s*\$?\s*(?P<value>\d+(?:\.\d+)?)", re.I)
DIMENSION_RE = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>mm|cm|m|in|inch|inches)\b", re.I)
DEADLINE_RE = re.compile(r"(?:due|deadline|by)\s+(?P<value>today|tomorrow|next week|[a-z]+\s+\d{1,2})", re.I)


def parse_quantity(text: str, default: int = 1) -> int:
    match = QUANTITY_RE.search(text)
    if not match:
        return default
    value = match.group("count") or match.group("paren") or match.group("prefix")
    if value:
        return max(1, int(value))
    word = match.group("word")
    return NUMBER_WORDS.get(word.lower(), default) if word else default
