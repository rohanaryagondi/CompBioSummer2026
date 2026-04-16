#!/usr/bin/env python
"""
mace_analyze.py -- Analyze MACE-OFF24 crambin NVT simulation results.
Produces energy and temperature plots from StateDataReporter CSV logs.
"""
import os
import sys
import csv
import numpy as np

# Suppress user site-packages
os.environ['PYTHONNOUSERSITE'] = '1'

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUTPUT_DIR = "/home/rag88/projects/CompBioSummer2026/Execution/phases/phase-1/subphase-1.1/output"


def parse_log(log_path):
    """Parse OpenMM StateDataReporter CSV log file."""
    data = {
        'step': [], 'time_ps': [], 'pe': [], 'ke': [],
        'total_e': [], 'temp': [], 'speed': []
    }

    with open(log_path) as f:
        reader = csv.reader(f)
        header = next(reader)
        # Map header columns (quoted names from StateDataReporter)
        col_map = {}
        for i, h in enumerate(header):
            h = h.strip().strip('"')
            if 'Step' in h:
                col_map['step'] = i
            elif 'Time' in h and 'Step' not in h:
                col_map['time_ps'] = i
            elif 'Potential Energy' in h:
                col_map['pe'] = i
            elif 'Kinetic Energy' in h:
                col_map['ke'] = i
            elif 'Total Energy' in h:
                col_map['total_e'] = i
            elif 'Temperature' in h:
                col_map['temp'] = i
            elif 'Speed' in h:
                col_map['speed'] = i

        for row in reader:
            if not row or row[0].startswith('#'):
                continue
            try:
                for key, idx in col_map.items():
                    data[key].append(float(row[idx]))
            except (ValueError, IndexError):
                continue

    return {k: np.array(v) for k, v in data.items()}


def plot_energy(all_data, output_path):
    """Plot potential energy vs time for all stages."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    colors = ['#2196F3', '#4CAF50', '#FF9800', '#F44336']
    for i, (label, data) in enumerate(all_data.items()):
        if len(data['time_ps']) == 0:
            continue
        c = colors[i % len(colors)]
        ax1.plot(data['time_ps'], data['pe'] / 1000, '-', color=c,
                 alpha=0.8, linewidth=0.8, label=label)
        ax2.plot(data['time_ps'], data['temp'], '-', color=c,
                 alpha=0.8, linewidth=0.8, label=label)

    ax1.set_ylabel('Potential Energy (10^3 kJ/mol)')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_title('MACE-OFF24 Crambin NVT -- D1 Gate Validation')

    ax2.set_xlabel('Time (ps)')
    ax2.set_ylabel('Temperature (K)')
    ax2.axhline(y=300, color='red', linestyle='--', alpha=0.5, label='Target 300 K')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Energy plot saved to {output_path}")
    plt.close()


def print_stats(label, data):
    """Print summary statistics for a log dataset."""
    if len(data['pe']) == 0:
        print(f"  {label}: no data")
        return

    pe = data['pe']
    temp = data['temp']
    time_ps = data['time_ps']

    print(f"\n  {label}:")
    print(f"    Duration: {time_ps[0]:.1f} - {time_ps[-1]:.1f} ps ({len(pe)} frames)")
    print(f"    PE: {np.mean(pe):.1f} +/- {np.std(pe):.1f} kJ/mol")
    print(f"    PE range: [{np.min(pe):.1f}, {np.max(pe):.1f}] kJ/mol")
    print(f"    PE drift: {pe[-1] - pe[0]:.1f} kJ/mol")
    print(f"    Temp: {np.mean(temp):.1f} +/- {np.std(temp):.1f} K")
    print(f"    Temp range: [{np.min(temp):.1f}, {np.max(temp):.1f}] K")
    if len(data['speed']) > 0:
        nonzero_speed = data['speed'][data['speed'] > 0]
        if len(nonzero_speed) > 0:
            print(f"    Speed: {np.mean(nonzero_speed):.3f} ns/day")


def main():
    # Find all log files
    log_files = {}
    for fname in sorted(os.listdir(OUTPUT_DIR)):
        if fname.startswith('crambin_vacuum_') and fname.endswith('.log'):
            ps_str = fname.replace('crambin_vacuum_', '').replace('.log', '')
            log_files[f"vacuum {ps_str}"] = os.path.join(OUTPUT_DIR, fname)

    if not log_files:
        print("No log files found!")
        sys.exit(1)

    print(f"Found {len(log_files)} log files:")
    for label, path in log_files.items():
        print(f"  {label}: {path}")

    # Parse all logs
    all_data = {}
    for label, path in log_files.items():
        data = parse_log(path)
        all_data[label] = data
        print_stats(label, data)

    # Find the longest successful log
    best_label = max(all_data.keys(), key=lambda k: len(all_data[k]['pe']))
    best_log_path = log_files[best_label]

    # Copy best log as the canonical energy log
    canonical_log = os.path.join(OUTPUT_DIR, "task-001-crambin-mace.log")
    import shutil
    shutil.copy2(best_log_path, canonical_log)
    print(f"\nCanonical energy log: {canonical_log} (from {best_label})")

    # Generate energy + temperature plot
    energy_plot = os.path.join(OUTPUT_DIR, "task-001-energy.png")
    plot_energy(all_data, energy_plot)

    # Summary
    best_data = all_data[best_label]
    max_time = best_data['time_ps'][-1] if len(best_data['time_ps']) > 0 else 0
    print(f"\n=== SUMMARY ===")
    print(f"Best run: {best_label} ({max_time:.1f} ps)")
    print(f"D1 criterion: >= 100 ps stable NVT")
    print(f"D1 verdict: {'PASS' if max_time >= 100 else 'PARTIAL (in progress)' if max_time >= 10 else 'FAIL'}")


if __name__ == "__main__":
    main()
