from datetime import datetime
import json
from .db import db

class Policy(db.Model):
    __tablename__ = 'policies'

    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    policy_name = db.Column(db.String(150), nullable=False)
    policy_type = db.Column(db.String(50), nullable=False, index=True)
    company_name = db.Column(db.String(100), nullable=False)
    min_property_age = db.Column(db.Integer, default=0)
    max_property_age = db.Column(db.Integer, default=60)
    min_property_value = db.Column(db.BigInteger, default=100000)
    max_property_value = db.Column(db.BigInteger, default=100000000)
    coverage_amount = db.Column(db.BigInteger, nullable=False)
    annual_premium = db.Column(db.Float, nullable=False)
    claim_settlement_ratio = db.Column(db.Float, nullable=False)
    third_party_liability = db.Column(db.BigInteger, default=500000)
    deductible_amount = db.Column(db.Integer, default=2000)
    fire_perils_covered = db.Column(db.String(10), default='Yes')
    natural_calamities_covered = db.Column(db.String(10), default='Yes')
    burglary_theft_covered = db.Column(db.String(10), default='Yes')
    loss_of_rent_covered = db.Column(db.String(10), default='Yes')
    key_features = db.Column(db.Text, default='')
    description = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'policy_id': self.policy_id,
            'policy_name': self.policy_name,
            'policy_type': self.policy_type,
            'company_name': self.company_name,
            'min_property_age': self.min_property_age,
            'max_property_age': self.max_property_age,
            'min_property_value': self.min_property_value,
            'max_property_value': self.max_property_value,
            'coverage_amount': self.coverage_amount,
            'annual_premium': self.annual_premium,
            'claim_settlement_ratio': self.claim_settlement_ratio,
            'third_party_liability': self.third_party_liability,
            'deductible_amount': self.deductible_amount,
            'fire_perils_covered': self.fire_perils_covered,
            'natural_calamities_covered': self.natural_calamities_covered,
            'burglary_theft_covered': self.burglary_theft_covered,
            'loss_of_rent_covered': self.loss_of_rent_covered,
            'key_features': [f.strip() for f in self.key_features.split(';') if f.strip()] if self.key_features else [],
            'key_features_str': self.key_features,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False, default='Customer')
    property_type = db.Column(db.String(50), nullable=False, default='Homeowners Comprehensive')
    property_age = db.Column(db.Integer, nullable=False, default=5)
    property_value = db.Column(db.BigInteger, nullable=False, default=5000000)
    annual_income = db.Column(db.BigInteger, nullable=False, default=1000000)
    insurance_budget = db.Column(db.Float, nullable=False, default=10000)
    required_coverage = db.Column(db.BigInteger, nullable=False, default=5000000)
    priority_preference = db.Column(db.String(50), default='balanced')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    recommendations = db.relationship('RecommendationHistory', backref='customer', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'property_type': self.property_type,
            'property_age': self.property_age,
            'property_value': self.property_value,
            'annual_income': self.annual_income,
            'insurance_budget': self.insurance_budget,
            'required_coverage': self.required_coverage,
            'priority_preference': self.priority_preference,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }

class RecommendationHistory(db.Model):
    __tablename__ = 'recommendation_history'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    recommended_policies_json = db.Column(db.Text, nullable=False)
    ai_explanation = db.Column(db.Text, nullable=True)
    recommended_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        try:
            policies_data = json.loads(self.recommended_policies_json)
        except Exception:
            policies_data = []

        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer': self.customer.to_dict() if self.customer else None,
            'recommended_policies': policies_data,
            'ai_explanation': self.ai_explanation,
            'recommended_at': self.recommended_at.strftime('%Y-%m-%d %H:%M:%S') if self.recommended_at else ''
        }
