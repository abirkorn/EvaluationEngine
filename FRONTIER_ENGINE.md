# Mathematical Specification: The Frontier Engine & Active Feedback Loop

This document outlines the core mathematical and algorithmic framework for the continuous student proficiency assessment and the subsequent active learning feedback loop.

## 1. The Statistical Model: The Knowledge Curve
A student's vocabulary knowledge is not treated as a discrete step-function, but as a continuous probability curve. The probability that a student with an overall proficiency level $\theta$ knows a word with a difficulty rank $x$ is modeled using a **Logistic Function (Sigmoid)**:

$$P(\text{Knows } x \mid \theta, \beta) = \sigma(\beta (\theta - x)) = \frac{1}{1 + e^{-\beta (\theta - x)}$$

### Parameters:
* $x \in [1, N]$: The continuous rank of the word in the catalog, sorted from easiest to hardest.
* $\theta$: The student's estimated vocabulary index (the specific rank where $P(x) = 0.5$). This is the single metric determining the student's level.
* $\beta$: The slope (discrimination parameter), representing how localized the student's knowledge is. A steep slope means a sharp drop-off; a gentle slope represents scattered knowledge.

---

## 2. Adaptive Initial Assessment Phase
The objective of the assessment is to approximate $\theta$ using the minimum number of active questions through stochastic optimization.

1. **Initialization**: Initialize $\theta_0 = \text{Median Rank}$ of the catalog with a wide confidence interval.
2. **Next Word Selection (Stochastic Binary Search)**: At each step $t$, select a word $x_t$ whose rank is closest to the current $\theta_{t-1}$ (the region of maximum uncertainty where $P \approx 0.5$).
3. **Estimation Update**: Upon receiving a hard binary signal $y_t \in \{0, 1\}$ (1 = Knows, 0 = Doesn't Know), update $\theta$ using an Online Stochastic Gradient Descent (SGD) step for logistic regression:

$$\theta_{t} = \theta_{t-1} + \eta \cdot (y_t - P(x_t \mid \theta_{t-1}, \beta))$$

*Where $\eta$ represents the learning rate (step size).*
4. **Convergence Criteria**: The assessment terminates when the change in $\theta$ falls below a threshold $|\theta_t - \theta_{t-1}| < \epsilon$, or when a maximum question cap (e.g., 15) is reached.

---

## 3. Active Continuous Feedback Loop
During the story-reading experience, the system shifts from gathering hard active signals to consuming **asymmetric passive signals**.

For every word $x$ exposed to the student, the system tracks:
* $E_x$ (Exposures): The number of times the word appeared in the read text.
* $C_x$ (Clicks/Translations): The number of times the student actively clicked the word for a translation.

### Signal Asymmetry:
* **Negative Signal (Hard)**: If a student clicks a word ($C_x > 0$), it is absolute proof they **do not know** it in this context ($y = 0$). The word is immediately flagged as unknown and sent to the Spaced Repetition queue.
* **Positive Signal (Probabilistic / Weak)**: If a word is exposed and *not* clicked ($C_x = 0$), it is a weak indicator of knowledge. The empirical local probability is smoothed using Laplace Smoothing:

$$\hat{P}(\text{Knows } x) = 1 - \frac{C_x + \alpha}{E_x + \beta}$$

*Where $\alpha, \beta$ are small prior weights preventing single exposures from skewing the overall curve.*

### Streaming Update:
At the end of each completed chapter, the engine runs a lightweight, zero-dependency streaming update applying the chapter's aggregated exposure/click matrix to refine the global $\theta$. The next "Frontier Window" from which target words are injected into future stories is dynamically derived around the new $\theta$, targeting the sweet spot where $0.3 < P(x) < 0.7$.
