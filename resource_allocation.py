import pulp
import pandas as pd
import sys

# Configurable variance percentages (in percent)
project_variance_percent = 3  # Adjust this value as needed (e.g., 3 for ±3%)
overall_variance_percent = 5  # Adjust this value as needed (e.g., 5 for ±5%)

# Optional: Uncomment to use command-line arguments
# if len(sys.argv) == 3:
#     project_variance_percent = float(sys.argv[1])
#     overall_variance_percent = float(sys.argv[2])

# Display the configured variances
print(f"Project Variance: ±{project_variance_percent}%")
print(f"Overall Variance: ±{overall_variance_percent}%")

# Sample input data
employees = [
    {'name': 'Alice', 'cost': 5000, 'is_lead': True},
    {'name': 'Bob', 'cost': 4000, 'is_lead': False},
    {'name': 'Charlie', 'cost': 4500, 'is_lead': False}
]
projects = [
    {'id': 1, 'name': 'Project A', 'start_month': 3, 'end_month': 7, 'budget': 60000},
    {'id': 2, 'name': 'Project B', 'start_month': 1, 'end_month': 12, 'budget': 150000}
]

# Prepare data structures
employee_names = [e['name'] for e in employees]
project_ids = [p['id'] for p in projects]
months = range(1, 13)  # January (1) to December (12)
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
project_active_months = {p['id']: list(range(p['start_month'], p['end_month'] + 1)) for p in projects}
employees_dict = {e['name']: e for e in employees}
projects_dict = {p['id']: p for p in projects}

# Calculate total budget
total_budget = sum(p['budget'] for p in projects)

# Define the LP problem
prob = pulp.LpProblem("Resource_Allocation", pulp.LpMaximize)

# Variables: A[e, p, m] = allocation of employee e to project p in month m (0 to 1)
A = pulp.LpVariable.dicts(
    "A",
    [(e, p, m) for e in employee_names for p in project_ids for m in project_active_months[p]],
    lowBound=0,
    upBound=1
)

# Objective: Maximize total allocation
prob += pulp.lpSum(A[(e, p, m)] for e in employee_names for p in project_ids for m in project_active_months[p])

# Constraints
# 1. Employee availability: 100% allocation per month
for e in employee_names:
    for m in months:
        active_projects = [p for p in project_ids if m in project_active_months[p]]
        if active_projects:
            prob += pulp.lpSum(A[(e, p, m)] for p in active_projects) == 1, f"Availability_{e}_{m}"

# 2. Project budget: Within ±project_variance_percent of project budget
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

# 3. Overall budget: Within ±overall_variance_percent of total budget
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

# Solve the problem
prob.solve()

# Check for solution
if pulp.LpStatus[prob.status] != 'Optimal':
    print("No optimal solution found.")
else:
    # Extract results
    results = []
    for e in employee_names:
        for p in project_ids:
            allocations = []
            total_cost = 0
            for m in months:
                if m in project_active_months[p]:
                    alloc = A[(e, p, m)].varValue if (e, p, m) in A else 0
                    allocations.append(round(alloc, 2) if alloc else 0)
                    total_cost += (alloc or 0) * employees_dict[e]['cost']
                else:
                    allocations.append(0)
            if total_cost > 0:
                results.append({
                    'Resource': e,
                    'Project': projects_dict[p]['name'],
                    'Project ID': p,
                    **{month_names[m-1]: allocations[m-1] for m in months},
                    'Total Cost': round(total_cost, 2)
                })

    # Load into a pandas DataFrame and print
    df = pd.DataFrame(results)
    print(df)