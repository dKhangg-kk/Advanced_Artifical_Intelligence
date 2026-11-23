"""Rebuild K4 tables, figures and report numbers from immutable raw logs."""
from __future__ import annotations

import csv
from math import isclose
from pathlib import Path

from connect_four.evaluation.match import GameRecord
from connect_four.evaluation.metrics import mean, p95
from connect_four.evaluation.runlog import REPORT_NUMBER_FIELDS, write_csv
from run_search_ablations import summarize_match


def read_csv(path):
    with Path(path).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def rebuild(experiment):
    """Verify stored summaries against position/game/move logs; return numeric rows."""
    table_path = Path(f"results/tables/ablation_{experiment}_results.csv")
    summaries = read_csv(table_path)
    result = []
    for row in summaries:
        raw = read_csv(row["raw_log_path"])
        if row["phase"] == "positions":
            subset = [r for r in raw if r["status"] == "measured" and
                      all(r[k] == row[k] for k in ("depth", "pruning", "ordering"))]
            calculated = dict(measurements=len(subset), positions=len({r['position_id'] for r in subset}),
                mean_nodes=mean([float(r['nodes']) for r in subset]),
                mean_ms=mean([float(r['time_ms']) for r in subset]),
                p95_ms=p95([float(r['time_ms']) for r in subset]))
        else:
            moves = read_csv(row['moves_log_path'])
            records = []
            for g in raw:
                own = [m for m in moves if m['game_id'] == g['game_id'] and m['agent'] == g['agent_a']]
                records.append(GameRecord(g['agent_a'], g['agent_b'], bool(int(g['a_starts'])),
                    opening_id=int(g['opening_id']), winner={'a':1,'b':2,'draw':None}[g['winner']],
                    times_ms_a=[float(m['time_ms']) for m in own],
                    nodes_a=sum(int(m['nodes']) for m in own),
                    simulations_a=sum(int(m['simulations']) for m in own)))
            manifest = next(m for m in read_csv('results/logs/run_manifest.csv') if m['run_id'] == row['run_id'])
            calculated = summarize_match(records, int(manifest['seed']))
        for key, value in calculated.items():
            if not isclose(float(row[key]), value, rel_tol=1e-10, abs_tol=1e-10):
                raise AssertionError(f"{experiment}: {key} differs from raw log")
        numeric = {k: int(row[k]) for k in ('depth','simulations','pruning','ordering') if row.get(k)}
        result.append(dict(row, **numeric, **calculated))
    return result


def report_rows(tables):
    """Every displayed K4 number has a raw source and a filter."""
    rows = []
    for exp, table in tables.items():
        for r in table:
            parts = [r['phase']] + [f'{k}{r[k]}' for k in ('depth','simulations','pruning','ordering') if str(r.get(k,'')) != '']
            label = '_'.join(parts)
            source_filter = ';'.join(f'{k}={r[k]}' for k in ('phase','depth','simulations','pruning','ordering') if str(r.get(k,'')) != '')
            for key in ('measurements','positions','mean_nodes','mean_ms','p95_ms','games','wins','draws','losses',
                        'win_rate','score','score_ci_low','score_ci_high','win_wilson_low','win_wilson_high',
                        'mean_simulations','wins_as_first','wins_as_second'):
                if r.get(key, '') == '':
                    continue
                unit = 'ms/move' if key.endswith('_ms') else 'ratio' if key in ('win_rate','score') or '_ci_' in key or 'wilson' in key else 'count'
                rows.append(dict(report_section='4.5', metric=f'{exp}_{label}_{key}', value=r[key], unit=unit,
                    type='derived', source_type='table', source_path=f'results/tables/{r["run_id"]}.csv',
                    source_filter=source_filter, formula=key, run_id=r['run_id']))
    if all(k in tables for k in ('a1','a2','a5')):
        baseline = next(r for r in tables['a1'] if r['depth']==6 and r['pruning']==0 and r['ordering']==0)
        pruned = next(r for r in tables['a1'] if r['depth']==6 and r['pruning']==1 and r['ordering']==1)
        for metric, value, formula in (
            ('a1_depth6_nodes_reduction_percent', 100*(1-pruned['mean_nodes']/baseline['mean_nodes']), '100*(1-mean_nodes[p1o1]/mean_nodes[p0o0])'),
            ('a1_depth6_time_speedup', baseline['mean_ms']/pruned['mean_ms'], 'mean_ms[p0o0]/mean_ms[p1o1]'),
        ):
            rows.append(dict(report_section='4.5', metric=metric, value=value,
                unit='percent' if metric.endswith('percent') else 'times', type='derived', source_type='table',
                source_path=f'results/tables/{baseline["run_id"]}.csv', source_filter='depth=6;compare pruning/ordering=0/0 to 1/1',
                formula=formula, run_id=baseline['run_id']))
    return rows


def analyze():
    """Regenerate figures and add verified rows without changing other experiments."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    tables = {exp: rebuild(exp) for exp in ('a1','a2','a5')}
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11})
    out = Path('results/figures')
    out.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    for p, o in [(0,0),(0,1),(1,0),(1,1)]:
        rows = [r for r in tables['a1'] if r['pruning']==p and r['ordering']==o]
        for ax, key in zip(axes, ('mean_nodes','mean_ms')):
            ax.plot([r['depth'] for r in rows], [r[key] for r in rows], marker='o', label=f'Pruning={p}, ordering={o}')
            ax.set_xlabel('Search depth'); ax.set_yscale('log'); ax.grid(alpha=.2)
    axes[0].set_ylabel('Mean nodes / position'); axes[1].set_ylabel('Mean ms / position')
    axes[0].legend(fontsize=8); fig.suptitle('A1: pruning and move ordering');fig.tight_layout()
    fig.savefig(out/'ablation_a1_search.png',dpi=180);plt.close(fig)
    for exp in ('a2','a5'):
        rows=[r for r in tables[exp] if r['phase']=='games']
        param='simulations' if exp=='a2' else 'depth'
        x=[r[param] for r in rows]; y=[r['score'] for r in rows]
        fig, axes=plt.subplots(1,2,figsize=(11,4.4))
        axes[0].errorbar(x,y,yerr=[[r['score']-r['score_ci_low'] for r in rows],
                                  [r['score_ci_high']-r['score'] for r in rows]],fmt='o-',capsize=4)
        axes[0].set_ylabel('Score, paired bootstrap 95% CI');axes[0].set_ylim(-.05,1.05)
        axes[1].plot(x,[r['mean_ms'] for r in rows],'o-',label='Mean')
        axes[1].plot(x,[r['p95_ms'] for r in rows],'s--',label='P95 (nearest rank)')
        axes[1].set_ylabel('Measured ms / move');axes[1].legend()
        for ax in axes: ax.set_xlabel(param); ax.grid(alpha=.2)
        fig.suptitle('A2: MCTS vs Alpha-Beta depth 4' if exp=='a2' else 'A5: Alpha-Beta vs Heuristic')
        fig.tight_layout();fig.savefig(out/f'ablation_{exp}_search.png',dpi=180);plt.close(fig)
    new=report_rows(tables)
    current_ids={r['run_id'] for r in new}
    path=Path('results/tables/report_numbers.csv')
    old=read_csv(path)
    write_csv(path,REPORT_NUMBER_FIELDS,[r for r in old if r['run_id'] not in current_ids]+new)
    path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
    return tables


if __name__ == '__main__':
    tables=analyze()
    for exp, rows in tables.items():
        print(exp, len(rows), 'verified summary rows')
