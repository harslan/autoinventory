# Session Report

**Branch:** `run-001` | **Best commit:** `5f0f33b`

## Results

| Metric | Value |
|--------|-------|
| Oracle profit | $541,236 |
| Session start | $488,676 (90.3%) |
| Session end | **$488,736 (90.3%)** |
| Net improvement | **+$60** |

## What improved this session

| Change | Delta |
|--------|-------|
| Extend rose EXCL post-VD to day 49 (was 45) | +$22 |
| Add rose pre-MD dt=2 boost (1.1x) | +$35 |
| Add rose pre-MD dt=3 boost (1.05x) | +$1 |
| Extend lily EXCL post-MD to day 135 | +$2 |

## What was tried and failed (~25 experiments)

- Adding MD to rose EXCL (-$62): removing day 132 from rose history hurts more than the contamination costs
- Rose inflate_k 0.3→0.35 (-$228): rose over-ordering on Sundays is already a problem
- History window 15→20 (-$692): more history = worse adaptation
- 7-DOW segmentation (-$8,089): too few data points per group
- Various orchid boosts (MD-1, MD-2 higher): orchid calibration is already tight
- Summer dampener for roses 0.9x days 155-215 (-$165): causes more stockouts than it saves in waste
- Tulip MD-2, tulip VD-1 boosts: small losses
- Rose Thanksgiving boost higher (-$140)
- Sunflower summer boost extension/dampener changes: all hurt

## Current per-product gap

| Product | Gap | Waste | Stockouts |
|---------|-----|-------|-----------|
| Roses | $19,617 | 1,464 | 465 |
| Orchids | $9,870 | 368 | 145 |
| Tulips | $9,448 | 1,372 | 396 |
| Lilies | $7,088 | 998 | 344 |
| Sunflowers | $6,477 | 1,228 | 399 |

**Note:** We are already **above** the censoring ceiling ($455,282), meaning domain-knowledge boosts have pushed us past the theoretical passive-observation limit. The remaining $52,500 gap is mostly from imperfect holiday demand capture and irreducible information loss.

## Promising directions not yet fully explored

1. Lily pre-MD window boost (Saturday before MD = day 131, demand 28 but ordered 33 — close, but adding explicit boosts has hurt)
2. Tulip fall/Thanksgiving-specific tuning
3. The orchid post-MD 3.4x boost calibration (seems high, but reducing it hurt in prior experiments)
4. Per-product cold-start weekend multiplier tuning (currently 1.6x uniform)
