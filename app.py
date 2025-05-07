from flask import Flask, render_template, request
from calculations.emi_logic import process_inputs
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    irr_value = None
    irr_monthly = None
    irr_annual = None
    table = []

    inputs = {
        'asset_cost': '',
        'rate': '',
        'tenure': '',
        'moratorium': '',
        'security_deposit_pct': '',
        'residual_pct': '',
        'advance_rentals': '',
        'upfront_fee_pct': '',
        'supplier_discount_pct': '',
        'payment_frequency': 'monthly'
    }

    if request.method == 'POST':
        try:
            result, irr_value, irr_monthly, irr_annual, table, inputs = process_inputs(request.form, inputs)
        except Exception as e:
            logging.exception("Error in calculation")
            result = f"Error: {e}"

    return render_template("index.html", result=result, inputs=inputs,
                           irr=irr_value, irr_monthly=irr_monthly,
                           irr_annual=irr_annual, table=table)

if __name__ == '__main__':
    app.run(debug=True)
