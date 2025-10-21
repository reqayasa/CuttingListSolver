import pulp
from core.optimizer_strategy.optimizer_strategy import OptimizerStrategy
from core.entities import Parts, Part, Stock

class ColumnGeneration(OptimizerStrategy):
    def optimize(self, required_parts_aggregated, stocks_aggregated):
        """
        Column Generation + Integer Recovery with Feasibility Correction
        ---------------------------------------------------------------
        Tahapan:
        1. Generate trivial patterns.
        2. Jalankan column generation (LP relax) sampai optimal.
        3. Jalankan integer master.
        - Jika infeasible → hasilkan pattern baru berdasarkan duals dari LP terakhir.
        - Ulangi sampai feasible atau tidak ada pattern baru yang berguna.
        """

        # =====================================================
        # 1️⃣ Generate trivial patterns
        # =====================================================
        patterns = self.generate_trivial_patterns(required_parts_aggregated, stocks_aggregated)
        if not patterns:
            raise ValueError("No trivial patterns (check item vs stock lengths).")

        # =====================================================
        # 2️⃣ Data dasar
        # =====================================================
        TOL = 1e-8
        MAX_LP_ITERS = 200
        MAX_INT_ITERS = 10  # batas tambahan pattern integer

        part_lengths = [p.length for p in required_parts_aggregated]
        demands = [p.quantity for p in required_parts_aggregated]
        stock_lengths = [s.length for s in stocks_aggregated]
        stock_limits = [s.quantity for s in stocks_aggregated]
        stock_costs = [s.length for s in stocks_aggregated]

        # =====================================================
        # 3️⃣ Column generation (LP relax)
        # =====================================================
        for it in range(MAX_LP_ITERS):
            # --- Build LP ---
            prob = pulp.LpProblem("RMP", pulp.LpMinimize)
            x_vars = []
            for j, patt in enumerate(patterns):
                x = pulp.LpVariable(f"x_{j}", lowBound=0, cat="Continuous")
                x_vars.append(x)

            # objective
            prob += pulp.lpSum(x_vars[j] * stock_costs[patterns[j]["stock_index"]] for j in range(len(patterns)))

            # demand constraints
            for i in range(len(part_lengths)):
                prob.addConstraint(
                    pulp.lpSum(patterns[j]["pattern"][i] * x_vars[j] for j in range(len(patterns))) >= demands[i],
                    name=f"dem_{i}"
                )

            # stock limits
            for k in range(len(stock_lengths)):
                prob.addConstraint(
                    pulp.lpSum(x_vars[j] for j, p in enumerate(patterns) if p["stock_index"] == k) <= stock_limits[k],
                    name=f"stock_limit_{k}_it{it}"
                )

            # --- Solve LP ---
            solver = pulp.PULP_CBC_CMD(msg=False)
            prob.solve(solver)
            status = pulp.LpStatus[prob.status]
            if status not in ("Optimal", "Optimal Solution Found"):
                raise RuntimeError(f"LP not optimal. Status: {status}")
            obj = pulp.value(prob.objective)

            # --- Duals (for subproblem) ---
            duals = []
            for i in range(len(part_lengths)):
                duals.append(prob.constraints[f"dem_{i}"].pi)
            self.last_duals = duals

            print(f"\nIteration {it+1}: LP Objective = {obj:.6f}")
            for j, p in enumerate(patterns):
                val = pulp.value(x_vars[j])
                print(f"  j={j:2d} stock={p['stock_length']:4d} patt={p['pattern']} x={val:.4f}")

            # --- Knapsack subproblem (column generation) ---
            best_reduced = 0.0
            best_new_pattern = None
            for k, Lk in enumerate(stock_lengths):
                values = duals[:]
                weights = part_lengths[:]
                best_val, counts = self.solve_unbounded_knapsack(values, weights, Lk)
                reduced_cost = stock_costs[k] - best_val
                if reduced_cost < best_reduced - TOL:
                    best_reduced = reduced_cost
                    best_new_pattern = {
                        "stock_index": k,
                        "stock_length": Lk,
                        "pattern": tuple(counts),
                        "waste": Lk - sum(c*w for c, w in zip(counts, weights))
                    }

            if best_new_pattern is None:
                print("No improving pattern found — LP relaxation optimal ✅")
                break
            else:
                print("Added new pattern:", best_new_pattern)
                patterns.append(best_new_pattern)
        else:
            print("Reached LP max iterations.")

        # LP selesai
        x_values = [pulp.value(x) for x in x_vars]
        print("\n=== LP Solution Done ===")

        # =====================================================
        # 4️⃣ Integer phase (feasibility repair)
        # =====================================================
        for int_iter in range(MAX_INT_ITERS):
            print(f"\n[Integer Phase] Attempt {int_iter+1}")
            x_int, status = self.solve_integer_master(
                patterns, part_lengths, demands, stock_lengths, stock_limits, stock_costs,
                use_active_only=False, x_lp=x_values, solver_msg=False
            )

            if status in ("Optimal", "Integer Feasible", "Optimal Solution Found"):
                print(f"Integer solution feasible ✅ (status={status})")
                return patterns, x_values, x_int

            print(f"Integer solution infeasible ❌ (status={status}), regenerating new pattern...")

            # --- Generate new column from duals again ---
            duals = getattr(self, "last_duals", None)
            if duals is None:
                print("No duals available for correction → abort.")
                break

            best_reduced = 0.0
            best_new_pattern = None
            for k, Lk in enumerate(stock_lengths):
                values = duals[:]
                weights = part_lengths[:]
                best_val, counts = self.solve_unbounded_knapsack(values, weights, Lk)
                reduced_cost = stock_costs[k] - best_val
                if reduced_cost < best_reduced - 1e-8:
                    best_reduced = reduced_cost
                    best_new_pattern = {
                        "stock_index": k,
                        "stock_length": Lk,
                        "pattern": tuple(counts),
                        "waste": Lk - sum(c*w for c,w in zip(counts, weights))
                    }

            if best_new_pattern is not None:
                print("Added new pattern to fix infeasibility:", best_new_pattern)
                patterns.append(best_new_pattern)
            else:
                print("No more improving pattern found, terminating.")
                break

        print("⚠️ Integer phase ended without feasible solution.")
        return patterns, x_values, x_int


        
    # Untuk kemudahan: tambahkan id pada pattern
    def pattern_id(p): return len(p)
        

    def generate_trivial_patterns(self, required_parts_aggregated, stocks_aggregated):
        trivial_patterns = []
        for stock_index, stock in enumerate(stocks_aggregated):
            for part_index, part in enumerate(required_parts_aggregated):
                qty = stock.length // part.length
                if qty > 0:
                    pattern = [0] * len(required_parts_aggregated)
                    pattern[part_index] = qty 
                    waste = stock.length - qty * part.length
                    trivial_patterns.append({
                        "stock_index": stock_index,
                        "stock_length": stock.length,
                        "pattern": tuple(pattern),
                        "waste": waste
                    })

        return trivial_patterns
    
    # ---------------------------
    # Helper: solve unbounded knapsack (maximize value)
    # returns (best_value, counts_list) where counts_list is int counts per item
    # unbounded so item can be chosen many times
    # Uses DP on capacity; time O(n * capacity)
    # ---------------------------
    
    def solve_unbounded_knapsack(self, values, weights, capacity):
        n = len(values)
        # dp[v] = max value achievable with capacity v
        dp = [-1e9] * (capacity + 1)
        dp[0] = 0
        # keep choice to reconstruct counts
        prev_choice = [-1] * (capacity + 1)
        for cap in range(1, capacity+1):
            for i in range(n):
                w = weights[i]
                if w <= cap:
                    val = dp[cap - w] + values[i]
                    if val > dp[cap]:
                        dp[cap] = val
                        prev_choice[cap] = i
        best_value = dp[capacity]
        # reconstruct counts greedily from prev_choice (unbounded)
        counts = [0]*n
        c = capacity
        while c > 0 and prev_choice[c] != -1:
            i = prev_choice[c]
            counts[i] += 1
            c -= weights[i]
        # Note: reconstruction gives one optimal packing for capacity; sometimes other capacities (< capacity) yield better value;
        # we should scan all cap<=capacity for best dp[cap]
        best_cap = max(range(capacity+1), key=lambda cap: dp[cap])
        best_value = dp[best_cap]
        # reconstruct from best_cap
        counts = [0]*n
        c = best_cap
        while c > 0 and prev_choice[c] != -1:
            i = prev_choice[c]
            counts[i] += 1
            c -= weights[i]
        return best_value, counts
    
    def solve_integer_master(self, patterns, part_lengths, demands,
                         stock_lengths, stock_limits, stock_costs,
                         use_active_only=False, x_lp=None, keep_only_positive_lp=True,
                         solver_msg=False):
        """
        Solve integer master using provided patterns (list of dict).
        parameters:
        - patterns: list of pattern dicts (must have 'pattern' tuple and 'stock_index','stock_length')
        - part_lengths: list[int]
        - demands: list[int]
        - stock_lengths, stock_limits, stock_costs: lists
        - use_active_only: if True, include only patterns where x_lp > 0 (requires x_lp passed)
        - x_lp: list of LP solution values (same order as patterns) - used if use_active_only True
        - keep_only_positive_lp: when use_active_only True, whether to include patterns with x_lp > tol
        returns:
        - x_int: list of integer counts per pattern (same order as patterns; 0 for excluded)
        - status: pulp status string
        """
        # select patterns to include
        include_mask = [True] * len(patterns)
        if use_active_only:
            if x_lp is None:
                raise ValueError("x_lp must be provided when use_active_only=True")
            tol = 1e-9
            include_mask = [(x_lp[i] > tol) if keep_only_positive_lp else True for i in range(len(patterns))]

        # build ILP
        prob = pulp.LpProblem("Integer_Master", pulp.LpMinimize)
        x_vars = []
        pattern_indices = []  # maps var index -> pattern index
        for j, p in enumerate(patterns):
            if not include_mask[j]:
                x_vars.append(None)
                continue
            var = pulp.LpVariable(f"X_int_{j}", lowBound=0, cat="Integer")
            # x_vars[j] = var
            x_vars.append(var)
            pattern_indices.append(j)

        # objective
        prob += pulp.lpSum((x_vars[j] if x_vars[j] is not None else 0) *
                        stock_costs[patterns[j]["stock_index"]] for j in range(len(patterns)))

        # demand constraints
        for i in range(len(part_lengths)):
            prob += pulp.lpSum(( (patterns[j]["pattern"][i]) * (x_vars[j] if x_vars[j] is not None else 0)
                                ) for j in range(len(patterns))) >= demands[i], f"dem_int_{i}"

        # stock limits constraints (if finite)
        for k in range(len(stock_lengths)):
            if stock_limits[k] is None:
                continue
            prob += pulp.lpSum((x_vars[j] if (x_vars[j] is not None and patterns[j]["stock_index"] == k) else 0)
                            for j in range(len(patterns))) <= stock_limits[k], f"stock_limit_int_{k}"

        # solve ILP (CBC default)
        solver = pulp.PULP_CBC_CMD(msg=solver_msg)
        res = prob.solve(solver)
        status = pulp.LpStatus[prob.status]

        if status not in ("Optimal", "Integer Feasible", "Optimal Solution Found"):
            # return zeros but include status so caller can handle
            x_int = [0] * len(patterns)
            return x_int, status

        x_int = [0] * len(patterns)
        for j in range(len(patterns)):
            if x_vars[j] is None:
                x_int[j] = 0
            else:
                x_int[j] = int(round(pulp.value(x_vars[j])))

        return x_int, status
