# accounts/ai_engine.py

from decimal import Decimal
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")   # 🔴 PUT YOUR KEY HERE


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

    # ---------- AI ----------
    ai_text = ""

    try:
        prompt = f"""
        A user earns ₹{income} monthly.

        Suggest how much they should invest in {plan_type}.
        Recommended percentage: {percent * 100}%.
        Investment amount: ₹{amount}.

        Explain benefits in simple words.
        Also mention Indian apps.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        ai_text = response.choices[0].message.content

    except Exception as e:
        ai_text = f"AI error: {str(e)}"

    return percent, amount, app_list, ai_text