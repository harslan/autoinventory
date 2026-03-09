# Inventory Research Agenda — Boston Flower Shop

## The Business
We sell cut flowers in Boston. Five products: roses, tulips, orchids,
sunflowers, and lilies. Everything unsold at end of day is worthless.
We cannot reorder mid-day.

## Cost Structure
- Roses:       $8 cost, $25 sale — highest margin, highest demand volatility
- Tulips:      $4 cost, $14 sale — rose substitute on big days
- Orchids:     $15 cost, $45 sale — price-insensitive buyers, steady demand
- Sunflowers:  $3 cost, $10 sale — strong summer seasonality
- Lilies:      $4 cost, $13 sale — Mother's Day is their Super Bowl

## What I Know (Human Intuitions)
- Valentine's Day (around day 44) is by far our biggest day for roses
- Mother's Day (around day 133) is huge for lilies and orchids
- Weekends are meaningfully stronger than weekdays
- When we run out of roses, some customers buy tulips instead
- We've been growing roughly 10% year-over-year
- I suspect we chronically under-order roses before Valentine's Day
  and over-order sunflowers in the fall

## Risk Preferences
- I am MORE afraid of stocking out on Valentine's Day than wasting
  flowers on a random Tuesday. A stockout on a peak day loses a loyal
  customer, not just one sale.
- For orchids specifically: never stock out. Our orchid customers are
  regulars who will switch shops permanently if we disappoint them.

## Research Goal
Maximize total annual profit. The Oracle profit (perfect information)
is the ceiling — I want to get as close to it as possible.
The gap between my actual profit and the oracle is the cost of
not being able to see my own lost sales.

---
*This file is edited by the human. agenda.md → policy.py is the
same division of labor as program.md → train.py in Karpathy's autoresearch.*
