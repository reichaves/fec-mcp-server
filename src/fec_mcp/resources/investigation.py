from ..server import mcp

@mcp.prompt()
def investigate_candidate(candidate_name: str) -> str:
    """Generate a structured prompt for investigating a candidate's finances"""
    return f"""I am going to investigate the campaign finances of {candidate_name}.

Please execute the following steps:

1. **Search for the candidate**
   Use search_candidates(name="{candidate_name}") to find the correct ID.

2. **Analyze general finances**
   With the candidate_id, use get_candidate_finances() to view total raised and spent amounts.

3. **Identify top donors**
   Use get_top_donors() with the committee_id to see who contributes the most.

4. **Verify donation patterns**
   - Is there a concentration of donors from a specific industry?
   - From which states does the money come? Use get_contributions_by_state()
   
5. **Analyze expenditures**
   Use get_campaign_expenditures() to see how the money is being spent.
   - Who are the biggest vendors?
   - How much goes to advertising vs consulting?

6. **Verify outside support**
   Use get_independent_expenditures(candidate_id=...) to see Super PAC spending.
   - Which groups support or oppose?
   - What is the volume of independent expenditures?

At the end, summarize:
- Total raised and spent
- Top 5 donors
- Top 5 employers of the donors
- Key Super PACs involved
- Any interesting or suspicious patterns
"""


@mcp.prompt()
def follow_the_money(company_name: str) -> str:
    """Generate a prompt for tracing corporate money in politics"""
    return f"""I am going to trace the political influence of {company_name}.

Please execute:

1. **Search for employees who donated**
   search_contributions(contributor_employer="{company_name}")
   
2. **Identify patterns**
   - Which candidates receive the most from employees of this company?
   - Is there a partisan preference?
   - Coordinated donations (same day, same amount)?

3. **Search for corporate PAC**
   search_pacs(name="{company_name}")
   - Does the company have its own PAC?
   - How much does the PAC raise and distribute?

4. **Verify independent expenditures**
   Are there Super PACs associated with or receiving money from the company?

5. **Additional context**
   - Does the company have specific regulatory interests?
   - Were there changes in donation patterns after specific events?

Summarize:
- Total donated by employees
- Top recipients
- Existence of a corporate PAC
- Potential conflicts of interest
"""


@mcp.prompt()
def compare_candidates(candidate1: str, candidate2: str) -> str:
    """Generate a prompt for comparing two candidates' finances"""
    return f"""I am going to compare the finances of {candidate1} vs {candidate2}.

For each candidate, obtain:

1. **IDs and basic information**
   search_candidates(name="...") for both

2. **Financial totals**
   get_candidate_finances() to compare:
   - Total raised
   - Total spent
   - Cash on hand
   - Debts

3. **Donor profile**
   get_top_donors() for each:
   - Who are the top donors?
   - Which industries predominate?
   
4. **Geography of the money**
   get_contributions_by_state() to map:
   - Where does the money for each come from?
   - Does either receive more from out of state/district?

5. **Outside support**
   get_independent_expenditures() for both:
   - Which Super PACs support each?
   - Volume of spending for and against

Produce a comparative table with:
| Metric | {candidate1} | {candidate2} |
|---------|--------------|--------------|
| Total raised | | |
| Total spent | | |
| Top donor | | |
| Top industry | | |
| % out of state | | |
| Super PAC support | | |
| Super PAC opposition | | |
"""
