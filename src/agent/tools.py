from database.models import Policy
from src.recommender.eligibility import filter_eligible_policies
from src.recommender.scoring import score_policy, rank_policies

class PolicySearchTool:
    """Tool for searching and filtering Property & Casualty insurance policies."""
    name = "policy_search_tool"
    description = "Searches P&C policies by property type, valuation, age, and budget."

    def execute(self, customer_dict, all_policies=None):
        if all_policies is None:
            all_policies = Policy.query.all()
        eligible_policies, is_relaxed = filter_eligible_policies(all_policies, customer_dict)
        return {
            'eligible_policies': eligible_policies,
            'count': len(eligible_policies),
            'is_relaxed': is_relaxed
        }

class PolicyScoringTool:
    """Tool for calculating multi-criteria suitability scores for P&C policies."""
    name = "policy_scoring_tool"
    description = "Calculates suitability scores based on property coverage, budget fit, CSR, and liability protection."

    def execute(self, policies, customer_dict, top_n=3):
        ranked = rank_policies(policies, customer_dict, top_n=top_n)
        return ranked

class PolicyCompareTool:
    """Tool for generating side-by-side comparison matrix of Property & Casualty policies."""
    name = "policy_compare_tool"
    description = "Produces a structured comparison of specified P&C policies."

    def execute(self, policy_ids):
        policies = Policy.query.filter(Policy.policy_id.in_(policy_ids)).all()
        if not policies:
            return {'error': 'No policies found for given IDs', 'comparison_matrix': []}

        attributes = [
            {'key': 'policy_name', 'label': 'Policy Name'},
            {'key': 'company_name', 'label': 'Insurance Company'},
            {'key': 'policy_type', 'label': 'Policy Category'},
            {'key': 'coverage_amount', 'label': 'Property Sum Insured', 'format': 'currency'},
            {'key': 'annual_premium', 'label': 'Annual Premium', 'format': 'currency'},
            {'key': 'claim_settlement_ratio', 'label': 'Claim Settlement Ratio (CSR)', 'format': 'percent'},
            {'key': 'third_party_liability', 'label': 'Casualty Liability Cover', 'format': 'currency'},
            {'key': 'deductible_amount', 'label': 'Policy Deductible', 'format': 'currency'},
            {'key': 'fire_perils_covered', 'label': 'Fire & Explosion Perils'},
            {'key': 'natural_calamities_covered', 'label': 'Natural Calamities (Flood/Earthquake)'},
            {'key': 'burglary_theft_covered', 'label': 'Burglary & Housebreaking'},
            {'key': 'loss_of_rent_covered', 'label': 'Loss of Rent / Temp Housing'},
            {'key': 'key_features', 'label': 'Key Protection Highlights'}
        ]

        matrix = []
        for attr in attributes:
            row = {'label': attr['label'], 'key': attr['key'], 'values': []}
            for p in policies:
                val = getattr(p, attr['key'], '')
                if attr.get('format') == 'currency':
                    val_str = f"₹{val:,.0f}" if isinstance(val, (int, float)) else str(val)
                elif attr.get('format') == 'percent':
                    val_str = f"{val}%"
                else:
                    val_str = str(val)
                row['values'].append({'policy_id': p.policy_id, 'value': val_str})
            matrix.append(row)

        return {
            'policies': [p.to_dict() for p in policies],
            'matrix': matrix
        }

class RecommendationExplainerTool:
    """Tool for generating natural language explanations for Property & Casualty policy recommendations."""
    name = "recommendation_explainer_tool"
    description = "Generates clear, persuasive explanations for recommended P&C policies."

    def execute(self, customer_dict, top_policies):
        if not top_policies:
            return "No eligible Property & Casualty policies matched your exact criteria. Please try adjusting your budget or coverage preferences."

        name = customer_dict.get('customer_name', 'Property Owner')
        budget = customer_dict.get('insurance_budget', 10000)
        coverage = customer_dict.get('required_coverage', customer_dict.get('property_value', 5000000))
        ptype = customer_dict.get('property_type', 'Residential Property')

        explanations = []

        # Primary recommendation explanation
        first = top_policies[0]
        p1 = first['policy_dict']
        prem_diff = budget - p1['annual_premium']
        savings_text = f"saving ₹{prem_diff:,.0f} below your allocated budget" if prem_diff > 0 else "utilizing your premium budget with optimal value"

        p1_exp = (
            f"**1. {p1['policy_name']} ({first['badge']}) - Suitability Score: {first['score']}%**\n"
            f"- **Why it fits**: Selected as your #1 match because it provides ₹{p1['coverage_amount']:,.0f} property protection at an annual premium of ₹{p1['annual_premium']:,.0f}, {savings_text}.\n"
            f"- **Casualty & Peril Shield**: Includes ₹{p1['third_party_liability']:,.0f} third-party public liability cover, alongside full natural catastrophe (earthquake/flood) and burglary defense.\n"
            f"- **Claim Reliability**: Backed by {p1['company_name']}'s outstanding {p1['claim_settlement_ratio']}% Claim Settlement Ratio with a low ₹{p1['deductible_amount']:,.0f} deductible."
        )
        explanations.append(p1_exp)

        # Secondary recommendation
        if len(top_policies) > 1:
            second = top_policies[1]
            p2 = second['policy_dict']
            p2_exp = (
                f"**2. {p2['policy_name']} ({second['badge']}) - Suitability Score: {second['score']}%**\n"
                f"- **Why it fits**: Solid alternative from {p2['company_name']} securing ₹{p2['coverage_amount']:,.0f} sum insured for ₹{p2['annual_premium']:,.0f}/year with {p2['claim_settlement_ratio']}% CSR.\n"
                f"- **Standout Feature**: Features {p2['third_party_liability']:,.0f} casualty defense and: {'; '.join(p2['key_features'][:2])}."
            )
            explanations.append(p2_exp)

        # Tertiary recommendation
        if len(top_policies) > 2:
            third = top_policies[2]
            p3 = third['policy_dict']
            p3_exp = (
                f"**3. {p3['policy_name']} ({third['badge']}) - Suitability Score: {third['score']}%**\n"
                f"- **Why it fits**: Cost-efficient package providing essential structural and contents cover under {p3['company_name']} at ₹{p3['annual_premium']:,.0f}/year.\n"
                f"- **Key Highlight**: {'; '.join(p3['key_features'][:2])}."
            )
            explanations.append(p3_exp)

        overall_summary = (
            f"### CoverWise AI Advisory for {name} ({ptype})\n\n"
            f"Based on your target budget of **₹{budget:,.0f}** and required sum insured of **₹{coverage:,.0f}**, our AI Agent evaluated leading Property & Casualty policies. "
            f"We analyzed physical structure risk, household contents, third-party casualty liability, and insurer claim track records.\n\n"
            + "\n\n".join(explanations)
        )

        return overall_summary
