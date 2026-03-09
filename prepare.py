"""
prepare.py — Fixed simulation engine. Do not modify.

Equivalent to Karpathy's prepare.py in autoresearch.
Generates ground-truth demand, computes the Oracle bound,
and provides the run_simulation() harness that scores any policy.

The agent never sees TRUE_DEMAND directly.
It only observes min(ordered, true_demand) each day — censored data.
"""

import numpy as np
import warnings

# ── Products & economics ──────────────────────────────────────────────────────
PRODUCTS = ['roses', 'tulips', 'orchids', 'sunflowers', 'lilies']

COST  = {'roses': 8,  'tulips': 4,  'orchids': 15, 'sunflowers': 3,  'lilies': 4 }
PRICE = {'roses': 25, 'tulips': 14, 'orchids': 45, 'sunflowers': 10, 'lilies': 13}
BASE  = {'roses': 25, 'tulips': 20, 'orchids': 8,  'sunflowers': 15, 'lilies': 18}

# ── Generate 365 days of TRUE demand (hidden from policy) ─────────────────────
# Fixed seed — deterministic for everyone. Same policy = same profit. Always.
_rng = np.random.default_rng(42)
TRUE_DEMAND: dict[str, list[int]] = {p: [] for p in PRODUCTS}

for _day in range(365):
    _dow     = _day % 7
    _weekend = (_dow >= 5)

    for _product in PRODUCTS:
        _d = float(BASE[_product])

        if _weekend:
            _d *= 1.6

        # Seasonal & special days
        if _product == 'roses':
            if   _day == 44:              _d *= 9.0   # Valentine's Day
            elif _day == 43:              _d *= 4.0   # Valentine's Eve
            elif _day == 45:              _d *= 3.0   # Day after
            elif _day == 133:             _d *= 4.5   # Mother's Day
            elif 120 <= _day <= 145:      _d *= 1.3   # Spring
        elif _product == 'tulips':
            if   _day == 44:              _d *= 4.0
            elif _day == 133:             _d *= 3.0
            elif 60 <= _day <= 150:       _d *= 1.4
        elif _product == 'orchids':
            if   _day == 44:              _d *= 2.5
            elif _day == 133:             _d *= 3.5
            elif _day == 357:             _d *= 2.0
        elif _product == 'sunflowers':
            if   150 <= _day <= 240:      _d *= 2.2
            elif _day == 133:             _d *= 1.8
        elif _product == 'lilies':
            if   _day == 133:             _d *= 4.0   # Mother's Day
            elif _day == 44:              _d *= 2.0
            elif _day == 357:             _d *= 2.5

        # Demand growth (~10% YoY)
        _d *= (1 + 0.10 * _day / 365)

        # Random noise
        _noise = _rng.normal(0, _d * 0.18)
        _d = max(0, int(round(_d + _noise)))
        TRUE_DEMAND[_product].append(_d)

# ── Oracle: order exactly true demand every day (theoretical upper bound) ─────
ORACLE_PROFIT: float = sum(
    TRUE_DEMAND[p][d] * (PRICE[p] - COST[p])
    for p in PRODUCTS
    for d in range(365)
)



# ── Censoring ceiling (theoretical maximum under passive observation) ──────────
# A policy that observes true demand on non-stockout days, None otherwise.
# No explore-exploit — purely reactive to what censored information reveals.
# The gap between this and ORACLE_PROFIT is IRREDUCIBLE:
#   it is the permanent cost of never observing demand when you stocked out.
def _compute_censoring_ceiling() -> float:
    total = 0.0
    true_hist  = {p: [] for p in PRODUCTS}

    for _d in range(365):
        _dow2    = _d % 7
        _wknd    = (_dow2 >= 5)
        for _p in PRODUCTS:
            _td = TRUE_DEMAND[_p][_d]
            _known = [x for x in true_hist[_p] if x is not None]
            if len(_known) >= 3:
                _est = float(np.mean(_known[-14:]))
                # Naive weekend boost (only thing it can infer from day number)
                if _wknd:
                    _est *= 1.5
                # Inflate for recent stockouts — knows demand was > order
                _recent = true_hist[_p][-14:]
                _n_so   = sum(1 for x in _recent if x is None)
                _n_tot  = max(1, len(_recent))
                _est   *= (1.0 + 0.45 * _n_so / _n_tot)
            elif _known:
                _est = float(np.mean(_known))
            else:
                _est = float(BASE[_p])
            _qty  = max(0, min(600, int(round(_est))))
            _sold = min(_qty, _td)
            _so   = (_qty < _td)
            total += _sold * PRICE[_p] - _qty * COST[_p]
            true_hist[_p].append(_td if not _so else None)
    return total

CENSORING_CEILING: float = _compute_censoring_ceiling()
IRREDUCIBLE_GAP:   float = ORACLE_PROFIT - CENSORING_CEILING

def run_simulation(policy_code: str, verbose: bool = False) -> float:
    """
    Run the 365-day simulation with the given policy code string.

    Returns total annual profit (float).
    Deterministic: same policy code → same profit, every time.

    The policy sees only:
      - day: int (0-364)
      - product: str
      - sales_history: list[int]  — CENSORED (min(ordered, true_demand))
      - order_history: list[int]

    It never sees TRUE_DEMAND directly.
    """
    namespace = {'np': np}

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            exec(compile(policy_code, '<policy>', 'exec'), namespace)
        compute_order = namespace.get('compute_order')
        if compute_order is None:
            if verbose:
                print("  ✗ compute_order function not found in policy")
            return float('-inf')
    except Exception as e:
        if verbose:
            print(f"  ✗ Policy compilation error: {e}")
        return float('-inf')

    total_profit = 0.0
    sales_hist   = {p: [] for p in PRODUCTS}
    order_hist   = {p: [] for p in PRODUCTS}
    n_exceptions = 0
    n_calls      = 365 * len(PRODUCTS)

    for day in range(365):
        for product in PRODUCTS:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    qty = compute_order(
                        day=day,
                        product=product,
                        sales_history=list(sales_hist[product]),
                        order_history=list(order_hist[product]),
                    )
                # Guard against None, NaN, inf, negative
                if qty is None:
                    qty = BASE[product]
                qty = float(qty)
                if np.isnan(qty) or np.isinf(qty) or qty < 0:
                    qty = BASE[product]
                qty = max(0, min(600, int(round(qty))))
            except Exception:
                qty = BASE[product]
                n_exceptions += 1

            true_d = TRUE_DEMAND[product][day]
            sold   = min(qty, true_d)

            total_profit += sold * PRICE[product] - qty * COST[product]
            sales_hist[product].append(sold)
            order_hist[product].append(qty)

    # If the policy crashed on more than 10% of calls, it is effectively broken.
    # Return -inf so the agent gets an honest signal rather than a misleading $392K.
    if n_exceptions / n_calls > 0.10:
        if verbose:
            print(f"  ✗ Policy crashed on {n_exceptions}/{n_calls} calls ({n_exceptions/n_calls*100:.0f}%) — treating as -inf")
        return float('-inf')

    return total_profit


if __name__ == '__main__':
    print("prepare.py — AutoInventory simulation engine")
    print(f"  Products      : {PRODUCTS}")
    print("  Horizon       : 365 days  (fixed seed=42)")
    print(f"  Oracle profit : ${ORACLE_PROFIT:>12,.0f}  (perfect information upper bound)")

    # Quick sanity check
    baseline_code = open('policy.py').read()
    bp = run_simulation(baseline_code)
    print(f"  Policy profit : ${bp:>12,.0f}  (current policy.py)")
    print(f"  Gap           : ${ORACLE_PROFIT - bp:>12,.0f}  ({(ORACLE_PROFIT-bp)/ORACLE_PROFIT*100:.1f}% of oracle)")
