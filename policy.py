import numpy as np

BASE = {'roses': 25, 'tulips': 20, 'orchids': 8, 'sunflowers': 15, 'lilies': 18}

VALENTINES = 44    # Feb 14
MOTHERS_DAY = 132  # 2nd Sunday in May (May 13)

# Exclude the full elevated-demand window from each product's history
EXCL = {
    'roses': set(range(VALENTINES - 3, VALENTINES + 2)),       # 41-45
    'tulips': set(range(VALENTINES - 1, VALENTINES + 2)),      # 43-45
    'orchids': set(range(MOTHERS_DAY - 3, MOTHERS_DAY + 4)) | {VALENTINES},  # 130-134 + V-day
    'sunflowers': set(),
    'lilies': set(range(MOTHERS_DAY - 3, MOTHERS_DAY + 4)) | {VALENTINES},   # 130-134 + V-day
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
            inf_k = 0.18 if product == 'orchids' else (0.35 if product == 'tulips' else 0.3)
            inflate = 1.0 + inf_k * n_so / len(g_s)
            alpha = 0.3 if product == 'sunflowers' else (-0.1 if product == 'orchids' else (0.0 if product == 'lilies' else 0.1))
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
                est *= 1.4
    else:
        # Cold-start: use slightly higher defaults to reduce early stockouts
        cold = {'roses': 26, 'tulips': 24, 'orchids': 10, 'sunflowers': 18, 'lilies': 22}
        est = float(cold[product])
        if is_weekend:
            est *= 1.5

    # --- Special day boosts ---
    if product == 'roses':
        dt = VALENTINES - day
        if dt == 0:
            est = max(est * 7.5, 220)
        elif dt == 1:
            est *= 4.3
        elif dt == 2:
            est *= 1.05
        elif dt == -1:
            est *= 2.9

    if product in ('orchids', 'lilies') and VALENTINES - day == 0:
        est *= 2.6 if product == 'orchids' else 1.9
    elif product == 'orchids' and VALENTINES - day == 1:
        est *= 1.3
    elif product == 'orchids' and VALENTINES - day == -1:
        est *= 1.3
    elif product == 'orchids' and MOTHERS_DAY - day == -1:
        est *= 3.5
    elif product == 'lilies' and MOTHERS_DAY - day == -1:
        est *= 2.0

    if product == 'tulips' and VALENTINES - day == 0:
        est *= 3.8

    # Spring ramp-up (Apr-May: days 90-129) - all products
    if 60 <= day <= 150:
        est *= 1.05

    # Thanksgiving/fall boost
    if 315 <= day <= 332:
        est *= 1.1

    # Winter holiday boost
    if 340 <= day <= 364:
        est *= 1.05

    # Summer transition boost for sunflowers (Jun 1-15 only: days 151-165)
    if product == 'sunflowers' and 150 <= day <= 160:
        est *= 1.9
    # Post-summer dampener for sunflowers (Sep: days 243-260)
    elif product == 'sunflowers' and 240 <= day <= 265:
        est *= 0.75

    return max(0, min(600, int(round(est))))
