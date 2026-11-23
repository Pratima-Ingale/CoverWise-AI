/**
 * CoverWise AI - Recommendations Controller
 * Property & Casualty form submission and Top 3 policy recommendations renderer.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Input Form
    const inputForm = document.getElementById('customerInputForm');
    if (inputForm) {
        initInputForm(inputForm);
    }

    // 2. Render Recommendations Page
    const recsContainer = document.getElementById('recommendationsContainer');
    if (recsContainer) {
        renderRecommendationsPage();
    }
});

/**
 * Handles form submission with the 5 Property & Casualty fields
 */
function initInputForm(form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = document.getElementById('submitBtn');
        const originalText = submitBtn.innerHTML;

        const propertyType = document.getElementById('property_type').value;
        const propertyValue = parseInt(document.getElementById('property_value').value);
        const propertyAge = parseInt(document.getElementById('property_age').value);
        const insuranceBudget = parseFloat(document.getElementById('insurance_budget').value);
        const requiredCoverage = parseInt(document.getElementById('required_coverage').value);

        const payload = {
            customer_name: 'Property Owner',
            property_type: propertyType,
            property_value: propertyValue,
            property_age: propertyAge,
            insurance_budget: insuranceBudget,
            required_coverage: requiredCoverage,
            annual_income: Math.round(propertyValue * 0.25),
            priority_preference: 'balanced'
        };

        try {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Finding Best P&C Policies...';

            const response = await fetch('/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await response.json();
            if (response.ok && result.success) {
                sessionStorage.setItem('coverwise_latest_result', JSON.stringify(result));
                showToast('Found top 3 Property & Casualty policies for you!', 'success');
                window.location.href = '/recommendations';
            } else {
                showToast(result.message || 'Could not find matching P&C policies.', 'error');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        } catch (error) {
            console.error('Submission error:', error);
            showToast('Could not connect to CoverWise recommendation agent.', 'error');
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });
}

/**
 * Renders the 3 recommended P&C policies with "Why recommended?" explanation
 */
function renderRecommendationsPage() {
    const rawData = sessionStorage.getItem('coverwise_latest_result');
    const container = document.getElementById('recommendationsContainer');
    const userSummary = document.getElementById('userInputSummary');

    if (!rawData) {
        if (container) {
            container.innerHTML = `
                <div class="card" style="text-align: center; padding: 3rem 1.5rem; grid-column: 1/-1;">
                    <i class="fa-solid fa-house-chimney-crack" style="font-size: 2.5rem; color: var(--primary-blue); margin-bottom: 1rem;"></i>
                    <h3>No Recommendations Yet</h3>
                    <p style="color: var(--text-muted); margin: 0.75rem 0 1.5rem;">
                        Please submit your property valuation and requirements in the Property Input form to view recommendations.
                    </p>
                    <a href="/input" class="btn btn-primary">
                        <i class="fa-solid fa-arrow-right"></i> Go to Property Input Form
                    </a>
                </div>
            `;
        }
        if (userSummary) userSummary.style.display = 'none';
        return;
    }

    const data = JSON.parse(rawData);
    const { customer, recommendations } = data;

    // Render User Input Summary Bar
    if (userSummary && customer) {
        userSummary.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
                <div style="display: flex; gap: 1.5rem; flex-wrap: wrap; font-size: 0.92rem;">
                    <span><i class="fa-solid fa-building" style="color: var(--primary-blue);"></i> Property: <strong>${customer.property_type}</strong></span>
                    <span><i class="fa-solid fa-calendar" style="color: var(--primary-blue);"></i> Age: <strong>${customer.property_age} yrs</strong></span>
                    <span><i class="fa-solid fa-calculator" style="color: var(--primary-blue);"></i> Valuation: <strong>${formatCurrency(customer.property_value)}</strong></span>
                    <span><i class="fa-solid fa-wallet" style="color: var(--primary-blue);"></i> Budget: <strong>${formatCurrency(customer.insurance_budget)}/yr</strong></span>
                </div>
                <span class="badge badge-green"><i class="fa-solid fa-circle-check"></i> 3 Top P&C Matches</span>
            </div>
        `;
    }

    // Render 3 Policy Cards
    if (container && recommendations) {
        container.innerHTML = '';
        const recIds = [];

        recommendations.slice(0, 3).forEach((item, index) => {
            const p = item.policy;
            recIds.push(p.policy_id);

            // Generate clear, friendly P&C "Why recommended?" explanation
            let whyText = '';
            const budgetDiff = customer.insurance_budget - p.annual_premium;
            const savingsStr = budgetDiff >= 0 
                ? `saving ₹${Math.abs(budgetDiff).toLocaleString('en-IN')} below your target budget`
                : `delivering high value within your stretch budget`;

            if (index === 0) {
                whyText = `Ranked as your <strong>#1 Best Match</strong>: Provides full <strong>${formatCurrency(p.coverage_amount)}</strong> property protection for <strong>${formatCurrency(p.annual_premium)}/yr</strong> (${savingsStr}). Includes <strong>${formatCurrency(p.third_party_liability)}</strong> casualty liability cover with an outstanding <strong>${p.claim_settlement_ratio}%</strong> Claim Settlement Ratio.`;
            } else if (index === 1) {
                whyText = `Excellent alternative by <strong>${p.company_name}</strong> offering <strong>${formatCurrency(p.coverage_amount)}</strong> property sum insured, strong flood & earthquake disaster coverage, and <strong>${p.claim_settlement_ratio}%</strong> CSR.`;
            } else {
                whyText = `Budget-smart choice securing essential structural damage, burglary, and <strong>${formatCurrency(p.third_party_liability)}</strong> public liability for an economical premium of <strong>${formatCurrency(p.annual_premium)}/yr</strong>.`;
            }

            const card = document.createElement('div');
            card.className = 'rec-card';
            card.innerHTML = `
                <div>
                    <!-- Header -->
                    <div class="rec-rank-header">
                        <span class="badge badge-blue">Rank #${index + 1} Best Match</span>
                        <span class="badge badge-green">${Math.round(item.score)}% Suitability</span>
                    </div>

                    <!-- Policy Name & Company -->
                    <h3 class="policy-title">${p.policy_name}</h3>
                    <div class="policy-company">
                        <i class="fa-solid fa-building-shield" style="color: var(--primary-blue); margin-right: 0.25rem;"></i>
                        ${p.company_name} &bull; <span style="color: var(--primary-blue); font-weight: 600;">${p.policy_type}</span>
                    </div>

                    <!-- Stats Box -->
                    <div class="rec-stats-box">
                        <div class="stat-metric highlight">
                            <div class="stat-label">Annual Premium</div>
                            <div class="stat-val">${formatCurrency(p.annual_premium)}</div>
                            <small style="font-size: 0.72rem; color: var(--text-muted);">per year</small>
                        </div>
                        <div class="stat-metric">
                            <div class="stat-label">Property Coverage</div>
                            <div class="stat-val">${formatCurrency(p.coverage_amount)}</div>
                            <small style="font-size: 0.72rem; color: var(--text-muted);">Sum Insured</small>
                        </div>
                        <div class="stat-metric">
                            <div class="stat-label">Claim Settlement</div>
                            <div class="stat-val" style="color: var(--success);">${p.claim_settlement_ratio}%</div>
                            <small style="font-size: 0.72rem; color: var(--text-muted);">CSR Ratio</small>
                        </div>
                        <div class="stat-metric">
                            <div class="stat-label">Casualty Liability</div>
                            <div class="stat-val" style="font-size: 1.15rem; color: var(--primary-blue);">${formatCurrency(p.third_party_liability)}</div>
                            <small style="font-size: 0.72rem; color: var(--text-muted);">Public Defense</small>
                        </div>
                    </div>

                    <!-- Why Recommended? Box -->
                    <div class="why-recommended-box">
                        <div class="why-title">
                            <i class="fa-solid fa-circle-question"></i> Why recommended?
                        </div>
                        <div>${whyText}</div>
                    </div>
                </div>

                <!-- Actions -->
                <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
                    <button class="btn btn-outline btn-sm btn-block" onclick="addSingleToCompare('${p.policy_id}')">
                        <i class="fa-solid fa-plus"></i> Add to Compare
                    </button>
                    <button class="btn btn-primary btn-sm btn-block" onclick="goToComparisonWithPolicy('${p.policy_id}')">
                        <i class="fa-solid fa-code-compare"></i> Compare Now
                    </button>
                </div>
            `;
            container.appendChild(card);
        });

        // Setup Compare All 3 button
        const compareAllBtn = document.getElementById('compareAllTopBtn');
        if (compareAllBtn) {
            compareAllBtn.addEventListener('click', () => {
                ComparisonStore.setIds(recIds);
                window.location.href = `/compare?ids=${recIds.join(',')}`;
            });
        }
    }
}

function addSingleToCompare(policyId) {
    ComparisonStore.addId(policyId);
    showToast(`Added ${policyId} to comparison. View it in Policy Comparison.`, 'success');
}

function goToComparisonWithPolicy(policyId) {
    const rawData = sessionStorage.getItem('coverwise_latest_result');
    let compareIds = [policyId];
    if (rawData) {
        try {
            const data = JSON.parse(rawData);
            if (data.recommendations) {
                const otherIds = data.recommendations.map(r => r.policy.policy_id).filter(id => id !== policyId);
                compareIds = [policyId, ...otherIds.slice(0, 2)];
            }
        } catch (e) {}
    }
    ComparisonStore.setIds(compareIds);
    window.location.href = `/compare?ids=${compareIds.join(',')}`;
}
