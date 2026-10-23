#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

@dataclass
class MetricSpec:
    column: str
    label: str
    unit: str
    higher_is_better: bool

METRICS: List[MetricSpec] = [
    MetricSpec("latency_avg_ms", "Latência média", "ms", higher_is_better=False),
    MetricSpec("latency_med_ms", "Latência mediana", "ms", higher_is_better=False),
    MetricSpec("latency_p95_ms", "Latência p95", "ms", higher_is_better=False),
    MetricSpec("latency_p99_ms", "Latência p99", "ms", higher_is_better=False),
    MetricSpec("latency_max_ms", "Latência máxima", "ms", higher_is_better=False),
    MetricSpec("throughput_rps", "Throughput", "req/s", higher_is_better=True),
    MetricSpec("cpu_avg_pct", "Uso médio de CPU", "%", higher_is_better=False),
    MetricSpec("cpu_max_pct", "Pico de CPU", "%", higher_is_better=False),
    MetricSpec("mem_avg_mib", "Uso médio de memória", "MiB", higher_is_better=False),
    MetricSpec("mem_max_mib", "Pico de memória", "MiB", higher_is_better=False),
]

DASHBOARD_METRICS = ["latency_avg_ms", "throughput_rps", "cpu_avg_pct", "mem_avg_mib"]

PROTOCOL_COLORS = {"rest": "#d64545", "grpc": "#3468c0"}
PROTOCOL_LABELS = {"rest": "REST (JSON)", "grpc": "gRPC (Protobuf)"}

def load_results(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    expected_cols = {"protocol", "size", "repetition"}
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"Colunas esperadas ausentes no CSV: {missing}")

    if "latency_p99_or_max_ms" in df.columns and "latency_max_ms" not in df.columns:
        df = df.rename(columns={"latency_p99_or_max_ms": "latency_max_ms"})
    return df

def build_summary_table(df: pd.DataFrame) -> pd.DataFrame:

    rows = []
    sizes = sorted(df["size"].unique())

    for size in sizes:
        subset_size = df[df["size"] == size]
        for metric in METRICS:
            if metric.column not in df.columns:
                continue

            per_protocol = {}
            for protocol in ("rest", "grpc"):
                values = subset_size[subset_size["protocol"] == protocol][metric.column].dropna()
                if len(values) == 0:
                    continue
                per_protocol[protocol] = values

            p_value = None
            if "rest" in per_protocol and "grpc" in per_protocol:
                if len(per_protocol["rest"]) >= 2 and len(per_protocol["grpc"]) >= 2:

                    _, p_value = stats.ttest_ind(
                        per_protocol["rest"], per_protocol["grpc"], equal_var=False
                    )

            for protocol, values in per_protocol.items():
                rows.append(
                    {
                        "metric": metric.column,
                        "metric_label": metric.label,
                        "unit": metric.unit,
                        "size": size,
                        "protocol": protocol,
                        "mean": values.mean(),
                        "std": values.std(ddof=1) if len(values) > 1 else 0.0,
                        "n": len(values),
                        "p_value_vs_other_protocol": p_value,
                        "significant_at_0.05": (p_value is not None and p_value < 0.05),
                    }
                )

    return pd.DataFrame(rows)

def render_markdown_table(summary: pd.DataFrame) -> str:
    lines = ["| Métrica | Volume | REST (média ± dp) | gRPC (média ± dp) | p-valor | Significativo? |",
             "|---|---|---|---|---|---|"]

    for metric in METRICS:
        sub = summary[summary["metric"] == metric.column]
        for size in sorted(sub["size"].unique()):
            row = sub[sub["size"] == size]
            rest_row = row[row["protocol"] == "rest"]
            grpc_row = row[row["protocol"] == "grpc"]

            def fmt(r: pd.DataFrame) -> str:
                if r.empty:
                    return "—"
                return f"{r['mean'].values[0]:.2f} ± {r['std'].values[0]:.2f}"

            p_val = None
            if not row.empty:
                p_series = row["p_value_vs_other_protocol"].dropna()
                if not p_series.empty:
                    p_val = p_series.values[0]

            p_str = f"{p_val:.4f}" if p_val is not None else "—"
            sig_str = "✅ sim" if (p_val is not None and p_val < 0.05) else ("não" if p_val is not None else "—")

            lines.append(
                f"| {metric.label} ({metric.unit}) | {size:,} | {fmt(rest_row)} | {fmt(grpc_row)} | {p_str} | {sig_str} |"
            )

    return "\n".join(lines)

def plot_metric(summary: pd.DataFrame, metric: MetricSpec, output_path: Path, ax=None) -> None:
    sub = summary[summary["metric"] == metric.column]
    own_fig = ax is None
    if own_fig:
        fig, ax = plt.subplots(figsize=(7, 5))

    for protocol in ("rest", "grpc"):
        prot_data = sub[sub["protocol"] == protocol].sort_values("size")
        if prot_data.empty:
            continue
        ax.errorbar(
            prot_data["size"],
            prot_data["mean"],
            yerr=prot_data["std"],
            marker="o",
            capsize=4,
            label=PROTOCOL_LABELS[protocol],
            color=PROTOCOL_COLORS[protocol],
            linewidth=2,
        )

    ax.set_xscale("log")
    ax.set_xlabel("Volume de registros (escala log)")
    ax.set_ylabel(f"{metric.label} ({metric.unit})")
    ax.set_title(metric.label)
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    ax.legend()

    if own_fig:
        fig.tight_layout()
        fig.savefig(output_path, dpi=150)
        plt.close(fig)

def plot_dashboard(summary: pd.DataFrame, output_path: Path) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    metrics_by_col = {m.column: m for m in METRICS}

    for ax, col in zip(axes.flat, DASHBOARD_METRICS):
        plot_metric(summary, metrics_by_col[col], output_path=None, ax=ax)

    fig.suptitle("REST (JSON/HTTP1.1) vs gRPC (Protobuf/HTTP2) — carga progressiva", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

def print_headline_findings(summary: pd.DataFrame) -> None:
    print("\n=== Achados-chave (comparação REST vs gRPC por volume) ===\n")
    for metric_col in ["latency_avg_ms", "throughput_rps"]:
        metric = next(m for m in METRICS if m.column == metric_col)
        sub = summary[summary["metric"] == metric_col]
        print(f"--- {metric.label} ({metric.unit}) ---")
        for size in sorted(sub["size"].unique()):
            row = sub[sub["size"] == size]
            rest_row = row[row["protocol"] == "rest"]
            grpc_row = row[row["protocol"] == "grpc"]
            if rest_row.empty or grpc_row.empty:
                continue
            rest_mean = rest_row["mean"].values[0]
            grpc_mean = grpc_row["mean"].values[0]
            p_val = row["p_value_vs_other_protocol"].dropna()
            p_val = p_val.values[0] if not p_val.empty else None

            if rest_mean == 0:
                diff_pct = float("nan")
            else:
                diff_pct = (grpc_mean - rest_mean) / rest_mean * 100

            sig = "significativo (p<0.05)" if (p_val is not None and p_val < 0.05) else "NÃO significativo"
            print(
                f"  size={size:>7,}: REST={rest_mean:9.2f} | gRPC={grpc_mean:9.2f} "
                f"| gRPC vs REST: {diff_pct:+6.1f}% | {sig} (p={p_val:.4f})" if p_val is not None else
                f"  size={size:>7,}: REST={rest_mean:9.2f} | gRPC={grpc_mean:9.2f} | dados insuficientes p/ teste t"
            )
        print()

def main() -> int:
    parser = argparse.ArgumentParser(description="Análise estatística REST vs gRPC")
    parser.add_argument("--input", default="results.csv", help="Caminho do results.csv")
    parser.add_argument("--output-dir", default="analysis_output", help="Diretório de saída")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_results(args.input)
    summary = build_summary_table(df)

    summary_csv_path = output_dir / "summary_table.csv"
    summary.to_csv(summary_csv_path, index=False)
    print(f"Tabela resumo salva em {summary_csv_path}")

    md_path = output_dir / "summary_table.md"
    md_path.write_text(render_markdown_table(summary), encoding="utf-8")
    print(f"Tabela em Markdown salva em {md_path}")

    for metric in METRICS:
        if metric.column not in df.columns:
            continue
        chart_path = output_dir / f"chart_{metric.column}.png"
        plot_metric(summary, metric, chart_path)
        print(f"Gráfico salvo em {chart_path}")

    dashboard_path = output_dir / "dashboard.png"
    plot_dashboard(summary, dashboard_path)
    print(f"Dashboard salvo em {dashboard_path}")

    print_headline_findings(summary)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
