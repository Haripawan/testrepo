import pandas as pd
from pulp import LpProblem, LpVariable, lpSum, LpMaximize, LpStatus, PULP_CBC_CMD
import os

# --- 1. Data Loading and Preprocessing ---
def load_data():
    """Loads resource and project data from CSV files."""
    try:
        resources_df = pd.read_csv("resources.csv")
        projects_df = pd.read_csv("projects.csv")
    except FileNotFoundError as e:
        print(f"Error: {e}. Please ensure 'resources.csv' and 'projects.csv' are in the same directory.")
        return None, None
    return resources_df, projects_df

def preprocess_data(projects_df, resources_df):
    """Preprocesses project data to include monthly costs and active status."""
    if projects_df is None or resources_df is None:
        return None, None

    # Calculate monthly project budget (pro-rated)
    projects_df['duration_months'] = projects_df['end_month'] - projects_df['start_month'] + 1
    projects_df['monthly_budget'] = projects_df['annual_cost'] / projects_df['duration_months']

    # Create a list of all unique months in the planning horizon
    all_months = sorted(list(set(projects_df['start_month'].tolist() + projects_df['end_month'].tolist())))
    min_month = projects_df['start_month'].min()
    max_month = projects_df['end_month'].max()
    planning_horizon = list(range(min_month, max_month + 1))

    return projects_df, resources_df, planning_horizon

# --- 2. Monthly Resource Allocation Algorithm (using PuLP) ---
def allocate_resources_for_month(month, resources_df, active_projects_df):
    """
    Allocates resources to active projects for a given month using linear programming.
    Tries to maximize resource utilization.
    """
    if active_projects_df.empty:
        print(f"Month {month}: No active projects. No allocations made.")
        # Return a dictionary indicating zero allocation for all resources
        allocations = {res_id: {} for res_id in resources_df['resource_id']}
        resource_utilization = {res_id: 0.0 for res_id in resources_df['resource_id']}
        return allocations, resource_utilization

    # Create the LP problem
    prob = LpProblem(f"Resource_Allocation_Month_{month}", LpMaximize)

    # Decision Variables: allocation_vars[resource_id][project_id]
    allocation_vars = {}
    for _, resource in resources_df.iterrows():
        res_id = resource['resource_id']
        allocation_vars[res_id] = LpVariable.dicts(
            f"Alloc_{res_id}",
            active_projects_df['project_id'],
            lowBound=0,
            upBound=1,
            cat='Continuous'
        )

    # Objective Function: Maximize total allocation (ensuring resources have work)
    # We want to make sure each resource is utilized, so we maximize the sum of their allocations.
    prob += lpSum(allocation_vars[res_id][proj_id]
                  for res_id in resources_df['resource_id']
                  for proj_id in active_projects_df['project_id']), "Maximize_Total_Allocation"

    # Constraints:
    # 1. Each resource's total allocation <= 1
    for _, resource in resources_df.iterrows():
        res_id = resource['resource_id']
        prob += lpSum(allocation_vars[res_id][proj_id] for proj_id in active_projects_df['project_id']) <= 1, \
                f"Resource_{res_id}_Capacity"

    # (Implicit constraint) Allocation only to active projects is handled by how allocation_vars are defined.

    # Solve the problem
    # You might need to specify the path to a solver if PuLP doesn't find one.
    # Example: solver = PULP_CBC_CMD(msg=False, path='path/to/cbc')
    # prob.solve(solver)
    try:
        prob.solve(PULP_CBC_CMD(msg=False)) # msg=False suppresses solver messages
    except Exception as e:
        print(f"Error during optimization for month {month}: {e}")
        print("Ensure a solver like CBC is installed and accessible, or try 'prob.solve()' to use the default.")
        # Fallback: no allocation if solver fails
        allocations = {res_id: {proj_id: 0.0 for proj_id in active_projects_df['project_id']} for res_id in resources_df['resource_id']}
        resource_utilization = {res_id: 0.0 for res_id in resources_df['resource_id']}
        return allocations, resource_utilization


    allocations_results = {}
    resource_utilization = {res_id: 0.0 for res_id in resources_df['resource_id']}

    if LpStatus[prob.status] == 'Optimal':
        print(f"\n--- Month {month}: Optimal Allocation Found ---")
        for _, resource in resources_df.iterrows():
            res_id = resource['resource_id']
            allocations_results[res_id] = {}
            total_alloc_for_resource = 0
            for _, project in active_projects_df.iterrows():
                proj_id = project['project_id']
                alloc_value = allocation_vars[res_id][proj_id].varValue
                if alloc_value > 1e-5: # Consider non-zero allocations
                    allocations_results[res_id][proj_id] = round(alloc_value, 2)
                    total_alloc_for_resource += alloc_value
            resource_utilization[res_id] = round(total_alloc_for_resource, 2)
    else:
        print(f"Month {month}: No optimal solution found or problem infeasible. Status: {LpStatus[prob.status]}")
        # Default to zero allocation if not optimal
        for res_id in resources_df['resource_id']:
            allocations_results[res_id] = {proj_id: 0.0 for proj_id in active_projects_df['project_id']}
            resource_utilization[res_id] = 0.0

    return allocations_results, resource_utilization

# --- 3. Cost Calculation ---
def calculate_costs(monthly_allocations, resources_df, projects_df):
    """Calculates actual resource costs for projects and compares with budget."""
    resource_map = resources_df.set_index('resource_id')['monthly_cost'].to_dict()
    project_budgets = projects_df.set_index('project_id')['monthly_budget'].to_dict()
    project_actual_costs = {month: {pid: 0 for pid in projects_df['project_id']} for month in monthly_allocations.keys()}
    resource_actual_costs_total = {res_id: 0 for res_id in resources_df['resource_id']}
    project_total_actual_costs = {pid: 0 for pid in projects_df['project_id']}

    for month, allocations_in_month in monthly_allocations.items():
        for resource_id, project_allocs in allocations_in_month.items():
            resource_cost = resource_map.get(resource_id, 0)
            for project_id, allocation_rate in project_allocs.items():
                cost_for_project = resource_cost * allocation_rate
                project_actual_costs[month][project_id] += cost_for_project
                resource_actual_costs_total[resource_id] += cost_for_project # For entire duration
                project_total_actual_costs[project_id] += cost_for_project # For entire duration


    print("\n--- Cost Analysis (Monthly) ---")
    for month, project_costs_in_month in project_actual_costs.items():
        print(f"Month {month}:")
        for project_id, actual_cost in project_costs_in_month.items():
            # Check if project is active to compare budget
            project_info = projects_df[projects_df['project_id'] == project_id].iloc[0]
            if project_info['start_month'] <= month <= project_info['end_month']:
                budget = project_budgets.get(project_id, 0)
                print(f"  Project {project_id}: Actual Cost: ${actual_cost:,.2f}, Budget: ${budget:,.2f}, Variance: ${actual_cost - budget:,.2f}")
            elif actual_cost > 0: # Cost incurred for an inactive project (should not happen with current logic)
                 print(f"  Project {project_id}: Actual Cost: ${actual_cost:,.2f} (Project Inactive this month but has costs!)")


    return project_actual_costs, resource_actual_costs_total, project_total_actual_costs

# --- 4. Recommendation Engine ---
def generate_recommendations(monthly_utilization, project_actual_costs, projects_df, resources_df, planning_horizon):
    """Generates recommendations based on utilization and cost analysis."""
    recommendations = []
    num_months = len(planning_horizon)

    # Resource Utilization Analysis
    avg_resource_utilization = {res_id: 0.0 for res_id in resources_df['resource_id']}
    for month_util in monthly_utilization.values():
        for res_id, util_rate in month_util.items():
            avg_resource_utilization[res_id] += util_rate
    for res_id in avg_resource_utilization:
        avg_resource_utilization[res_id] /= num_months if num_months > 0 else 1

    print("\n--- Average Resource Utilization Over Planning Horizon ---")
    for res_id, avg_util in avg_resource_utilization.items():
        res_name = resources_df[resources_df['resource_id'] == res_id]['resource_name'].iloc[0]
        print(f"Resource {res_name} ({res_id}): Average Utilization = {avg_util:.2%}")
        if avg_util < 0.6: # Threshold for under-utilization
            recommendations.append(
                f"LOW UTILIZATION: Resource {res_name} ({res_id}) has an average utilization of {avg_util:.2%}. "
                f"Consider if this resource is needed long-term or if skills can be used on more projects."
            )
        elif avg_util < 0.1 and num_months > 2 : # Consistently very low
             recommendations.append(
                f"CONSIDER LETTING GO: Resource {res_name} ({res_id}) has extremely low average utilization ({avg_util:.2%}). "
                f"Evaluate if this resource is still required."
            )


    # Project Cost Analysis (Overall)
    print("\n--- Overall Project Cost vs. Budget ---")
    for _, project in projects_df.iterrows():
        proj_id = project['project_id']
        total_budget = project['annual_cost'] # Using annual_cost as total budget for simplicity
        total_actual_project_cost = sum(project_actual_costs[month].get(proj_id, 0) for month in planning_horizon)

        print(f"Project {proj_id} ({project['project_name']}): Total Actual Cost: ${total_actual_project_cost:,.2f}, Total Budget: ${total_budget:,.2f}")
        if total_actual_project_cost > total_budget * 1.1: # 10% over budget
            recommendations.append(
                f"PROJECT OVER BUDGET: Project {proj_id} ({project['project_name']}) is significantly over budget. "
                f"Actual: ${total_actual_project_cost:,.2f}, Budget: ${total_budget:,.2f}. Review scope or funding."
            )
        elif total_actual_project_cost < total_budget * 0.8 and total_actual_project_cost > 0: # Significantly under
             recommendations.append(
                f"PROJECT UNDER BUDGET: Project {proj_id} ({project['project_name']}) is significantly under budget. "
                f"Actual: ${total_actual_project_cost:,.2f}, Budget: ${total_budget:,.2f}. Investigate if project is on track or if funds can be reallocated."
            )


    # Check if more resources might be needed (heuristic)
    # If all resources are consistently near full utilization AND projects are still running
    fully_utilized_months = 0
    active_project_months = 0
    for month in planning_horizon:
        all_res_fully_utilized_this_month = True
        if not monthly_utilization.get(month): # Month might have no active projects
            continue

        # Check if there are active projects in this month
        if any(p['start_month'] <= month <= p['end_month'] for _, p in projects_df.iterrows()):
            active_project_months +=1
            for res_id in resources_df['resource_id']:
                if monthly_utilization[month].get(res_id, 0) < 0.95: # Threshold for "fully" utilized
                    all_res_fully_utilized_this_month = False
                    break
            if all_res_fully_utilized_this_month:
                fully_utilized_months += 1

    if active_project_months > 0 and (fully_utilized_months / active_project_months) > 0.75: # If resources are >95% busy for >75% of active project months
        recommendations.append(
            "POTENTIAL NEED FOR MORE RESOURCES: Resources are consistently highly utilized. "
            "If project demand is expected to continue or grow, consider hiring additional resources."
        )


    print("\n--- Recommendations ---")
    if recommendations:
        for i, rec in enumerate(recommendations):
            print(f"{i+1}. {rec}")
    else:
        print("No specific recommendations at this time based on current thresholds.")

    return recommendations

# --- Main Execution ---
if __name__ == "__main__":
    print("Starting Resource Allocation Process...")

    resources_df, projects_df_orig = load_data()

    if resources_df is not None and projects_df_orig is not None:
        projects_df, resources_df, planning_horizon = preprocess_data(projects_df_orig.copy(), resources_df.copy())

        if not planning_horizon:
            print("No valid planning horizon determined. Exiting.")
        else:
            print(f"Planning Horizon: Months {min(planning_horizon)} to {max(planning_horizon)}")

            all_monthly_allocations = {}
            all_monthly_utilization = {}

            for month in planning_horizon:
                # Get projects active in the current month
                active_projects = projects_df[
                    (projects_df['start_month'] <= month) & (projects_df['end_month'] >= month)
                ]
                allocations, utilization = allocate_resources_for_month(month, resources_df, active_projects)
                all_monthly_allocations[month] = allocations
                all_monthly_utilization[month] = utilization

                # Print detailed allocations for the month
                if LpStatus[LpProblem(f"Resource_Allocation_Month_{month}").status] == 'Optimal' or not active_projects.empty : # check if solver ran
                    for res_id, projs in allocations.items():
                        res_name = resources_df[resources_df['resource_id'] == res_id]['resource_name'].iloc[0]
                        if projs:
                             print(f"  Resource {res_name} ({res_id}) Utilization: {utilization.get(res_id, 0.0):.2f}")
                             for proj_id, rate in projs.items():
                                 print(f"    -> Project {proj_id}: {rate:.2f}")
                        elif active_projects.empty : # No active projects, so no work
                            pass # Already handled by allocate_resources_for_month
                        else: # Active projects, but this resource got no allocation (should be rare with current objective)
                             print(f"  Resource {res_name} ({res_id}) Utilization: {utilization.get(res_id, 0.0):.2f} (No specific project allocations this month, check overall demand)")


            project_monthly_actual_costs, _, _ = calculate_costs(all_monthly_allocations, resources_df, projects_df)
            generate_recommendations(all_monthly_utilization, project_monthly_actual_costs, projects_df, resources_df, planning_horizon)

    print("\nResource Allocation Process Finished.")


resource_id,resource_name,monthly_cost
R1,Developer A,6000
R2,Developer B,6500
R3,QA Engineer A,5000
R4,Project Manager A,7000
R5,UX Designer A,5800
R6,Developer C,6200
R7,Intern D,3000

project_id,project_name,annual_cost,start_month,end_month
P1,Alpha Platform,100000,1,12
P2,Beta Feature Dev,60000,1,6
P3,Gamma Mobile App,75000,4,10
P4,Delta Integration,40000,7,12
P5,Epsilon Support,20000,3,9



