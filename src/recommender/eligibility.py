def filter_eligible_policies(policies, customer):
    """
    Filters Property & Casualty policies based on property characteristics,
    valuation, property age, and budget criteria.
    Returns:
        eligible_policies (list): policies meeting eligibility
        is_relaxed (bool): whether criteria were relaxed to provide recommendations
    """
    property_age = customer.get('property_age', customer.get('age', 5))
    property_value = customer.get('property_value', customer.get('required_coverage', 5000000))
    budget = customer.get('insurance_budget', 10000)
    preferred_type = customer.get('property_type', customer.get('preferred_policy_type', 'All'))

    eligible = []
    for policy in policies:
        # 1. Property Age boundary check
        min_age = getattr(policy, 'min_property_age', 0)
        max_age = getattr(policy, 'max_property_age', 60)
        if not (min_age <= property_age <= max_age):
            continue

        # 2. Property Value range check
        min_val = getattr(policy, 'min_property_value', 100000)
        max_val = getattr(policy, 'max_property_value', 100000000)
        if property_value < min_val or property_value > max_val:
            continue

        # 3. Property Type Match
        if preferred_type and preferred_type.lower() not in ['all', 'any']:
            pref = preferred_type.lower()
            ptype = policy.policy_type.lower()
            
            # Allow flexible sub-category matching
            is_match = (
                pref in ptype or
                ptype in pref or
                ('residential' in pref and ('homeowner' in ptype or 'apartment' in ptype)) or
                ('home' in pref and ('apartment' in ptype or 'homeowner' in ptype)) or
                ('commercial' in pref and ('business' in ptype or 'commercial' in ptype)) or
                ('tenant' in pref and 'renter' in ptype) or
                ('renter' in pref and 'tenant' in ptype)
            )
            if not is_match:
                continue

        # 4. Budget tolerance check (allow up to 30% stretch for comprehensive peril protection)
        max_acceptable_premium = budget * 1.30 if budget > 0 else float('inf')
        if policy.annual_premium > max_acceptable_premium:
            continue

        eligible.append(policy)

    # If fewer than 3 policies are found, apply a soft relaxation (expand budget & type boundaries)
    if len(eligible) < 3:
        relaxed = []
        for policy in policies:
            min_age = getattr(policy, 'min_property_age', 0)
            max_age = getattr(policy, 'max_property_age', 60)
            if not (min_age <= property_age <= (max_age + 10)):
                continue
            relaxed.append(policy)
        if len(relaxed) >= len(eligible):
            return relaxed, True

    return eligible, False
