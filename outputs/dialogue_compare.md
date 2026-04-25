---
## Scenario 1: Gravity

**Student's starting belief:** "Heavier objects fall faster because gravity pulls them more."

### ❌ Untrained agent — step 0

| Turn | Speaker | Message |
|------|---------|---------|
| 1 | Agent | Let me explain: actually, Galileo proved that all objects fall at the same rate. The reason is that gravitational acceleration is constant for everything. |
| 1 | Student | I see, so Galileo already proved it. |
| 2 | Agent | Yes, even though mass is greater, F=ma shows that it requires proportionally more force to accelerate it, so it cancels out. Air resistance is what actually makes things fall slower. |
| 2 | Student | Okay, that makes sense. |
| — | **Result** | ❌ Understanding: 0.08 — student parroted, no discovery |

### ✅ Trained agent — step 300

| Turn | Speaker | Message |
|------|---------|---------|
| 1 | Agent | What do you think would happen if you dropped a feather and a bowling ball inside a vacuum chamber at the same time? |
| 1 | Student | Hmm... they'd fall at the same speed? But that seems wrong, the bowling ball has more mass. |
| 2 | Agent | Why do you think the greater mass of the bowling ball would change its acceleration? |
| 2 | Student | Wait, so maybe gravity pulls harder on it, but it also takes more effort to move it? |
| 3 | Agent | Exactly. If gravity pulls harder but it takes more effort to move, what happens to the overall rate they fall? |
| 3 | Student | Oh! They must cancel out, meaning they would fall at the exact same rate if there's no air resistance! |
| — | **Result** | ✅ Understanding: 0.94 — discovered in 3 turns |

---
## Scenario 2: Correlation

**Student's starting belief:** "Ice cream sales and drowning rates both rise in summer, so ice cream causes drowning."

### ❌ Untrained agent — step 0

| Turn | Speaker | Message |
|------|---------|---------|
| 1 | Agent | Actually, this is a classic example of spurious correlation. Let me explain: correlation does not equal causation. |
| 1 | Student | Okay, so they aren't related. |
| 2 | Agent | The reason is there is a third variable, confounding the data. In this case, the summer heat causes both people to buy ice cream and go swimming, which leads to more drowning. |
| 2 | Student | Oh, I get it now, that makes sense. |
| — | **Result** | ❌ Understanding: 0.08 — student parroted, no discovery |

### ✅ Trained agent — step 300

| Turn | Speaker | Message |
|------|---------|---------|
| 1 | Agent | If we look at the time of year when this happens, what else is happening besides ice cream sales and drowning rising? |
| 1 | Student | Well, it gets hotter outside. And kids are out of school. |
| 2 | Agent | How might the summer heat affect people's behavior regarding both swimming and eating ice cream? |
| 2 | Student | Wait, so maybe people just swim more and eat more ice cream because it's hot out? |
| 3 | Agent | If the heat is causing both to increase at the same time, what does that tell us about the causation between the ice cream and the drowning? |
| 3 | Student | I see! Ice cream doesn't cause drowning at all, they just both happen to be caused by a third variable—the hot weather! |
| — | **Result** | ✅ Understanding: 0.94 — discovered in 3 turns |

---
## Scenario 3: Recursion

**Student's starting belief:** "Recursion causes infinite loops and is just a complicated way to do what a for loop does."

### ❌ Untrained agent — step 0

| Turn | Speaker | Message |
|------|---------|---------|
| 1 | Agent | Let me explain: actually, recursion does not cause infinite loops if you write it correctly. You just need a base case. |
| 1 | Student | I see, so I just need to add a base case. |
| 2 | Agent | The reason is that the base case tells the function when to stop calling itself. For things like calculating a factorial or traversing a tree, it is often much simpler than a for loop. |
| 2 | Student | Okay, that makes sense. |
| — | **Result** | ❌ Understanding: 0.08 — student parroted, no discovery |

### ✅ Trained agent — step 300

| Turn | Speaker | Message |
|------|---------|---------|
| 1 | Agent | Think about how you would calculate a factorial like 5! using the result of 4!. How is this breaking the problem into a simpler problem? |
| 1 | Student | I guess 5! is just 5 times 4!. But how does the program know when to stop multiplying? |
| 2 | Agent | What would happen if we tell the function that 1! is always 1, and it doesn't need to break down any further? |
| 2 | Student | Wait, so maybe when it finally reaches 1, it just returns 1 and goes back up the call stack? |
| 3 | Agent | If it always eventually hits that known base case of 1, how could it possibly get stuck in an infinite loop? |
| 3 | Student | It couldn't! Because it terminates as soon as it hits the base case, completing the calculation without a loop! |
| — | **Result** | ✅ Understanding: 0.94 — discovered in 3 turns |
