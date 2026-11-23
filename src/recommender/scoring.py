def calculate_budget_fit_score(premium, budget):
    """Calculates budget score (0 - 100) for Property & Casualty policies."""
    if budget <= 0:
        return 60.0
    if premium <= budget:
        # Well within budget
        ratio = premium / budget
        return round(100.0 - (ratio * 12.0), 1)
    else:
        # Over budget
        excess_ratio = (premium - budget) / budget
        score = 100.0 - (excess_ratio * 160.0)
        return max(15.0, round(score, 1))

def calculate_coverage_score(policy_coverage, requested_coverage):
    """Calculates property coverage adequacy score (0 - 100)."""
    if requested_coverage <= 0:
        return 75.0
    ratio = policy_coverage / requested_coverage
    if ratio >= 1.0:
        # Fully satisfies or exceeds requested property sum insured
        return min(100.0, round(90.0 + min(10.0, (ratio - 1.0) * 5.0), 1))
    else:
        # Below required coverage
        return max(20.0, round(ratio * 90.0, 1))

def calculate_csr_score(csr):
    """Calculates claim settlement ratio score (0 - 100)."""
    if csr >= 98.0:
        return 100.0
    elif csr >= 96.0:
        return round(92.0 + ((csr - 96.0) / 2.0) * 6.0, 1)
    elif csr >= 93.0:
        return round(82.0 + ((csr - 93.0) / 3.0) * 8.0, 1)
    elif csr >= 90.0:
        return round(70.0 + ((csr - 90.0) / 3.0) * 10.0, 1)
    else:
        return max(40.0, round(csr * 0.75, 1))

def calculate_pc_feature_score(policy):
    """Calculates Property & Casualty peril protection and liability score (0 - 100)."""
    score = 0.0

    # 1. Third-party liability cover (up to 30 pts)
    liability = getattr(policy, 'third_party_liability', 0)
    if liability >= 2000000:
        score += 30.0
    elif liability >= 1000000:
        score += 24.0
    elif liability >= 500000:
        score += 18.0
    elif liability > 0:
        score += 10.0

    # 2. Natural calamities (Earthquake, Flood, Storm) (up to 25 pts)
    nat = getattr(policy, 'natural_calamities_covered', 'Yes')
    if str(nat).strip().lower() == 'yes':
        score += 25.0

    # 3. Burglary & Theft cover (up to 25 pts)
    theft = getattr(policy, 'burglary_theft_covered', 'Yes')
    if str(theft).strip().lower() == 'yes':
        score += 25.0

    # 4. Loss of Rent / Alternative Living (up to 20 pts)
    rent = getattr(policy, 'loss_of_rent_covered', 'Yes')
    if str(rent).strip().lower() == 'yes':
        score += 20.0

    return min(100.0, round(score, 1))

def score_policy(policy, customer):
    """
    Computes suitability score and component breakdowns for a single P&C policy.
    """
    budget = customer.get('insurance_budget', 10000)
    requested_coverage = customer.get('required_coverage', customer.get('property_value', 5000000))

    budget_score = calculate_budget_fit_score(policy.annual_premium, budget)
    coverage_score = calculate_coverage_score(policy.coverage_amount, requested_coverage)
    csr_score = calculate_csr_score(policy.claim_settlement_ratio)
    feature_score = calculate_pc_feature_score(policy)

    # Weights: Coverage 30%, Budget 25%, Claim Track Record 25%, Peril/Liability Features 20%
    total_score = (
        coverage_score * 0.30 +
        budget_score * 0.25 +
        csr_score * 0.25 +
        feature_score * 0.20
    )

    score_breakdown = {
        'total_score': round(total_score, 1),
        'budget_score': budget_score,
        'coverage_score': coverage_score,
        'csr_score': csr_score,
        'feature_score': feature_score
    }

    return score_breakdown

def rank_policies(eligible_policies, customer, top_n=3):
    """
    Scores and ranks eligible P&C policies, returning top N with distinct badges.
    """
    scored_list = []
    for policy in eligible_policies:
        breakdown = score_policy(policy, customer)
        scored_list.append({
            'policy': policy,
            'policy_dict': policy.to_dict(),
            'score': breakdown['total_score'],
            'breakdown': breakdown
        })

    scored_list.sort(key=lambda x: x['score'], reverse=True)
    top_results = scored_list[:top_n]

    badges = [
        {"badge": "Best Overall P&C Shield", "badge_class": "badge-blue"},
        {"badge": "Top Claim Reliability", "badge_class": "badge-green"},
        {"badge": "Budget Smart Cover", "badge_class": "badge-blue"}
    ]

    for idx, item in enumerate(top_results):
        b = badges[idx] if idx < len(badges) else {"badge": f"Top Match #{idx+1}", "badge_class": "badge-blue"}
        item['badge'] = b['badge']
        item['badge_class'] = b['badge_class']

    return top_results
