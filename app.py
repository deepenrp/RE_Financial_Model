import os

import pandas as pd
import numpy as np
import numpy_financial as npf
import math

import datetime as dt
from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta

from flask import Flask, jsonify, render_template, request
import json
import plotly

app = Flask(__name__)


def RE_Financial_Model(form):
    #################################################
    # Build Residential Real Estate Financial Model #
    ################################################

    #################################################
    #             Amortization Schedule             #
    # ----------------------------------------------#

    # Purchase Details (Input:- Purchase Price, HOA Fees, Property Taxes, Homeowner's Insurance, Purchase Date)

    purchase_price = int(request.form['purchasePrice'])
    print(purchase_price)
    hoa_fees = 0
    property_taxes = 10307.00
    property_tax_monthly = round((property_taxes / 12), 2)
    property_tax_rate = property_taxes / purchase_price
    homeowners_insurance_annual = 900
    homeowners_insurance_monthly = homeowners_insurance_annual / 12
    purchase_date = datetime.strptime("2024-01-01", "%Y-%m-%d")
    month_start = datetime(purchase_date.year, purchase_date.month + 2, 1)

    # Loan Details (Input Loan Type, LTV, Interest Rate, Term, Additional Principal)
    loan_type = "Conventional"
    ltv = float(request.form['ltv']) / 100
    print(ltv)
    downpayment = round((purchase_price * (1 - ltv)), 2)
    loan_amount = round((purchase_price * ltv), 2)
    interest_rate = float(request.form['interestRate']) / 100
    print(interest_rate)
    term_annual = int(request.form['term'])
    print(term_annual)
    no_of_months = term_annual * 12
    monthly_p_i = round((-1 * npf.pmt(interest_rate / 12, no_of_months, loan_amount)), 2)
    additional_principal = 0

    pitia = monthly_p_i + property_tax_monthly + homeowners_insurance_monthly + homeowners_insurance_monthly


    ### Closing Costs (Input Total Loan Costs, Other Costs, Lender Credits, Seller Credits)
    # Total Loan Costs (A + B + C)
    total_loan_costs = 5000.00
    # Other Costs (E + F + G + H)
    other_costs = 6000.00
    # Prepaids (3 Months)
    prepaids = round((3 * (property_tax_monthly + homeowners_insurance_monthly)), 2)
    escrows = round((3 * (property_tax_monthly + homeowners_insurance_monthly)), 2)
    lender_credits = - 0
    seller_credits = - 0
    total_closing_costs = round((total_loan_costs + other_costs + prepaids + escrows + lender_credits), 2)
    cash_to_close = downpayment + total_closing_costs
    going_in_costs = total_loan_costs + other_costs + lender_credits + seller_credits

    # Borrower Profile (Input All)
    current_address = "321 Niam Ave, East Brunswick, NJ 08340"
    own_or_rent = "Rent"
    current_housing_payment = int(request.form['rent'])
    print(current_housing_payment)
    credit_score = 720

    # Appreciation Forecast (According to past 5-Yr NJ HPI)
    appreciation_rate = float(request.form['appreciation'])
    print(appreciation_rate)

    # Resale Scenario (Input All)
    agent_commission = 5 / 100
    inflation = 1.81 / 100

    # Period to calculate
    per = 1

    # Calculate the interest payment
    ipmt = npf.ipmt(interest_rate / 12, per, no_of_months, loan_amount)

    # Calculate the principal payment
    ppmt = npf.ppmt(interest_rate / 12, per, no_of_months, loan_amount)

    # build a DateTimeIndex Range for the next 30 years based on MS (Month Start)
    rng = pd.date_range(month_start, periods=term_annual * 12, freq='MS')
    rng.name = "payment_date"

    # Create Amortization Schedule DataFrame
    amortization_schedule_df = pd.DataFrame()

    dates = []
    for d in rng:
        date1 = np.datetime64(d)
        date2 = np.datetime_as_string(date1, unit='D')
        dates.append(date2)

    amortization_schedule_df["payment_date"] = dates
    amortization_schedule_df["month"] = list(range(1, (len(amortization_schedule_df["payment_date"]) + 1)))

    #Year
    periods = list(range(1, (len(amortization_schedule_df["payment_date"]) + 1)))
    year = []
    for x in periods:
        year.append(math.ceil( x / 12 ))
    # Year Column
    amortization_schedule_df["year"] = year

    # Payment, Principal, Interest
    amortization_schedule_df["payment"] = npf.pmt(interest_rate/12, term_annual*12, loan_amount)
    amortization_schedule_df["principal"] = npf.ppmt(interest_rate/12, amortization_schedule_df.index, term_annual*12, loan_amount)
    amortization_schedule_df["interest"] = npf.ipmt(interest_rate/12, amortization_schedule_df.index, term_annual*12, loan_amount)

    # Additional Principal. Convert to a negative value in order to keep the signs the same
    amortization_schedule_df["additional_principal"] = -additional_principal

    # Cumulative Principal, Cumulative Interest
    amortization_schedule_df["cumulative_principal"] = (amortization_schedule_df["principal"] + amortization_schedule_df["additional_principal"]).cumsum()
    amortization_schedule_df["cumulative_interest"] = (amortization_schedule_df["interest"]).cumsum()

    # Ending Balance at end of period
    amortization_schedule_df["ending_balance"] = loan_amount + amortization_schedule_df["cumulative_principal"]

    # Loan-To-Value
    amortization_schedule_df["loan_to_value_%"] = (amortization_schedule_df["ending_balance"] / purchase_price) * 100
    # Round number to 2 decimal points
    amortization_schedule_df = amortization_schedule_df.round(2)


    #################################################
    #                Equity DataFrame               #
    # ----------------------------------------------#

    
    equity_df = pd.DataFrame()
    equity_df["payment_date"] = amortization_schedule_df["payment_date"]
    equity_df["month"] = amortization_schedule_df["month"]
    equity_df["year"] = amortization_schedule_df["year"]
    equity_df["ending_balance"] = amortization_schedule_df["ending_balance"]
    equity_df["payment"] = amortization_schedule_df["payment"]

    house_value = []
    value = purchase_price
    for row, index in equity_df.iterrows():
        value = round((value * (1 + ((appreciation_rate/100) / 12))), 2)
        house_value.append(value)
        value = value

    equity_df["home_value"] = house_value
    equity_df["home_equity_without_appreciation"] = purchase_price - equity_df["ending_balance"]
    equity_df["home_equity_minus_downpayment_closing_costs"] = equity_df["home_equity_without_appreciation"] - downpayment - going_in_costs
    equity_df["equity_from_appreciation"] = equity_df["home_value"] - purchase_price


    #################################################
    #             Cash Flow DataFrame               #
    # ----------------------------------------------#

    cashflow_df = pd.DataFrame()

    cashflow_df["payment_date"] = amortization_schedule_df["payment_date"]
    cashflow_df["month"] = amortization_schedule_df["month"]
    cashflow_df["year"] = amortization_schedule_df["year"]
    cashflow_df["payment"] = amortization_schedule_df["payment"]
    cashflow_df["home_value"] = equity_df["home_value"]
    cashflow_df["property_taxes"] = cashflow_df["home_value"] * (property_tax_rate / 12)
    cashflow_df["monthly_housing_expense_owning"] = -cashflow_df["payment"] + cashflow_df["property_taxes"] + homeowners_insurance_monthly + hoa_fees
    # ^^^ Need Mortgage Insurance calculation for monthly housing expense calculation

    # Calculation for Total Owning Costs
    monthly_cost = 0
    total_costs = []
    for cost in cashflow_df["monthly_housing_expense_owning"]:
        monthly_cost += cost
        total_costs.append(round((cash_to_close + monthly_cost), 2))
    cashflow_df["total_owning_cost"] = total_costs

    cashflow_df["monthly_rent"] = current_housing_payment
    # ^^^  Need Monthly Rent Growth Calculations

    # Calculation for Total Rent Costs ("current_housing_payment")
    monthly_rent = 0
    total_rent = []
    for rent in cashflow_df["monthly_rent"]:
        monthly_rent += rent
        total_rent.append(round(monthly_rent, 2))

    cashflow_df["total_renting_cost"] = total_rent
    cashflow_df["monthly_saving_expense"] = np.around(cashflow_df["monthly_rent"], decimals=2) - np.around(cashflow_df["monthly_housing_expense_owning"], decimals=2)

    # Calculation for Total Cash Flow
    saved_spent = 0
    total_saved_spent = []
    for cash_flow in cashflow_df["monthly_saving_expense"]:
        saved_spent += cash_flow
        total_saved_spent.append(round(saved_spent, 2))

    cashflow_df["total_cash_flow"] = total_saved_spent


    #################################################
    #          Wealth Created DataFrame             #
    # ----------------------------------------------#

    wealth_created_df = pd.DataFrame()
    wealth_created_df["payment_date"] = amortization_schedule_df["payment_date"]
    wealth_created_df["month"] = amortization_schedule_df["month"]
    wealth_created_df["year"] = amortization_schedule_df["year"]
    wealth_created_df["monthly_saving_expense"] = cashflow_df["monthly_saving_expense"]
    wealth_created_df["total_cash_flow"] = cashflow_df["total_cash_flow"]
    wealth_created_df["home_equity_minus_downpayment_closing_costs"] = equity_df["home_equity_minus_downpayment_closing_costs"]
    wealth_created_df["equity_from_appreciation"] = equity_df["equity_from_appreciation"]
    wealth_created_df["wealth_created"] = wealth_created_df["total_cash_flow"] + wealth_created_df["home_equity_minus_downpayment_closing_costs"] + wealth_created_df["equity_from_appreciation"]


    #################################################
    #          Rate of Return DataFrame             #
    # ----------------------------------------------#

    rate_of_return_df = pd.DataFrame()

    rate_of_return_df["payment_date"] = amortization_schedule_df["payment_date"]
    rate_of_return_df["month"] = amortization_schedule_df["month"]
    rate_of_return_df["year"] = amortization_schedule_df["year"]
    rate_of_return_df["home_value"] = equity_df["home_value"]
    rate_of_return_df["wealth_created"] = wealth_created_df["wealth_created"]
    rate_of_return_df["money_received_after_selling_property"] = round((rate_of_return_df["wealth_created"] - (rate_of_return_df["home_value"] * agent_commission)), 2)
    rate_of_return_df["present_value_benefit_of_owning_vs_renting"] = round((rate_of_return_df["money_received_after_selling_property"] / \
        (np.power((1 + inflation ), (1/12)))), 2)
    rate_of_return_df["percent_return_inflation_adjusted"] = round(((rate_of_return_df["present_value_benefit_of_owning_vs_renting"] / cash_to_close) * 100), 2)

    # Calculation for = Annualized Rate of Return
    periods = list(range(1, (len(rate_of_return_df["percent_return_inflation_adjusted"]) + 1)))
    rate_of_return_df["annualized_rate_of_return_inflation_adjusted"] = round(((rate_of_return_df["percent_return_inflation_adjusted"] / (periods)) * 12), 2)


    #################################################
    #              10 Year DataFrame               #
    # ----------------------------------------------#

    ten_years_df = pd.DataFrame()
    ten_years_df["month"] = amortization_schedule_df["month"].loc[0 : 120 - 1]
    ten_years_df["year"] = amortization_schedule_df["year"].loc[0 : 120 - 1]
    ten_years_df["home_appreciation"] = equity_df["home_value"].loc[0 : 120 - 1]
    ten_years_df["equity_from_appreciation"] = equity_df["equity_from_appreciation"].loc[0 : 120 - 1]
    ten_years_df["wealth_created"] = wealth_created_df["wealth_created"].loc[0 : 120 - 1]
    ten_years_df["percent_return_inflation_adjusted"] = rate_of_return_df["percent_return_inflation_adjusted"].loc[0 : 120 - 1]
    ten_years_df["annualized_rate_of_return_inflation_adjusted"] = rate_of_return_df["annualized_rate_of_return_inflation_adjusted"].loc[0 : 120 - 1]
    ten_years_df["total_owning_cost"] = cashflow_df["total_owning_cost"].loc[0 : 120 - 1]
    ten_years_df["total_renting_cost"] = cashflow_df["total_renting_cost"].loc[0 : 120 - 1]


    #################################################
    #           Yearly DataFrame (10 Yrs)           #
    # ----------------------------------------------#

    yearly_df = pd.DataFrame()

    ten = list(range(1, 10 +1))

    month = []
    for x in ten:
        month.append(x * 12)

    year = []
    home_appreciation = []
    equity_from_appreciation = []
    wealth_created = []
    percent_roi = []
    annualized_roi = []
    total_owning_cost = []
    total_renting_cost = []

    for x in month:
        year.append(ten_years_df["year"].loc[x - 1])
        home_appreciation.append(ten_years_df["home_appreciation"].loc[x - 1])
        equity_from_appreciation.append(ten_years_df["equity_from_appreciation"].loc[x - 1])
        wealth_created.append(ten_years_df["wealth_created"].loc[x - 1])
        percent_roi.append(ten_years_df["percent_return_inflation_adjusted"].loc[x - 1])
        annualized_roi.append(ten_years_df["annualized_rate_of_return_inflation_adjusted"].loc[x - 1])
        total_owning_cost.append(ten_years_df["total_owning_cost"].loc[x - 1])
        total_renting_cost.append(ten_years_df["total_renting_cost"].loc[x - 1])

    yearly_df["month"] = month
    yearly_df["year"] = year
    yearly_df["home_appreciation"] = home_appreciation
    yearly_df["equity_from_appreciation"] = equity_from_appreciation
    yearly_df["wealth_created"] = wealth_created
    yearly_df["percent_return_inflation_adjusted"] = percent_roi
    yearly_df["annualized_rate_of_return_inflation_adjusted"] = annualized_roi
    yearly_df["total_owning_cost"] = total_owning_cost
    yearly_df["total_renting_cost"] = total_renting_cost

    return (amortization_schedule_df, equity_df, cashflow_df, wealth_created_df, rate_of_return_df, ten_years_df)


@app.route("/")
def index():
    return render_template("index.html")

#-----------------------------

@app.route("/results", methods=['POST'])
def results():
    """Return the homepage."""
    if request.method == 'POST':
        form = request.form
        RE_Financial_Model_Results = RE_Financial_Model(form)

        schedule = RE_Financial_Model_Results[0]
        schedule_dict = schedule.to_dict(orient="list")

        equity = RE_Financial_Model_Results[1]
        equity_dict = equity.to_dict(orient="list")

        ten_years = RE_Financial_Model_Results[5]
        ten_years_dict = ten_years.to_dict(orient="list")

    return render_template(
        "results.html", 
        RE_Financial_Model_Results=RE_Financial_Model_Results,
        schedule_dict=schedule_dict,
        equity_dict=equity_dict,
        ten_years_dict=ten_years_dict
    )

#----------------------------- 


if __name__ == "__main__":
    app.run(debug=True)
