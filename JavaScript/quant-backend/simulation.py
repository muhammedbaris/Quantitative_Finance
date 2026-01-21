# ======================
# 📦 1. IMPORT LIBRARIES
# ======================

import numpy as np                # for numerical arrays and math
import pandas as pd              # for working with tabular data
import numpy_financial as npf    # for calculating IRR (internal rate of return)


# ======================================
# 🧱 2. DEFINE THE PRIVATEINVESTMENT CLASS
# ======================================

class PrivateInvestment:
    """
    This class models a private market investment (e.g., VC, PE, Real Assets)
    including capital calls, NAV growth, and distributions.
    """

    def __init__(
        self,
        commitment,         # Total committed capital (e.g. $1,000,000)
        start_month,        # When the fund starts (e.g. month 0 or month 12)
        fund_life=120,      # Duration of the fund in months (default: 10 years)
        call_schedule=None,             # Optional: % of capital called each month
        nav_growth_schedule=None,       # Optional: NAV growth per month
        distribution_schedule=None      # Optional: distributions per month
    ):
        self.commitment = commitment
        self.start_month = start_month
        self.fund_life = fund_life

        # If no schedule is passed, use default behavior
        self.call_schedule = call_schedule or self.default_call_schedule()
        self.nav_growth_schedule = nav_growth_schedule or self.default_nav_growth()
        self.distribution_schedule = distribution_schedule or self.default_distributions()

        # Output lists to track results
        self.nav_history = []
        self.cash_flows = []

        # Run the simulation upon initialization
        self.simulate()

    def default_call_schedule(self):
        """
        Spread 20% capital calls evenly over the first 5 years (60 months).
        """
        schedule = [0] * self.fund_life
        for i in range(60):
            schedule[i] = 0.2 / 60  # Equal calls per month
        return schedule

    def default_nav_growth(self):
        """
        Define NAV growth behavior (mimics a J-curve):
        - First 2 years: slight loss (drag)
        - Years 3–5: slow growth
        - After 5 years: higher growth
        """
        growth = [0] * self.fund_life
        for i in range(self.fund_life):
            if i < 24:
                growth[i] = 0.99  # drag
            elif i < 60:
                growth[i] = 1.01  # slow growth
            else:
                growth[i] = 1.03  # higher growth
        return growth

    def default_distributions(self):
        """
        Start distributing 2% of commitment per month after year 5.
        """
        dist = [0] * self.fund_life
        for i in range(60, self.fund_life):
            dist[i] = 0.02
        return dist

    def simulate(self):
        """
        Run the NAV and cash flow simulation.
        Tracks NAV and net cash flow (calls = negative, distributions = positive).
        """
        nav = 0
        total_called = 0
        cash_flows = []
        navs = []

        for i in range(self.fund_life):
            # Capital called this month
            call = self.call_schedule[i] * self.commitment
            total_called += call

            # Grow NAV based on previous NAV + new call
            nav = nav * self.nav_growth_schedule[i] + call

            # Distribute based on schedule (from NAV)
            dist = self.distribution_schedule[i] * self.commitment
            nav = max(nav - dist, 0)

            # Track history
            navs.append(nav)
            cash_flows.append(-call + dist)  # Net cash flow = dist - call

        self.nav_history = navs
        self.cash_flows = cash_flows


# ===========================================
# 📈 3. SIMULATE A TOTAL PORTFOLIO (PUBLIC + PRIVATE + CASH)
# ===========================================

def simulate_total_portfolio(
    initial_capital,
    public_weights,
    returns_df,
    private_investments,
    n_months=120,
    cash_rate=0.02  # 2% annual interest on unused cash
):
    """
    Simulate a full portfolio that includes:
    - Public assets (stocks, bonds, etc.)
    - Private investments (VC/PE)
    - Cash account for liquidity buffer
    """
    assert len(public_weights) == returns_df.shape[1], "Mismatch between weights and asset columns"

    # Allocate starting capital
    public_value = initial_capital * sum(public_weights)
    cash_balance = initial_capital * (1 - sum(public_weights))

    # Track portfolio values over time
    public_values = [public_value]
    private_navs = [sum([pi.nav_history[0] for pi in private_investments])]
    cash_balances = [cash_balance]
    total_values = [public_value + private_navs[-1] + cash_balance]

    # Simulate month-by-month
    for month in range(1, n_months):
        # Apply public market returns
        monthly_returns = returns_df.iloc[month % len(returns_df)].values
        public_value *= (1 + np.dot(public_weights, monthly_returns))
        public_values.append(public_value)

        # Private NAV and cash flow
        private_nav = 0
        net_private_cashflow = 0
        for pi in private_investments:
            if month < len(pi.cash_flows):
                private_nav += pi.nav_history[month]
                net_private_cashflow += pi.cash_flows[month]

        private_navs.append(private_nav)

        # Update cash with private market cash flows and interest
        cash_balance += net_private_cashflow
        cash_balance *= (1 + cash_rate / 12)
        cash_balances.append(cash_balance)

        # Total value = public + private + cash
        total = public_value + private_nav + cash_balance
        total_values.append(total)

    return {
        "public": public_values,
        "private": private_navs,
        "cash": cash_balances,
        "total": total_values
    }


# ===================================================
# 📊 4. CALCULATE PORTFOLIO PERFORMANCE METRICS
# ===================================================

def calculate_total_portfolio_metrics(portfolio_result, initial_capital, risk_free_rate=0.02):
    """
    Calculate key performance stats for the total portfolio.
    """
    total_values = portfolio_result['total']
    public_values = portfolio_result['public']
    private_navs = portfolio_result['private']
    cash_balances = portfolio_result['cash']

    # Time horizon
    n_months = len(total_values) - 1
    n_years = n_months / 12

    # Final portfolio value and returns
    final_value = total_values[-1]
    annualized_return = (final_value / initial_capital) ** (1 / n_years) - 1
    cumulative_return = final_value / initial_capital - 1

    # Risk metrics
    monthly_returns = np.diff(total_values) / total_values[:-1]
    annualized_volatility = np.std(monthly_returns) * np.sqrt(12)

    running_max = np.maximum.accumulate(total_values)
    drawdowns = (running_max - total_values) / running_max
    max_drawdown = np.max(drawdowns)

    # Cash flow-based IRR
    cash_flows = [-initial_capital] + list(np.diff(total_values))
    irr = npf.irr(cash_flows)

    # Final allocation
    total_final = final_value
    public_pct = public_values[-1] / total_final
    private_pct = private_navs[-1] / total_final
    cash_pct = cash_balances[-1] / total_final

    return {
        "Final Portfolio Value ($)": round(float(final_value), 2),
        "Cumulative Return (%)": round(float(cumulative_return) * 100, 2),
        "Annualized Return (%)": round(float(annualized_return) * 100, 2),
        "Annualized Volatility (%)": round(float(annualized_volatility) * 100, 2),
        "Sharpe Ratio": round(float((annualized_return - risk_free_rate) / annualized_volatility), 2),
        "Max Drawdown (%)": round(float(max_drawdown) * 100, 2),
        "Portfolio IRR (%)": round(float(irr) * 100, 2),
        "Final Allocation - Public (%)": round(float(public_pct) * 100, 2),
        "Final Allocation - Private (%)": round(float(private_pct) * 100, 2),
        "Final Allocation - Cash (%)": round(float(cash_pct) * 100, 2)
    }


# =====================================================
# 🚀 5. FLASK WRAPPER: run_simulation(input_data)
# =====================================================

def run_simulation(input_data):
    """
    This is the main function called by Flask when the user hits /simulate

    It:
    - Parses the input data (capital, weights, returns, private commitments)
    - Runs the simulation
    - Returns the result (portfolio + metrics)
    """

    # Parse inputs
    initial_capital = input_data["initial_capital"]
    weights_dict = input_data["public_weights"]
    private_commitments = input_data["private_commitments"]
    returns_data = input_data["returns_data"]

    # Create DataFrame of historical monthly returns
    returns_df = pd.DataFrame(returns_data)
    returns_df = returns_df[list(weights_dict.keys())]  # ensure correct order

    # Convert weight dict to list (ordered)
    weights = [weights_dict[col] for col in returns_df.columns]

    # Create private investment objects
    private_investments = []
    for item in private_commitments:
        pi = PrivateInvestment(
            commitment=item["commitment"],
            start_month=item.get("start_month", 0)
        )
        private_investments.append(pi)

    # Run simulation
    portfolio_result = simulate_total_portfolio(
        initial_capital=initial_capital,
        public_weights=weights,
        returns_df=returns_df,
        private_investments=private_investments,
        n_months=len(returns_df)
    )

    # Compute performance stats
    metrics = calculate_total_portfolio_metrics(portfolio_result, initial_capital)

    return {
        "portfolio": portfolio_result,
        "metrics": metrics
    }
