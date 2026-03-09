# CHANGE: Newsvendor with stockout-corrected demand (censored demand inflate)

import numpy as np

COSTS = {
    'roses':       8,
    'tulips':      4,
    'orchids':     15,
    'sunflowers':  3,
    'lilies':      4,
}

PRICES = {
    'roses':       25,
    'tulips':      14,
    'orchids':     45,
    'sunflowers':  10,
    'lilies':      13,
}

BASE_QTY = {
    'roses':       25,
    'tulips':      20,
    'orchids':      8,
    'sunflowers':  15,
    'lilies':      18,
}

ALPHA = 0.3


def compute_order(day: int, product: str,
                  sales_history: list, order_history: list) -> int:
    """
    Censored demand estimation: when we sold everything we ordered,
    true demand was likely higher. Inflate those observations before
    smoothing. This is a structural change from just using raw sales.
    """

    day_of_week = day % 7  # 0=Mon, ..., 5=Sat, 6=Sun

    # Build censored-corrected demand history
    corrected_history = []
    if len(sales_history) > 5 and len(order_history) > 5:
        n = min(len(sales_history), len(order_history))
        for i in range(n):
            s = float(sales_history[i])
            o = float(order_history[i])
            # If we sold >= 95% of what we ordered, demand was likely censored
            if o > 0 and s / o >= 0.95:
                # Inflate by a factor based on sellthrough - true demand was higher
                inflated = s * 1.25
                corrected_history.append(inflated)
            else:
                corrected_history.append(s)
    elif len(sales_history) > 5:
        corrected_history = [float(s) for s in sales_history]

    if len(corrected_history) > 5:
        # Day-of-week specific smoothing over corrected history
        same_dow = []
        for i, val in enumerate(corrected_history):
            hist_day = (day - len(corrected_history) + i)
            if hist_day % 7 == day_of_week:
                same_dow.append(val)

        if len(same_dow) >= 2:
            est = same_dow[0]
            for obs in same_dow[1:]:
                est = ALPHA * obs + (1.0 - ALPHA) * est
            smoothed_demand = est
        elif len(same_dow) == 1:
            overall_mean = float(np.mean(corrected_history[-14:]))
            smoothed_demand = 0.6 * same_dow[0] + 0.4 * overall_mean
        else:
            overall_mean = float(np.mean(corrected_history[-14:]))
            smoothed_demand = overall_mean * (1.25 if day_of_week in [5, 6] else 1.0)
    else:
        smoothed_demand = float(BASE_QTY[product])
        if day_of_week in [5, 6]:
            smoothed_demand *= 1.25

    # === SEASONAL ADJUSTMENTS ===
    if product == 'roses' and 38 <= day <= 50:
        smoothed_demand *= 2.0

    if product == 'lilies' and 130 <= day <= 136:
        smoothed_demand *= 2.2

    if product == 'orchids' and 130 <= day <= 136:
        smoothed_demand *= 1.6

    if product == 'sunflowers' and 150 <= day <= 270:
        smoothed_demand *= 1.4

    # === NEWSVENDOR CRITICAL RATIO ===
    cost = COSTS[product]
    price = PRICES[product]
    critical_ratio = (price - cost) / price

    # Compute std from corrected history
    if len(corrected_history) > 5:
        same_dow = []
        for i, val in enumerate(corrected_history):
            hist_day = (day - len(corrected_history) + i)
            if hist_day % 7 == day_of_week:
                same_dow.append(val)

        if len(same_dow) >= 4:
            demand_std = float(np.std(same_dow)) + 0.1
        else:
            demand_std = float(np.std(corrected_history[-14:])) + 0.1
    else:
        demand_std = smoothed_demand * 0.3

    # Normal quantile approximation
    # critical_ratio for orchids ~ 0.667, roses ~ 0.68, tulips ~ 0.714
    z_approx = -0.5 + (critical_ratio - 0.5) * 4.0
    z_approx = float(np.clip(z_approx, -1.0, 3.0))

    order_qty = smoothed_demand + z_approx * demand_std

    # === PRODUCT-SPECIFIC SAFETY FLOORS ===
    if product == 'orchids':
        order_qty = max(order_qty, 10)

    if product == 'roses' and 30 <= day <= 55:
        order_qty = max(order_qty, 20)

    if product == 'lilies' and 125 <= day <= 140:
        order_qty = max(order_qty, 15)

    # === HARD CAPS ===
    max_order = {
        'roses':       65,
        'tulips':      50,
        'orchids':     20,
        'sunflowers':  40,
        'lilies':      40,
    }

    order_qty = min(order_qty, float(max_order[product]))
    order_qty = max(order_qty, 0.0)

    return int(round(order_qty))