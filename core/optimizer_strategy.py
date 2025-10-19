from abc import ABC, abstractmethod
from math import floor
from pprint import pprint
import pulp
from collections import defaultdict

class OptimizerStrategy(ABC):
    @abstractmethod
    def optimize(self, required_parts_aggregated, stocks_aggregated):
        pass

class ColumnGeneration(OptimizerStrategy):
    def optimize(self, required_parts_aggregated, stocks_aggregated):
        # ---------------------------
        # Build initial patterns
        # ---------------------------
        patterns = self.generate_trivial_patterns(required_parts_aggregated, stocks_aggregated)
        # ensure at least one pattern exists (should be, unless some item longer than all stocks)
        if not patterns:
            raise ValueError("No trivial patterns (check item vs stock lengths).")

        # ---------------------------
        # Column generation loop
        # ---------------------------
        TOL = 1e-8
        max_iters = 200

        part_lengths = []
        for part in required_parts_aggregated:
            part_lengths.append(part.length)
        demands = []
        for part in required_parts_aggregated:
            demands.append(part.quantity)
        stock_lengths = []
        for stock in stocks_aggregated:
            stock_lengths.append(stock.length)
        stock_limits = []
        for stock in stocks_aggregated:
            stock_limits.append(stock.quantity)
        stock_costs = []
        for stock in stocks_aggregated:
            stock_costs.append(stock.length)

        for it in range(max_iters):
            # Build RMP (LP)
            prob = pulp.LpProblem("RMP", pulp.LpMinimize)
            x_vars = []
            for j, patt in enumerate(patterns):
                x = pulp.LpVariable(f"x_{j}", lowBound=0, cat="Continuous")
                x_vars.append(x)
            # objective: sum of x_j * cost_of_stock_type
            prob += pulp.lpSum(x_vars[j] * stock_costs[patterns[j]["stock_index"]] for j in range(len(patterns)))
            # constraints: for each item i, sum_j a_ij * x_j >= demand_i
            constraints = []
            for i in range(len(part_lengths)):
                cons = pulp.lpSum(patterns[j]["pattern"][i] * x_vars[j] for j in range(len(patterns))) >= demands[i]
                prob.addConstraint(cons, name=f"dem_{i}")

            for k in range(len(stock_lengths)):
                cons = pulp.lpSum(x_vars[j] for j, p in enumerate(patterns) if p["stock_index"] == k) <= stock_limits[k]
                # Ensure unique constraint name by appending iteration number
                prob.addConstraint(cons, name=f"stock_limit_{k}_it{it}")

            # solve LP
            solver = pulp.PULP_CBC_CMD(msg=False)
            res = prob.solve(solver)
            status = pulp.LpStatus[prob.status]
            if status not in ("Optimal", "Optimal Solution Found"):
                raise RuntimeError("LP solver did not return optimal. Status: " + status)
            obj = pulp.value(prob.objective)

            # Try to read duals (pi_i). Not all solvers expose duals via PuLP; handle gracefully.
            duals = []
            duals_ok = True
            try:
                for i in range(len(part_lengths)):
                    con = prob.constraints[f"dem_{i}"]
                    pi = con.pi  # dual value
                    duals.append(pi)
            except Exception as e:
                duals_ok = False
                # If duals not available, cannot continue classical column generation here.
                # We abort loop and inform user.
            if not duals_ok:
                raise RuntimeError(
                    "Solver did not provide duals via PuLP constraints. "
                    "Use a solver that returns duals (e.g., GLPK, CPLEX, Gurobi) or use Pyomo with a solver "
                    "supporting duals."
                )

            # Print iteration summary
            print(f"\nIteration {it+1}: LP objective = {obj:.6f}")
            print(" Current patterns (j : stock_idx, pattern, x_j):")
            for j, p in enumerate(patterns):
                val = pulp.value(x_vars[j])
                print(f"  j={j:2d} stock={p['stock_length']:4d} patt={p['pattern']} x={val:.4f}")

            # For each stock type, solve knapsack (maximize sum(pi_i * a_i))
            best_reduced = 0.0
            best_new_pattern = None
            for k, Lk in enumerate(stock_lengths):
                values = duals[:]    # value per item = pi_i
                weights = part_lengths[:]
                best_val, counts = self.solve_unbounded_knapsack(values, weights, Lk)
                reduced_cost = stock_costs[k] - best_val
                # We may want only integer counts >0 pattern
                if reduced_cost < best_reduced - TOL:
                    best_reduced = reduced_cost
                    best_new_pattern = {
                        "stock_index": k,
                        "stock_length": Lk,
                        "pattern": tuple(counts),
                        "waste": Lk - sum(c*w for c,w in zip(counts, weights))
                    }

            if best_new_pattern is None:
                print(" No improving pattern found for any stock type -> LP-optimal (relaxation) reached.")
                break
            else:
                # Add new pattern
                patterns.append(best_new_pattern)
                print(" Added new pattern:", best_new_pattern)
        else:
            print("Reached max iterations.")

        # Final LP solution summary
        print("\n=== Final LP solution ===")
        for j, p in enumerate(patterns):
            # if variable exists (some patterns might have been added after), try to display value
            try:
                xj = pulp.value(x_vars[j])
            except Exception:
                xj = None
            print(f" j={j:2d} stock={p['stock_length']:4d} patt={p['pattern']} x={xj}")

        # Display final patterns compactly
        print("\nFinal patterns list:")
        pprint(patterns)

        return patterns
        
        
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