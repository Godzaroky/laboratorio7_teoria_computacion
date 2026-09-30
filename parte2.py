import csv
import sys
import time

import matplotlib.pyplot as plt

SIZES = [1, 10, 100, 1000, 10000, 100000, 1000000]
MAX_OPERATIONS = int(float(sys.argv[1])) if len(sys.argv) > 1 else 10**9


def run_a(n):
    counter = 0
    for i in range(n // 2, n + 1):
        for j in range(1, n - n // 2 + 1):
            k = 1
            while k <= n:
                counter += 1
                k *= 2
    return counter


def run_b(n):
    counter = 0
    if n <= 1:
        return counter
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            counter += 1
            break
    return counter


def run_c(n):
    counter = 0
    for i in range(1, n // 3 + 1):
        for j in range(1, n + 1, 4):
            counter += 1
    return counter


def expected_a(n):
    half = n - n // 2
    return (half + 1) * half * n.bit_length()


def expected_b(n):
    return n if n > 1 else 0


def expected_c(n):
    return (n // 3) * ((n + 3) // 4)


ALGORITHMS = {
    "a": (run_a, expected_a),
    "b": (run_b, expected_b),
    "c": (run_c, expected_c),
}


def profile():
    rows = []
    for name, (run, expected) in ALGORITHMS.items():
        seconds_per_operation = 0.0
        for n in SIZES:
            operations = expected(n)
            if operations <= MAX_OPERATIONS:
                start = time.perf_counter()
                counted = run(n)
                seconds = time.perf_counter() - start
                assert counted == operations
                if counted > 0:
                    seconds_per_operation = seconds / counted
                measured = True
            else:
                seconds = operations * seconds_per_operation
                measured = False
            rows.append({
                "algorithm": name,
                "n": n,
                "seconds": seconds,
                "operations": operations,
                "measured": measured,
            })
            status = "measured" if measured else "estimated"
            print(f"{name}  n={n:>9}  ops={operations:>18,}  t={seconds:.6f}s  ({status})", flush=True)
    return rows


def save_csv(rows, path):
    with open(path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def plot(rows, path):
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    for ax, name in zip(axes, ALGORITHMS):
        data = [r for r in rows if r["algorithm"] == name]
        ns = [r["n"] for r in data]
        seconds = [r["seconds"] for r in data]
        operations = [r["operations"] for r in data]

        ax.plot(ns, seconds, "o-", color="tab:blue", label="Real time (s)")
        estimated = [r for r in data if not r["measured"]]
        if estimated:
            ax.plot([r["n"] for r in estimated], [r["seconds"] for r in estimated],
                    "o", markerfacecolor="white", color="tab:blue", label="Estimated time (s)")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("n")
        ax.set_ylabel("Seconds", color="tab:blue")

        ops_axis = ax.twinx()
        positive = [(n, o) for n, o in zip(ns, operations) if o > 0]
        ops_axis.plot([p[0] for p in positive], [p[1] for p in positive],
                      "s--", color="tab:red", label="Operations")
        ops_axis.set_yscale("log")
        ops_axis.set_ylabel("Operations", color="tab:red")

        lines = ax.get_legend_handles_labels()
        ops_lines = ops_axis.get_legend_handles_labels()
        ax.legend(lines[0] + ops_lines[0], lines[1] + ops_lines[1], loc="upper left")
        ax.set_title(f"Algorithm {name}")
        ax.grid(True, which="both", alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=150)


if __name__ == "__main__":
    results = profile()
    save_csv(results, "Lab7_24170_Gonzalez_results.csv")
    plot(results, "Lab7_24170_Gonzalez_graphs.png")