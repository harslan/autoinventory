import numpy as np

BASE = {'roses': 25, 'tulips': 20, 'orchids': 8, 'sunflowers': 15, 'lilies': 18}

VALENTINES = 44    # Feb 14
MOTHERS_DAY = 132  # 2nd Sunday in May (May 13)

# Exclude the full elevated-demand window from each product's history
EXCL = {
    'roses': set(range(VALENTINES - 3, VALENTINES + 2)),       # 41-45
    'tulips': set(),
    'orchids': set(range(MOTHERS_DAY - 3, MOTHERS_DAY + 4)),  # 130-134
    'sunflowers': set(),
    'lilies': set(range(MOTHERS_DAY - 3, MOTHERS_DAY + 4)),   # 130-134
}


def compute_order(day, product, sales_history, order_history):
    n = len(sales_history)
    dow = day % 7
    is_weekend = dow >= 5
    excl = EXCL[product]

    # --- Demand estimate: group weekdays/weekends, exclude holiday outliers ---
    if n >= 7:
        if is_weekend:
            grp_idx = [i for i in range(n) if i % 7 >= 5 and i not in excl]
        else:
            grp_idx = [i for i in range(n) if i % 7 < 5 and i not in excl]

        if len(grp_idx) >= 3:
            g_s = [sales_history[i] for i in grp_idx[-15:]]
            g_o = [order_history[i] for i in grp_idx[-15:]]
            n_so = sum(s >= o for s, o in zip(g_s, g_o))
            inflate = 1.0 + 0.3 * n_so / len(g_s)
            alpha = 0.25 if product == 'sunflowers' else 0.1
            w = np.exp(alpha * np.arange(len(g_s)))
            est = float(np.average(g_s, weights=w)) * inflate
        else:
            r_idx = [i for i in range(n) if i not in excl][-14:]
            r_s = [sales_history[i] for i in r_idx]
            r_o = [order_history[i] for i in r_idx]
            n_so = sum(s >= o for s, o in zip(r_s, r_o))
            inflate = 1.0 + 0.3 * n_so / max(1, len(r_s))
            est = float(np.mean(r_s)) * inflate if r_s else float(BASE[product])
            if is_weekend:
                est *= 1.5
    else:
        # Cold-start: use slightly higher defaults to reduce early stockouts
        cold = {'roses': 30, 'tulips': 24, 'orchids': 10, 'sunflowers': 18, 'lilies': 22}
        est = float(cold[product])
        if is_weekend:
            est *= 1.5

    # --- Special day boosts ---
    if product == 'roses':
        dt = VALENTINES - day
        if dt == 0:
            est = max(est * 8.0, 190)
        elif -1 <= dt <= 3:
            est *= 2.7

    if product in ('orchids', 'lilies'):
        dm = MOTHERS_DAY - day
        if dm == 0:
            est *= 3.0

    # Spring ramp-up (Apr-May: days 90-129) - all products
    if 60 <= day <= 150:
        est *= 1.05

    # Summer transition boost for sunflowers (Jun 1-15 only: days 151-165)
    if product == 'sunflowers' and 151 <= day <= 165:
        est *= 1.9
    # Post-summer dampener for sunflowers (Sep: days 243-260)
    elif product == 'sunflowers' and 240 <= day <= 265:
        est *= 0.75

    return max(0, min(600, int(round(est))))
