# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Word lists and patterns used by the gates in ai/checks.py.

Kept apart from the gate code so the lists can be read and reviewed on their own.
Every list is matched on word boundaries, ignoring case. The linter blocks the
listed phrasings only; a rewording can slip past it, which is why every model
sentence is also read by a reviewer (design, component E).

The gates and the linter run on model-written sentences and on template text.
They never run on verbatim NASA quotations, which are shown as quotes with their
field label: PSI's own text contains 'worst case' (PSI-25), 'spherical'
(PSI-10, PSI-23, PSI-159) and 'ensure' (PSI-47).
"""
import re

# ---------------------------------------------------------------- gate 3: number words
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20,
    # reviewer addition: without the tens, 'thirty percent oxygen' passed the number gate unchecked
    "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
    "hundred": 100, "thousand": 1000,
}
# Quantity words with no numeral ('twice as fast', 'half the oxygen'). In a model sentence each must
# be in a cited quote, like a number.
QUANTITY_WORDS = ("half", "twice", "double", "doubles", "doubled", "triple", "triples", "tripled",
                  "dozen", "dozens", "hundreds", "thousands", "tenfold", "twofold", "threefold")

# Unit tokens that may follow a number. A number followed by one of these in a model
# sentence must be followed by the same unit in the cited quote (no unit conversion).
UNITS = (
    "%", "percent", "per cent", "kpa", "pa", "mpa", "psi", "psia", "atm", "bar", "torr",
    "mm", "cm", "m", "km", "um", "µm", "μm", "nm", "mm/s", "cm/s", "m/s", "mm2/s", "mm^2/s", "mm²/s",
    "s", "ms", "sec", "second", "seconds", "min", "minute", "minutes", "h", "hr", "hour", "hours",
    "day", "days", "g", "mg", "kg", "mg/min", "k", "°c", "°f", "c", "w", "kw", "mw", "j", "kj",
    "ppm", "ppb", "hz", "l", "ml", "w/cm2", "kw/m2", "w/m2", "g/s", "mg/s",
)

# Gravity-level names written with a numeral. In template text these name a gravity level,
# not a value from a table, so the template number check does not ask for them in facts.
GRAVITY_NAMES = re.compile(r"\b[01]\s?-?\s?g\b(?![a-z])", re.I)

# ---------------------------------------------------------------- gate 4: always-allowed names
# Names that may appear in any sentence without being in the record text:
# the repository and agency that the page itself names.
ALLOWED_NAMES = {"nasa", "psi"}
# Lower-case words that say where or for whom a result matters. The capital-letter rule does not see
# them, so a model sentence could attach 'lunar habitat' or 'crew' to a record that never says it.
# Each must occur in the record's own text (none of the 24 PSI records says lunar, Martian, habitat,
# rover or spacesuit).
APPLICATION_WORDS = (
    "lunar", "martian", "spacesuit", "spacesuits", "habitat", "habitats", "rover", "rovers",
    "partial gravity", "partial-gravity", "deep space", "exploration", "crew", "crews", "crewed",
    "astronaut", "astronauts", "cabin", "cabins", "spacecraft", "vehicle", "vehicles", "safety",
)

# ---------------------------------------------------------------- gate 5: advice / verdict lexicon
# 'safety' is deliberately not here: 'safe' as a substring occurs in 19 PSI fields, mostly as 'safety',
# and 'fire safety' must pass. Whole words only.
ADVICE_WORDS = (
    "should", "must", "recommend", "recommends", "recommended", "recommending", "recommendation",
    "recommendations", "safe", "safer", "safest", "safely", "unsafe", "ensure", "ensures", "ensured",
    "ensuring", "guarantee", "guarantees", "guaranteed", "certified", "certify", "certifies",
    "approved", "approve", "approves", "proves", "proven",
    # reviewer additions: advice and verdict words the first list let through
    "ought", "advise", "advises", "advised", "advisable", "acceptable", "unacceptable",
    "fireproof", "fire-proof", "risk-free", "hazard-free", "harmless",
)
ADVICE_PHRASES = ("NASA recommends", "NASA concluded", "NASA concludes", "NASA has concluded", "NASA advises",
                  "NASA found", "NASA has found", "NASA showed", "NASA has shown", "NASA determined",
                  "NASA confirmed", "NASA proved", "NASA requires", "NASA approves")

# ---------------------------------------------------------------- gate 10: modality
# A sentence that rests only on objective, hypothesis or approach units must carry one of these frames.
MODALITY_FRAMES = (
    "aims to", "aimed to", "was designed to", "were designed to", "is designed to", "sought to",
    "seeks to", "the objective was", "the objective is", "the objectives were", "the objectives are",
    "the record hypothesizes", "the record hypothesises", "hypothesized that", "hypothesised that",
    "hypothesizes that", "the hypothesis is", "the hypothesis was", "the planned approach",
    "planned to", "plans to", "proposes to", "proposed to",
)
# A sentence that rests only on impact statements may instead be attributed to the record. An
# impact statement is the record's own claim of significance ('will provide technology for ...'),
# not a measured result, so it is not reported in the page's own voice either.
ATTRIBUTION_FRAMES = (
    "the record states", "the record says", "the record describes", "the record notes",
    "the record lists", "the record expects", "according to the record",
)
# Result verbs that turn an aim or a hypothesis into a finding. Allowed only when the same
# word is in the cited quote.
RESULT_VERBS = (
    "showed", "shows", "shown", "found", "finds", "demonstrated", "demonstrates", "confirmed",
    "confirms", "observed", "observes", "revealed", "reveals", "proved", "proves", "proven",
    "established", "establishes",
    # reviewer additions
    "determined", "discovered", "verified", "validated", "concluded", "concludes", "indicated",
    "indicates", "yielded", "resulted in", "results show", "results showed", "data show", "data showed",
    "turned out",
)
NON_RESULT_FIELDS = ("objective", "hypothesis", "approach")
IMPACT_FIELDS = ("researchImpacts",)

# ---------------------------------------------------------------- gate 11: hedges
# The design's list. A cited quote with any of TRIGGER asks the sentence to carry one of ACCEPTED.
# TRIGGER is the wider list evidence.json uses (ai/evidence.py HEDGE_WORDS), so the gate errs strict.
# 'should' triggers but does not count as a kept hedge, because gate 5 rejects it.
HEDGE_DESIGN = ("may", "might", "could", "would", "expected", "potential", "suggest", "preliminary")
HEDGE_TRIGGER = HEDGE_DESIGN + ("should", "potentially", "suggests", "suggested", "possible", "possibly",
                                "likely", "believe")
# A hypothesis frame ('the record hypothesizes') is not a kept hedge: gate 10 asks for the frame and
# gate 11 asks, in addition, for the source's own hedge word.
HEDGE_ACCEPTED = tuple(w for w in HEDGE_TRIGGER if w != "should") + ("expect", "expects", "suggesting")
# The other direction of the same gate: words that make a sentence more certain or stronger than its
# source. Each may be used only when a cited quote has the same word ('to validate' must not become
# 'will validate').
CERTAINTY_WORDS = ("will", "always", "never", "cannot", "certainly", "definitely", "clearly",
                   "undoubtedly", "significantly", "dramatically", "greatly", "fundamentally")

# ---------------------------------------------------------------- gate 7: one complete sentence
# Words that point at text the reader is not shown ('can demonstrate the following').
DANGLING_REFERENCES = ("the following", "as follows", "listed below", "see below", "see above",
                       "the above", "aforementioned", "the former", "the latter")
# 'hypothesizes that due to X.' is a subordinate clause with no main clause. After one of these
# openers a comma (and then the main clause) must follow.
FRAGMENT_OPENERS = ("due to", "because of", "owing to", "as a result of", "in order to")
# gate 2: a clipped quote may stop before one of these words (a new clause or list item starts
# there) or before punctuation; anywhere else it stops in the middle of a phrase.
CLAUSE_STARTERS = ("and", "or", "but", "nor", "while", "whereas", "which", "that", "who", "where",
                   "when", "because", "so", "as well as")

# ---------------------------------------------------------------- template text
# Template notes never carry a score, a rank number or 'best'.
BANNED_TEMPLATE = (
    ("best", re.compile(r"\bbest\b", re.I)),
    ("score with a number", re.compile(r"\bscor(?:e|es|ed|ing)\b[^.;]{0,25}?\d", re.I)),
    ("number of points", re.compile(r"\d+(?:\.\d+)?\s*(?:points?|pts)\b", re.I)),
    ("rank number", re.compile(
        r"\b(?:rank|ranks|ranked|ranking)\s+(?:#\s*|no\.\s*|number\s+)?(?:\d+|first|second|third|top)\b"
        r"|#\s?\d+\b|\b\d+(?:st|nd|rd|th)\b|\btop[- ]?\d+\b"
        r"|\b(?:first|second|third)[- ](?:place|ranked)\b", re.I)),
)
# Wording that no team or model text may use (gate 'banned' for template text, gate 5 for model
# sentences): a count is never worded as coverage, as a statement that something was never tested, as a
# prediction or as a flammability verdict. The gates do not read quoted verbatim NASA text
# (ai/checks.py strip_nasa_quotes), so a NASA phrase quoted in a copied line ('models and predictions of
# heat release') does not trip it, while the same words written by the team or the model do.
WORDING = (
    ("covered", re.compile(r"\b(?:well[- ])?cover(?:ed|s)\b", re.I)),
    ("never tested", re.compile(r"\b(?:never|not)\s+(?:been\s+)?tested\b|\buntested\b", re.I)),
    ("prediction", re.compile(r"\bpredict\w*|\bforecasts?\b"
                              r"|\b(?:will|would)\s+(?:not\s+)?(?:burn|ignite|spread|self-extinguish)\b", re.I)),
    ("flammability verdict", re.compile(r"\b(?:is|are)\s+(?:not\s+)?(?:non-?)?flammable\b|\bnon-?flammable\b", re.I)),
)
# Exact phrases of copied data-role text in which 'covers' speaks of the scope of the needs file (which
# topics the six needs address), not of what the recorded tests cover. Only gate 'banned' for template
# text sets them aside, and only as whole phrases; model sentences never get this allowance.
SCOPE_PHRASES_ALLOWED = (
    "no need of this file covers it",
)
INVERSE_WORDS = re.compile(r"\bburner stream\b|\binverse\b", re.I)

# ---------------------------------------------------------------- gate 6: misconception linter
# Reviewed and widened by the wording review (14 Nov): each pattern now also catches the rewordings
# listed in ai/test_checks.py (LinterGapTest). It still blocks listed phrasings only.
NEGATIONS = ("not", "no", "never", "cannot", "neither", "nor", "none", "without", "n't", "dont", "doesnt",
             "isnt", "arent", "wont")
_NEG_TOKENS = set(NEGATIONS) | {"cant", "didnt", "wasnt", "werent", "hasnt", "havent"}
# Words that state a bounds claim outright.
BOUND_WORDS = ("bound", "bounds", "bounded", "bounding", "bracket", "brackets", "bracketed", "bracketing",
               "envelope", "envelopes", "enveloped", "between")
# Softer words that make the same claim only when the sentence is about partial gravity
# ('lunar gravity lies in the range spanned by microgravity and 1 g').
WEAK_BOUND_WORDS = ("between", "interpolate", "interpolated", "interpolates", "interpolating", "interpolation",
                    "intermediate", "span", "spans", "spanned", "spanning", "range", "within",
                    "extremes", "endpoints")
# 'the lower and upper limits for Martian gravity'. Bare 'limits' is not a bound word: 'flammability
# limits' and 'the low-gravity limits' are everywhere in the PSI text and in the team's own sentences.
_UPPER_LOWER_LIMITS = r"\b(?:upper|lower)\s+(?:and\s+(?:upper|lower)\s+)?(?:limits?|ends?)\b"

# A space or low-gravity setting, with or without a preposition ('in space', 'microgravity makes ...').
_SPACE = (r"\b(?:space|microgravity|micro-gravity|orbit|weightless(?:ness)?|zero[- ]?g(?:ravity)?|0[- ]?g|"
          r"low[- ]g(?:ravity)?|reduced[- ]gravity|spacecraft|space\s+station|ISS)\b")
_COMPARATIVE = (r"\b(?:more|less)\s+(?:flammable|combustible|easily|readily|quickly|intense(?:ly)?|dangerous|"
                r"hazardous|severe|violent(?:ly)?|vigorous(?:ly)?|aggressive(?:ly)?|risky|"
                r"likely\s+to\s+(?:burn|ignite|spread))\b"
                r"|\b(?:easier|harder|faster|slower|quicker)\s+to\s+(?:ignite|burn|extinguish|spread|put\s+out)\b"
                r"|\b(?:burns?|burning|ignites?|spreads?|spreading)\s+(?:faster|slower|hotter|longer|more|less)\b"
                r"|\b(?:more|less|higher|lower|greater|increased|reduced)\s+(?:fire\s+)?(?:risk|hazard|flammability)\b")
_NO_FLOW = (r"\b(?:no|without|absence\s+of|lack\s+of|zero)\s+(?:air\s*flow|airflow|ventilation|forced\s+flow|"
            r"flow|convection|buoyancy)\b|\bquiescent\b|\bstill\s+air\b|\bstagnant\b"
            r"|\b(?:fans?|ventilation|air\s*flow|airflow|flow)\s+(?:is|are|was|were)?\s*"
            r"(?:turned\s+|switched\s+|shut\s+)?(?:off|stopped|stops)\b")
_GOES_OUT = (r"\b(?:goes?|went|going)\s+out\b|\bcan(?:not|'t|\s+not)\s+(?:burn|survive|be\s+sustained|spread)\b"
             r"|\b(?:will|would|do|does)\s*(?:not|n't)\s+burn\b|\bwon't\s+burn\b|\bputs?\s+(?:itself\s+)?out\b"
             r"|\balways\s+(?:self-)?extinguish(?:es)?\b|\bsuffocates?\b|\bsmothers?\s+itself\b"
             # present tense only: a rule ('the flame self-extinguishes'), not a reported observation
             # ('in 21% O2 such flames self-extinguished', a NASA result in the catalog)
             r"|\bself-extinguish(?:es)?\b|\bextinguish(?:es)?\s+(?:itself|on\s+its\s+own)\b"
             r"|\bdies(?:\s+out)?\b|\bstops?\s+burning\b|\bno\s+fire\s+(?:risk|hazard)\b")
# A gravity level as a test condition: 'lunar gravity', 'Martian-g', 'partial gravity', "the Moon's gravity".
# A scenario name such as 'Lunar base' or 'Mars habitat' is not a gravity condition. 'reduced gravity' is
# not here: PSI records use it for microgravity (PSI-69, PSI-98 to PSI-102).
_GRAVITY_TERM = (r"\b(?:lunar|moon(?:'s)?|martian|mars(?:'s)?|partial|fractional)[- ]?(?:gravity|g)\b"
                 r"|\b1/6[- ]?g\b|\b0\.16[- ]?g\b|\b0\.38[- ]?g\b")
# A place whose gravity and atmosphere no PSI test has: 'on the Moon', 'in a lunar habitat', 'on Mars'.
_PLACE_TERM = (r"\bon\s+(?:the\s+)?(?:moon|mars)\b|\b(?:lunar|martian|mars|moon)\s+"
               r"(?:surface|habitat|habitats|base|bases|rover|rovers|outpost|mission|missions)\b"
               r"|\b(?:in|inside)\s+a\s+spacesuit\b")
# A result or a run attributed to a test: verbs only, so that 'tests run at lunar gravity' in a
# needed-data line and 'every test ... is a microgravity test' do not hit. 'recorded' is not here:
# the templates use it as an adjective ('every recorded test is a microgravity test').
_ATTRIB = (r"\b(?:tested|measured|showed|shows|shown|found|observed|burned|burnt|ignited|extinguished|"
           r"demonstrated|confirmed|revealed|reported|burns?|ignites?|spreads?|"
           r"extinguish(?:es)?|self-extinguish(?:es|ed)?)\b")
# Behaviour stated for a place (present or future tense): 'cotton burns on the Moon', 'will ignite'.
_BEHAVIOUR = (r"\b(?:burns?|burned|burnt|ignites?|ignited|spreads?|extinguish(?:es|ed)?|self-extinguish(?:es|ed)?|"
              r"flammable|non-?flammable|flammability\s+is)\b")
ATTRIB_NEGATION_WINDOW = 6  # a negation this many tokens before the verb makes it a statement of absence
# A sentence that names a non-PSI facility or study attributes the result to it, not to a PSI test.
_NON_PSI = r"\bdrop[- ]tower\b|\bparabolic\b|\bcentrifuge\b|\bOlson\s+and\s+Ferkul\b|\boutside\s+PSI\b"
_MICRO = (r"\b(?:microgravity|micro-gravity|micro-?g|0[- ]?g|zero[- ]?g|zero\s+gravity|weightless(?:ness)?|"
          r"low[- ]g(?:ravity)?|reduced[- ]gravity|free[- ]?fall)\b|[µμ]g\b")
_ONE_G = (r"\b(?:1[- ]?g|one[- ]?g|normal[- ]gravity|normal\s+g|unit\s+gravity|earth(?:'s)?(?:[- ]gravity)?|"
          r"terrestrial(?:\s+gravity)?)\b")
_PARTIAL = r"\b(?:lunar|moon|martian|mars|partial|intermediate|fractional)\b"
BETWEEN_WINDOW = 8  # 'between' counts only when both gravity terms follow within this many tokens
# What a normal-gravity screening test is called, and what the misconception says about it.
_TEST1 = r"\bTest\s*#?\s*1\b|\bNASA-STD-6001\w*"
_SCREENING_TEST = (r"\b(?:upward|normal[- ]gravity|1[- ]?g|ground(?:[- ]based)?)\s+"
                   r"(?:flammability\s+|flame\s+|burning\s+|propagation\s+|screening\s+)*(?:tests?|testing|limits?)\b"
                   r"|\bscreening\s+tests?\b")
_CONSERVATIVE = (r"\bconservative\b|\bworst[- ]case\b|\bbounding\b|\bupper\s+bound\b|\bsafety\s+margin\b"
                 r"|\bmargin\s+of\s+safety\b")
_EARTH_AIR = r"(?:earth|sea[- ]level|normal|ordinary|standard|cabin)(?:'s)?\s+(?:air|atmosphere)"

LINT = [
    # (name, test). Each test takes the sentence (str) and returns True on a hit.
    ("comparative_in_space",
     lambda s: bool(re.search(_COMPARATIVE, s, re.I)) and bool(re.search(_SPACE, s, re.I))),
    ("burns_more_easily",
     lambda s: bool(re.search(r"\b(?:burns?|burning|ignites?)\s+(?:more|less)\s+(?:easily|readily)\b", s, re.I))),
    ("test1_conservative", lambda s: _test1_claim(s)),
    ("no_airflow_goes_out",
     lambda s: bool(re.search(_NO_FLOW, s, re.I)) and bool(re.search(_GOES_OUT, s, re.I))),
    ("cool_flame_harmless",
     lambda s: bool(re.search(r"\bcool\s+flames?\b", s, re.I))
     and bool(re.search(r"\bharmless\b|\bbenign\b|\binnocuous\b|\bnegligible\b|\blow[- ]risk\b"
                        r"|\b(?:no|not\s+an?|without)\s+(?:real\s+|fire\s+|safety\s+)?"
                        r"(?:hazard|risk|danger|threat|concern)\b|\bnot\s+(?:dangerous|hazardous)\b", s, re.I))),
    ("equivalent_to_earth_air",
     lambda s: bool(re.search(r"\b(?:equivalent|equal|identical|same)\s+(?:to|as)\s+(?:the\s+)?" + _EARTH_AIR, s, re.I)
                    or re.search(r"\bsame\b[^.;]{0,50}\bas\b[^.;]{0,25}" + _EARTH_AIR, s, re.I)
                    or re.search(r"\b(?:as|no\s+more|not\s+more)\s+flammable\s+(?:as|than)\b[^.;]{0,25}" + _EARTH_AIR, s, re.I)
                    or re.search(r"\b(?:like|just\s+like)\s+(?:the\s+)?" + _EARTH_AIR, s, re.I)
                    or (re.search(r"\bnormoxic\b", s, re.I)
                        and re.search(r"\b(?:equivalent|same|no\s+more|identical)\b", s, re.I)))),
    ("flames_spherical_in_space",
     lambda s: bool(re.search(r"\bspherical\b", s, re.I)) and bool(re.search(r"\bflames?\b", s, re.I))
     and bool(re.search(r"\b(?:in|into)\s+(?:space|microgravity|orbit|weightlessness|zero[- ]?g|0[- ]?g|low[- ]gravity)"
                        r"|\bmicrogravity\b|\bweightless", s, re.I))),
    ("partial_gravity_result_from_psi",
     lambda s: bool(re.search(_GRAVITY_TERM, s, re.I)) and _unnegated(s, _ATTRIB)
     and not re.search(_NON_PSI, s, re.I)),
    ("behaviour_at_untested_place",
     lambda s: bool(re.search(_PLACE_TERM, s, re.I)) and _unnegated(s, _BEHAVIOUR)
     and not re.search(_NON_PSI, s, re.I)),
    ("micro_and_1g_as_bounds", lambda s: _bounds_claim(s)),
]


def tokens(s):
    """Word tokens, lower case; "doesn't" -> "doesnt", "1g" stays one token, "1 g" is two."""
    return [t.replace("'", "").replace("’", "") for t in re.findall(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)?", s.lower())]


def _is_negation(tok):
    return tok in _NEG_TOKENS or (tok.endswith("nt") and tok[:-2] in ("do", "does", "is", "are", "wo", "ca", "did"))


def _has_negation(s):
    return any(_is_negation(t) for t in tokens(s))


def _test1_claim(s):
    """'Test 1' or 'NASA-STD-6001' with 'conservative' or 'worst case': always a hit, as designed (a
    correct paraphrase of NASA's sentence falls back to the quote). The same claim about a test named
    only by what it is ('the upward flame test', 'normal-gravity screening tests', '1 g limits') is a
    hit unless it is negated: 'the upward 1g test may not be conservative' is NASA's own point."""
    if not re.search(_CONSERVATIVE, s, re.I):
        return False
    if re.search(_TEST1, s, re.I):
        return True
    return bool(re.search(_SCREENING_TEST, s, re.I)) and _unnegated(s, _CONSERVATIVE, window=4)


def _unnegated(s, pattern, window=None):
    """True when the sentence has a match of `pattern` with no negation in the
    ATTRIB_NEGATION_WINDOW tokens before it. 'none was run at lunar gravity' and 'no test was
    recorded at lunar gravity' state an absence; 'tests at lunar gravity showed flames that did not
    go out' does not (the old rule let any 'not' anywhere excuse the sentence)."""
    for m in re.finditer(pattern, s, re.I):
        before = tokens(s[:m.start()])[-(window or ATTRIB_NEGATION_WINDOW):]
        if not any(_is_negation(b) for b in before):
            return True
    return False


def _bounds_claim(s):
    """The 'microgravity and 1 g are bounds' claim. A hit needs microgravity|0 g|zero-g together with
    1 g|normal gravity|Earth, and a bound word with no negation in the four tokens before it.
    Outright words (bound, bounds, bracket, envelope) always count. 'between' counts only when both
    gravity terms follow it within BETWEEN_WINDOW tokens and the sentence names partial, lunar or
    Martian gravity (PSI-26 and PSI-60 objectives compare 1 g and 0 g with 'between' and make no
    bounds claim). The softer words (range, span, interpolate, intermediate, within, limits) count
    only when the sentence names partial, lunar or Martian gravity."""
    if not re.search(_MICRO, s, re.I) or not re.search(_ONE_G, s, re.I):
        return False
    partial = bool(re.search(_PARTIAL, s, re.I))
    if partial:
        for m in re.finditer(_UPPER_LOWER_LIMITS, s, re.I):
            if not any(_is_negation(b) for b in tokens(s[:m.start()])[-4:]):
                return True
    toks = tokens(s)
    for i, t in enumerate(toks):
        strong = t in BOUND_WORDS and t != "between"
        weak = t in WEAK_BOUND_WORDS
        if not strong and not weak:
            continue
        before = toks[max(0, i - 4):i]
        if any(_is_negation(b) for b in before):
            continue
        if strong:
            return True
        if not partial:
            continue
        if t == "between":
            after = " ".join(toks[i + 1:i + 1 + BETWEEN_WINDOW])
            if not (re.search(_MICRO, after, re.I) and re.search(_ONE_G, after, re.I)):
                continue
        return True
    return False


def lint(sentence):
    """Names of the linter patterns that the sentence hits (empty list = clean)."""
    return [name for name, test in LINT if test(sentence)]
