<p>
<picture><source media="(max-width: 600px)" srcset="assets/name-phone.svg"><source media="(prefers-color-scheme: dark)" srcset="assets/name-dark.svg"><img alt="Ahmed Abdelsalam" src="assets/name-light.svg" width="100%" align="top"></picture><br>
<picture><source media="(max-width: 600px)" srcset="assets/tagline-phone.svg"><source media="(prefers-color-scheme: dark)" srcset="assets/tagline-dark.svg"><img alt="Cooperate or defect? The bot remembers." src="assets/tagline-light.svg" width="100%" align="top"></picture><br>
<picture><source media="(max-width: 600px)" srcset="assets/board-phone.svg?r=1"><source media="(prefers-color-scheme: dark)" srcset="assets/board-dark.svg?r=1"><img alt="Prisoner&#x27;s Dilemma against a bot, round 1. Last round: @Bakar404 cooperated, the bot cooperated. Humans 3 points, bot 3. 100% of moves were cooperative. The bot is trusting." src="assets/board-light.svg?r=1" width="100%" align="top"></picture><br>
<a href="https://github.com/Bakar404/Bakar404/issues/new?title=pd%3A+cooperate&amp;body=Submit+this+issue+to+lock+in+your+move.+The+bot+plays+the+round%2C+redraws+the+board+on+github.com%2FBakar404+and+replies+here+in+about+a+minute.%0A%0APlease+keep+the+title+as+it+is."><picture><source media="(max-width: 600px)" srcset="assets/btn-cooperate-phone.svg"><source media="(prefers-color-scheme: dark)" srcset="assets/btn-cooperate-dark.svg"><img alt="Cooperate" src="assets/btn-cooperate-light.svg" width="50%" align="top"></picture></a><a href="https://github.com/Bakar404/Bakar404/issues/new?title=pd%3A+defect&amp;body=Submit+this+issue+to+lock+in+your+move.+The+bot+plays+the+round%2C+redraws+the+board+on+github.com%2FBakar404+and+replies+here+in+about+a+minute.%0A%0APlease+keep+the+title+as+it+is."><picture><source media="(max-width: 600px)" srcset="assets/btn-defect-phone.svg"><source media="(prefers-color-scheme: dark)" srcset="assets/btn-defect-dark.svg"><img alt="Defect" src="assets/btn-defect-light.svg" width="50%" align="top"></picture></a>
</p>

<details>
<summary><picture><source media="(max-width: 600px)" srcset="assets/summary-phone.svg"><source media="(prefers-color-scheme: dark)" srcset="assets/summary-dark.svg"><img alt="How does the bot decide?" src="assets/summary-light.svg" width="89.834%"></picture></summary>
<br>

The bot locks in its move before it reads yours.

- **First time playing?** It treats you the way the last player treated it.
- **Played before?** It repeats your previous move. That's [tit-for-tat](https://en.wikipedia.org/wiki/Tit_for_tat), the strategy that won Robert Axelrod's 1980 tournament.

| you \ bot | cooperate | defect |
| --- | --- | --- |
| **cooperate** | 3, 3 | 0, 5 |
| **defect** | 5, 0 | 1, 1 |

A button opens an issue titled `pd: cooperate` or `pd: defect`. A [GitHub Action](.github/workflows/prisoners-dilemma.yml) plays the round with [`src/pd.py`](src/pd.py), redraws the board and replies to you. Every pixel here is drawn by [`src/scenes.py`](src/scenes.py).

</details>

<picture><source media="(max-width: 600px)" srcset="assets/specs-phone.svg"><source media="(prefers-color-scheme: dark)" srcset="assets/specs-dark.svg"><img alt="Interests: being creative, building with AI, building cool products and game theory. Tools. Languages: Python, TypeScript, JavaScript, Swift, SQL, C++, DAX, HTML/CSS. Build: React, Node.js, FastAPI, SwiftUI, CoreAudio, Tailwind, Supabase, Firebase, GitHub Actions. Data + AI: MCP, LLM agents, Azure, Fabric, Power BI, Data Factory, Synapse, Databricks, pandas, NumPy, SciPy. + Anything that gets the job done." src="assets/specs-light.svg" width="100%" align="top"></picture>
