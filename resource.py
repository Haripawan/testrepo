import pandas as pd
from pulp import LpProblem, LpVariable, lpSum, LpMaximize
import calendar

# Data
projects = {
    "P1": {"monthly_budget": 10000, "months": [1, 2, 3, 4, 5, 6]},
    "P2": {"monthly_budget": 8000, "months": list(range(1, 13))},
    "P3": {"monthly_budget": 12000, "months": list(range(1, 13))},
}

employees = {
    "A": 4000,
    "B": 3200,
    "C": 4800,
    "D": 3600,
}

# Initialize problem
problem = LpProblem("Employee_Allocation", LpMaximize)

# Decision variables
x = {(i, j, k): LpVariable(f"x_{i}_{j}_{k}", lowBound=0, upBound=1) 
     for i in employees 
     for j in projects 
     for k in range(1, 13)}

# Objective: Maximize total allocation
problem += lpSum(x[i, j, k] for i in employees for j in projects for k in range(1, 13))

# Constraints
# 1. Each employee must work full time every month
for i in employees:
    for k in range(1, 13):
        problem += lpSum(x[i, j, k] for j in projects) == 1

# 2. Each project's monthly cost must not exceed its budget
for j, project in projects.items():
    for k in project["months"]:
        problem += lpSum(x[i, j, k] * employees[i] for i in employees) <= project["monthly_budget"]

# Solve the problem
problem.solve()

# Prepare the output as a DataFrame
results = []
for k in range(1, 13):
    for i in employees:
        for j in projects:
            if x[i, j, k].varValue > 0:
                results.append({
                    "Employee": i,
                    "Project": j,
                    "Month": calendar.month_name[k],  # Convert month number to name
                    "Allocation": round(x[i, j, k].varValue, 2),
                })

df_results = pd.DataFrame(results)

# Pivot the data to have months as columns
final_df = df_results.pivot_table(
    index=["Employee", "Project"],
    columns="Month",
    values="Allocation",
    aggfunc="first"
).fillna(0).reset_index()

# Display the final DataFrame
print(final_df)