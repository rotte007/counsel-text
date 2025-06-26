Designing Strategic AI for social games
# Counsel: An AI-Driven Political Crisis Game

Counsel is a text-based strategy game where you play as a ruler facing recurring national crises. Your decisions are influenced by a council of AI-powered advisors, each with their own secret agenda. The game demonstrates emergent, strategic, and manipulative advisor behavior using generative AI.

---

## Features

- **AI Advisors:** Three advisors (Treasurer, General, Diplomat) each have a public persona and a hidden goal. Their advice adapts to your actions and the current crisis.
- **Dynamic Crises:** Each turn presents a new crisis with multiple policy options, each affecting kingdom stats differently.
- **Resource Allocation:** Allocate resources among policy options (e.g., 50% to A, 30% to B, 20% to C) to resolve crises.
- **Emergent Behavior:** Advisors may persuade, stay silent, or manipulate based on their secret goals.
- **Stat Tracking:** Treasury, stability, popularity, and army stats are updated each turn.
- **Influence System:** Advisors gain influence if your choices align with their hidden goals.
- **Rich Terminal UI:** Uses [rich](https://github.com/Textualize/rich) for colored output and panels.

---

## Tech Stack

- **Python 3.12+**
- **Google Gemini API** (via `google-generativeai`)
- **Rich** (for terminal UI)
- **dotenv** (for environment variable management)

---

## Key Libraries

- [`google-generativeai`](https://pypi.org/project/google-generativeai/): For interacting with Google's Gemini models.
- [`rich`](https://pypi.org/project/rich/): For beautiful terminal output.
- [`python-dotenv`](https://pypi.org/project/python-dotenv/): For loading API keys from `.env` files.
- Standard Python libraries: `asyncio`, `random`, `os`

See [requirements.txt](requirements.txt) for the full list.

---


Gameplay
 - Each turn, a crisis is presented with three policy options.
 - Advisors give advice (or stay silent), influenced by their secret goals.
 - You can ask advisors questions, broadcast to all, or allocate resources using commands like:
 - Stats are updated, and advisors gain influence if your choices help their secret goals.
 - The game ends after 6 turns, revealing each advisor's true motives and influence.

Technical Highlights
 - Prompt Engineering: Advisors are prompted with their persona, secret goal, and real policy effects for contextually rich, strategic responses.
 - Asynchronous AI Calls: Uses asyncio for efficient interaction with the Gemini API.
 - Replayable & Extensible: Crises, advisors, and goals are easily extendable via core/crisis.py and core/advisor.py.

