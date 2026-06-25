# **CYOA Story Engine PRD Skeleton & Project Context**

This document defines the project context, system architecture, and functional specifications for the second language (English) learning platform using "Choose Your Own Adventure" (CYOA) stories. The system integrates a precise pedagogical learning frontier with a dynamic LLM-driven content engine, optimizing for cost, latency, and gamified user experience.

## **1\. Background & Pedagogical Context**

Unlike traditional language learning platforms that force vocabulary acquisition within rigid "lexical fields" (e.g., clothes, food, animals), this project applies Krashen's Input Hypothesis (i+1) over a Continuous Difficulty Index. The system tracks a dynamic "learning frontier" for each student and pulls words from their immediate ranking window regardless of thematic categories. The LLM acts as a context wizard, seamlessly embedding these words into the chosen story setting.

## **2\. End-to-End User Flow**

1. **Placement Assessment:** New users complete a short, structured assessment that outputs a numerical placement index rank.  
2. **Victory Screen:** Converts the numerical score into a gamified rank (e.g., "Adventurer Tier 3") with visual rewards.  
3. **Genre Selection:** The user selects the visual and thematic wrapper for the story (e.g., Space, Fantasy, Mystery).  
4. **The Chat Wizard (Launchpad):** Displays fast, dynamic options to establish the launchpad anchors: Hero (Who), World (Where), and Inciting Incident. This step is entirely powered by a pre-generated JSON object retrieved in a single API call.  
5. **Reading & Decision:** The user reads Chapter 1, which integrates the target words, and makes a narrative choice based on predefined behavioral archetypes (e.g., bravery vs. caution).  
6. **Active Feedback Loop:** Tracks user interactions with the text (clicks, translations) and continuously updates their placement index.

## **3\. Milestone Map & Development Prioritization**

| Milestone | Functional & Technical Description | Priority   |
| :---- | :---- | :---- |
| **Milestone 1: Assessment & Frontier Mapping** | Develop a short, dynamic client-side assessment. Establish the algorithm to slice the target vocabulary window (i+1 window) from the continuous word dataset based on the user score. | **High (P0)** |
| **Milestone 2: Launchpad Generator & Option Tree** | Implement the first LLM API call to generate a complete option tree in a strict JSON format. The model weaves target vocabulary into hero/world descriptions in Hebrew and English, matching the syntax complexity to the student's level. | **High (P0)** |
| **Milestone 3: UI Chat Wizard & Manual Input Override** | Build a conversational UI component (Quick Replies) that feeds instantly off the local JSON data. Develop an override path allowing free-text or voice inputs, triggering a fast supplementary LLM validation call. | **Medium (P1)** |
| **Milestone 4: Story Engine & Chapter 1** | Execute the second LLM API call to generate the narrative arc and full English text for Chapter 1 (3-4 sentences). The text must conclude with a structured dilemma based on fixed archetypes and tag target words for UI highlighting. | **High (P0)** |
| **Milestone 5: Active Engagement Loop & Index Updates** | Develop the difficulty index adjustment algorithm based on active reading metrics (clicks, text-to-speech, choices) and manage the evolutionary context state between subsequent chapters. | Low (P2) |

## **4\. Technical Specification: Launchpad Single-Call Architecture**

To guarantee zero latency during the conversational wizard and minimize API compute costs, the system pre-generates the entire launch tree via a structured JSON schema.

**Target Data Structure (JSON Schema Example):**

{  
  "heroes": \[  
    {  
      "id": "hero\_1",  
      "display\_name\_en": "A tiny robot who loves to paint",  
      "display\_name\_he": "רובוט קטן שאוהב לצייר",  
      "associated\_target\_words": \["robot", "paint", "battery"\],  
      "worlds": \[  
        {  
          "id": "world\_1\_1",  
          "display\_name\_en": "The Candy Kingdom",  
          "display\_name\_he": "בממלכת הממתקים",  
          "inciting\_incidents": \[  
            {  
              "id": "inc\_1\_1\_1",  
              "display\_name\_en": "The chocolate river completely froze over\!",  
              "display\_name\_he": "נהר השוקולד קפא לחלוטין"  
            },  
            {  
              "id": "inc\_1\_1\_2",  
              "display\_name\_en": "The royal candy disappeared from the castle tower\!",  
              "display\_name\_he": "הסוכרייה המלכותית נעלמה מראש הארמון"  
            }  
          \]  
        }  
      \]  
    }  
  \]  
}

## **5\. Core Development Principles**

* **The Skin Principle:** The narrative theme (space, dragons, etc.) acts purely as a visual and contextual skin. The statistical language engine does not require lexical tagging; it relies entirely on the LLM's natural contextualization capabilities.  
* **Fixed Narrative Archetypes:** Dilemmas at the end of each chapter are mapped to fixed algorithmic archetypes (bravery vs. caution, analysis vs. quick action). This keeps the tree uniform and behavior-trackable.  
* **Prompt Engineering & Playground Validation:** The next urgent step involves robust prompt design for Milestone 2 inside the developer playground to enforce structural JSON integrity and eliminate syntax regressions.