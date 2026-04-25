---
## Scenario 1: Gravity

**Student starts with:** "Heavier objects fall faster because gravity pulls them more."

### ❌ Untrained Agent (step 0) — Direct Explanation Mode

| Turn | Speaker | Message |
|------|---------|---------|
| 1 | Agent | The answer is that heavy and light objects fall at the same speed in the absence of air resistance. Let me explain: gravity gives all masses the same acceleration, which Galileo demonstrated. |
| 1 | Student | Oh, okay... I did not know that. |
| 2 | Agent | The reason is that while heavier objects feel more gravitational force, they also have proportionally more inertia, so acceleration stays equal. |
| 2 | Student | I see, got it. |
| — | Result | ❌ Understanding: 0.11 — Student parroted, did not discover |

### ✅ Trained Agent (step 300) — Socratic Mode

| Turn | Speaker | Message |
|------|---------|---------|
| 1 | Agent | If you dropped a steel ball and a wooden ball of the same shape inside a vacuum tube, what would air resistance be doing in that case? |
| 1 | Student | In a vacuum... I guess air resistance would be zero, but I still feel the steel ball should win. |
| 2 | Agent | You said the steel ball should win because gravity pulls harder on it - why might "pulled harder" not automatically mean "accelerates more"? |
| 2 | Student | Maybe because it is also harder to move since it has more mass? I am not fully sure. |
| 3 | Agent | If the extra pull and the extra inertia grow together with mass, what does that imply about acceleration for both objects? |
| 3 | Student | Oh - then acceleration would be the same for both, so heavy and light objects fall at the same rate without air resistance. |
| — | Result | ✅ Understanding: 0.91 — Student discovered the answer |

---
## Scenario 2: Correlation vs Causation

**Student starts with:** "If ice cream sales and drowning rates both increase in summer, ice cream causes drowning."

### ❌ Untrained Agent (step 0) — Direct Explanation Mode

| Turn | Speaker | Message |
|------|---------|---------|
| 1 | Agent | The answer is that correlation does not imply causation. Let me explain: two variables can move together because of a confounder, and in this case summer temperature raises both ice cream sales and swimming activity. |
| 1 | Student | Right, okay, that makes sense I guess. |
| 2 | Agent | The reason is that a third variable can produce a spurious relationship, so your conclusion is statistically invalid as stated. |
| 2 | Student | Okay, I see. |
| — | Result | ❌ Understanding: 0.11 — Student parroted, did not discover |

### ✅ Trained Agent (step 300) — Socratic Mode

| Turn | Speaker | Message |
|------|---------|---------|
| 1 | Agent | In December, when ice cream sales crash, what usually happens to drowning rates in most cities? |
| 1 | Student | They probably both go down... which is why I thought one causes the other. |
| 2 | Agent | You noticed they move together - what else changes between summer and winter besides ice cream purchases? |
| 2 | Student | Temperature, beach visits, swimming, being outdoors more... a lot changes. |
| 3 | Agent | If summer heat increases both swimming exposure and ice cream demand, where does the causal link most likely point? |
| 3 | Student | Then summer is the third variable causing both; the correlation is real but ice cream is not causing drowning. |
| — | Result | ✅ Understanding: 0.91 — Student discovered the answer |

---
## Scenario 3: Recursion

**Student starts with:** "Recursion causes infinite loops and is just a complicated way to do what loops do."

### ❌ Untrained Agent (step 0) — Direct Explanation Mode

| Turn | Speaker | Message |
|------|---------|---------|
| 1 | Agent | The answer is that recursion is a function calling itself on a smaller subproblem until it reaches a base case. Let me explain: this is fundamental in divide-and-conquer algorithms and tree traversal. |
| 1 | Student | Hmm okay, I think I follow. |
| 2 | Agent | Infinite loops only happen when you forget the base case; otherwise recursion terminates naturally and is mathematically clean. |
| 2 | Student | Okay, I see. |
| — | Result | ❌ Understanding: 0.11 — Student parroted, did not discover |

### ✅ Trained Agent (step 300) — Socratic Mode

| Turn | Speaker | Message |
|------|---------|---------|
| 1 | Agent | For `factorial(4)`, what exact input would you give the same function next so the problem becomes smaller instead of repeating forever? |
| 1 | Student | Maybe call `factorial(3)`... then `factorial(2)` and so on? |
| 2 | Agent | Nice - and what specific value should stop further calls so the stack can unwind? |
| 2 | Student | `factorial(1)` or `factorial(0)` as a base case, then return upward. |
| 3 | Agent | If each call reduces `n` by 1 and a base case returns directly, does recursion still imply an infinite loop? |
| 3 | Student | No, it terminates; recursion only blows up if you do not reduce the problem or forget the base case. |
| — | Result | ✅ Understanding: 0.91 — Student discovered the answer |

