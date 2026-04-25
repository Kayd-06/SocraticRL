"""
TRAINING_SCENARIOS  — used by GRPO trainer only. Safe to expand later.
EVAL_SCENARIOS      — HELD-OUT. Never passed to trainer. Used only in eval.py.
SCENARIOS           — alias for TRAINING_SCENARIOS, used by environment.py.
"""

from students.profiles import StudentProfile

TRAINING_SCENARIOS = [
    StudentProfile(
        name="ConfusedAboutGravity",
        topic="Why do heavy and light objects fall at the same speed?",
        target_understanding="All objects fall at the same rate regardless of mass because gravity accelerates all masses equally (ignoring air resistance). Galileo proved this.",
        misconception="Heavier objects fall faster because gravity pulls them more.",
        persona="A high-school student who trusts gut intuition over physics. Says 'but that doesn't make sense' often. Gets excited when something clicks.",
        progress_keywords=["acceleration", "same rate", "air resistance", "galileo", "mass doesn't matter", "vacuum"],
        correct_answer="All objects fall at the same rate regardless of mass because gravity gives the same acceleration to everything.",
        difficulty="easy",
    ),
    StudentProfile(
        name="CorrelationCausation",
        topic="Why does correlation not imply causation?",
        target_understanding="Two variables moving together does not mean one causes the other. A hidden third variable or coincidence could explain it.",
        misconception="If ice cream sales and drowning rates both increase in summer, ice cream causes drowning.",
        persona="An overconfident data-science student who trusts numbers completely. Uses phrases like 'the data clearly shows'.",
        progress_keywords=["confounding", "third variable", "coincidence", "spurious", "causation", "summer heat"],
        correct_answer="Correlation shows two things move together but cannot prove one causes the other — a hidden variable like summer heat explains both.",
        difficulty="medium",
    ),
    StudentProfile(
        name="RecursionFear",
        topic="How does recursion work in programming?",
        target_understanding="A function that calls itself with a simpler version of the problem until it hits a base case that stops the recursion.",
        misconception="Recursion causes infinite loops and is just a complicated way to do what loops do.",
        persona="A CS student who learned loops first and distrusts recursion. Skeptical but curious. Asks 'why not just use a for loop?'",
        progress_keywords=["base case", "simpler problem", "call stack", "terminates", "fibonacci", "factorial"],
        correct_answer="Recursion works by breaking a problem into smaller versions of itself until reaching a base case that returns directly.",
        difficulty="medium",
    ),
    StudentProfile(
        name="EvolutionGoal",
        topic="Does evolution have a direction or goal?",
        target_understanding="Evolution has no goal. Natural selection is blind — organisms that happen to survive and reproduce pass on genes, with no foresight toward complexity.",
        misconception="Evolution is working toward making species more complex and perfect over time.",
        persona="A curious biology student who watches nature documentaries. Impressed by complexity in nature and assumes it must be intentional.",
        progress_keywords=["natural selection", "blind", "random", "survive", "reproduce", "no goal", "environment", "fittest"],
        correct_answer="Evolution has no direction — natural selection keeps whatever helps organisms survive and reproduce in their current environment.",
        difficulty="medium",
    ),
    StudentProfile(
        name="BigOConfusion",
        topic="What does Big-O notation actually measure?",
        target_understanding="Big-O describes how an algorithm's runtime scales as input grows — it is about growth rate, not actual time in seconds.",
        misconception="O(n²) means the algorithm takes n² seconds to run.",
        persona="A junior developer who learned Big-O by memorisation. Confident but mixing up growth rate with wall-clock time.",
        progress_keywords=["growth rate", "scales", "input size", "asymptotic", "not seconds", "relative", "n grows"],
        correct_answer="Big-O measures how runtime grows relative to input size — O(n²) means doubling input roughly quadruples work, not that it takes n² seconds.",
        difficulty="medium",
    ),
]

EVAL_SCENARIOS = [
    StudentProfile(
        name="PValueMisunderstanding",
        topic="What does a p-value actually mean?",
        target_understanding="A p-value is the probability of seeing results at least as extreme as observed, assuming the null hypothesis is true. It is NOT the probability that your hypothesis is correct.",
        misconception="A p-value of 0.05 means there is a 95% chance my hypothesis is correct.",
        persona="A psychology student who just took introductory statistics. Eager but muddled. Asks follow-up questions about what 'null hypothesis' means.",
        progress_keywords=["null hypothesis", "assuming", "probability", "extreme", "not the probability of being correct", "type I error"],
        correct_answer="P-value is the probability of getting results this extreme IF the null hypothesis were true — not the probability your hypothesis is right.",
        difficulty="hard",
    ),
    StudentProfile(
        name="MontyHallDenial",
        topic="Should you switch doors in the Monty Hall problem?",
        target_understanding="Always switch. Switching wins 2/3 of the time. Staying wins only 1/3. The host's action of revealing a goat gives you new information.",
        misconception="After one door is revealed it's 50/50 — switching doesn't help.",
        persona="A stubborn but smart student convinced by intuition. Says '50/50 is obvious' repeatedly until the right question cracks it open.",
        progress_keywords=["2/3", "new information", "conditional probability", "host knows", "always switch", "probability changes"],
        correct_answer="Always switch — you win 2/3 of the time because the host's action changes the probability distribution.",
        difficulty="hard",
    ),
    StudentProfile(
        name="AntibioticResistance",
        topic="How does antibiotic resistance develop?",
        target_understanding="Antibiotic resistance evolves in bacterial populations through natural selection. Antibiotics don't cause mutations — they kill susceptible bacteria, leaving resistant ones to multiply.",
        misconception="Bacteria become resistant because the antibiotic teaches them to fight back.",
        persona="A nursing student who understands antibiotics clinically but not evolutionarily. Treats 'teaching' as a reasonable metaphor.",
        progress_keywords=["natural selection", "mutation", "population", "susceptible", "survive", "reproduce", "random"],
        correct_answer="Resistance arises through natural selection: random mutations exist before antibiotic exposure; the drug kills susceptible bacteria and resistant ones survive to multiply.",
        difficulty="hard",
    ),
]

SCENARIOS = TRAINING_SCENARIOS  # alias used by environment.py
