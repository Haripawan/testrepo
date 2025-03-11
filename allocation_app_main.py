import pulp
import pandas as pd

# Configurable variances
project_variance_percent = 3  # ±3% for project budgets
overall_variance_percent = 5  # ±5% for total budget

# Sample data
employees = [
    {'name': 'Alice', 'cost': 5000, 'is_lead': True},
    {'name': 'Bob', 'cost': 4000, 'is_lead': False},
    {'name': 'Charlie', 'cost': 4500, 'is_lead': False},
    {'name': 'David', 'cost': 5500, 'is_lead': True},
    {'name': 'Eve', 'cost': 6000, 'is_lead': False}
]

projects = [
    {'id': 1, 'name': 'Project A', 'start_month': 3, 'end_month': 7, 'budget': 70000},
    {'id': 2, 'name': 'Project B', 'start_month': 1, 'end_month': 12, 'budget': 160000},
    {'id': 3, 'name': 'Project C', 'start_month': 6, 'end_month': 9, 'budget': 70000}
]

# Prepare data structures
employee_names = [e['name'] for e in employees]
project_ids = [p['id'] for p in projects]
months = range(1, 13)  # Months 1 to 12 (Jan to Dec)
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
project_active_months = {p['id']: list(range(p['start_month'], p['end_month'] + 1)) for p in projects}
employees_dict = {e['name']: e for e in employees}
projects_dict = {p['id']: p for p in projects}
total_budget = sum(p['budget'] for p in projects)

# Define the LP problem
prob = pulp.LpProblem("Resource_Allocation", pulp.LpMaximize)

# Variables
# A[e, p, m]: Allocation fraction for employee e on project p in month m
A = pulp.LpVariable.dicts(
    "A",
    [(e, p, m) for e in employee_names for p in project_ids for m in project_active_months[p]],
    lowBound=0,
    upBound=1
)

# B[e, p]: Binary variable indicating if employee e is allocated to project p
B = pulp.LpVariable.dicts("B", [(e, p) for e in employee_names for p in project_ids], cat='Binary')

# Objective: Maximize total allocation
prob += pulp.lpSum(A[(e, p, m)] for e in employee_names for p in project_ids for m in project_active_months[p])

# Constraints
# 1. Employee Availability: Total allocation per employee per month = 1
for e in employee_names:
    for m in months:
        active_projects = [p for p in project_ids if m in project_active_months[p]]
        if active_projects:  # Only add constraint if there are active projects in the month
            prob += pulp.lpSum(A[(e, p, m)] for p in active_projects) == 1, f"Availability_{e}_{m}"

# 2. Project Budget: Total cost within ±3%
for p in project_ids:
    total_cost = pulp.lpSum(
        A[(e, p, m)] * employees_dict[e]['cost']
        for e in employee_names
        for m in project_active_months[p]
    )
    lower_bound = projects_dict[p]['budget'] * (1 - project_variance_percent / 100)
    upper_bound = projects_dict[p]['budget'] * (1 + project_variance_percent / 100)
    prob += total_cost >= lower_bound, f"Budget_Lower_{p}"
    prob += total_cost <= upper_bound, f"Budget_Upper_{p}"

# 3. Overall Budget: Total cost within ±5%
total_allocation_cost = pulp.lpSum(
    A[(e, p, m)] * employees_dict[e]['cost']
    for e in employee_names
    for p in project_ids
    for m in project_active_months[p]
)
total_lower_bound = total_budget * (1 - overall_variance_percent / 100)
total_upper_bound = total_budget * (1 + overall_variance_percent / 100)
prob += total_allocation_cost >= total_lower_bound, "Total_Budget_Lower"
prob += total_allocation_cost <= total_upper_bound, "Total_Budget_Upper"

# 4. Non-Zero Allocation: Link A and B variables
M = 12  # Upper bound for total allocation sum (max months in a project)
for e in employee_names:
    for p in project_ids:
        total_alloc = pulp.lpSum(A[(e, p, m)] for m in project_active_months[p])
        prob += total_alloc <= M * B[(e, p)], f"Link_B_{e}_{p}_upper"
        prob += total_alloc >= B[(e, p)], f"Link_B_{e}_{p}_lower"

# 5. Lead Condition: Leads must be allocated to at least 2 projects
for e in employee_names:
    if employees_dict[e]['is_lead']:
        prob += pulp.lpSum(B[(e, p)] for p in project_ids) >= 2, f"Lead_Allocation_{e}"

# Solve the problem
prob.solve()

# Check solution and display results
if pulp.LpStatus[prob.status] != 'Optimal':
    print("No optimal solution found. Please adjust constraints or data.")
else:
    results = []
    for e in employee_names:
        for p in project_ids:
            if B[(e, p)].varValue > 0:  # Only include if employee is allocated to the project
                allocations = []
                total_cost = 0
                for m in months:
                    if m in project_active_months[p]:
                        alloc = A[(e, p, m)].varValue if (e, p, m) in A else 0
                        allocations.append(round(alloc, 2) if alloc else 0)
                        total_cost += (alloc or 0) * employees_dict[e]['cost']
                    else:
                        allocations.append(0)
                # Verify non-zero allocation
                if any(alloc > 0 for alloc in allocations):
                    results.append({
                        'Resource': e,
                        'Project': projects_dict[p]['name'],
                        'Project ID': p,
                        **{month_names[m-1]: allocations[m-1] for m in months},
                        'Total Cost': round(total_cost, 2)
                    })

    df = pd.DataFrame(results)
    print("\nResource Allocation Results:")
    print(df)