from .finance_utils import irr
import logging

def calc_emi(P, r, n, R=0):
    if r != 0:
        pv_res = R/(1+r)**n
        return r*(P - pv_res)/(1 - (1+r)**-n)
    else:
        return (P - R)/n

def process_inputs(form_data, inputs):
    table = []

    # Parse inputs
    asset_cost            = float(form_data.get('asset_cost', 0) or 0)
    rate                  = float(form_data.get('interest_rate', 0) or 0)
    tenure_months         = int(form_data.get('tenure_months', 0) or 0)
    moratorium            = int(form_data.get('moratorium', 0) or 0)
    security_deposit_pct  = float(form_data.get('security_deposit_pct', 0) or 0)
    residual_pct          = float(form_data.get('residual_pct', 0) or 0)
    advance_rentals       = int(form_data.get('advance_rentals', 0) or 0)
    upfront_fee_pct       = float(form_data.get('upfront_fee_pct', 0) or 0)
    supplier_discount_pct = float(form_data.get('supplier_discount_pct', 0) or 0)
    payment_frequency     = form_data.get('payment_frequency', 'monthly')
    loan_or_lease         = form_data.get('loan_or_lease', 'lease')
    loan_type             = form_data.get('loan_type', 'standard')

    inputs.update({
        'asset_cost': asset_cost,
        'rate': rate,
        'tenure': tenure_months,
        'moratorium': moratorium,
        'security_deposit_pct': security_deposit_pct,
        'residual_pct': residual_pct,
        'advance_rentals': advance_rentals,
        'upfront_fee_pct': upfront_fee_pct,
        'supplier_discount_pct': supplier_discount_pct,
        'payment_frequency': payment_frequency
    })

    if asset_cost <= 0 or rate < 0 or tenure_months <= 0:
        raise ValueError("Asset cost, rate, and tenure must be positive numbers.")

    # Pre-calculations
    net_cost = asset_cost * (1 - supplier_discount_pct/100)
    deposit_amt = net_cost * (security_deposit_pct/100)
    fee_amt = net_cost * (upfront_fee_pct/100)
    residual_amt = net_cost * (residual_pct/100)
    principal = net_cost - deposit_amt + fee_amt

    freq_map = {'monthly': 1, 'quarterly': 3}
    freq_factor = freq_map.get(payment_frequency, 1)
    total_periods = tenure_months // freq_factor or 1
    periodic_rate = rate/100 * freq_factor/12

    if moratorium > 0 and periodic_rate > 0:
        principal *= (1 + periodic_rate) ** moratorium

    remaining_periods = max(total_periods - advance_rentals, 1)

    cashflows = [-principal]

    if loan_or_lease == 'lease':
        emi = round(calc_emi(principal, periodic_rate, remaining_periods, residual_amt), 2)
        bal = principal
        for i in range(1, remaining_periods+1):
            interest = round(bal * periodic_rate, 2)
            princ = round(emi - interest, 2)
            bal = round(bal - princ, 2)
            pay = emi + (residual_amt if i == remaining_periods else 0)
            cashflows.append(pay)
            table.append({'Period': i*freq_factor, 'Payment': pay, 'Principal': princ, 'Interest': interest, 'Balance': max(bal, 0)})
        result = f"Lease EMI: ₹{emi:.2f}"

    else:
        if loan_type == 'standard':
            emi = round(calc_emi(principal, periodic_rate, remaining_periods, residual_amt), 2)
        elif loan_type == 'bullet':
            emi = round(principal * periodic_rate, 2)
        else:  # equal_principal
            emi = None

        bal = principal
        for i in range(1, remaining_periods+1):
            interest = round(bal * periodic_rate, 2)
            if loan_type == 'bullet':
                princ = 0 if i < remaining_periods else principal
                pay = interest + princ + (residual_amt if i == remaining_periods else 0)
            elif loan_type == 'equal_principal':
                princ = round(principal / remaining_periods, 2)
                pay = round(princ + interest + (residual_amt if i == remaining_periods else 0), 2)
            else:
                princ = round(emi - interest, 2)
                pay = emi + (residual_amt if i == remaining_periods else 0)
            bal = round(bal - princ, 2)
            cashflows.append(pay)
            table.append({'Period': i*freq_factor, 'Payment': pay, 'Principal': princ, 'Interest': interest, 'Balance': max(bal, 0)})
        result = f"{loan_type.replace('_',' ').title()} EMI: ₹{emi:.2f}" if emi else f"{loan_type.title()} schedule calculated"

    irr_m = irr(cashflows)
    if irr_m:
        irr_monthly = round(irr_m * 100, 2)
        irr_annual = round(irr_m * 12 * 100, 2)
        irr_value = irr_monthly
    else:
        irr_value = irr_monthly = irr_annual = None

    return result, irr_value, irr_monthly, irr_annual, table, inputs
