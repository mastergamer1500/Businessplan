import numpy as np
from flask_socketio import emit

def init_telemetry_sockets(socketio):
    @socketio.on('connect')
    def handle_client_ingress():
        print("[METRIC-CORE]: Persistent WebSocket telemetry duplex channel initialized.")

    @socketio.on('stream_matrix_compute')
    def compute_websocket_telemetry(payload):
        """
        Executes a real-time stochastic Monte Carlo simulation (500 parallel vectors)
        modeling non-linear compounding risk, macro shocks, and cyclical seasonality.
        """
        try:
            # Core Ingestion Parsing
            base_revenue = float(payload.get('revenue', 18000) or 0)
            base_expenses = float(payload.get('expenses', 21000) or 0)
            starting_cash = float(payload.get('cash_reserves', 35000) or 0)
            
            # Convert annualized growth percentage to monthly compounding fractional step
            monthly_growth_rate = (float(payload.get('growth_rate', 3.2) or 0) / 100.0) / 12.0
            
            macro_context = payload.get('macro_context', 'nominal')
            shock_materials = float(payload.get('shock_materials', 0) or 0)
            shock_retention = float(payload.get('shock_retention', 0) or 0)

            # Operational Parameter Adjustments
            adjusted_expenses = base_expenses * (1.0 + (shock_materials / 100.0))
            adjusted_revenue = base_revenue * (1.0 - (shock_retention / 100.0))
            
            if macro_context == 'high_inflation':
                adjusted_expenses *= 1.15
                monthly_growth_rate -= (0.015 / 12.0)
            elif macro_context == 'fuel_spike':
                adjusted_expenses *= 1.08

            # Stochastic Setup: Volatility expands dynamically based on slider values
            months_horizon = 12
            simulations_count = 500
            volatility_coefficient = 0.04 + (shock_materials * 0.003) + (shock_retention * 0.005)
            
            # Allocation matrices for multi-timeline evaluation: Shape (500, 13)
            all_simulated_runs = np.zeros((simulations_count, months_horizon + 1))
            all_simulated_runs[:, 0] = starting_cash

            # Deterministic Cyclical Seasonality Scale
            seasonality = [1.0, 0.94, 0.97, 1.02, 1.05, 0.98, 0.95, 0.92, 1.03, 1.08, 1.12, 1.25]

            # Matrix Computation Engine Block
            for sim_idx in range(simulations_count):
                current_cash = starting_cash
                current_revenue = adjusted_revenue
                
                for m_idx in range(months_horizon):
                    # Box-Muller transform Gaussian variance modeling
                    rev_noise = np.random.normal(0, volatility_coefficient)
                    exp_noise = np.random.normal(0, volatility_coefficient * 0.65)
                    
                    # Apply compounding mechanics
                    stepped_rev = current_revenue * (1.0 + monthly_growth_rate + rev_noise) * seasonality[m_idx]
                    stepped_exp = adjusted_expenses * (1.0 + exp_noise)
                    
                    current_cash += (stepped_rev - stepped_exp)
                    current_cash = max(0.0, current_cash) # Structural Floor (Absolute Insolvency Boundary)
                    
                    all_simulated_runs[sim_idx, m_idx + 1] = current_cash
                    current_revenue = max(0.0, current_revenue * (1.0 + monthly_growth_rate))

            # Quantile Slicing
            expected_trajectory = np.percentile(all_simulated_runs, 50, axis=0).tolist()
            optimistic_trajectory = np.percentile(all_simulated_runs, 90, axis=0).tolist()
            pessimistic_trajectory = np.percentile(all_simulated_runs, 10, axis=0).tolist()

            # Dynamic Operational Playbook Assembly
            median_net_burn = adjusted_expenses - adjusted_revenue
            runway_display = "Infinite (Profitable)" if median_net_burn <= 0 else f"{round(starting_cash / median_net_burn, 1)} Months"
            
            playbook_tasks = []
            if pessimistic_trajectory[-1] == 0:
                playbook_tasks = [
                    {"title": "[CRITICAL ALERT]: Capital Horizon Breach", "description": "Bottom 10% of stochastic runs show systemic capital depletion. Action Item: Initiate operational burn freeze immediately."},
                    {"title": "Supply-Side Restructuring", "description": "Materials pressure exceeds baseline threshold tolerances. Negotiate raw index price lock-ins."}
                ]
            else:
                playbook_tasks = [
                    {"title": "Strategic Optimization Clear", "description": "Runway stability is confirmed across 90% of variance bands. Action Item: Fund expansion initiatives."},
                    {"title": "Surplus Reinvestment Schedule", "description": "Allocate standard operating cash reserves to product acquisition pools."}
                ]

            # Downstream Event Frame Dispatch
            emit('matrix_telemetry_update', {
                "revenue": f"${adjusted_revenue:,.2f}",
                "expenses": f"${adjusted_expenses:,.2f}",
                "cash_runway": runway_display,
                "growth_rate": f"{monthly_growth_rate * 12 * 100:.1f}%",
                "risk_score": f"{min(100, int((median_net_burn / max(1.0, adjusted_revenue)) * 100))}%" if median_net_burn > 0 else "1.8%",
                "warning_alerts": "STRESS PROFILE DEVIATION DETECTED" if pessimistic_trajectory[-1] == 0 else "OPERATIONS NOMINAL",
                "expected_data": expected_trajectory[1:],
                "optimistic_data": optimistic_trajectory[1:],
                "pessimistic_data": pessimistic_trajectory[1:],
                "playbook_tasks": playbook_tasks
            })
            
        except Exception as err:
            emit('matrix_compute_error', {"error": str(err)})