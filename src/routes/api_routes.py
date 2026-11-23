import json
import os
from flask import Blueprint, request, jsonify
from database.models import db, Policy, Customer, RecommendationHistory
from src.agent.agent_controller import PolicyAssistAgent

api_bp = Blueprint('api', __name__, url_prefix='/api')
agent = PolicyAssistAgent()

@api_bp.route('/recommend', methods=['POST'])
def recommend():
    """
    Receives property profile, runs the AI agent recommendation workflow for P&C,
    stores records in MySQL/SQLite via SQLAlchemy, and returns top 3 recommendations.
    """
    data = request.get_json() or {}

    try:
        customer_name = str(data.get('customer_name', 'Property Owner')).strip() or 'Property Owner'
        property_type = str(data.get('property_type', data.get('preferred_policy_type', 'All'))).strip()
        property_age = int(data.get('property_age', data.get('age', 5)))
        property_value = int(data.get('property_value', data.get('required_coverage', 5000000)))
        insurance_budget = float(data.get('insurance_budget', 10000))
        required_coverage = int(data.get('required_coverage', property_value))
        annual_income = int(data.get('annual_income', 1000000))
        priority_preference = str(data.get('priority_preference', 'balanced')).strip()
    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'message': f'Invalid input format: {str(e)}'}), 400

    customer_dict = {
        'customer_name': customer_name,
        'property_type': property_type,
        'property_age': property_age,
        'property_value': property_value,
        'insurance_budget': insurance_budget,
        'required_coverage': required_coverage,
        'annual_income': annual_income,
        'priority_preference': priority_preference
    }

    # Run AI recommendation agent
    result = agent.run_recommendation(customer_dict, top_n=3)
    if not result['success']:
        return jsonify(result), 404

    # Save to database
    try:
        customer = Customer(
            customer_name=customer_name,
            property_type=property_type,
            property_age=property_age,
            property_value=property_value,
            annual_income=annual_income,
            insurance_budget=insurance_budget,
            required_coverage=required_coverage,
            priority_preference=priority_preference
        )
        db.session.add(customer)
        db.session.flush()

        stored_recommendations = []
        for item in result['recommendations']:
            p = item['policy_dict']
            stored_recommendations.append({
                'policy_id': p['policy_id'],
                'policy_name': p['policy_name'],
                'company_name': p['company_name'],
                'annual_premium': p['annual_premium'],
                'coverage_amount': p['coverage_amount'],
                'third_party_liability': p.get('third_party_liability', 500000),
                'score': item['score'],
                'badge': item['badge'],
                'badge_class': item.get('badge_class', 'badge-blue')
            })

        history = RecommendationHistory(
            customer_id=customer.id,
            recommended_policies_json=json.dumps(stored_recommendations),
            ai_explanation=result['explanation']
        )
        db.session.add(history)
        db.session.commit()

        result['customer_id'] = customer.id
        result['history_id'] = history.id
    except Exception as e:
        db.session.rollback()
        print(f"[DATABASE ERROR] Could not persist recommendation: {e}")

    # Serialize top recommendations for JSON response
    serialized_recommendations = []
    for item in result['recommendations']:
        serialized_recommendations.append({
            'policy': item['policy_dict'],
            'score': item['score'],
            'breakdown': item['breakdown'],
            'badge': item['badge'],
            'badge_class': item['badge_class']
        })

    return jsonify({
        'success': True,
        'customer': customer_dict,
        'is_relaxed': result['is_relaxed'],
        'total_eligible': result['total_eligible'],
        'recommendations': serialized_recommendations,
        'explanation': result['explanation']
    })

@api_bp.route('/compare', methods=['GET'])
def compare():
    """Returns side-by-side comparison data for comma-separated policy IDs."""
    policy_ids_str = request.args.get('ids', '')
    if not policy_ids_str:
        return jsonify({'success': False, 'message': 'No policy IDs provided.'}), 400

    policy_ids = [pid.strip() for pid in policy_ids_str.split(',') if pid.strip()]
    comparison_data = agent.compare(policy_ids)
    return jsonify({'success': True, 'data': comparison_data})

@api_bp.route('/policies', methods=['GET'])
def get_policies():
    """Returns catalog of Property & Casualty policies."""
    ptype = request.args.get('type')
    query = Policy.query
    if ptype and ptype.lower() != 'all':
        query = query.filter_by(policy_type=ptype)
    policies = query.all()
    return jsonify({'success': True, 'count': len(policies), 'policies': [p.to_dict() for p in policies]})

@api_bp.route('/sample-profiles', methods=['GET'])
def get_sample_profiles():
    """Loads sample Property & Casualty customer profiles for instant testing."""
    json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sample_customers.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            profiles = json.load(f)
        return jsonify({'success': True, 'profiles': profiles})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
