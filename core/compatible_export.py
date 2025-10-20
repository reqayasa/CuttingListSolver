import csv
import math
from collections import defaultdict
import pulp

# def _get_length(x):
#     """Helper: accept either object with .length or numeric"""
#     try:
#         return x.length
#     except Exception:
#         return x

# def _get_name(x, default_prefix="Item"):
#     """Try get name attribute if exists"""
#     try:
#         return x.name
#     except Exception:
#         return None

# def aggregate_and_export_from_trivial(trivial_patterns,
#                                     x_values,
#                                     required_parts_aggregated,
#                                     stocks_aggregated,
#                                     rounding_mode='round',
#                                     out_pattern_csv="pattern_summary.csv",
#                                     out_trace_csv="cut_trace_detail.csv",
#                                     out_summary_csv="summary_metrics.csv"):
#     """
#     Produce 3 CSVs from trivial pattern list and x_values.

#     Parameters
#     ----------
#     trivial_patterns : list of dict
#         Each dict as produced by your generate_trivial_patterns():
#         {
#             "stock_index": int,
#             "stock_length": int,
#             "pattern": tuple(int, int, ...),
#             "waste": int
#         }
#         Order must match x_values order.
#     x_values : list of float
#         LP solution values for each pattern entry (same order).
#     required_parts_aggregated : list
#         Each element either object with .length (and optional .name) or numeric length.
#     stocks_aggregated : list
#         Each element either object with .length (and optional .name) or numeric length.
#     rounding_mode : str
#         One of 'fractional'|'round'|'floor'|'ceil'. Determines how many integer instances to create per pattern.
#     out_* : filenames
#         Output CSV filenames.

#     Output
#     ------
#     Writes three CSV files:
#     - out_pattern_csv : pattern-level summary (pattern_id per unique pattern)
#     - out_trace_csv   : one row per pattern-instance (instance_id)
#     - out_summary_csv : global metrics key,value
#     """

#     # --- validate lengths
#     if len(trivial_patterns) != len(x_values):
#         raise ValueError("trivial_patterns and x_values must have same length")

#     # --- normalize parts lengths & names
#     part_lengths = [_get_length(p) for p in required_parts_aggregated]
#     part_names = [_get_name(p) for p in required_parts_aggregated]

#     # --- build grouped patterns by (pattern_tuple, stock_length)
#     grouped = {}  # key -> dict with aggregated info
#     # We'll assign pattern IDs P1, P2, ...
#     for idx, patt in enumerate(trivial_patterns):
#         key = (patt["pattern"], patt["stock_length"])
#         xj = float(x_values[idx]) if x_values is not None else 0.0
#         if key not in grouped:
#             grouped[key] = {
#                 "stock_length": patt["stock_length"],
#                 "pattern": patt["pattern"],
#                 "waste_per_piece": patt.get("waste", patt["stock_length"] - sum(a*b for a,b in zip(patt["pattern"], part_lengths))),
#                 "x_total": 0.0,
#                 "occurrences": 0,
#                 "source_indices": []
#             }
#         grouped[key]["x_total"] += xj
#         grouped[key]["occurrences"] += 1
#         grouped[key]["source_indices"].append(idx)

#     # assign pattern ids
#     pattern_list = []
#     for i, (key, info) in enumerate(grouped.items(), start=1):
#         pid = f"P{i}"
#         info["pattern_id"] = pid
#         pattern_list.append(info)

#     # --- Determine integer instance counts per pattern based on rounding_mode
#     # Keep both fractional_count and integer_count
#     for info in pattern_list:
#         frac = info["x_total"]
#         if rounding_mode == 'fractional':
#             info["count_int"] = 0  # no integer instances created
#             info["count_frac"] = frac
#         elif rounding_mode == 'round':
#             info["count_int"] = int(round(frac))
#             info["count_frac"] = frac
#         elif rounding_mode == 'floor':
#             info["count_int"] = int(math.floor(frac))
#             info["count_frac"] = frac
#         elif rounding_mode == 'ceil':
#             info["count_int"] = int(math.ceil(frac))
#             info["count_frac"] = frac
#         else:
#             raise ValueError("rounding_mode must be one of 'fractional','round','floor','ceil'")

#     # --- Build trace-detail rows (one row per instance). If rounding_mode == 'fractional', we will still
#     #     output one row with fractional qty in 'count' instead of many instances.
#     trace_rows = []
#     pattern_summary_rows = []

#     for info in pattern_list:
#         pat = info["pattern"]
#         stock_len = info["stock_length"]
#         leftover_one = info["waste_per_piece"]
#         pid = info["pattern_id"]
#         frac_count = info.get("count_frac", 0.0)
#         int_count = info.get("count_int", 0)

#         # pattern summary row (leftover is per single piece)
#         pattern_summary_rows.append({
#             "pattern_id": pid,
#             "stock_length": stock_len,
#             "cuts": tuple(pat),
#             "leftover": leftover_one,
#             "count": int_count if rounding_mode != 'fractional' else round(frac_count, 6),
#             "total_leftover": leftover_one * (int_count if rounding_mode != 'fractional' else frac_count)
#         })

#         # trace detail:
#         if rounding_mode == 'fractional':
#             # single aggregated trace row (indicates fractional usage)
#             trace_rows.append({
#                 "pattern_id": pid,
#                 "instance_id": pid + "_FRAC",
#                 "stock_source": "main",
#                 "stock_length": stock_len,
#                 "cuts": tuple(pat),
#                 "count_fractional": round(frac_count, 6),
#                 "leftover": leftover_one
#             })
#         else:
#             # produce instance rows repeated int_count times
#             for k in range(int_count):
#                 inst_id = f"{pid}_{k+1}"
#                 trace_rows.append({
#                     "pattern_id": pid,
#                     "instance_id": inst_id,
#                     "stock_source": "main",
#                     "stock_length": stock_len,
#                     "cuts": tuple(pat),
#                     "leftover": leftover_one
#                 })

#     # --- compute global metrics
#     total_patterns_instances = sum(r["count"] for r in pattern_summary_rows)
#     total_stock_used = sum(r["stock_length"] * r["count"] for r in pattern_summary_rows)
#     total_cut_length = sum(sum(r["cuts"]) * r["count"] for r in pattern_summary_rows)
#     total_waste = sum(r["total_leftover"] for r in pattern_summary_rows)
#     total_items_cut = sum(len(r["cuts"]) * r["count"] for r in pattern_summary_rows)
#     waste_ratio = (total_waste / total_stock_used * 100) if total_stock_used > 0 else 0.0
#     efficiency = 100 - waste_ratio

#     metrics = {
#         "total_patterns": int(total_patterns_instances),
#         "total_stock_used": total_stock_used,
#         "total_cut_length": total_cut_length,
#         "total_waste": total_waste,
#         "waste_ratio": round(waste_ratio, 4),
#         "efficiency": round(efficiency, 4),
#         "lower_bound": "",  # user may supply LB/UB if available
#         "upper_bound": "",
#         "total_items_cut": int(total_items_cut)
#     }

#     # --- WRITE pattern_summary.csv
#     with open(out_pattern_csv, mode="w", newline="") as f:
#         writer = csv.writer(f)
#         writer.writerow(["pattern_id", "stock_length", "cuts", "leftover", "count", "total_leftover"])
#         for r in pattern_summary_rows:
#             writer.writerow([r["pattern_id"], r["stock_length"], r["cuts"], r["leftover"], r["count"], r["total_leftover"]])

#     # --- WRITE cut_trace_detail.csv
#     with open(out_trace_csv, mode="w", newline="") as f:
#         writer = csv.writer(f)
#         writer.writerow(["pattern_id", "instance_id", "stock_source", "stock_length", "cuts", "leftover", "count_fractional"])
#         for tr in trace_rows:
#             # ensure count_fractional exists (for non-fractional rows will be empty)
#             cf = tr.get("count_fractional", "")
#             writer.writerow([tr["pattern_id"], tr["instance_id"], tr["stock_source"], tr["stock_length"], tr["cuts"], tr["leftover"], cf])

#     # --- WRITE summary_metrics.csv
#     with open(out_summary_csv, mode="w", newline="") as f:
#         writer = csv.writer(f)
#         writer.writerow(["key", "value"])
#         for k, v in metrics.items():
#             writer.writerow([k, v])

#     print(f"Exported: {out_pattern_csv}, {out_trace_csv}, {out_summary_csv}")
#     return {
#         "pattern_summary": pattern_summary_rows,
#         "trace_rows": trace_rows,
#         "metrics": metrics
#     }


def export_pattern_summary(self, patterns, x_values, required_parts_aggregated, output_folder="output"):
    part_types = [p.part_type for p in required_parts_aggregated]
    part_lengths = [p.length for p in required_parts_aggregated]

    summary_path = f"{output_folder}/pattern_summary.csv"
    with open(summary_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pattern_id", "stock_length", "cuts_detail", "leftover", "count"])

        for j, p in enumerate(patterns):
            x_val = pulp.value(x_values[j])
            if x_val is None or x_val <= 1e-8:
                continue

            int_part = int(math.floor(x_val))
            frac_part = x_val - int_part

            cuts_desc = []
            for idx, qty in enumerate(p["pattern"]):
                if qty > 0:
                    cuts_desc.append(f"{qty}×{part_types[idx]} ({part_lengths[idx]})")
            cuts_str = " + ".join(cuts_desc)

            # --- tulis bagian integer ---
            if int_part > 0:
                writer.writerow([
                    f"P{j+1}",
                    p["stock_length"],
                    cuts_str,
                    p["waste"],
                    int_part
                ])

            # --- tulis bagian fractional jika ada ---
            if frac_part > 1e-6:
                writer.writerow([
                    f"P{j+1}_frac",
                    p["stock_length"],
                    cuts_str,
                    p["waste"],
                    round(frac_part, 3)
                ])

    # === CUT TRACE DETAIL ===
    detail_path = f"{output_folder}/cut_trace_detail.csv"
    with open(detail_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pattern_id", "instance_id", "stock_source", "stock_length", "part_type", "cut_length", "leftover"])

        for j, p in enumerate(patterns):
            x_val = pulp.value(x_values[j])
            if x_val is None or x_val <= 1e-8:
                continue

            int_part = int(math.floor(x_val))
            frac_part = x_val - int_part
            pattern_id = f"P{j+1}"

            # --- tulis bagian integer ---
            for inst in range(int_part):
                instance_id = f"{pattern_id}_{inst+1}"
                for idx, qty in enumerate(p["pattern"]):
                    for _ in range(qty):
                        writer.writerow([
                            pattern_id,
                            instance_id,
                            "main" if p["stock_index"] == 0 else f"stock_{p['stock_index']}",
                            p["stock_length"],
                            part_types[idx],
                            part_lengths[idx],
                            p["waste"] if _ == qty - 1 else 0
                        ])

            # --- tulis bagian fractional ---
            if frac_part > 1e-6:
                instance_id = f"{pattern_id}_frac"
                for idx, qty in enumerate(p["pattern"]):
                    if qty > 0:
                        writer.writerow([
                            f"{pattern_id}_frac",
                            instance_id,
                            "main" if p["stock_index"] == 0 else f"stock_{p['stock_index']}",
                            p["stock_length"],
                            part_types[idx],
                            part_lengths[idx],
                            p["waste"]
                        ])