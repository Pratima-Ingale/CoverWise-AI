import csv
import os
from .models import Policy, db

def seed_policies_from_csv(csv_path=None, force=False):
    """
    Reads Property & Casualty insurance policies from CSV and populates the database table.
    Idempotent: Skips policies that already exist by policy_id unless force=True.
    """
    if csv_path is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        csv_path = os.path.join(base_dir, 'data', 'insurance_policies.csv')

    if not os.path.exists(csv_path):
        print(f"[SEED ERROR] CSV file not found at: {csv_path}")
        return 0

    existing_count = Policy.query.count()
    if existing_count > 0 and not force:
        # Check if the database has old POL101 (health) policies and re-seed if so
        first_policy = Policy.query.first()
        if first_policy and 'POL1' in first_policy.policy_id:
            print("[SEED INFO] Detected legacy policies. Re-seeding with Property & Casualty dataset...")
            Policy.query.delete()
            db.session.commit()
        else:
            print(f"[SEED INFO] Database already contains {existing_count} Property & Casualty policies. Skipping seed.")
            return existing_count

    inserted = 0
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = row['policy_id'].strip()
            existing = Policy.query.filter_by(policy_id=pid).first()
            if existing and not force:
                continue

            policy = Policy(
                policy_id=pid,
                policy_name=row['policy_name'].strip(),
                policy_type=row['policy_type'].strip(),
                company_name=row['company_name'].strip(),
                min_property_age=int(row.get('min_property_age', 0)),
                max_property_age=int(row.get('max_property_age', 60)),
                min_property_value=int(row.get('min_property_value', 100000)),
                max_property_value=int(row.get('max_property_value', 100000000)),
                coverage_amount=int(row.get('coverage_amount', 3000000)),
                annual_premium=float(row.get('annual_premium', 5000)),
                claim_settlement_ratio=float(row.get('claim_settlement_ratio', 95.0)),
                third_party_liability=int(row.get('third_party_liability', 500000)),
                deductible_amount=int(row.get('deductible_amount', 2000)),
                fire_perils_covered=row.get('fire_perils_covered', 'Yes').strip(),
                natural_calamities_covered=row.get('natural_calamities_covered', 'Yes').strip(),
                burglary_theft_covered=row.get('burglary_theft_covered', 'Yes').strip(),
                loss_of_rent_covered=row.get('loss_of_rent_covered', 'Yes').strip(),
                key_features=row.get('key_features', '').strip(),
                description=row.get('description', '').strip()
            )
            db.session.add(policy)
            inserted += 1

    db.session.commit()
    print(f"[SEED SUCCESS] Seeded {inserted} Property & Casualty policies into database.")
    return inserted
