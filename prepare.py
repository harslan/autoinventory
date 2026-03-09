"""
prepare.py — Fixed simulation engine. Do not modify.

Loads pre-computed demand data, computes the Oracle bound,
and provides the run_simulation() harness that scores any policy.

The policy never sees TRUE_DEMAND directly.
It only observes min(ordered, true_demand) each day — censored data.
"""

import numpy as np
import warnings
import zlib
import base64

# ── Products & economics ──────────────────────────────────────────────────────
PRODUCTS = ['roses', 'tulips', 'orchids', 'sunflowers', 'lilies']

COST  = {'roses': 8,  'tulips': 4,  'orchids': 15, 'sunflowers': 3,  'lilies': 4 }
PRICE = {'roses': 25, 'tulips': 14, 'orchids': 45, 'sunflowers': 10, 'lilies': 13}
BASE  = {'roses': 25, 'tulips': 20, 'orchids': 8,  'sunflowers': 15, 'lilies': 18}

# ── Pre-computed demand (365 days × 5 products, deterministic) ────────────────
# Same policy = same profit. Always.
_BLOB = (
    "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"
    "ln4zd/8D8ZmkXg=="
)
_arr = np.frombuffer(
    zlib.decompress(base64.b64decode(_BLOB)), dtype=np.int16
).reshape(len(PRODUCTS), 365)
TRUE_DEMAND: dict[str, list[int]] = {
    p: _arr[i].tolist() for i, p in enumerate(PRODUCTS)
}

# ── Oracle: order exactly true demand every day (theoretical upper bound) ─────
ORACLE_PROFIT: float = sum(
    TRUE_DEMAND[p][d] * (PRICE[p] - COST[p])
    for p in PRODUCTS
    for d in range(365)
)


# ── Censoring ceiling (theoretical maximum under passive observation) ──────────
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
                if _wknd:
                    _est *= 1.5
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
    # Return -inf so the agent gets an honest signal rather than a misleading profit.
    if n_exceptions / n_calls > 0.10:
        if verbose:
            print(f"  ✗ Policy crashed on {n_exceptions}/{n_calls} calls ({n_exceptions/n_calls*100:.0f}%) — treating as -inf")
        return float('-inf')

    return total_profit


if __name__ == '__main__':
    print("prepare.py — AutoInventory simulation engine")
    print(f"  Products      : {PRODUCTS}")
    print("  Horizon       : 365 days")
    print(f"  Oracle profit : ${ORACLE_PROFIT:>12,.0f}  (perfect information upper bound)")

    # Quick sanity check
    baseline_code = open('policy.py').read()
    bp = run_simulation(baseline_code)
    print(f"  Policy profit : ${bp:>12,.0f}  (current policy.py)")
    print(f"  Gap           : ${ORACLE_PROFIT - bp:>12,.0f}  ({(ORACLE_PROFIT-bp)/ORACLE_PROFIT*100:.1f}% of oracle)")
