# AutoInventory

![Profit trajectory across 639 experiments](progress.png)

*Every morning, 30 million small businesses in America make the same bet: how
much to order today. Too much and you eat the loss. Too little and you'll never
know what you missed — the customer who found an empty shelf just leaves. For a
century, the only tool was instinct. Someday soon, an owner will write a few
paragraphs about their business, hand it to an AI, and go to sleep. By morning,
the AI will have tested more ideas than the owner would try in a decade. It'll
be wrong most of the time. It won't matter. This repo is a rough draft of that
future.*
— [@harslan](https://github.com/harslan), March 2026

---

A Boston flower shop. Five products. One order placed each morning, no second
chances. Whatever doesn't sell by closing is thrown in the trash.

Order too many and you're composting money. Order too few and you'll never
know — a customer who walks into an empty store doesn't leave a note.

That last part is the real problem. **Your sales data is lying to you.** On the
days you need it most — Valentine's Day, Mother's Day — you sell out early and
your records say "sold 50 roses." But maybe 200 people wanted them. You'll
never know. And the worse you understock, the more your data tells you demand
is low. It's a trap that gets tighter the longer you're in it.

The idea: give an AI agent the business context, a deterministic simulator, and
one rule — *only keep changes that measurably improve profit* — then let it run.
**639 experiments later, it closes the gap from 72.5% to 90.7% of the
theoretical maximum** (the profit you'd get if you could see the future).

## The setup

A human writes two files and never touches them again:

- **`prepare.py`** — A sealed simulator. One year of daily ordering against
  hidden true demand. Deterministic: same policy in, same profit out, every
  time. This is the judge.
- **`agenda.md`** — The business brief. Five products, their costs and margins,
  what the owner knows about seasonality and customer behavior, and a protocol
  for the agent to follow.

The agent edits one file:

- **`policy.py`** — Given the day, the product, and the (censored) sales
  history, return a number: how many to order. This is the only lever.

The loop: edit the policy, run the simulator, measure profit. Better? Keep it.
Worse? Revert. Repeat 639 times.

## Quick start

```bash
git clone https://github.com/harslan/autoinventory.git
cd autoinventory
python prepare.py          # evaluate the current policy (~1 sec)
```

```
  Oracle profit : $    541,236  (perfect information upper bound)
  Policy profit : $    491,103  (90.7% of oracle)
```

## Running the agent

Point any coding agent at this repo and let it go. With
[Claude Code](https://docs.anthropic.com/en/docs/claude-code):

```bash
claude --print "Read agenda.md and start the experiment loop."
```

The `agenda.md` file contains the full protocol. The agent reads it, forms
hypotheses, edits `policy.py`, runs the simulator, logs results, and repeats.
No GPU required — just Python and numpy. Each experiment takes about 1 second.

## Why this is hard

**The data lies.** When you sell out, your records show a sale — not the true
demand. Every stockout makes your historical average a little too low, which
makes you order a little too little, which causes more stockouts. This is
called *censored demand*, and it's the central challenge of inventory
management.

**The costs are lopsided.** A wasted rose costs you $8 (the purchase price). A
missed rose sale costs you $17 (the lost margin). For orchids it's $15 wasted
vs $30 lost. The rational move is to over-order slightly — but "slightly" is
doing a lot of work in that sentence when Valentine's Day demand is 8x a normal
Tuesday.

**Holidays are cliffs, not hills.** Rose demand doesn't gently rise into
Valentine's Day. It spikes 8x on the day, 4x the day before, then crashes
back to normal. Mother's Day is the same for orchids and lilies. Getting the
*shape* of these spikes right — not just their existence — is where most of
the profit hides.

**Products contaminate each other.** When roses sell out on Valentine's Day,
some customers buy tulips instead. This makes tulip demand *appear* elevated,
which inflates future tulip orders, which wastes money for weeks when demand
is actually normal.

## What the agent discovered

| Milestone | Profit | % Oracle | |
|-----------|--------|----------|-|
| Baseline | $392,449 | 72.5% | Fixed quantities, no learning |
| Adaptive + holidays | $460,382 | 85.1% | Learns from history, boosts for holidays |
| Per-product tuning | $485,209 | 89.6% | Each flower gets its own parameters |
| Final | **$491,103** | **90.7%** | Post-holiday corrections, seasonal shaping |

Some of the more surprising findings:

- **The Monday after Mother's Day** is the single biggest miss. Orchid and lily
  customers who couldn't buy on Sunday come back Monday. A 3.5x orchid boost
  on that one day added $3,000 in annual profit.
- **Orchids have memory.** For most products, recent sales are the best
  predictor. For orchids, the opposite: older data is *more* informative
  because orchid demand is remarkably stable. The agent discovered this by
  finding that a *negative* smoothing weight outperforms a positive one.
- **Holidays poison the forecast.** After Valentine's Day, the moving average
  is inflated by the spike. Without a dampener (0.85x for the days right
  after), the policy over-orders roses for weeks.
- **Censoring correction must be per-product.** Orchids need gentle inflation
  (0.18), tulips need aggressive inflation (0.35). One size fits nobody.

## Lessons

**Most experiments fail, and that's the point.** Of 639 experiments, 461 were
discarded. The agent tried widening windows that needed narrowing, boosting
holidays that didn't exist, and adding safety stock that created more waste
than it prevented. Each failure eliminated a hypothesis. The value isn't in any
single experiment — it's in the *volume* of experimentation.

**The first 10% of effort captures 70% of the gains.** The jump from 72.5% to
85.1% took 2 experiments. The crawl from 85.1% to 90.7% took 637. This is the
universal shape of optimization: early wins are structural (learn from
history, acknowledge holidays exist), late wins are surgical (the exact
dampening factor for roses the week after Valentine's Day). Both matter, but
they feel very different.

**Domain knowledge is the scaffold.** The agent didn't discover Valentine's Day
from data — the human said "Valentine's Day is big for roses" in a two-sentence
aside. What the agent *did* discover is that demand spikes 4.4x the day
*before*, that orchids and tulips also spike (but differently), and that the
data stays corrupted for days afterward. The human draws the map; the agent
walks every path on it.

**The hardest problems are second-order.** The obvious challenge is forecasting
demand. The subtle one is that your forecasting errors compound: a stockout
biases your data, which biases your next order, which causes another stockout.
The best improvements didn't come from better forecasting — they came from
understanding how the system's own behavior corrupts its own inputs.

## Project structure

```
autoinventory/
├── agenda.md       # business context + experiment protocol
├── prepare.py      # deterministic simulator (never modified)
├── policy.py       # ordering policy (the agent's canvas)
├── results.tsv     # full experiment log (639 rows)
├── progress.png    # profit trajectory chart
└── CLAUDE.md       # agent instructions
```

## License

MIT
