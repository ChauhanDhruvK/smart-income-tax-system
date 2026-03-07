# accounts/ai_engine.py

from decimal import Decimal


def get_plan_recommendation(plan_type, income):

    income = Decimal(income)

    # ---------- Percentage Logic ----------
    percent_map = {
        "sip": Decimal("0.30"),
        "insurance": Decimal("0.10"),
        "health": Decimal("0.15"),
        "nps": Decimal("0.20"),
        "ppf": Decimal("0.15"),
        "fd": Decimal("0.10"),
    }

    percent = percent_map.get(plan_type, Decimal("0.10"))
    amount = income * percent

    # ---------- Apps ----------
    apps = {
        "sip": ["Groww", "Zerodha Coin", "Paytm Money"],
        "insurance": ["PolicyBazaar", "LIC", "Acko"],
        "health": ["Star Health", "HDFC Ergo", "Care Insurance"],
        "nps": ["NSDL NPS", "HDFC Pension"],
        "ppf": ["SBI", "Post Office"],
        "fd": ["HDFC Bank", "ICICI Bank"],
    }

    app_list = apps.get(plan_type, [])

    # ---------- Dynamic AI Text ----------
    if plan_type == "sip":

        ai_text = f"""
🤖 AI Investment Analysis — SIP / Mutual Funds

Based on your monthly income of ₹{income},

We recommend investing approximately {percent*100}% 
(₹{amount}) into SIP or ELSS mutual funds.

📈 Why SIP?
• Long-term wealth creation
• Market-linked higher returns
• Tax benefit under Section 80C

💡 Strategy:
Start a disciplined monthly SIP to benefit from compounding
and rupee cost averaging.
"""

    elif plan_type == "health":

        ai_text = f"""
🤖 AI Financial Protection Analysis — Health Insurance

With your income level ₹{income},

Allocating {percent*100}% (₹{amount}) toward health insurance
is strongly recommended.

🏥 Why Health Insurance?
• Protects savings from medical emergencies
• Tax deduction under Section 80D
• Financial risk management

💡 Strategy:
Choose a comprehensive policy with sufficient coverage
for you and your family.
"""

    elif plan_type == "insurance":

        ai_text = f"""
🤖 AI Risk Protection Analysis — Life Insurance

For your income ₹{income},

We recommend allocating {percent*100}% (₹{amount})
towards life insurance protection.

🛡 Benefits:
• Family financial security
• Tax benefits under Section 80C
• Long-term risk coverage

💡 Strategy:
Prefer term insurance with high coverage at low premium.
"""

    elif plan_type == "nps":

        ai_text = f"""
🤖 AI Retirement Planning Analysis — NPS

Based on your earnings ₹{income},

Investing {percent*100}% (₹{amount}) in NPS can help
build retirement wealth.

📊 Benefits:
• Extra ₹50,000 deduction under 80CCD
• Market-linked growth
• Pension security after retirement

💡 Strategy:
Maintain long-term contributions for maximum compounding.
"""

    elif plan_type == "ppf":

        ai_text = f"""
🤖 AI Safe Investment Analysis — PPF

For income ₹{income},

We suggest allocating {percent*100}% (₹{amount})
into Public Provident Fund.

🔒 Benefits:
• Government-backed safety
• Tax-free returns
• Long-term stable growth

💡 Strategy:
Use PPF for low-risk portfolio diversification.
"""

    else:  # FD

        ai_text = f"""
🤖 AI Fixed Income Analysis — Tax Saving FD

With income ₹{income},

Investing {percent*100}% (₹{amount}) in tax-saving FD
is a conservative strategy.

🏦 Benefits:
• Guaranteed returns
• Tax deduction under 80C
• Low investment risk

💡 Strategy:
Suitable for short-to-medium-term financial stability.
"""

    return percent, amount, app_list, ai_text