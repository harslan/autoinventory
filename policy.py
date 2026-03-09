import numpy as np

BASE = {'roses': 25, 'tulips': 20, 'orchids': 8, 'sunflowers': 15, 'lilies': 18}

VALENTINES = 44    # Feb 14
MOTHERS_DAY = 132  # 2nd Sunday in May (May 13)


def compute_order(day, product, sales_history, order_history):
    n = len(sales_history)
    dow = day % 7
    is_weekend = dow >= 5

    # --- Demand estimate: group weekdays/weekends together ---
    if n >= 7:
        if is_weekend:
            grp_idx = [i for i in range(n) if i % 7 >= 5]
        else:
            grp_idx = [i for i in range(n) if i % 7 < 5]

        if len(grp_idx) >= 3:
            g_s = [sales_history[i] for i in grp_idx[-10:]]
            g_o = [order_history[i] for i in grp_idx[-10:]]
            n_so = sum(s >= o for s, o in zip(g_s, g_o))
            inflate = 1.0 + 0.4 * n_so / len(g_s)
            est = float(np.mean(g_s)) * inflate
        else:
            r_s = sales_history[-14:]
            r_o = order_history[-14:]
            n_so = sum(s >= o for s, o in zip(r_s, r_o))
            inflate = 1.0 + 0.4 * n_so / len(r_s)
            est = float(np.mean(r_s)) * inflate
            if is_weekend:
                est *= 1.5
    else:
        est = float(BASE[product])
        if is_weekend:
            est *= 1.5

    # --- Special day boosts ---
    if product == 'roses':
        dt = VALENTINES - day
        if dt == 0:
            est = max(est * 5.0, 130)
        elif -2 <= dt <= 3:
            est *= 2.0

    if product in ('orchids', 'lilies'):
        dm = MOTHERS_DAY - day
        if dm == 0:
            est *= 3.0
        elif -2 <= dm <= 3:
            est *= 1.8

    # Summer sunflower boost (Jun 1 – Aug 31: days 151–242)
    if product == 'sunflowers' and 151 <= day <= 242:
        est *= 1.3

    return max(0, min(600, int(round(est))))
