import scipy.optimize
from datetime import date

class QuantService:
    @staticmethod
    def calculate_cagr(start_value: float, end_value: float, years: float) -> float:
        if start_value <= 0 or years <= 0:
            return 0.0
        return (end_value / start_value) ** (1 / years) - 1

    @staticmethod
    def _xnpv(rate, cash_flows):
        t0 = cash_flows[0][0]
        return sum(cf / (1 + rate)**((t - t0).days / 365.0) for t, cf in cash_flows)

    @staticmethod
    def calculate_xirr(cash_flows: list[tuple[date, float]]) -> float:
        if not cash_flows or len(cash_flows) < 2:
            return 0.0
        try:
            return scipy.optimize.newton(QuantService._xnpv, 0.1, args=(cash_flows,))
        except RuntimeError:
            return 0.0