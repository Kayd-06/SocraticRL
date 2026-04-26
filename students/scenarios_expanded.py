"""
Expanded training scenarios for SocraticRL.
50+ high-quality scenarios across physics, math, logic, and more.
Each with topic, misconception, correct answer, and persona.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Scenario:
    topic: str
    misconception: str
    correct_answer: str
    persona: str


# ═══════════════════════════════════════════════════════════════
# PHYSICS SCENARIOS (15)
# ═══════════════════════════════════════════════════════════════

PHYSICS_SCENARIOS = [
    Scenario(
        topic="Falling objects and gravity",
        misconception="Heavier objects fall faster than lighter objects.",
        correct_answer="All objects fall at the same acceleration (9.8 m/s²) regardless of mass, ignoring air resistance.",
        persona="High school student, confused about Galileo's experiment"
    ),
    Scenario(
        topic="Newton's First Law",
        misconception="Objects need a constant force to keep moving.",
        correct_answer="Objects in motion stay in motion without any force (inertia). Force is only needed to change motion.",
        persona="Physics student, thinks force = motion"
    ),
    Scenario(
        topic="Friction and motion",
        misconception="Friction always stops objects from moving.",
        correct_answer="Friction opposes motion but doesn't always stop it. Static friction can enable motion (like walking).",
        persona="Confused about why we need friction"
    ),
    Scenario(
        topic="Heat and temperature",
        misconception="Heat and temperature are the same thing.",
        correct_answer="Temperature is molecular kinetic energy. Heat is energy transfer between objects.",
        persona="Middle school student mixing up concepts"
    ),
    Scenario(
        topic="Light and shadows",
        misconception="Shadows are made of darkness.",
        correct_answer="Shadows are the absence of light. They form when light is blocked by an object.",
        persona="Elementary student with intuitive misconception"
    ),
    Scenario(
        topic="Buoyancy and floating",
        misconception="Heavy objects always sink; light objects always float.",
        correct_answer="Objects float if their density is less than the fluid. A heavy steel ship floats because its average density is low.",
        persona="Student thinking about density incorrectly"
    ),
    Scenario(
        topic="Velocity and speed",
        misconception="Velocity and speed are the same thing.",
        correct_answer="Speed is distance/time (scalar). Velocity is displacement/time (vector with direction).",
        persona="Physics student confusing scalar and vector"
    ),
    Scenario(
        topic="Momentum conservation",
        misconception="Momentum is lost when objects collide.",
        correct_answer="Total momentum is conserved in isolated systems. It's transferred between objects, not lost.",
        persona="Student watching collision experiments"
    ),
    Scenario(
        topic="Electricity and circuits",
        misconception="Electricity gets used up as it flows through a circuit.",
        correct_answer="Charge flows in a circuit. Energy is transferred, but charge is conserved.",
        persona="Electronics beginner"
    ),
    Scenario(
        topic="Magnetism",
        misconception="Only magnets attract metal. All metal is magnetic.",
        correct_answer="Only ferromagnetic metals (iron, cobalt, nickel) are attracted to magnets. Most metals are not.",
        persona="Student generalizing from iron"
    ),
    Scenario(
        topic="Sound waves",
        misconception="Sound travels faster in air than in water.",
        correct_answer="Sound travels faster in denser media. It travels ~4x faster in water than air.",
        persona="Intuitive guess based on air being 'thinner'"
    ),
    Scenario(
        topic="Pressure",
        misconception="Pressure is the same as force.",
        correct_answer="Pressure = Force / Area. Same force on smaller area = higher pressure.",
        persona="Student confusing related concepts"
    ),
    Scenario(
        topic="Energy conservation",
        misconception="Energy can be created or destroyed.",
        correct_answer="Energy is conserved. It transforms between forms (kinetic, potential, heat, etc.) but total is constant.",
        persona="Student learning thermodynamics"
    ),
    Scenario(
        topic="Planetary orbits",
        misconception="Planets orbit because they're falling toward the sun.",
        correct_answer="Planets orbit because gravity provides centripetal force. They're in continuous free fall around the sun.",
        persona="Astronomy student"
    ),
    Scenario(
        topic="Refraction of light",
        misconception="Light bends because the medium is thicker.",
        correct_answer="Light bends because it travels at different speeds in different media. Speed change causes direction change.",
        persona="Optics student"
    ),
]

# ═══════════════════════════════════════════════════════════════
# MATHEMATICS SCENARIOS (15)
# ═══════════════════════════════════════════════════════════════

MATH_SCENARIOS = [
    Scenario(
        topic="Negative numbers",
        misconception="Negative times negative equals negative.",
        correct_answer="Negative times negative equals positive. (-2) × (-3) = +6.",
        persona="Middle school student learning integers"
    ),
    Scenario(
        topic="Division by zero",
        misconception="Any number divided by zero equals zero.",
        correct_answer="Division by zero is undefined. You cannot divide by zero.",
        persona="Student trying to apply division rules"
    ),
    Scenario(
        topic="Fractions",
        misconception="1/2 + 1/3 = 2/5 (just add numerators and denominators).",
        correct_answer="1/2 + 1/3 = 3/6 + 2/6 = 5/6. You need a common denominator.",
        persona="Elementary student learning fractions"
    ),
    Scenario(
        topic="Exponents",
        misconception="2³ means 2 × 3 = 6.",
        correct_answer="2³ means 2 × 2 × 2 = 8. The exponent tells you how many times to multiply.",
        persona="Student confusing exponents with multiplication"
    ),
    Scenario(
        topic="Square roots",
        misconception="√9 = ±3 always.",
        correct_answer="√9 = 3 (principal root). The equation x² = 9 has solutions ±3, but √9 specifically means +3.",
        persona="Algebra student"
    ),
    Scenario(
        topic="Order of operations",
        misconception="2 + 3 × 4 = 20 (left to right).",
        correct_answer="2 + 3 × 4 = 2 + 12 = 14. Multiplication before addition (PEMDAS).",
        persona="Student not following order of operations"
    ),
    Scenario(
        topic="Probability",
        misconception="If a coin landed heads 5 times, it's more likely to land tails next.",
        correct_answer="Each flip is independent. Probability of heads is always 50%, regardless of history.",
        persona="Student with gambler's fallacy"
    ),
    Scenario(
        topic="Averages",
        misconception="The average of 1, 2, 3, 100 is around 25.",
        correct_answer="The average is (1+2+3+100)/4 = 26.5. One outlier can skew the mean.",
        persona="Student not calculating correctly"
    ),
    Scenario(
        topic="Percentages",
        misconception="50% of 200 is 50.",
        correct_answer="50% of 200 is 100. Percentage means 'per hundred'.",
        persona="Student confusing percentage with the number"
    ),
    Scenario(
        topic="Algebra variables",
        misconception="In 2x, the x is just a label, not a number.",
        correct_answer="x is an unknown number. 2x means 2 times that number.",
        persona="Student new to algebra"
    ),
    Scenario(
        topic="Linear equations",
        misconception="x + 5 = 10 means x = 5 + 10 = 15.",
        correct_answer="x + 5 = 10 means x = 10 - 5 = 5. Subtract 5 from both sides.",
        persona="Student not isolating variables"
    ),
    Scenario(
        topic="Geometry angles",
        misconception="All angles in a triangle add up to 180°, so each angle is 60°.",
        correct_answer="Angles add to 180°, but each angle can be different. Only equilateral triangles have 60° angles.",
        persona="Geometry student generalizing"
    ),
    Scenario(
        topic="Area vs perimeter",
        misconception="A shape with larger perimeter always has larger area.",
        correct_answer="Perimeter and area are independent. A long thin rectangle can have large perimeter but small area.",
        persona="Student confusing measurements"
    ),
    Scenario(
        topic="Ratios",
        misconception="A ratio of 2:3 means 2 out of 3.",
        correct_answer="A ratio of 2:3 means for every 2 of one thing, there are 3 of another. Total is 5 parts.",
        persona="Student misunderstanding ratios"
    ),
    Scenario(
        topic="Logarithms",
        misconception="log(10) = 1 means 10 = 1.",
        correct_answer="log(10) = 1 means 10¹ = 10. Logarithm is the exponent.",
        persona="Student learning logarithms"
    ),
]

# ═══════════════════════════════════════════════════════════════
# BIOLOGY SCENARIOS (10)
# ═══════════════════════════════════════════════════════════════

BIOLOGY_SCENARIOS = [
    Scenario(
        topic="Photosynthesis",
        misconception="Plants eat soil to grow.",
        correct_answer="Plants use sunlight, water, and CO₂ to make glucose. Soil provides minerals, not food.",
        persona="Elementary student"
    ),
    Scenario(
        topic="Evolution",
        misconception="Evolution means animals are trying to adapt. Giraffes stretched their necks to reach leaves.",
        correct_answer="Evolution is natural selection. Giraffes with longer necks survived better and reproduced more.",
        persona="Student misunderstanding mechanism"
    ),
    Scenario(
        topic="DNA",
        misconception="DNA is only in the nucleus.",
        correct_answer="DNA is in the nucleus (nuclear DNA) and in mitochondria and chloroplasts (mtDNA).",
        persona="Biology student"
    ),
    Scenario(
        topic="Cells",
        misconception="All cells have a nucleus.",
        correct_answer="Prokaryotic cells (bacteria) have no nucleus. Only eukaryotic cells have nuclei.",
        persona="Cell biology student"
    ),
    Scenario(
        topic="Digestion",
        misconception="Food goes directly into the bloodstream after eating.",
        correct_answer="Food is broken down in the digestive system. Nutrients are absorbed into the bloodstream.",
        persona="Health class student"
    ),
    Scenario(
        topic="Immunity",
        misconception="Antibodies attack viruses directly.",
        correct_answer="Antibodies mark viruses for destruction. White blood cells do the actual attacking.",
        persona="Immunology student"
    ),
    Scenario(
        topic="Genetics",
        misconception="If both parents have brown eyes, all children have brown eyes.",
        correct_answer="Brown is dominant, but both parents could carry recessive genes. Children could have blue eyes.",
        persona="Genetics student"
    ),
    Scenario(
        topic="Respiration",
        misconception="Respiration is just breathing.",
        correct_answer="Breathing is gas exchange. Respiration is cellular process that uses oxygen to make ATP.",
        persona="Biology student confusing terms"
    ),
    Scenario(
        topic="Ecosystems",
        misconception="Decomposers are bad for ecosystems.",
        correct_answer="Decomposers recycle nutrients. Without them, dead matter would accumulate.",
        persona="Ecology student"
    ),
    Scenario(
        topic="Homeostasis",
        misconception="Body temperature is always exactly 37°C.",
        correct_answer="Body temperature is regulated around 37°C but varies slightly. Homeostasis is dynamic balance.",
        persona="Physiology student"
    ),
]

# ═══════════════════════════════════════════════════════════════
# CHEMISTRY SCENARIOS (10)
# ═══════════════════════════════════════════════════════════════

CHEMISTRY_SCENARIOS = [
    Scenario(
        topic="Atoms and molecules",
        misconception="Atoms are the smallest things in the universe.",
        correct_answer="Atoms contain protons, neutrons, and electrons. Quarks are smaller.",
        persona="Chemistry student"
    ),
    Scenario(
        topic="Chemical reactions",
        misconception="When things burn, they disappear.",
        correct_answer="Burning is oxidation. Matter is conserved. It becomes ash and gases.",
        persona="Student watching combustion"
    ),
    Scenario(
        topic="Acids and bases",
        misconception="All acids are dangerous and burn.",
        correct_answer="Acids have pH < 7. Some are weak and safe (vinegar). Danger depends on concentration.",
        persona="Chemistry student"
    ),
    Scenario(
        topic="Ionic bonds",
        misconception="Ionic bonds are stronger than covalent bonds.",
        correct_answer="Covalent bonds are typically stronger. Ionic bonds are strong but different type.",
        persona="Chemistry student"
    ),
    Scenario(
        topic="Solubility",
        misconception="Salt dissolves in water but sugar doesn't.",
        correct_answer="Both salt and sugar dissolve in water. Solubility depends on polarity and temperature.",
        persona="Student observing solutions"
    ),
    Scenario(
        topic="Oxidation states",
        misconception="Oxidation means adding oxygen.",
        correct_answer="Oxidation is loss of electrons. It can happen without oxygen.",
        persona="Chemistry student learning redox"
    ),
    Scenario(
        topic="Catalysts",
        misconception="Catalysts are used up in reactions.",
        correct_answer="Catalysts speed up reactions but are regenerated. They're not consumed.",
        persona="Kinetics student"
    ),
    Scenario(
        topic="Equilibrium",
        misconception="At equilibrium, the reaction stops.",
        correct_answer="At equilibrium, forward and reverse reactions occur at equal rates. It's dynamic.",
        persona="Chemistry student"
    ),
    Scenario(
        topic="Molar mass",
        misconception="Molar mass is the same as atomic mass.",
        correct_answer="Atomic mass is for one atom (amu). Molar mass is for one mole (g/mol).",
        persona="Chemistry student"
    ),
    Scenario(
        topic="Electron shells",
        misconception="Electrons orbit the nucleus like planets around the sun.",
        correct_answer="Electrons exist in probability clouds (orbitals), not fixed orbits.",
        persona="Quantum chemistry student"
    ),
]

# ═══════════════════════════════════════════════════════════════
# LOGIC & REASONING SCENARIOS (5)
# ═══════════════════════════════════════════════════════════════

LOGIC_SCENARIOS = [
    Scenario(
        topic="Correlation vs causation",
        misconception="Ice cream sales increase in summer, so ice cream causes summer.",
        correct_answer="Correlation ≠ causation. Both are caused by warm weather.",
        persona="Student learning critical thinking"
    ),
    Scenario(
        topic="Logical fallacies",
        misconception="If most people believe something, it must be true.",
        correct_answer="Appeal to majority is a fallacy. Truth is independent of popularity.",
        persona="Philosophy student"
    ),
    Scenario(
        topic="Probability and statistics",
        misconception="A study with 100 people is always more reliable than one with 1000.",
        correct_answer="Sample size matters, but methodology matters more. 1000 is generally better.",
        persona="Statistics student"
    ),
    Scenario(
        topic="Deductive reasoning",
        misconception="All birds can fly. Penguins are birds. Therefore, penguins can fly.",
        correct_answer="The first premise is false. Not all birds can fly. Deduction requires true premises.",
        persona="Logic student"
    ),
    Scenario(
        topic="Inductive reasoning",
        misconception="I've seen 10 white swans, so all swans are white.",
        correct_answer="Induction is probabilistic. One black swan disproves the generalization.",
        persona="Student learning induction"
    ),
]

# ═══════════════════════════════════════════════════════════════
# COMBINE ALL SCENARIOS
# ═══════════════════════════════════════════════════════════════

ALL_EXPANDED_SCENARIOS = (
    PHYSICS_SCENARIOS +
    MATH_SCENARIOS +
    BIOLOGY_SCENARIOS +
    CHEMISTRY_SCENARIOS +
    LOGIC_SCENARIOS
)

# For training: use all 50 scenarios
TRAINING_SCENARIOS_EXPANDED = ALL_EXPANDED_SCENARIOS

# For evaluation: use a subset (held-out)
EVAL_SCENARIOS_EXPANDED = [
    Scenario(
        topic="Momentum",
        misconception="A heavy truck moving slowly has more momentum than a light car moving fast.",
        correct_answer="Momentum = mass × velocity. It depends on both. The fast car could have more.",
        persona="Physics student"
    ),
    Scenario(
        topic="Fractions comparison",
        misconception="3/4 is less than 4/5 because 3 < 4.",
        correct_answer="3/4 = 0.75 and 4/5 = 0.8. Compare decimals or use common denominator.",
        persona="Math student"
    ),
    Scenario(
        topic="Photosynthesis location",
        misconception="Photosynthesis happens in the roots of plants.",
        correct_answer="Photosynthesis happens in leaves where there's sunlight. Roots absorb water.",
        persona="Biology student"
    ),
]

if __name__ == "__main__":
    print(f"Total expanded scenarios: {len(ALL_EXPANDED_SCENARIOS)}")
    print(f"Training scenarios: {len(TRAINING_SCENARIOS_EXPANDED)}")
    print(f"Eval scenarios: {len(EVAL_SCENARIOS_EXPANDED)}")
    print("\nSample scenario:")
    print(ALL_EXPANDED_SCENARIOS[0])
