from .tools import (
    PolicySearchTool,
    PolicyScoringTool,
    PolicyCompareTool,
    RecommendationExplainerTool
)
from .llm_service import generate_enhanced_ai_explanation

class PolicyAssistAgent:
    """
    Core AI Agent coordinating policy discovery, scoring, comparison, 
    and natural language reasoning.
    """
    def __init__(self):
        self.search_tool = PolicySearchTool()
        self.scoring_tool = PolicyScoringTool()
        self.compare_tool = PolicyCompareTool()
        self.explainer_tool = RecommendationExplainerTool()

    def run_recommendation(self, customer_data, all_policies=None, top_n=3):
        """
        End-to-end agent workflow:
        1. Search & Filter eligible policies
        2. Score & Rank policies
        3. Formulate transparent natural language explanation
        """
        # Step 1: Tool call - search
        search_result = self.search_tool.execute(customer_data, all_policies=all_policies)
        eligible_policies = search_result['eligible_policies']
        is_relaxed = search_result['is_relaxed']

        if not eligible_policies:
            return {
                'success': False,
                'message': 'No eligible policies found for your criteria. Consider expanding your budget or coverage preferences.',
                'recommendations': [],
                'explanation': ''
            }

        # Step 2: Tool call - scoring & ranking
        top_ranked = self.scoring_tool.execute(eligible_policies, customer_data, top_n=top_n)

        # Step 3: Tool call - explanation generation (deterministic)
        base_explanation = self.explainer_tool.execute(customer_data, top_ranked)

        # Step 4: Optional LLM enhancement
        final_explanation = generate_enhanced_ai_explanation(customer_data, top_ranked, base_explanation)

        return {
            'success': True,
            'is_relaxed': is_relaxed,
            'total_eligible': len(eligible_policies),
            'recommendations': top_ranked,
            'explanation': final_explanation
        }

    def compare(self, policy_ids):
        """Tool call - compare multiple policies side-by-side."""
        return self.compare_tool.execute(policy_ids)
