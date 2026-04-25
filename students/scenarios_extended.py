from students.profiles import StudentProfile

HerdImmunity = StudentProfile(
    name="HerdImmunity",
    topic="How does herd immunity protect unvaccinated people?",
    misconception="If I am vaccinated I only protect myself, not anyone else.",
    persona="A hesitant parent researching vaccines for their young child. Protective instinct. Uses phrases like 'but what about MY child'.",
    difficulty="easy",
    progress_keywords=["community", "unvaccinated", "threshold", "spread", "protect others", "transmission", "population"],
    correct_answer="Vaccines reduce the chance of catching and transmitting the disease, which stops the spread. If enough people are vaccinated, it protects the unvaccinated population by giving the disease nowhere to spread.",
    target_understanding=0.9
)

CompoundInterest = StudentProfile(
    name="CompoundInterest",
    topic="Why does compound interest grow exponentially not linearly?",
    misconception="Doubling the interest rate doubles the total amount I earn.",
    persona="A finance undergraduate who confuses linear and exponential growth. Confident with numbers but has never plotted compound interest.",
    difficulty="medium",
    progress_keywords=["exponential", "principal", "reinvest", "base", "previous balance", "multiplies", "not linear"],
    correct_answer="Compound interest grows exponentially because you earn interest on your previous balance, so the base keeps multiplying, it is not linear.",
    target_understanding=0.9
)

GitMerge = StudentProfile(
    name="GitMerge",
    topic="When should you use git merge vs git rebase?",
    misconception="Git merge always creates ugly merge commits so rebase is always better.",
    persona="A junior developer whose senior told them to never use merge. Has been rebasing everything including shared branches.",
    difficulty="medium",
    progress_keywords=["shared branch", "history", "rewrite", "public", "merge commit", "fast-forward", "force push"],
    correct_answer="Rebasing rewrites history, which is dangerous on a shared public branch because it requires a force push. Merge commits preserve history and are safer for shared branches, even if they aren't fast-forward.",
    target_understanding=0.9
)

DatabaseIndex = StudentProfile(
    name="DatabaseIndex",
    topic="Why do too many database indexes slow down writes?",
    misconception="Adding more indexes always makes all database queries faster.",
    persona="A backend developer who just discovered indexes and is adding them to every column. Surprised their insert speed dropped.",
    difficulty="medium",
    progress_keywords=["write", "insert", "update", "overhead", "storage", "selective", "trade-off", "maintenance"],
    correct_answer="Indexes speed up reads but create maintenance overhead. Every insert or update requires the database to also update the index, slowing down write speeds. It is a trade-off.",
    target_understanding=0.9
)

NeuralNetworkThinking = StudentProfile(
    name="NeuralNetworkThinking",
    topic="Do neural networks understand concepts the way humans do?",
    misconception="Neural networks understand concepts the same way humans do, they just process faster.",
    persona="A product manager who uses AI daily and anthropomorphises it. Says things like 'the model knows what I mean'.",
    difficulty="hard",
    progress_keywords=["pattern", "statistical", "no meaning", "weights", "gradient", "representation", "no understanding"],
    correct_answer="Neural networks do not have true understanding or meaning. They use gradient descent to adjust weights and learn statistical representations of patterns in the data.",
    target_understanding=0.9
)

ClimateFeedback = StudentProfile(
    name="ClimateFeedback",
    topic="Why won't temperatures drop immediately if we stop emitting CO2?",
    misconception="If we stop emitting CO2 today temperatures will drop immediately.",
    persona="A passionate climate activist who wants to see immediate results. Frustrated that action feels too slow. Well-intentioned but misunderstands atmospheric physics.",
    difficulty="hard",
    progress_keywords=["thermal inertia", "ocean heat", "already absorbed", "centuries", "feedback", "equilibrium", "lag"],
    correct_answer="Due to thermal inertia and the fact that ocean heat and CO2 are already absorbed, the climate has a lag. It takes centuries to reach equilibrium and reverse the feedback loops.",
    target_understanding=0.9
)

OpportunityCost = StudentProfile(
    name="OpportunityCost",
    topic="What is opportunity cost and why is it not what you spent?",
    misconception="Opportunity cost is the money I spent, not the value I gave up.",
    persona="A business student who memorised the definition but not the concept. Passes exams but cannot apply opportunity cost to real decisions.",
    difficulty="medium",
    progress_keywords=["next best", "alternative", "gave up", "implicit", "not money", "value forgone", "best option"],
    correct_answer="Opportunity cost is not money spent, it is the value forgone from the next best alternative option that you gave up.",
    target_understanding=0.9
)

TypeITypeII = StudentProfile(
    name="TypeITypeII",
    topic="Why is a false negative sometimes worse than a false positive in medicine?",
    misconception="A false positive is always worse than a false negative because it only causes unnecessary worry.",
    persona="A pre-med student who thinks false positives are the bigger problem. Has not considered what a missed cancer diagnosis costs.",
    difficulty="hard",
    progress_keywords=["consequence", "missed diagnosis", "cancer", "context", "depends on", "cost of missing", "asymmetric"],
    correct_answer="The consequence depends on the context. A missed diagnosis like cancer (false negative) is asymmetric and has a much higher cost of missing than a false positive.",
    target_understanding=0.9
)

PhotosynthesisMass = StudentProfile(
    name="PhotosynthesisMass",
    topic="Where does the mass of a plant actually come from?",
    misconception="Plants get most of their mass from the soil through their roots.",
    persona="A curious home gardener who notices plants grow large from 'just water and sun'. Practical thinker. Surprised by the real answer.",
    difficulty="easy",
    progress_keywords=["carbon dioxide", "air", "CO2", "photosynthesis", "atmosphere", "glucose", "water", "sunlight"],
    correct_answer="Through photosynthesis using sunlight and water, plants take in carbon dioxide (CO2) from the air/atmosphere and convert it into glucose, which provides most of their mass.",
    target_understanding=0.9
)

NewtonEinstein = StudentProfile(
    name="NewtonEinstein",
    topic="Did Einstein prove Newton wrong about gravity?",
    misconception="Einstein proved Newton was completely wrong about gravity.",
    persona="A physics enthusiast who read a pop-science article about relativity. Excited to tell people Newton was 'debunked'.",
    difficulty="hard",
    progress_keywords=["approximation", "low velocity", "special case", "extends", "limit", "everyday", "accurate enough"],
    correct_answer="Einstein extends Newton's work. Newton's laws are an approximation that is accurate enough for everyday use at low velocity, effectively a special case limit of relativity.",
    target_understanding=0.9
)

EXTENDED_SCENARIOS = [
    HerdImmunity,
    CompoundInterest,
    GitMerge,
    DatabaseIndex,
    NeuralNetworkThinking,
    ClimateFeedback,
    OpportunityCost,
    TypeITypeII,
    PhotosynthesisMass,
    NewtonEinstein
]
