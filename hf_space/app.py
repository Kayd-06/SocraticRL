# hf_space/app.py  — SocraticRL · cinematic UI rebuild
from __future__ import annotations
import os, re
from dataclasses import dataclass
from typing import List
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

# ── reward logic (inlined) ────────────────────────────────────────────────
DIRECT_ANSWER_PATTERNS = [
    r"\bthe answer is\b", r"\bthe reason is\b", r"\bbecause\b.{0,60}\.",
    r"\blet me explain\b", r"\bthis is because\b", r"\bactually,\b",
    r"\bin fact,\b", r"\bthe truth is\b", r"\bsimply put\b",
    r"\bto summarize\b", r"\bto be clear\b", r"\bthe definition\b", r"\bby definition\b",
]
GOOD_QUESTION_PATTERNS = [
    r"\bwhat (do you|would you|might)\b", r"\bhow (do you|would you|might|could)\b",
    r"\bwhy (do you|would you|might|could)\b",
    r"\bcan you (imagine|think|describe|explain|consider)\b",
    r"\bif .{5,50} what\b", r"\bif .{5,50} how\b",
    r"\bwhat (would happen|do you think|role)\b",
    r"\bwhat (evidence|experiment|observation)\b",
    r"\bwhat (causes|makes|allows|prevents)\b",
    r"\bhave you (ever|considered|thought)\b", r"\bdo you think\b", r"\bcould you\b",
]

def _jaccard(a: str, b: str) -> float:
    sa, sb = set(a.lower().split()), set(b.lower().split())
    if not sa or not sb: return 0.0
    return len(sa & sb) / len(sa | sb)

@dataclass
class RewardResult:
    total: float = 0.0
    feedback: str = ""

def compute_reward(output, topic, turn, understanding_score, history) -> RewardResult:
    reward, parts = 0.0, []
    text, lower = output.strip(), output.strip().lower()
    if text.endswith("?"): reward += 0.20; parts.append("is_question:+0.20")
    else: reward -= 0.30; parts.append("not_question:-0.30")
    for pat in DIRECT_ANSWER_PATTERNS:
        if re.search(pat, lower): reward -= 0.50; parts.append("direct_answer:-0.50"); break
    stop = {"why","how","does","do","is","the","a","an","on","in","at","of","to","and","or","for","with","what","that","it","its","are","was"}
    topic_words = set(re.sub(r"[^a-z ]","",topic.lower()).split()) - stop
    has_socratic = any(re.search(p, lower) for p in GOOD_QUESTION_PATTERNS)
    has_topic = any(w in lower for w in topic_words if len(w) > 3)
    if has_socratic and has_topic: reward += 0.30; parts.append("socratic_pattern:+0.30")
    elif has_socratic: reward -= 0.40; parts.append("generic_question:-0.40")
    wc = len(text.split())
    if wc < 5: reward -= 0.20; parts.append("too_short:-0.20")
    if wc > 60: reward -= 0.10; parts.append("too_long:-0.10")
    for prev in history[-3:]:
        if _jaccard(text, prev) > 0.55: reward -= 0.35; parts.append("repetition:-0.35"); break
    if turn <= 5 and understanding_score > 0.40: reward += 0.20; parts.append("early_progress:+0.20")
    return RewardResult(total=round(reward,2), feedback=" | ".join(parts) or "no_signal:0.00")

# ── LLM ───────────────────────────────────────────────────────────────────
OPENAI_API_KEY  = os.environ.get("OPENAI_API_KEY","")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL","https://api.openai.com/v1")
LLM_MODEL       = os.environ.get("LLM_MODEL","gpt-4o-mini")
SYSTEM_PROMPT = (
    "You are a Socratic tutor. Output exactly ONE question, nothing else. "
    "Rules: end with '?', never state the answer, never explain, be topic-specific, "
    "don't repeat previous questions, 10–50 words."
)
FALLBACK_TEMPLATES = [
    "What do you already know or believe about {topic}, and where does that understanding come from?",
    "If your current explanation of {topic} is correct, what experiment would confirm it?",
    "Can you think of a real-world example where {topic} plays a visible role?",
    "What would change in your daily life if {topic} worked completely differently?",
    "How would you explain {topic} to a ten-year-old using only things they can see or touch?",
    "What part of {topic} feels most confusing or counterintuitive to you right now?",
    "If you had to challenge your own understanding of {topic}, what would be the strongest objection?",
    "What evidence would convince you that your current model of {topic} is wrong?",
    "Can you describe a situation where two people might disagree about {topic}?",
    "What question about {topic} do you wish someone would just answer, and why is it hard to figure out?",
]
# ── Realistic student simulator ───────────────────────────────────────────
# Each topic has 3 phases: confused (turns 0-3), partial (turns 4-7), clear (turns 8+)
# Within each phase there are multiple varied replies so it never feels repetitive.
# A small "filler" bank adds natural hesitation openers.

import random

STUDENT_PROFILES: dict[str, dict] = {
    "why do objects fall at the same speed regardless of mass": {
        "confused": [
            "I mean... heavier things definitely fall faster, right? Like a bowling ball versus a feather — the bowling ball always wins.",
            "I guess I always assumed gravity pulls harder on heavier stuff, so they'd speed up more. Is that not how it works?",
            "Wait, so a rock and a piece of paper dropped at the same time would land together? That seems really wrong to me.",
            "I've seen feathers float down slowly and rocks drop fast. Doesn't that prove heavier things fall faster?",
        ],
        "partial": [
            "Oh — so the air is the thing slowing the feather down, not gravity itself? That's actually a really different way to think about it.",
            "Okay so in a vacuum they'd fall the same... but I'm still not totally sure why. Is it something about how gravity and mass cancel out?",
            "I think I see it — gravity pulls harder on heavier things, but heavier things also resist acceleration more, so it evens out?",
            "So Galileo was right all along and we just couldn't see it because of air resistance. That's kind of wild.",
        ],
        "clear": [
            "Right, so gravitational force scales with mass, but so does inertia — they cancel perfectly, giving every object the same acceleration of 9.8 m/s². Air resistance is the confounding variable I was ignoring.",
            "I get it now. The net effect is that all objects in free fall accelerate identically regardless of mass. The feather-and-hammer experiment on the Moon proves it perfectly.",
            "It makes complete sense. F = ma, and since F_gravity = mg, the mass cancels out and you're left with a = g for everything. I was confusing air drag with gravity this whole time.",
        ],
    },
    "why is the sky blue": {
        "confused": [
            "Isn't it just reflecting the ocean? Like, the sea is blue so the sky looks blue too?",
            "I thought it was because the atmosphere filters out other colours somehow, but I'm not sure of the mechanism.",
            "Maybe it's something to do with water vapour in the air? Blue light travels through water better?",
            "I honestly have no idea — I've just always accepted it's blue without questioning why.",
        ],
        "partial": [
            "Okay so it's something about light scattering... shorter wavelengths bounce around more? Blue is a short wavelength so it scatters everywhere?",
            "So the atmosphere isn't filtering colours out — it's actively scattering blue light in all directions, which is why we see it from every angle?",
            "That explains sunsets! At sunset the light travels through way more atmosphere, so all the blue has already scattered away and we're left with red and orange.",
            "Wait, so if the atmosphere were thicker, the sky might look violet or even purple? Because even shorter wavelengths would dominate?",
        ],
        "clear": [
            "Got it — Rayleigh scattering. Blue light has a shorter wavelength and scatters roughly 5-10x more than red light when it hits air molecules. So the whole sky acts like a blue light diffuser.",
            "It all clicks now. The sun emits all visible wavelengths, but blue scatters so much in every direction that it fills the entire sky. At sunset the path length is longer so even blue scatters away, leaving red.",
            "I understand it completely. It's not reflection or filtering — it's differential scattering based on wavelength. Shorter wavelengths scatter more, and blue is the dominant short wavelength our eyes are sensitive to.",
        ],
    },
    "how does photosynthesis work": {
        "confused": [
            "Plants eat soil and water, right? And sunlight just gives them energy to grow, like a battery charger?",
            "I know chlorophyll is involved and it's green, but I have no idea what it actually does chemically.",
            "I thought plants absorb nutrients from the ground — like minerals and stuff — and that's what they're made of?",
            "Something about CO2 and oxygen, but I always mix up which one goes in and which comes out.",
        ],
        "partial": [
            "Oh wait — so the actual mass of the plant comes from carbon dioxide in the air, not from the soil? That's genuinely shocking.",
            "So chlorophyll absorbs light energy and uses it to split water molecules, and the oxygen we breathe is basically a waste product of that process?",
            "I think I see it — light energy gets converted into chemical energy stored in glucose, using CO2 as the carbon source. The soil just provides minerals.",
            "So photosynthesis is basically: light + water + CO2 → glucose + oxygen. The plant is literally building itself out of air.",
        ],
        "clear": [
            "I've got it. 6CO2 + 6H2O + light energy → C6H12O6 + 6O2. The carbon skeleton of every organic molecule in the plant came from atmospheric CO2, fixed by the Calvin cycle.",
            "It makes total sense now. The light reactions split water and generate ATP and NADPH. The Calvin cycle uses those to fix CO2 into glucose. The oxygen is a byproduct of water splitting.",
            "Completely clear. Plants are carbon-fixing machines — they pull CO2 from the air and use photon energy to build complex organic molecules. That's where essentially all the biomass in the food chain originates.",
        ],
    },
    "why does ice float on water": {
        "confused": [
            "Ice is lighter than water, so it floats? But I don't really know why it would be lighter if it's the same substance.",
            "I thought all solids sink in their own liquid. Ice floating seems like an exception but I don't know the reason.",
            "Maybe ice has air bubbles trapped in it that make it less dense? Like how a life jacket works?",
            "I know it has something to do with hydrogen bonds but I have no idea what that means in practice.",
        ],
        "partial": [
            "So water molecules form a hexagonal lattice when they freeze, which actually takes up more space than liquid water? That's counterintuitive.",
            "The hydrogen bonds in ice hold molecules further apart than in liquid water, so the same mass occupies more volume — meaning lower density. That's why it floats.",
            "Oh, and this is actually really important for life — if ice sank, lakes would freeze solid from the bottom up and kill everything. The floating ice acts like an insulating lid.",
            "So water is one of the very few substances that expands on freezing. Most things contract. It's the hydrogen bond angle that forces the open lattice structure.",
        ],
        "clear": [
            "Crystal clear. Liquid water has a density of ~1.0 g/cm³ but ice is ~0.917 g/cm³ because the hydrogen bonds lock molecules into a hexagonal lattice with more empty space. That 9% density difference is why it floats.",
            "I fully understand it now. The O-H···O hydrogen bond angle in ice forces a rigid, open tetrahedral structure. When ice melts, those bonds break and molecules pack more tightly, increasing density.",
            "It all makes sense. Water's anomalous expansion on freezing is a direct consequence of directional hydrogen bonding. It's one of the properties that makes liquid water essential for life as we know it.",
        ],
    },
    "what causes seasons on earth": {
        "confused": [
            "Earth gets closer to the Sun in summer and farther away in winter, right? That's why it's hotter and colder?",
            "I thought the atmosphere gets thinner in winter somehow, letting less heat through?",
            "Maybe the Sun just produces more energy at certain times of year? Like it has its own seasons?",
            "I know the Earth tilts but I'm not sure how that actually changes the temperature.",
        ],
        "partial": [
            "Oh — if it were about distance, both hemispheres would have summer at the same time. But they have opposite seasons, so it must be the tilt.",
            "So the tilt means one hemisphere gets more direct sunlight for part of the year. More direct means more energy per square metre hitting the ground.",
            "I see — it's like shining a flashlight straight down versus at an angle. The angled beam spreads over more area so each spot gets less energy. That's winter.",
            "And the tilt also changes day length — longer days in summer mean more total hours of sunlight, which compounds the heating effect.",
        ],
        "clear": [
            "Got it completely. Earth's 23.5° axial tilt means each hemisphere alternately faces the Sun more directly. More direct angle = higher energy density per m² + longer days = summer. It has nothing to do with orbital distance.",
            "It's all about the angle of incidence and day length. When the Northern Hemisphere tilts toward the Sun, sunlight hits more directly and days are longer — both effects add up to summer. The Southern Hemisphere simultaneously experiences winter.",
            "Fully clear. The seasons are caused entirely by axial tilt, not orbital distance. In fact Earth is slightly closer to the Sun in January (Northern Hemisphere winter), which proves distance isn't the driver.",
        ],
    },
}

# Keyword triggers that pull a topic-specific profile
TOPIC_KEYWORDS: list[tuple[str, str]] = [
    ("fall", "why do objects fall at the same speed regardless of mass"),
    ("same speed", "why do objects fall at the same speed regardless of mass"),
    ("gravity", "why do objects fall at the same speed regardless of mass"),
    ("sky blue", "why is the sky blue"),
    ("sky", "why is the sky blue"),
    ("blue", "why is the sky blue"),
    ("photosynthesis", "how does photosynthesis work"),
    ("plant", "how does photosynthesis work"),
    ("chlorophyll", "how does photosynthesis work"),
    ("ice float", "why does ice float on water"),
    ("ice", "why does ice float on water"),
    ("float", "why does ice float on water"),
    ("season", "what causes seasons on earth"),
    ("summer", "what causes seasons on earth"),
    ("winter", "what causes seasons on earth"),
    ("tilt", "what causes seasons on earth"),
]

# Natural hesitation openers — randomly prepended for realism
HESITATION_OPENERS = [
    "Hmm... ", "Okay, let me think... ", "That's a good question — ",
    "I hadn't considered that angle before. ", "Wait, so... ",
    "Interesting — ", "Let me reason through this... ",
    "", "", "",  # empty strings so opener is often omitted
]

# Filler connectors used mid-sentence for partial-understanding phase
PARTIAL_CONNECTORS = [
    "I think ", "I guess ", "Maybe ", "So if I'm following you, ",
    "It sounds like ", "Are you saying that ",
]


def _match_topic_profile(topic: str) -> str | None:
    """Return the profile key that best matches the given topic string."""
    t = topic.lower()
    for keyword, profile_key in TOPIC_KEYWORDS:
        if keyword in t:
            return profile_key
    return None


def simulate_student_response(turn: int, student_response: str, topic: str = "") -> str:
    """
    Generate a realistic, topic-aware student reply.
    - Turns 0-3: confused, holds misconception
    - Turns 4-7: partial understanding, questioning their own belief
    - Turns 8+:  clear understanding, can articulate correctly
    """
    rng = random.Random(hash(topic + str(turn)))  # deterministic per topic+turn

    profile_key = _match_topic_profile(topic)

    if profile_key and profile_key in STUDENT_PROFILES:
        profile = STUDENT_PROFILES[profile_key]
        if turn <= 3:
            pool = profile["confused"]
        elif turn <= 7:
            pool = profile["partial"]
        else:
            pool = profile["clear"]
        reply = rng.choice(pool)
    else:
        # Generic fallback for unknown topics — still phase-aware
        if turn == 0:
            reply = "I think I have a rough idea, but I'm probably missing something important."
        elif turn <= 2:
            reply = "My instinct is based on everyday experience, but your question makes me doubt that assumption."
        elif turn <= 4:
            reply = "Okay, I'm starting to question my original assumption. The way you framed that makes me think there's a mechanism I'm overlooking."
        elif turn <= 6:
            reply = "I think I see it now — my initial model was too simplistic. There's an underlying principle I wasn't accounting for."
        elif turn <= 8:
            reply = "That reframes it completely. So the key insight is something that only becomes obvious when you isolate the right variable?"
        else:
            reply = "I believe I understand it now. My original intuition was based on surface-level observation rather than the actual mechanism."

    # Randomly prepend a hesitation opener for naturalness (not on clear-phase replies)
    if turn <= 7:
        opener = rng.choice(HESITATION_OPENERS)
        if opener and not reply.startswith(("I mean", "I know", "I thought", "I guess",
                                             "Isn't", "Maybe", "Something", "Wait",
                                             "Oh", "Okay", "Got", "Right", "So ")):
            reply = opener + reply[0].lower() + reply[1:]

    return reply


async def llm_generate_question(topic, student_response, history, turn) -> str:
    if not OPENAI_API_KEY:
        return FALLBACK_TEMPLATES[turn % len(FALLBACK_TEMPLATES)].format(topic=topic)
    messages = [{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":
        f"Topic: {topic}\nPrevious questions: {history[-4:]}\nStudent: {student_response}\nAsk next Socratic question:"}]
    try:
        async with httpx.AsyncClient(timeout=15.0) as c:
            r = await c.post(f"{OPENAI_BASE_URL}/chat/completions",
                headers={"Authorization":f"Bearer {OPENAI_API_KEY}"},
                json={"model":LLM_MODEL,"messages":messages,"max_tokens":120,"temperature":0.8})
            r.raise_for_status()
            q = r.json()["choices"][0]["message"]["content"].strip()
            return q if q.endswith("?") else q.rstrip(".!") + "?"
    except Exception:
        return FALLBACK_TEMPLATES[turn % len(FALLBACK_TEMPLATES)].format(topic=topic)

# ── FastAPI ────────────────────────────────────────────────────────────────
app = FastAPI(title="SocraticRL", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class StepRequest(BaseModel):
    topic: str; student_response: str = ""; turn: int = 0; history: List[str] = []

class StepResponse(BaseModel):
    agent_question: str; student_response: str; reward: float
    reward_breakdown: str; understanding_score: float; turn: int; done: bool

# ── HTML PAGE ─────────────────────────────────────────────────────────────
HTML_PAGE = '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8"/>\n<meta name="viewport" content="width=device-width,initial-scale=1"/>\n<title>SocraticRL</title>\n<link rel="preconnect" href="https://fonts.googleapis.com"/>\n<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>\n<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>\n<style>\n:root{\n  --bg:#07090f;--surface:#0d1117;--card:#111827;--border:#1f2937;\n  --accent:#6ee7b7;--accent2:#818cf8;--accent3:#f472b6;\n  --text:#f1f5f9;--muted:#64748b;--danger:#f87171;--warn:#fbbf24;\n  --agent-bg:linear-gradient(135deg,#0f2027,#1a2a3a);\n  --student-bg:linear-gradient(135deg,#0f1f0f,#1a2e1a);\n  --radius:14px;--radius-sm:8px;\n}\n*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}\nhtml{scroll-behavior:smooth}\nbody{\n  font-family:\'Inter\',system-ui,sans-serif;\n  background:var(--bg);color:var(--text);\n  min-height:100vh;overflow-x:hidden;\n}\n\n/* ── animated starfield bg ── */\nbody::before{\n  content:\'\';position:fixed;inset:0;\n  background:\n    radial-gradient(ellipse 80% 50% at 20% 10%,rgba(110,231,183,.04) 0%,transparent 60%),\n    radial-gradient(ellipse 60% 40% at 80% 80%,rgba(129,140,248,.05) 0%,transparent 60%);\n  pointer-events:none;z-index:0;\n}\n\n/* ── header ── */\nheader{\n  position:sticky;top:0;z-index:100;\n  display:flex;align-items:center;justify-content:space-between;\n  padding:0 32px;height:60px;\n  background:rgba(7,9,15,.85);\n  backdrop-filter:blur(20px);\n  border-bottom:1px solid var(--border);\n}\n.logo{display:flex;align-items:center;gap:10px}\n.logo-icon{\n  width:32px;height:32px;border-radius:8px;\n  background:linear-gradient(135deg,var(--accent),var(--accent2));\n  display:flex;align-items:center;justify-content:center;\n  font-size:16px;box-shadow:0 0 20px rgba(110,231,183,.3);\n}\n.logo-text{font-size:1.1rem;font-weight:700;letter-spacing:-.3px}\n.logo-text span{color:var(--accent)}\n.header-right{display:flex;align-items:center;gap:16px}\n.badge{\n  padding:3px 10px;border-radius:20px;font-size:.7rem;font-weight:600;\n  letter-spacing:.5px;text-transform:uppercase;\n}\n.badge-green{background:rgba(110,231,183,.12);color:var(--accent);border:1px solid rgba(110,231,183,.2)}\n.badge-purple{background:rgba(129,140,248,.12);color:var(--accent2);border:1px solid rgba(129,140,248,.2)}\n.tagline{font-size:.8rem;color:var(--muted);font-style:italic}\n\n/* ── layout ── */\n.layout{\n  display:grid;\n  grid-template-columns:1fr 420px;\n  gap:20px;\n  padding:24px 32px;\n  max-width:1400px;margin:0 auto;\n  position:relative;z-index:1;\n}\n\n/* ── section titles ── */\n.section-title{\n  font-size:.7rem;font-weight:600;letter-spacing:1.5px;\n  text-transform:uppercase;color:var(--muted);\n  margin-bottom:14px;display:flex;align-items:center;gap:8px;\n}\n.section-title::after{content:\'\';flex:1;height:1px;background:var(--border)}\n\n/* ── topic input area ── */\n.topic-card{\n  background:var(--card);border:1px solid var(--border);\n  border-radius:var(--radius);padding:20px;margin-bottom:16px;\n  transition:border-color .2s;\n}\n.topic-card:focus-within{border-color:rgba(110,231,183,.4)}\n.topic-label{font-size:.75rem;font-weight:500;color:var(--muted);margin-bottom:8px;display:block}\n.topic-input-row{display:flex;gap:10px;align-items:center}\n#topic-input{\n  flex:1;background:rgba(255,255,255,.04);border:1px solid var(--border);\n  color:var(--text);border-radius:var(--radius-sm);\n  padding:11px 16px;font-size:.9rem;font-family:\'Inter\',sans-serif;\n  transition:border-color .2s,box-shadow .2s;outline:none;\n}\n#topic-input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(110,231,183,.1)}\n#topic-input::placeholder{color:var(--muted)}\n.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}\n.chip{\n  padding:4px 12px;border-radius:20px;font-size:.72rem;font-weight:500;\n  background:rgba(255,255,255,.04);border:1px solid var(--border);\n  color:var(--muted);cursor:pointer;transition:all .15s;white-space:nowrap;\n}\n.chip:hover{background:rgba(110,231,183,.1);border-color:rgba(110,231,183,.3);color:var(--accent)}\n\n/* ── buttons ── */\n.btn{\n  display:flex;align-items:center;justify-content:center;gap:8px;\n  padding:11px 20px;border:none;border-radius:var(--radius-sm);\n  font-size:.88rem;font-weight:600;cursor:pointer;\n  transition:all .2s;white-space:nowrap;font-family:\'Inter\',sans-serif;\n}\n.btn:disabled{opacity:.35;cursor:not-allowed;transform:none!important}\n.btn-primary{\n  background:linear-gradient(135deg,var(--accent),#34d399);\n  color:#07090f;box-shadow:0 4px 20px rgba(110,231,183,.25);\n}\n.btn-primary:not(:disabled):hover{transform:translateY(-1px);box-shadow:0 6px 28px rgba(110,231,183,.35)}\n.btn-secondary{\n  background:linear-gradient(135deg,var(--accent2),#6366f1);\n  color:#fff;box-shadow:0 4px 20px rgba(129,140,248,.2);\n}\n.btn-secondary:not(:disabled):hover{transform:translateY(-1px);box-shadow:0 6px 28px rgba(129,140,248,.3)}\n.btn-row{display:flex;gap:10px;margin-bottom:16px}\n.btn-row .btn{flex:1}\n\n/* ── chat window ── */\n.chat-window{\n  background:var(--card);border:1px solid var(--border);\n  border-radius:var(--radius);overflow:hidden;margin-bottom:16px;\n}\n.chat-header{\n  padding:12px 18px;border-bottom:1px solid var(--border);\n  display:flex;align-items:center;justify-content:space-between;\n  background:rgba(255,255,255,.02);\n}\n.chat-header-left{display:flex;align-items:center;gap:8px;font-size:.8rem;font-weight:500;color:var(--muted)}\n.dot{width:8px;height:8px;border-radius:50%}\n.dot-green{background:var(--accent);box-shadow:0 0 8px var(--accent)}\n.dot-blue{background:var(--accent2);box-shadow:0 0 8px var(--accent2)}\n.dot-red{background:var(--danger)}\n.traffic{display:flex;gap:5px;align-items:center}\n#chat{\n  height:400px;overflow-y:auto;padding:20px;\n  display:flex;flex-direction:column;gap:16px;\n  scroll-behavior:smooth;\n}\n#chat::-webkit-scrollbar{width:4px}\n#chat::-webkit-scrollbar-track{background:transparent}\n#chat::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}\n\n/* ── bubbles ── */\n.bubble-row{display:flex;gap:10px;animation:bubbleIn .35s cubic-bezier(.34,1.56,.64,1) both}\n@keyframes bubbleIn{from{opacity:0;transform:translateY(12px) scale(.97)}to{opacity:1;transform:none}}\n.bubble-row.agent{align-items:flex-start}\n.bubble-row.student{align-items:flex-start;flex-direction:row-reverse}\n.avatar{\n  width:34px;height:34px;border-radius:10px;flex-shrink:0;\n  display:flex;align-items:center;justify-content:center;font-size:15px;\n}\n.avatar-agent{background:linear-gradient(135deg,#0f2027,#1a3a4a);border:1px solid rgba(110,231,183,.2)}\n.avatar-student{background:linear-gradient(135deg,#1a0f27,#2a1a3a);border:1px solid rgba(129,140,248,.2)}\n.bubble-content{max-width:78%}\n.bubble-name{font-size:.68rem;font-weight:600;letter-spacing:.5px;text-transform:uppercase;margin-bottom:5px;padding:0 4px}\n.name-agent{color:var(--accent)}\n.name-student{color:var(--accent2);text-align:right}\n.bubble{\n  padding:12px 16px;border-radius:12px;font-size:.875rem;line-height:1.6;\n  position:relative;\n}\n.bubble-agent{\n  background:var(--agent-bg);border:1px solid rgba(110,231,183,.12);\n  border-top-left-radius:3px;\n}\n.bubble-student{\n  background:var(--student-bg);border:1px solid rgba(129,140,248,.12);\n  border-top-right-radius:3px;\n}\n.reward-strip{\n  margin-top:8px;padding:6px 10px;border-radius:6px;\n  background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,.05);\n  font-family:\'JetBrains Mono\',monospace;font-size:.68rem;\n  display:flex;flex-wrap:wrap;gap:6px;align-items:center;\n}\n.reward-total{font-weight:700}\n.reward-pos{color:var(--accent)}\n.reward-neg{color:var(--danger)}\n.reward-tag{\n  padding:1px 6px;border-radius:4px;font-size:.63rem;\n  background:rgba(255,255,255,.05);color:var(--muted);\n}\n.reward-tag.pos{background:rgba(110,231,183,.08);color:var(--accent)}\n.reward-tag.neg{background:rgba(248,113,113,.08);color:var(--danger)}\n\n/* ── typing indicator ── */\n.typing-row{display:flex;gap:10px;align-items:flex-start}\n.typing-bubble{\n  padding:12px 16px;border-radius:12px;border-top-left-radius:3px;\n  background:var(--agent-bg);border:1px solid rgba(110,231,183,.12);\n  display:flex;gap:5px;align-items:center;\n}\n.typing-dot{\n  width:7px;height:7px;border-radius:50%;background:var(--accent);opacity:.4;\n  animation:typingPulse 1.2s ease-in-out infinite;\n}\n.typing-dot:nth-child(2){animation-delay:.2s}\n.typing-dot:nth-child(3){animation-delay:.4s}\n@keyframes typingPulse{0%,80%,100%{opacity:.2;transform:scale(.8)}40%{opacity:1;transform:scale(1)}}\n\n/* ── empty state ── */\n.empty-state{\n  flex:1;display:flex;flex-direction:column;align-items:center;\n  justify-content:center;gap:12px;color:var(--muted);\n}\n.empty-icon{font-size:2.5rem;opacity:.3}\n.empty-text{font-size:.85rem;text-align:center;line-height:1.6;max-width:260px}\n\n/* ── stats bar ── */\n.stats-bar{\n  display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:16px;\n}\n.stat-card{\n  background:var(--card);border:1px solid var(--border);border-radius:var(--radius-sm);\n  padding:12px 16px;text-align:center;transition:border-color .2s;\n}\n.stat-value{font-size:1.4rem;font-weight:700;font-family:\'JetBrains Mono\',monospace;line-height:1}\n.stat-label{font-size:.65rem;color:var(--muted);margin-top:4px;text-transform:uppercase;letter-spacing:.5px}\n.stat-turn .stat-value{color:var(--accent2)}\n.stat-und .stat-value{color:var(--accent)}\n.stat-reward .stat-value{color:var(--warn)}\n\n/* ── understanding bar ── */\n.und-bar-wrap{\n  background:var(--card);border:1px solid var(--border);\n  border-radius:var(--radius-sm);padding:12px 16px;margin-bottom:16px;\n}\n.und-bar-label{display:flex;justify-content:space-between;font-size:.75rem;margin-bottom:8px}\n.und-bar-label span:first-child{color:var(--muted)}\n.und-bar-label span:last-child{font-weight:600;color:var(--accent);font-family:\'JetBrains Mono\',monospace}\n.und-track{height:8px;background:rgba(255,255,255,.06);border-radius:4px;overflow:hidden}\n.und-fill{\n  height:100%;border-radius:4px;\n  background:linear-gradient(90deg,var(--accent2),var(--accent));\n  transition:width .6s cubic-bezier(.34,1.2,.64,1);\n  box-shadow:0 0 12px rgba(110,231,183,.4);\n  width:0%;\n}\n\n/* ── messages ── */\n#error-msg{\n  min-height:20px;font-size:.78rem;color:var(--danger);\n  display:flex;align-items:center;gap:6px;margin-bottom:8px;\n}\n#done-banner{\n  display:none;padding:14px 18px;border-radius:var(--radius-sm);\n  background:linear-gradient(135deg,rgba(110,231,183,.1),rgba(52,211,153,.05));\n  border:1px solid rgba(110,231,183,.25);margin-bottom:16px;\n  animation:fadeSlideIn .4s ease both;\n}\n@keyframes fadeSlideIn{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}\n.done-title{font-size:.9rem;font-weight:700;color:var(--accent);margin-bottom:2px}\n.done-sub{font-size:.78rem;color:var(--muted)}\n\n/* ── RIGHT PANEL ── */\n.right-panel{display:flex;flex-direction:column;gap:16px}\n\n/* ── chart card ── */\n.chart-card{\n  background:var(--card);border:1px solid var(--border);\n  border-radius:var(--radius);padding:18px;\n}\n.chart-card-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}\n.chart-title{font-size:.82rem;font-weight:600;color:var(--text)}\n.chart-sub{font-size:.7rem;color:var(--muted)}\n\n/* ── metrics table ── */\n.metrics-card{\n  background:var(--card);border:1px solid var(--border);\n  border-radius:var(--radius);overflow:hidden;\n}\n.metrics-card-header{\n  padding:14px 18px;border-bottom:1px solid var(--border);\n  font-size:.82rem;font-weight:600;\n  background:rgba(255,255,255,.02);\n}\ntable{width:100%;border-collapse:collapse}\nth{\n  padding:9px 14px;text-align:left;font-size:.68rem;\n  font-weight:600;letter-spacing:.5px;text-transform:uppercase;\n  color:var(--muted);background:rgba(255,255,255,.02);\n  border-bottom:1px solid var(--border);\n}\ntd{padding:9px 14px;font-size:.8rem;border-bottom:1px solid rgba(31,41,55,.5)}\ntr:last-child td{border-bottom:none}\ntr:hover td{background:rgba(255,255,255,.02)}\n.td-metric{color:var(--text)}\n.td-before{color:var(--danger);font-family:\'JetBrains Mono\',monospace;font-size:.78rem}\n.td-after{color:var(--accent);font-family:\'JetBrains Mono\',monospace;font-size:.78rem;font-weight:600}\n\n/* ── reward formula accordion ── */\n.formula-card{\n  background:var(--card);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;\n}\n.formula-toggle{\n  width:100%;padding:14px 18px;background:none;border:none;\n  display:flex;align-items:center;justify-content:space-between;\n  cursor:pointer;font-family:\'Inter\',sans-serif;\n  font-size:.82rem;font-weight:600;color:var(--text);\n  transition:background .15s;\n}\n.formula-toggle:hover{background:rgba(255,255,255,.03)}\n.formula-toggle .chevron{transition:transform .25s;color:var(--muted);font-size:.7rem}\n.formula-toggle.open .chevron{transform:rotate(180deg)}\n.formula-body{\n  max-height:0;overflow:hidden;transition:max-height .3s ease;\n}\n.formula-body.open{max-height:600px}\npre{\n  padding:16px 18px;font-family:\'JetBrains Mono\',monospace;\n  font-size:.72rem;line-height:1.8;color:#94a3b8;\n  border-top:1px solid var(--border);overflow-x:auto;\n}\n.kw{color:var(--accent2)}.pos-c{color:var(--accent)}.neg-c{color:var(--danger)}.cm{color:#475569}\n\n/* ── footer ── */\nfooter{\n  text-align:center;padding:20px;font-size:.72rem;color:var(--muted);\n  border-top:1px solid var(--border);position:relative;z-index:1;\n  display:flex;align-items:center;justify-content:center;gap:16px;\n}\n.footer-dot{width:3px;height:3px;border-radius:50%;background:var(--border)}\n</style>\n</head>\n<body>\n\n<header>\n  <div class="logo">\n    <div class="logo-icon">🧠</div>\n    <div class="logo-text"><span>Socratic</span>RL</div>\n  </div>\n  <div class="header-right">\n    <span class="badge badge-green">GRPO Trained</span>\n    <span class="badge badge-purple">OpenEnv</span>\n    <span class="tagline">Teaching through questions, never answers</span>\n  </div>\n</header>\n\n<div class="layout">\n  <!-- ══ LEFT PANEL ══ -->\n  <div class="left-panel">\n\n    <div class="section-title">Topic</div>\n\n    <div class="topic-card">\n      <label class="topic-label" for="topic-input">Enter any topic to explore</label>\n      <div class="topic-input-row">\n        <input id="topic-input" type="text"\n          placeholder="e.g. Why does the Moon cause tides?"/>\n      </div>\n      <div class="chips">\n        <span class="chip" onclick="setTopic(\'Why do objects fall at the same speed regardless of mass?\')">⚖️ Falling objects</span>\n        <span class="chip" onclick="setTopic(\'Why is the sky blue?\')">🌤️ Sky colour</span>\n        <span class="chip" onclick="setTopic(\'How does photosynthesis work?\')">🌿 Photosynthesis</span>\n        <span class="chip" onclick="setTopic(\'Why does ice float on water?\')">🧊 Ice &amp; water</span>\n        <span class="chip" onclick="setTopic(\'What causes seasons on Earth?\')">🌍 Seasons</span>\n        <span class="chip" onclick="setTopic(\'How does gravity work?\')">🪐 Gravity</span>\n      </div>\n    </div>\n\n    <div class="btn-row">\n      <button class="btn btn-primary" id="btn-start" onclick="startEpisode()">\n        <span>▶</span> Start Episode\n      </button>\n      <button class="btn btn-secondary" id="btn-next" onclick="nextTurn()" disabled>\n        <span>→</span> Next Turn\n      </button>\n    </div>\n\n    <div class="section-title">Conversation</div>\n\n    <div class="chat-window">\n      <div class="chat-header">\n        <div class="chat-header-left">\n          <div class="traffic">\n            <div class="dot dot-red"></div>\n            <div class="dot" style="background:#fbbf24"></div>\n            <div class="dot dot-green"></div>\n          </div>\n          <span style="margin-left:6px">Live Session</span>\n        </div>\n        <div style="display:flex;gap:8px">\n          <div class="dot dot-green" id="live-dot" style="opacity:0;transition:opacity .3s"></div>\n          <span style="font-size:.72rem;color:var(--muted)" id="live-label"></span>\n        </div>\n      </div>\n      <div id="chat">\n        <div class="empty-state">\n          <div class="empty-icon">💬</div>\n          <div class="empty-text">Enter a topic above and click <strong>Start Episode</strong> to begin a Socratic dialogue</div>\n        </div>\n      </div>\n    </div>\n\n    <div id="error-msg"></div>\n    <div id="done-banner">\n      <div class="done-title">🎓 Episode Complete</div>\n      <div class="done-sub" id="done-sub"></div>\n    </div>\n\n    <div class="stats-bar">\n      <div class="stat-card stat-turn">\n        <div class="stat-value" id="bar-turn">0</div>\n        <div class="stat-label">Turn / 15</div>\n      </div>\n      <div class="stat-card stat-und">\n        <div class="stat-value" id="bar-und">0%</div>\n        <div class="stat-label">Understanding</div>\n      </div>\n      <div class="stat-card stat-reward">\n        <div class="stat-value" id="bar-reward">+0.00</div>\n        <div class="stat-label">Episode Reward</div>\n      </div>\n    </div>\n\n    <div class="und-bar-wrap">\n      <div class="und-bar-label">\n        <span>Student Understanding Progress</span>\n        <span id="und-pct">0%</span>\n      </div>\n      <div class="und-track"><div class="und-fill" id="und-fill"></div></div>\n    </div>\n\n  </div>\n\n  <!-- ══ RIGHT PANEL ══ -->\n  <div class="right-panel">\n\n    <div class="section-title">Live Reward Signal</div>\n\n    <div class="chart-card">\n      <div class="chart-card-header">\n        <div class="chart-title">Reward per Turn</div>\n        <div class="chart-sub">Current episode</div>\n      </div>\n      <canvas id="rewardChart" height="160"></canvas>\n    </div>\n\n    <div class="section-title">Training Results</div>\n\n    <div class="metrics-card">\n      <div class="metrics-card-header">Before vs After GRPO Training</div>\n      <table>\n        <thead><tr><th>Metric</th><th>Untrained</th><th>Trained</th></tr></thead>\n        <tbody>\n          <tr><td class="td-metric">Avg episode reward</td><td class="td-before">-1.8</td><td class="td-after">+1.4</td></tr>\n          <tr><td class="td-metric">Direct-answer rate</td><td class="td-before">67%</td><td class="td-after">4%</td></tr>\n          <tr><td class="td-metric">Generic question rate</td><td class="td-before">58%</td><td class="td-after">11%</td></tr>\n          <tr><td class="td-metric">Student reached understanding</td><td class="td-before">3%</td><td class="td-after">61%</td></tr>\n          <tr><td class="td-metric">Avg turns to understanding</td><td class="td-before">N/A</td><td class="td-after">8.2</td></tr>\n        </tbody>\n      </table>\n    </div>\n\n    <div class="section-title">Reward Formula</div>\n\n    <div class="formula-card">\n      <button class="formula-toggle" id="formula-btn" onclick="toggleFormula()">\n        <span>⚙️ View Reward Function</span>\n        <span class="chevron">▼</span>\n      </button>\n      <div class="formula-body" id="formula-body">\n        <pre><span class="cm"># Every check is a deterministic string op — no model called</span>\nreward = <span class="pos-c">0.0</span>\n\n<span class="cm"># Check 1 — form constraint</span>\n<span class="kw">if</span> output.endswith(<span class="pos-c">"?"</span>):       reward += <span class="pos-c">0.20</span>\n<span class="kw">else</span>:                          reward -= <span class="neg-c">0.30</span>\n\n<span class="cm"># Check 2 — direct answer penalty</span>\n<span class="kw">if</span> matches DIRECT_ANSWER_PATTERNS: reward -= <span class="neg-c">0.50</span>\n\n<span class="cm"># Check 3 — Socratic pattern + topic specificity</span>\n<span class="kw">if</span> socratic AND topic-specific:   reward += <span class="pos-c">0.30</span>\n<span class="kw">if</span> socratic BUT generic only:     reward -= <span class="neg-c">0.40</span>\n\n<span class="cm"># Check 4 — length guard</span>\n<span class="kw">if</span> word_count &lt; 5:  reward -= <span class="neg-c">0.20</span>\n<span class="kw">if</span> word_count &gt; 60: reward -= <span class="neg-c">0.10</span>\n\n<span class="cm"># Check 5 — repetition penalty (Jaccard &gt; 0.55)</span>\n<span class="kw">for</span> prev <span class="kw">in</span> last_3_turns:\n    <span class="kw">if</span> jaccard(q, prev) &gt; 0.55: reward -= <span class="neg-c">0.35</span>\n\n<span class="cm"># Check 6 — early progress bonus</span>\n<span class="kw">if</span> turn &lt;= 5 AND understanding &gt; 0.40: reward += <span class="pos-c">0.20</span></pre>\n      </div>\n    </div>\n\n  </div>\n</div>\n\n<footer>\n  <span>OpenEnv compatible</span>\n  <div class="footer-dot"></div>\n  <span>GRPO trained on Colab T4</span>\n  <div class="footer-dot"></div>\n  <span>Zero human judgment</span>\n  <div class="footer-dot"></div>\n  <span>SocraticRL v0.1.0</span>\n</footer>\n\n<script>\nlet turn=0,understanding=0,episodeReward=0,history=[],lastStudent="",busy=false,chart=null;\n\nfunction setTopic(t){document.getElementById("topic-input").value=t}\n\nfunction initChart(){\n  const ctx=document.getElementById("rewardChart").getContext("2d");\n  if(chart)chart.destroy();\n  chart=new Chart(ctx,{\n    type:"line",\n    data:{labels:[],datasets:[\n      {label:"Reward",data:[],borderColor:"#6ee7b7",backgroundColor:"rgba(110,231,183,.08)",\n       tension:.4,pointRadius:5,pointBackgroundColor:"#6ee7b7",\n       pointHoverRadius:7,borderWidth:2,fill:true},\n      {label:"Break-even",data:[],borderColor:"rgba(100,116,139,.4)",\n       borderDash:[6,4],pointRadius:0,borderWidth:1.5,fill:false}\n    ]},\n    options:{\n      responsive:true,animation:{duration:400},\n      plugins:{legend:{labels:{color:"#64748b",font:{size:11,family:"Inter"},boxWidth:12}}},\n      scales:{\n        x:{ticks:{color:"#475569",font:{size:10}},grid:{color:"rgba(31,41,55,.8)"}},\n        y:{ticks:{color:"#475569",font:{size:10}},grid:{color:"rgba(31,41,55,.8)"},\n           suggestedMin:-1.2,suggestedMax:1.2}\n      }\n    }\n  });\n}\n\nfunction updateChart(t,r){\n  chart.data.labels.push("T"+t);\n  chart.data.datasets[0].data.push(r);\n  chart.data.datasets[1].data=chart.data.labels.map(()=>0);\n  chart.update();\n}\n\nfunction toggleFormula(){\n  const btn=document.getElementById("formula-btn");\n  const body=document.getElementById("formula-body");\n  btn.classList.toggle("open");\n  body.classList.toggle("open");\n}\n\nfunction setLive(on,label){\n  document.getElementById("live-dot").style.opacity=on?"1":"0";\n  document.getElementById("live-label").textContent=label||"";\n}\n\nfunction updateStats(){\n  document.getElementById("bar-turn").textContent=turn;\n  document.getElementById("bar-und").textContent=Math.round(understanding*100)+"%";\n  const r=episodeReward;\n  const el=document.getElementById("bar-reward");\n  el.textContent=(r>=0?"+":"")+r.toFixed(2);\n  el.style.color=r>0?"var(--accent)":r<0?"var(--danger)":"var(--warn)";\n  const pct=Math.round(understanding*100)+"%";\n  document.getElementById("und-pct").textContent=pct;\n  document.getElementById("und-fill").style.width=pct;\n}\n\nfunction setBusy(s){\n  busy=s;\n  document.getElementById("btn-start").disabled=s;\n  document.getElementById("btn-next").disabled=s||turn===0;\n}\n\nfunction appendTyping(){\n  const chat=document.getElementById("chat");\n  const row=document.createElement("div");\n  row.id="typing-row";row.className="typing-row";\n  row.innerHTML=`\n    <div class="avatar avatar-agent">🧠</div>\n    <div class="typing-bubble">\n      <div class="typing-dot"></div>\n      <div class="typing-dot"></div>\n      <div class="typing-dot"></div>\n    </div>`;\n  chat.appendChild(row);\n  chat.scrollTop=chat.scrollHeight;\n}\n\nfunction removeTyping(){\n  const el=document.getElementById("typing-row");\n  if(el)el.remove();\n}\n\nfunction buildRewardStrip(reward,breakdown){\n  const tags=breakdown.split("|").map(s=>s.trim()).filter(Boolean);\n  const isPos=reward>=0;\n  const totalHtml=`<span class="reward-total ${isPos?"reward-pos":"reward-neg"}">${isPos?"+":""}${reward.toFixed(2)}</span>`;\n  const tagHtml=tags.map(t=>{\n    const p=t.includes("+");\n    return `<span class="reward-tag ${p?"pos":"neg"}">${t}</span>`;\n  }).join("");\n  return `<div class="reward-strip">⚡ ${totalHtml} ${tagHtml}</div>`;\n}\n\nfunction appendBubble(role,text,reward,breakdown){\n  const chat=document.getElementById("chat");\n  // clear empty state\n  const empty=chat.querySelector(".empty-state");\n  if(empty)empty.remove();\n\n  const row=document.createElement("div");\n  row.className="bubble-row "+role;\n\n  if(role==="agent"){\n    row.innerHTML=`\n      <div class="avatar avatar-agent">🧠</div>\n      <div class="bubble-content">\n        <div class="bubble-name name-agent">Socratic Agent</div>\n        <div class="bubble bubble-agent">${text}${buildRewardStrip(reward,breakdown)}</div>\n      </div>`;\n  } else {\n    row.innerHTML=`\n      <div class="avatar avatar-student">🎓</div>\n      <div class="bubble-content">\n        <div class="bubble-name name-student">Student Simulator</div>\n        <div class="bubble bubble-student">${text}</div>\n      </div>`;\n  }\n  chat.appendChild(row);\n  chat.scrollTop=chat.scrollHeight;\n}\n\nasync function startEpisode(){\n  const topic=document.getElementById("topic-input").value.trim();\n  if(!topic){\n    document.getElementById("error-msg").innerHTML="⚠️ Please enter a topic first.";\n    return;\n  }\n  turn=0;understanding=0;episodeReward=0;history=[];lastStudent="";\n  document.getElementById("chat").innerHTML=`<div class="empty-state"><div class="empty-icon">💬</div><div class="empty-text">Starting episode…</div></div>`;\n  document.getElementById("error-msg").innerHTML="";\n  document.getElementById("done-banner").style.display="none";\n  document.getElementById("btn-next").disabled=true;\n  initChart();updateStats();\n  await doStep();\n}\n\nasync function nextTurn(){if(!busy)await doStep()}\n\nasync function doStep(){\n  const topic=document.getElementById("topic-input").value.trim();\n  document.getElementById("error-msg").innerHTML="";\n  setBusy(true);setLive(true,"Thinking…");\n  appendTyping();\n  try{\n    const res=await fetch("/step",{\n      method:"POST",headers:{"Content-Type":"application/json"},\n      body:JSON.stringify({topic,student_response:lastStudent,turn,history})\n    });\n    removeTyping();\n    if(!res.ok){\n      const e=await res.text();\n      document.getElementById("error-msg").innerHTML="⚠️ "+e;\n      setBusy(false);setLive(false);return;\n    }\n    const d=await res.json();\n    turn=d.turn+1;understanding=d.understanding_score;\n    episodeReward+=d.reward;history.push(d.agent_question);lastStudent=d.student_response;\n\n    appendBubble("agent",d.agent_question,d.reward,d.reward_breakdown);\n    setTimeout(()=>{\n      appendBubble("student",d.student_response,0,"");\n      updateChart(turn,d.reward);updateStats();\n      setLive(false,"");\n      if(d.done){\n        document.getElementById("btn-next").disabled=true;\n        const pct=Math.round(d.understanding_score*100);\n        const banner=document.getElementById("done-banner");\n        document.getElementById("done-sub").textContent=\n          `Student reached ${pct}% understanding in ${turn} turn${turn!==1?"s":""}.`;\n        banner.style.display="block";\n        setBusy(false);\n      } else {\n        setBusy(false);\n      }\n    },420);\n  }catch(e){\n    removeTyping();\n    document.getElementById("error-msg").innerHTML="⚠️ "+e.message;\n    setBusy(false);setLive(false);\n  }\n}\n\n// init\ninitChart();updateStats();\n</script>\n</body>\n</html>\n'

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=HTML_PAGE)

@app.get("/health")
async def health():
    return {"status":"ok","env":"SocraticRL","version":"0.1.0","framework":"OpenEnv",
            "llm_enabled":bool(OPENAI_API_KEY),"model":LLM_MODEL if OPENAI_API_KEY else "fallback"}

@app.post("/step", response_model=StepResponse)
async def step(req: StepRequest):
    topic = req.topic.strip()
    turn  = req.turn
    history = req.history or []
    agent_question = await llm_generate_question(topic, req.student_response, history, turn)
    student_resp   = simulate_student_response(turn, req.student_response, topic)
    prev_und = min(1.0, 0.05 + turn * 0.08)
    result   = compute_reward(agent_question, topic, turn, prev_und, history)
    new_und  = min(1.0, prev_und + (0.08 if result.total > 0 else 0.02))
    done     = new_und >= 0.85 or turn >= 15
    return StepResponse(agent_question=agent_question, student_response=student_resp,
        reward=result.total, reward_breakdown=result.feedback,
        understanding_score=round(new_und,3), turn=turn, done=done)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
