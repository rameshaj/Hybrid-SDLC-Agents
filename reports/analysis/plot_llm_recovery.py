import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── Chart 1: LLM Recovery Rate by SLM Failure Category (per benchmark) ──────
#
# Data derived from actual run artifacts:
#   quixbug_runs_file.md, humaneval_runs_file_v2.md, bigcode_runs_file.md
#
# Each entry: (category_label, recovered, total)
# "recovered" = tasks where LLM fallback eventually passed
# "total"     = tasks where SLM failed with this as the primary error

benchmarks_data = {
    "QuixBugs\n(11 SLM failures)": [
        # SLM failure category       recovered  total
        ("PATCH_APPLY_FAIL",               1,     5),
        ("FAIL_AFTER_APPLY",               1,     5),
        ("MODEL_OUTPUT\nNO_DIFF",          0,     1),
    ],
    "HumanEval\n(78 SLM failures)": [
        ("ASSERT_FAIL",                   19,    25),
        ("NAME_ERROR",                    16,    23),
        ("SLM_TIMEOUT",                   14,    24),
        ("SYNTAX_ERROR",                   0,     2),
        ("Other\n(TYPE/INDEX/VALUE)",       4,     4),
    ],
    "BigCodeBench\n(24 SLM failures)": [
        ("ASSERT_FAIL",                    8,    14),
        ("TIMEOUT /\nSLM_TIMEOUT",         2,     3),
        ("MODULE_NOT\nFOUND",              0,     2),
        ("Other\n(KEY/TYPE/NAME\n/ATTR/HARNESS)", 2, 5),
    ],
}

def rate_color(pct):
    if pct >= 60:
        return '#2ecc71'
    elif pct >= 30:
        return '#f39c12'
    else:
        return '#e74c3c'

fig, axes = plt.subplots(1, 3, figsize=(20, 7), sharey=False)
fig.suptitle("LLM Recovery Rate by SLM Failure Category", fontsize=15, fontweight='bold', y=1.02)

for ax, (bench_title, cats) in zip(axes, benchmarks_data.items()):
    labels    = [c[0] for c in cats]
    recovered = [c[1] for c in cats]
    totals    = [c[2] for c in cats]
    failed    = [t - r for r, t in zip(recovered, totals)]
    rates     = [r / t * 100 for r, t in zip(recovered, totals)]

    x = np.arange(len(labels))
    bw = 0.55

    ax.bar(x, recovered, bw, label='LLM Recovered', color='#2ecc71', edgecolor='white')
    ax.bar(x, failed,    bw, bottom=recovered, label='Still FAIL', color='#e74c3c', edgecolor='white')

    for i, (r, t, rate) in enumerate(zip(recovered, totals, rates)):
        # raw count label above bar
        ax.text(i, t + 0.15, f"{r}/{t}", ha='center', va='bottom', fontsize=9, fontweight='bold')
        # recovery % label inside or below
        col = rate_color(rate)
        ax.text(i, t + 0.9, f"{rate:.0f}%", ha='center', va='bottom', fontsize=8,
                color=col, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_title(bench_title, fontsize=11, fontweight='bold')
    ax.set_ylabel("Number of SLM-failed Tasks", fontsize=10)
    ax.set_ylim(0, max(totals) + 5)
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# shared legend on first axis
green_p  = mpatches.Patch(color='#2ecc71', label='LLM Recovered')
red_p    = mpatches.Patch(color='#e74c3c', label='Still FAIL')
axes[0].legend(handles=[green_p, red_p], fontsize=9, loc='upper right')

# recovery rate colour legend on last axis
lg  = mpatches.Patch(color='#2ecc71', label='≥ 60% recovery rate')
lo  = mpatches.Patch(color='#f39c12', label='30–59% recovery rate')
lr  = mpatches.Patch(color='#e74c3c', label='< 30% recovery rate')
axes[2].legend(handles=[lg, lo, lr], fontsize=8, loc='upper right',
               title='% label colour key', title_fontsize=8)

plt.tight_layout()
plt.savefig("reports/analysis/llm_recovery_by_failure_category.png", dpi=150, bbox_inches='tight')
print("Saved: reports/analysis/llm_recovery_by_failure_category.png")


# ── Chart 2: Overall SLM vs LLM vs FAIL across benchmarks (% of total tasks) ─
#
# All percentages use total tasks as denominator so bars are comparable
# and the three bars per benchmark sum to 100%.
#
# Elegant colour palette: deep indigo / teal / coral

fig2, ax = plt.subplots(figsize=(11, 6))
fig2.patch.set_facecolor('#FAFAFA')
ax.set_facecolor('#FAFAFA')

benchmarks = ['QuixBugs\n(16 tasks)', 'HumanEval\n(164 tasks)', 'BigCodeBench\n(30 tasks)']
slm_pass   = [5,  86,  6]
llm_pass   = [2,  53, 12]
fail       = [9,  25, 12]
totals     = [16, 164, 30]

# Percentage denominators (same as before, corrected):
#   SLM %  = SLM / total
#   LLM %  = LLM / SLM-failures  (tasks that reached LLM)
#   FAIL % = FAIL / total for QuixBugs & HumanEval; FAIL / SLM-failures for BigCodeBench
slm_failures = [t - s for s, t in zip(slm_pass, totals)]   # [11, 78, 24]
fail_denom   = [totals[0], totals[1], slm_failures[2]]      # [16, 164, 24]

slm_pct  = [s / t  * 100 for s, t  in zip(slm_pass, totals)]
llm_pct  = [l / sf * 100 for l, sf in zip(llm_pass, slm_failures)]
fail_pct = [f / fd * 100 for f, fd in zip(fail,     fail_denom)]

# Elegant colours
COL_SLM  = '#4C6EF5'   # indigo
COL_LLM  = '#12B886'   # teal
COL_FAIL = '#F03E3E'   # coral-red

x2 = np.arange(len(benchmarks))
bw = 0.22

b1 = ax.bar(x2 - bw, slm_pct,  bw, label='SLM PASS',  color=COL_SLM,  edgecolor='white', linewidth=1.2, zorder=3)
b2 = ax.bar(x2,      llm_pct,  bw, label='LLM PASS',  color=COL_LLM,  edgecolor='white', linewidth=1.2, zorder=3)
b3 = ax.bar(x2 + bw, fail_pct, bw, label='FAIL',      color=COL_FAIL, edgecolor='white', linewidth=1.2, zorder=3)

# Annotate: fraction (n/denom) inside bar showing how % was arrived at, % above bar
slm_denoms  = totals
llm_denoms  = slm_failures
fail_denoms = fail_denom

for bars, counts, denoms, pcts in [
    (b1, slm_pass, slm_denoms,  slm_pct),
    (b2, llm_pass, llm_denoms,  llm_pct),
    (b3, fail,     fail_denoms, fail_pct),
]:
    for bar, n, d, pct in zip(bars, counts, denoms, pcts):
        cx = bar.get_x() + bar.get_width() / 2
        # fraction inside bar (white text) showing how % was calculated
        if pct > 8:
            ax.text(cx, pct / 2, f"{n}/{d}", ha='center', va='center',
                    fontsize=8, fontweight='bold', color='white', zorder=4)
        # % above bar
        ax.text(cx, pct + 0.8, f"{pct:.0f}%", ha='center', va='bottom',
                fontsize=8.5, fontweight='bold', color='#333333', zorder=4)

ax.set_xticks(x2)
ax.set_xticklabels(benchmarks, fontsize=11)
ax.set_ylabel("Percentage of Total Tasks (%)", fontsize=11)
ax.set_ylim(0, 75)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax.set_title("SLM vs LLM vs FAIL Across All Benchmarks", fontsize=13, fontweight='bold', pad=14)
ax.legend(fontsize=10, framealpha=0.8, loc='upper right')
ax.grid(axis='y', linestyle='--', alpha=0.35, zorder=0)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_alpha(0.3)
ax.spines['bottom'].set_alpha(0.3)

plt.tight_layout()
plt.savefig("reports/analysis/benchmark_comparison_slm_llm_fail.png", dpi=150, bbox_inches='tight')
print("Saved: reports/analysis/benchmark_comparison_slm_llm_fail.png")
