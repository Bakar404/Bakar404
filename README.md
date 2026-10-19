<p>
<picture><source media="(max-width: 600px)" srcset="assets/hero-phone.svg"><source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg"><img alt="Ahmed Abdelsalam, drawn in pixels, waving: &quot;Hi, I&#x27;m Ahmed. I turn ideas into products, mostly with AI.&quot;" src="assets/hero-light.svg" width="100%" align="top"></picture><br>
<picture><source media="(max-width: 600px)" srcset="assets/specs-phone.svg"><source media="(prefers-color-scheme: dark)" srcset="assets/specs-dark.svg"><img alt="Interests: being creative, building with AI, building cool products and game theory. Tools. AI + agents: MCP, Multi-agent orchestration, Agent evals, Microsoft Agent Framework, Azure AI. Languages: Python, TypeScript, JavaScript, Swift, SQL, C++, R, DAX, HTML/CSS. Build: React, Next.js, Vite, Tailwind, Node.js, FastAPI, SwiftUI, CoreAudio. Data + cloud: Azure, Microsoft Fabric, Power BI, Power Platform, Data Factory, Synapse, Databricks, pandas, NumPy, SciPy. Ship: Supabase, Firebase, Cloudflare Workers, GitHub Actions, Playwright, Git, Azure DevOps, Jira. + Anything that gets the job done." src="assets/specs-light.svg" width="100%" align="top"></picture><br>
<!-- game -->
<picture><source media="(max-width: 600px)" srcset="assets/board-phone.svg?v=1-2"><source media="(prefers-color-scheme: dark)" srcset="assets/board-dark.svg?v=1-2"><img alt="Nim against a perfect bot, game 1, move 3. Heaps: A has 0, B has 1, C has 1; nim-sum 0. Games won: humans 0, bot 0. Last move: @Bakar404 took 3 from B, then the bot took 3 from C. Pick a heap and how many matches to take with the keys below." src="assets/board-light.svg?v=1-2" width="100%" align="top"></picture><br>
<picture><source media="(max-width: 600px)" srcset="assets/heap-a-phone.svg"><source media="(prefers-color-scheme: dark)" srcset="assets/heap-a-dark.svg"><img alt="Heap A:" src="assets/heap-a-light.svg" width="16.666%" align="top"></picture><picture><source media="(max-width: 600px)" srcset="assets/empty-phone.svg"><source media="(prefers-color-scheme: dark)" srcset="assets/empty-dark.svg"><img alt="empty" src="assets/empty-light.svg" width="16.666%" align="top"></picture><br>
<picture><source media="(max-width: 600px)" srcset="assets/heap-b-phone.svg"><source media="(prefers-color-scheme: dark)" srcset="assets/heap-b-dark.svg"><img alt="Heap B:" src="assets/heap-b-light.svg" width="16.666%" align="top"></picture><a href="https://github.com/Bakar404/Bakar404/issues/new?title=nim%3A+take+1+from+B+%28game+1%2C+move+3%29&amp;body=Submit+this+issue+to+make+your+move.+The+bot+answers%2C+redraws+the+board+on+github.com%2FBakar404+and+replies+here+in+about+a+minute.%0A%0APlease+keep+the+title+as+it+is."><picture><source media="(max-width: 600px)" srcset="assets/take-1-phone.svg"><source media="(prefers-color-scheme: dark)" srcset="assets/take-1-dark.svg"><img alt="Take 1 from heap B" src="assets/take-1-light.svg" width="16.666%" align="top"></picture></a><br>
<picture><source media="(max-width: 600px)" srcset="assets/heap-c-phone.svg"><source media="(prefers-color-scheme: dark)" srcset="assets/heap-c-dark.svg"><img alt="Heap C:" src="assets/heap-c-light.svg" width="16.666%" align="top"></picture><a href="https://github.com/Bakar404/Bakar404/issues/new?title=nim%3A+take+1+from+C+%28game+1%2C+move+3%29&amp;body=Submit+this+issue+to+make+your+move.+The+bot+answers%2C+redraws+the+board+on+github.com%2FBakar404+and+replies+here+in+about+a+minute.%0A%0APlease+keep+the+title+as+it+is."><picture><source media="(max-width: 600px)" srcset="assets/take-1-phone.svg"><source media="(prefers-color-scheme: dark)" srcset="assets/take-1-dark.svg"><img alt="Take 1 from heap C" src="assets/take-1-light.svg" width="16.666%" align="top"></picture></a>
<!-- /game -->
</p>

<details>
<summary><picture><source media="(max-width: 600px)" srcset="assets/summary-phone.svg"><source media="(prefers-color-scheme: dark)" srcset="assets/summary-dark.svg"><img alt="How does the bot decide?" src="assets/summary-light.svg" width="89.834%"></picture></summary>
<br>

The bot never guesses. It writes each heap in binary and XORs them together, column by column with no carrying. That's the **nim-sum**.

- **Facing a nim-sum of 0?** Any move you make breaks the zero, and the bot can always restore it. It keeps handing you zeros until it takes the last match.
- **Facing anything else?** Some move turns it into 0. Make that move every turn and you take the last match. Charles L. Bouton proved this in 1901, one of the first results in [combinatorial game theory](https://en.wikipedia.org/wiki/Nim).

Every game starts with a nonzero nim-sum and you move first, so a perfect bot can still be beaten.

A key opens an issue titled like `nim: take 2 from A (game 1, move 1)`. A [GitHub Action](.github/workflows/nim.yml) plays your move and the bot's with [`src/nim.py`](src/nim.py), redraws the board and replies to you. Every pixel here is drawn by [`src/scenes.py`](src/scenes.py).

</details>
