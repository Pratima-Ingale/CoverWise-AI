/**
 * CoverWise AI - Property & Casualty Policy Comparison Controller
 * Renders visual bar metrics and side-by-side comparison for 2 or 3 policies.
 */

document.addEventListener('DOMContentLoaded', () => {
    initComparePage();
});

let availablePolicies = [];

async function initComparePage() {
    // 1. Fetch all policies for the dropdown selector
    try {
        const res = await fetch('/api/policies');
        const data = await res.json();
        if (data.success && data.policies) {
            availablePolicies = data.policies;
            populateDropdown();
        }
    } catch (err) {
        console.error('Error fetching policies:', err);
    }

    // 2. Determine policies to compare
    const urlParams = new URLSearchParams(window.location.search);
    const queryIds = urlParams.get('ids');

    let policyIds = [];
    if (queryIds) {
        policyIds = queryIds.split(',').map(s => s.trim()).filter(Boolean);
        ComparisonStore.setIds(policyIds);
    } else {
        policyIds = ComparisonStore.getIds();
    }

    // If still empty, check if we have recommendations in sessionStorage
    if (policyIds.length === 0) {
        const rawRecs = sessionStorage.getItem('coverwise_latest_result');
        if (rawRecs) {
            try {
                const recData = JSON.parse(rawRecs);
                if (recData.recommendations && recData.recommendations.length > 0) {
                    policyIds = recData.recommendations.slice(0, 3).map(r => r.policy.policy_id);
                    ComparisonStore.setIds(policyIds);
                }
            } catch (e) {}
        }
    }

    // Fallback: Pick first 2 available P&C policies so user sees a working comparison
    if (policyIds.length === 0 && availablePolicies.length >= 2) {
        policyIds = [availablePolicies[0].policy_id, availablePolicies[1].policy_id];
        ComparisonStore.setIds(policyIds);
    }

    // Limit to 3 policies maximum
    policyIds = policyIds.slice(0, 3);
    ComparisonStore.setIds(policyIds);

    // 3. Render visualization & table
    await renderComparison(policyIds);
}

function populateDropdown() {
    const select = document.getElementById('policySelect');
    if (!select) return;

    select.innerHTML = '<option value="">-- Choose a Property & Casualty policy to compare (Up to 3) --</option>';
    const currentIds = ComparisonStore.getIds();

    availablePolicies.forEach(p => {
        const isSelected = currentIds.includes(p.policy_id);
        select.innerHTML += `
            <option value="${p.policy_id}" ${isSelected ? 'disabled' : ''}>
                ${p.policy_name} (${p.company_name}) - ${formatCurrency(p.annual_premium)}/yr
            </option>
        `;
    });

    select.addEventListener('change', (e) => {
        const id = e.target.value;
        if (!id) return;
        const ids = ComparisonStore.getIds();
        if (ids.length >= 3) {
            showToast('You can compare a maximum of 3 policies. Remove one first.', 'warning');
            select.value = '';
            return;
        }
        ComparisonStore.addId(id);
        window.location.href = `/compare?ids=${ComparisonStore.getIds().join(',')}`;
    });
}

async function renderComparison(policyIds) {
    const container = document.getElementById('compareContentArea');
    if (!container) return;

    if (policyIds.length === 0) {
        container.innerHTML = `
            <div class="card" style="text-align: center; padding: 3rem 1.5rem;">
                <i class="fa-solid fa-code-compare" style="font-size: 2.5rem; color: var(--primary-blue); margin-bottom: 1rem;"></i>
                <h3>No Policies Selected</h3>
                <p style="color: var(--text-muted); margin: 0.75rem 0 1.5rem;">
                    Please select 2 or 3 Property & Casualty policies from the dropdown above to view their visual comparison.
                </p>
                <button class="btn btn-primary" onclick="loadTopRecommendationsToCompare()">
                    <i class="fa-solid fa-wand-magic-sparkles"></i> Compare Recommended Policies
                </button>
            </div>
        `;
        return;
    }

    try {
        const res = await fetch(`/api/compare?ids=${policyIds.join(',')}`);
        const data = await res.json();

        if (res.ok && data.success && data.data && data.data.policies.length > 0) {
            const policies = data.data.policies;

            // Compute maximums for relative visual bar scaling
            const maxPremium = Math.max(...policies.map(p => p.annual_premium || 1), 20000);
            const maxCoverage = Math.max(...policies.map(p => p.coverage_amount || 1), 10000000);
            const maxLiability = Math.max(...policies.map(p => p.third_party_liability || 1), 2500000);

            // Find best in category for quick verdict
            const lowestPrem = [...policies].sort((a,b) => a.annual_premium - b.annual_premium)[0];
            const highestCov = [...policies].sort((a,b) => b.coverage_amount - a.coverage_amount)[0];
            const highestCsr = [...policies].sort((a,b) => b.claim_settlement_ratio - a.claim_settlement_ratio)[0];

            // 1. Build Visual Cards for 2 or 3 policies
            let visualHtml = `
                <div style="margin-bottom: 1.25rem;">
                    <h3 style="margin-bottom: 0.25rem;">Visual P&C Policy Comparison (${policies.length} Policies)</h3>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">Comparing annual premium, property sum insured, casualty liability, and claim settlement.</p>
                </div>
                <div class="compare-cards-grid">
            `;

            policies.forEach(p => {
                const premPct = Math.min(100, Math.round((p.annual_premium / maxPremium) * 100));
                const covPct = Math.min(100, Math.round((p.coverage_amount / maxCoverage) * 100));
                const csrPct = Math.round(p.claim_settlement_ratio);
                const liabPct = Math.min(100, Math.round((p.third_party_liability / maxLiability) * 100));

                visualHtml += `
                    <div class="compare-visual-card">
                        <div class="compare-header">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem;">
                                <div>
                                    <h4 style="font-size: 1.15rem; margin-bottom: 0.2rem;">${p.policy_name}</h4>
                                    <div style="font-size: 0.85rem; color: var(--text-muted); font-weight: 500;">
                                        <i class="fa-solid fa-building-shield" style="color: var(--primary-blue);"></i> ${p.company_name}
                                    </div>
                                </div>
                                <button class="btn btn-outline btn-sm" style="color: #ef4444; border-color: transparent; padding: 0.2rem 0.4rem;" onclick="removeComparePolicy('${p.policy_id}')" title="Remove">
                                    <i class="fa-solid fa-xmark"></i>
                                </button>
                            </div>
                        </div>

                        <!-- Visual Bars -->
                        <div class="visual-bar-item">
                            <div class="visual-bar-label">
                                <span>Annual Premium</span>
                                <strong style="color: var(--primary-blue);">${formatCurrency(p.annual_premium)}/yr</strong>
                            </div>
                            <div class="visual-bar-track">
                                <div class="visual-bar-fill" style="width: ${premPct}%;"></div>
                            </div>
                        </div>

                        <div class="visual-bar-item">
                            <div class="visual-bar-label">
                                <span>Property Sum Insured</span>
                                <strong>${formatCurrency(p.coverage_amount)}</strong>
                            </div>
                            <div class="visual-bar-track">
                                <div class="visual-bar-fill sky" style="width: ${covPct}%;"></div>
                            </div>
                        </div>

                        <div class="visual-bar-item">
                            <div class="visual-bar-label">
                                <span>Casualty Liability Cover</span>
                                <strong style="color: var(--primary-blue);">${formatCurrency(p.third_party_liability)}</strong>
                            </div>
                            <div class="visual-bar-track">
                                <div class="visual-bar-fill sky" style="width: ${liabPct}%;"></div>
                            </div>
                        </div>

                        <div class="visual-bar-item">
                            <div class="visual-bar-label">
                                <span>Claim Settlement Ratio</span>
                                <strong style="color: var(--success);">${p.claim_settlement_ratio}%</strong>
                            </div>
                            <div class="visual-bar-track">
                                <div class="visual-bar-fill green" style="width: ${csrPct}%;"></div>
                            </div>
                        </div>

                        <div style="background: var(--bg-page); border-radius: var(--radius-sm); padding: 0.75rem; margin-top: 1rem; font-size: 0.85rem; display: flex; justify-content: space-between;">
                            <span>Standard Deductible:</span>
                            <strong>${formatCurrency(p.deductible_amount)}</strong>
                        </div>
                    </div>
                `;
            });

            visualHtml += `</div>`;

            // Quick Comparison Summary Verdict
            let verdictHtml = `
                <div class="card" style="background: var(--bg-light-blue); border-color: var(--border-blue); padding: 1.25rem 1.5rem; margin-bottom: 2rem;">
                    <h4 style="color: var(--primary-blue); font-size: 1rem; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.4rem;">
                        <i class="fa-solid fa-lightbulb"></i> P&C Comparison Summary:
                    </h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 0.75rem; font-size: 0.88rem;">
                        <div>🏷️ <strong>Lowest Premium:</strong> ${lowestPrem.policy_name} (${formatCurrency(lowestPrem.annual_premium)}/yr)</div>
                        <div>🛡️ <strong>Highest Coverage:</strong> ${highestCov.policy_name} (${formatCurrency(highestCov.coverage_amount)})</div>
                        <div>⭐ <strong>Best Claim Ratio:</strong> ${highestCsr.policy_name} (${highestCsr.claim_settlement_ratio}%)</div>
                    </div>
                </div>
            `;

            // 2. Build Clean Side-by-Side Table
            let tableHtml = `
                <div style="margin: 1.5rem 0 1rem;">
                    <h3 style="margin-bottom: 0.25rem;">Detailed P&C Feature Comparison</h3>
                </div>
                <div class="table-wrapper">
                    <table class="clean-table">
                        <thead>
                            <tr>
                                <th style="width: 28%;">Feature / Coverage</th>
                                ${policies.map(p => `<th>${p.policy_name}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>Insurance Company</strong></td>
                                ${policies.map(p => `<td>${p.company_name}</td>`).join('')}
                            </tr>
                            <tr>
                                <td><strong>Policy Category</strong></td>
                                ${policies.map(p => `<td><span class="badge badge-blue">${p.policy_type}</span></td>`).join('')}
                            </tr>
                            <tr>
                                <td><strong>Annual Premium</strong></td>
                                ${policies.map(p => `<td><strong style="color: var(--primary-blue); font-size: 1.05rem;">${formatCurrency(p.annual_premium)}</strong>/yr</td>`).join('')}
                            </tr>
                            <tr>
                                <td><strong>Property Sum Insured</strong></td>
                                ${policies.map(p => `<td><strong>${formatCurrency(p.coverage_amount)}</strong></td>`).join('')}
                            </tr>
                            <tr>
                                <td><strong>Third-Party Casualty Liability</strong></td>
                                ${policies.map(p => `<td><strong style="color: var(--primary-blue);">${formatCurrency(p.third_party_liability)}</strong></td>`).join('')}
                            </tr>
                            <tr>
                                <td><strong>Claim Settlement Ratio</strong></td>
                                ${policies.map(p => `<td><strong style="color: var(--success);">${p.claim_settlement_ratio}%</strong></td>`).join('')}
                            </tr>
                            <tr>
                                <td><strong>Fire & Explosion Perils</strong></td>
                                ${policies.map(p => `<td>${p.fire_perils_covered || 'Yes'}</td>`).join('')}
                            </tr>
                            <tr>
                                <td><strong>Natural Calamities (Flood/Quake)</strong></td>
                                ${policies.map(p => `<td>${p.natural_calamities_covered || 'Yes'}</td>`).join('')}
                            </tr>
                            <tr>
                                <td><strong>Burglary & Housebreaking</strong></td>
                                ${policies.map(p => `<td>${p.burglary_theft_covered || 'Yes'}</td>`).join('')}
                            </tr>
                            <tr>
                                <td><strong>Loss of Rent / Temp Housing</strong></td>
                                ${policies.map(p => `<td>${p.loss_of_rent_covered || 'Yes'}</td>`).join('')}
                            </tr>
                            <tr>
                                <td><strong>Policy Deductible</strong></td>
                                ${policies.map(p => `<td>${formatCurrency(p.deductible_amount)}</td>`).join('')}
                            </tr>
                        </tbody>
                    </table>
                </div>
            `;

            container.innerHTML = visualHtml + verdictHtml + tableHtml;
        }
    } catch (err) {
        console.error('Error rendering comparison:', err);
    }
}

function removeComparePolicy(id) {
    ComparisonStore.removeId(id);
    const remaining = ComparisonStore.getIds();
    window.location.href = `/compare?ids=${remaining.join(',')}`;
}

function clearComparison() {
    ComparisonStore.clear();
    window.location.href = '/compare';
}

function loadTopRecommendationsToCompare() {
    const rawRecs = sessionStorage.getItem('coverwise_latest_result');
    if (rawRecs) {
        try {
            const data = JSON.parse(rawRecs);
            if (data.recommendations && data.recommendations.length > 0) {
                const ids = data.recommendations.slice(0, 3).map(r => r.policy.policy_id);
                ComparisonStore.setIds(ids);
                window.location.href = `/compare?ids=${ids.join(',')}`;
                return;
            }
        } catch (e) {}
    }
    showToast('No recommendations found. Please submit the Property Input form first.', 'info');
}
