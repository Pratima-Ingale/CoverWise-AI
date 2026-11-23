import os

def generate_enhanced_ai_explanation(customer_dict, top_policies, fallback_explanation):
    """
    Attempts to call Gemini API if GEMINI_API_KEY is configured.
    Otherwise returns the deterministic fallback explanation cleanly.
    """
    api_key = os.environ.get('GEMINI_API_KEY', '').strip()
    if not api_key:
        return fallback_explanation

    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        policies_summary = []
        for item in top_policies:
            p = item['policy_dict']
            policies_summary.append(
                f"- Name: {p['policy_name']} by {p['company_name']}, Type: {p['policy_type']}, "
                f"Premium: Rs {p['annual_premium']}, Coverage: Rs {p['coverage_amount']}, "
                f"CSR: {p['claim_settlement_ratio']}%, Waiting Period: {p['waiting_period_months']} months, "
                f"Features: {p['key_features_str']}, Suitability Score: {item['score']}%"
            )

        prompt = f"""You are 'PolicyAssist AI', an empathetic, transparent, certified insurance advisory agent.
Analyze the following customer requirements and explain why the top 3 recommended insurance policies were selected:

Customer Details:
- Name: {customer_dict.get('customer_name')}
- Age: {customer_dict.get('age')} years
- Family Size: {customer_dict.get('family_size')} members
- Annual Income: Rs {customer_dict.get('annual_income')}
- Annual Budget: Rs {customer_dict.get('insurance_budget')}
- Required Coverage: Rs {customer_dict.get('required_coverage')}
- Pre-existing Conditions: {customer_dict.get('pre_existing_conditions', 'None')}
- Stated Priority: {customer_dict.get('priority_preference', 'balanced')}

Top 3 Recommended Policies:
{chr(10).join(policies_summary)}

Instructions:
1. Provide a warm, concise advisory statement.
2. Clearly explain the rationale for Policy #1, highlighting how it balances their budget, coverage, and health needs.
3. Briefly mention the trade-offs/strengths of Policy #2 and #3.
4. Give a practical recommendation on what to look out for (e.g., waiting period, disclosures).
Keep it structured, clear, and professional using markdown bullet points. Do not include markdown code fence formatting.
"""

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        if response and response.text:
            return response.text
    except Exception as e:
        print(f"[LLM SERVICE NOTICE] Optional Gemini call not executed ({e}). Using deterministic NLG engine.")
    
    return fallback_explanation
