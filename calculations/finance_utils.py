import numpy as np
from scipy.optimize import root_scalar
import logging

def npv(rate, cashflows):
    return sum(cf / (1 + rate) ** t for t, cf in enumerate(cashflows))

def irr(cashflows):
    try:
        result = root_scalar(lambda r: npv(r, cashflows), bracket=[0.00001, 1], method='brentq')
        return result.root if result.converged else None
    except Exception as e:
        logging.warning("IRR calculation failed: %s", e)
        return None
