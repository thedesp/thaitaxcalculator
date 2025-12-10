import streamlit as st
import pandas as pd
import altair as alt

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Thai Tax Calculator 2025",
    page_icon="🇹🇭",
    layout="centered"
)

# --- CSS STYLING ---
st.markdown("""
<style>
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
        color: #2E86C1;
    }
    .result-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

def calculate_tax(taxable_income):
    """Calculates tax based on the 2024/2025 progressive tax brackets."""
    brackets = [
        (150000, 0.00),
        (300000, 0.05),
        (500000, 0.10),
        (750000, 0.15),
        (1000000, 0.20),
        (2000000, 0.25),
        (5000000, 0.30),
        (float('inf'), 0.35)
    ]
    
    tax = 0
    remaining_income = taxable_income
    prev_limit = 0
    
    breakdown = []

    for limit, rate in brackets:
        if taxable_income <= prev_limit:
            break
            
        # Determine the amount of income in this bracket
        current_bracket_cap = limit - prev_limit
        amount_in_bracket = min(remaining_income, current_bracket_cap)
        
        # Calculate tax for this chunk
        tax_chunk = amount_in_bracket * rate
        tax += tax_chunk
        
        if amount_in_bracket > 0:
            breakdown.append({
                "Bracket": f"{prev_limit+1:,.0f} - {limit if limit != float('inf') else 'Max'}",
                "Rate": f"{int(rate*100)}%",
                "Amount Taxed": amount_in_bracket,
                "Tax Payable": tax_chunk
            })

        remaining_income -= amount_in_bracket
        prev_limit = limit
        
        if remaining_income <= 0:
            break
            
    return tax, breakdown

# --- MAIN APP ---

st.title("🇹🇭 Thai Personal Income Tax Calculator")
st.markdown("Estimate your personal income tax for **Tax Year 2024 & 2025**.")

with st.expander("ℹ️ How to use this calculator"):
    st.write("""
    1. Enter your **Annual Income** details in the first tab.
    2. Enter your **Deductions & Allowances** in the second tab.
    3. Review your estimated tax liability and bracket breakdown at the bottom.
    """)

# --- TABS FOR INPUT ---
tab_income, tab_deductions = st.tabs(["💰 Income", "📉 Deductions"])

# --- TAB 1: INCOME ---
with tab_income:
    st.header("Annual Assessable Income")
    col1, col2 = st.columns(2)
    
    with col1:
        salary_monthly = st.number_input("Monthly Salary (THB)", min_value=0.0, value=50000.0, step=1000.0)
        bonus_annual = st.number_input("Annual Bonus (THB)", min_value=0.0, value=0.0, step=1000.0)
    
    with col2:
        other_income = st.number_input("Other Taxable Income (THB)", min_value=0.0, value=0.0, help="Freelance, commissions, etc.")
        foreign_income = st.number_input("Foreign Income Remitted (THB)", min_value=0.0, value=0.0, help="Only taxable if you stay in Thailand >180 days.")

    total_income = (salary_monthly * 12) + bonus_annual + other_income + foreign_income
    
    # Calculate Expenses (50% of income, Max 100k)
    expenses_deduction = min(total_income * 0.5, 100000)
    
    st.info(f"**Total Annual Income:** {total_income:,.2f} THB")
    st.info(f"**Standard Expense Deduction:** {expenses_deduction:,.2f} THB (Max 100k or 50%)")

# --- TAB 2: DEDUCTIONS ---
with tab_deductions:
    st.header("Allowances & Deductions")
    
    # Personal & Family
    st.subheader("Family")
    c1, c2, c3 = st.columns(3)
    with c1:
        status = st.selectbox("Marital Status", ["Single", "Married (File Jointly)", "Married (File Separate)"])
        spouse_allowance = 60000 if status == "Married (File Jointly)" else 0
    with c2:
        children = st.number_input("Number of Children", min_value=0, value=0)
        # Simplified: Assuming 30k per child. 
        # (Note: 2nd child born >2018 is 60k, but we keep UI simple for now)
        child_allowance = children * 30000 
    with c3:
        parents = st.number_input("Parents (>60yo, Low Income)", min_value=0, max_value=4, value=0)
        parent_allowance = parents * 30000

    # Social Security & Insurance
    st.subheader("Insurance & Savings")
    c4, c5 = st.columns(2)
    with c4:
        sso_annual = st.number_input("Social Security Paid (Annual)", min_value=0.0, max_value=9000.0, value=9000.0, help="Usually max 750/month = 9,000/year")
        life_insurance = st.number_input("Life Insurance Premium", min_value=0.0, value=0.0)
        health_insurance = st.number_input("Health Insurance Premium", min_value=0.0, value=0.0, help="Max 25,000 deduction")
    
    with c5:
        provident_fund = st.number_input("Provident Fund (PVD)", min_value=0.0, value=0.0, help="Max 15% of wages, capped at 500k")
        rmf = st.number_input("RMF Investment", min_value=0.0, value=0.0, help="Max 30% of income, capped at 500k")
        ssf = st.number_input("SSF Investment", min_value=0.0, value=0.0, help="Max 30% of income, capped at 200k")
        thai_esg = st.number_input("Thai ESG Fund", min_value=0.0, value=0.0, help="Max 30% of income, capped at 100k")

    # Government Stimulus
    st.subheader("Stimulus")
    easy_e_receipt = st.number_input("Easy E-Receipt (2025)", min_value=0.0, max_value=50000.0, value=0.0, help="Purchases Jan 1 - Feb 15, 2025 with e-Tax Invoice")
    teawdeemeekeun = st.number_input("เที่ยวดีมีคืน เมืองหลัก", min_value=0.0, max_value=20000.0, value=0.0, help="ค่าเที่ยว ค่ากิน Nov 1 - Dec 15, 2025"),
    mortgage_interest = st.number_input("Home Mortgage Interest", min_value=0.0, max_value=100000.0, value=0.0)

    # Logic for Insurance/Fund Caps
    # Health insurance max 25k, but combined with Life max 100k
    health_deductible = min(health_insurance, 25000)
    life_health_total = min(life_insurance + health_deductible, 100000)

    # Retirement Group Cap (PVD + RMF + SSF + Pension Life Insurance) <= 500,000
    # Note: SSF has its own 200k cap, RMF 500k cap.
    # Simplified Logic:
    retirement_sum = provident_fund + rmf + ssf 
    retirement_deductible = min(retirement_sum, 500000)

    total_deductions = (
        60000 + # Personal Allowance
        spouse_allowance +
        child_allowance +
        parent_allowance +
        sso_annual +
        life_health_total +
        retirement_deductible +
        thai_esg + 
        easy_e_receipt +
        teawdeemeekeun +
        mortgage_interest
    )

    st.warning(f"**Total Deductions & Allowances:** {total_deductions:,.2f} THB")

# --- CALCULATIONS ---

net_taxable_income = max(0, total_income - expenses_deduction - total_deductions)
tax_payable, tax_breakdown = calculate_tax(net_taxable_income)
effective_tax_rate = (tax_payable / total_income * 100) if total_income > 0 else 0

# --- RESULTS DISPLAY ---

st.divider()
st.header("📊 Tax Calculation Results")

col_res1, col_res2, col_res3 = st.columns(3)

with col_res1:
    st.metric(label="Net Taxable Income", value=f"{net_taxable_income:,.2f} THB")

with col_res2:
    st.metric(label="Estimated Tax Payable", value=f"{tax_payable:,.2f} THB", delta="- Tax")

with col_res3:
    st.metric(label="Net Income (After Tax)", value=f"{total_income - tax_payable:,.2f} THB", delta="Keep")

st.markdown(f"<div class='big-font'>Effective Tax Rate: {effective_tax_rate:.2f}%</div>", unsafe_allow_html=True)

# --- VISUALIZATION ---

if tax_breakdown:
    st.subheader("Tax Bracket Breakdown")
    df_breakdown = pd.DataFrame(tax_breakdown)
    st.table(df_breakdown)
    
    # Visual Chart
    chart_data = pd.DataFrame({
        'Category': ['Tax', 'Net Income'],
        'Amount': [tax_payable, total_income - tax_payable]
    })
    
    c = alt.Chart(chart_data).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Amount", type="quantitative"),
        color=alt.Color(field="Category", type="nominal"),
        tooltip=["Category", "Amount"]
    ).properties(title="Income Distribution")
    
    st.altair_chart(c, use_container_width=True)

else:
    st.success("You have no tax liability! 🎉")