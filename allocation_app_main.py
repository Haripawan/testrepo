import pandas as pd
import numpy as np
from datetime import datetime
import calendar

class ResourceAllocationSystem:
    def __init__(self):
        self.employees = {}
        self.projects = {}
        self.allocations = []
        self.months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        self.lead_employees = set()
        self.change_history = []  # Track changes for analysis

    def add_employee(self, employee_id, name, monthly_cost, is_lead=False):
        """Add an employee to the system"""
        self.employees[employee_id] = {
            'name': name,
            'monthly_cost': monthly_cost,
            'is_lead': is_lead
        }
        
        if is_lead:
            self.lead_employees.add(employee_id)
        
        return self

    def add_project(self, project_id, name, start_date, end_date, budget):
        """Add a project with start and end dates, and budget"""
        # Convert string dates to datetime objects
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
        self.projects[project_id] = {
            'name': name,
            'start_date': start_date,
            'end_date': end_date,
            'budget': budget,
            'start_month': start_date.month - 1,  # 0-indexed (Jan=0)
            'end_month': end_date.month - 1,      # 0-indexed (Jan=0)
            'duration_months': self._calculate_duration_months(start_date, end_date)
        }
        
        return self
    
    def _calculate_duration_months(self, start_date, end_date):
        """Calculate the duration in months between two dates"""
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
        return months
    
    def allocate_resources(self, haircut_percentage=5, budget_tolerance_percentage=3):
        """
        Allocate resources to projects based on the constraints:
        1. Each employee must be fully allocated (12 months in total across all projects)
        2. Lead employees participate in most projects
        3. Project budget must be within tolerance
        4. Allocations follow project start and end dates
        """
        # Apply haircut to project budgets
        for project_id in self.projects:
            self.projects[project_id]['adjusted_budget'] = self.projects[project_id]['budget'] * (1 - haircut_percentage/100)
        
        # Initialize employee availability matrix (12 months per employee)
        employee_availability = {emp_id: [1.0] * 12 for emp_id in self.employees}
        
        # Sort projects by duration (shortest first)
        sorted_projects = sorted(
            self.projects.items(), 
            key=lambda x: x[1]['duration_months']
        )
        
        # First pass: Allocate lead employees to projects
        for project_id, project in sorted_projects:
            project_start = project['start_month']
            project_end = project['end_month']
            months_range = range(project_start, project_end + 1)
            
            # Allocate lead employees first (with smaller allocations)
            for emp_id in self.lead_employees:
                # Default allocation per month for lead employees
                lead_allocation_per_month = 0.2  # 20% allocation for leads
                
                for month_idx in months_range:
                    # Check if employee has availability in this month
                    if employee_availability[emp_id][month_idx] >= lead_allocation_per_month:
                        # Create allocation
                        self.allocations.append({
                            'employee_id': emp_id,
                            'project_id': project_id,
                            'month_idx': month_idx,
                            'allocation': lead_allocation_per_month,
                            'cost': lead_allocation_per_month * self.employees[emp_id]['monthly_cost']
                        })
                        
                        # Update employee availability
                        employee_availability[emp_id][month_idx] -= lead_allocation_per_month
        
        # Second pass: Allocate remaining employees to projects
        for project_id, project in sorted_projects:
            project_start = project['start_month']
            project_end = project['end_month']
            months_range = range(project_start, project_end + 1)
            
            # Calculate project's allocated cost so far
            project_cost = sum(
                alloc['cost'] for alloc in self.allocations 
                if alloc['project_id'] == project_id
            )
            
            # Calculate how much more budget we can allocate
            remaining_budget = project['adjusted_budget'] - project_cost
            
            # Skip if project is already at or over budget
            if remaining_budget <= 0:
                continue
                
            # Allocate regular employees
            for emp_id, employee in self.employees.items():
                if emp_id in self.lead_employees:
                    continue  # Skip leads (already allocated)
                    
                for month_idx in months_range:
                    # Check if employee has availability in this month
                    if employee_availability[emp_id][month_idx] > 0:
                        # How much can we allocate without exceeding budget
                        max_allocation = min(
                            employee_availability[emp_id][month_idx],
                            remaining_budget / employee['monthly_cost']
                        )
                        
                        if max_allocation > 0:
                            # Create allocation
                            self.allocations.append({
                                'employee_id': emp_id,
                                'project_id': project_id,
                                'month_idx': month_idx,
                                'allocation': max_allocation,
                                'cost': max_allocation * employee['monthly_cost']
                            })
                            
                            # Update employee availability
                            employee_availability[emp_id][month_idx] -= max_allocation
                            
                            # Update remaining budget
                            remaining_budget -= max_allocation * employee['monthly_cost']
                            
                            # Break if budget is exhausted
                            if remaining_budget <= 0:
                                break
        
        # Third pass: Ensure all employees are fully allocated
        self._ensure_full_allocation(employee_availability)
        
        # Validate budget constraints
        self._validate_budget_constraints(budget_tolerance_percentage)
        
        return self
    
    def _ensure_full_allocation(self, employee_availability):
        """Make sure all employees are fully allocated (100% for 12 months)"""
        # Find employees with remaining availability
        for emp_id, availability in employee_availability.items():
            for month_idx, avail in enumerate(availability):
                if avail > 0:
                    # Find any project active in this month
                    for project_id, project in self.projects.items():
                        if project['start_month'] <= month_idx <= project['end_month']:
                            # Create allocation with remaining availability
                            self.allocations.append({
                                'employee_id': emp_id,
                                'project_id': project_id,
                                'month_idx': month_idx,
                                'allocation': avail,
                                'cost': avail * self.employees[emp_id]['monthly_cost']
                            })
                            
                            # Update availability
                            employee_availability[emp_id][month_idx] = 0
                            break
    
    def _validate_budget_constraints(self, budget_tolerance_percentage):
        """Validate that project allocations are within budget tolerance"""
        for project_id, project in self.projects.items():
            # Calculate total allocated cost for this project
            allocated_cost = sum(
                alloc['cost'] for alloc in self.allocations 
                if alloc['project_id'] == project_id
            )
            
            # Check if allocation is within tolerance
            budget = project['adjusted_budget']
            min_budget = budget * (1 - budget_tolerance_percentage/100)
            max_budget = budget * (1 + budget_tolerance_percentage/100)
            
            if allocated_cost < min_budget or allocated_cost > max_budget:
                print(f"Warning: Project {project_id} allocation (${allocated_cost:.2f}) is outside "
                      f"budget tolerance (${min_budget:.2f} - ${max_budget:.2f})")
    
    def generate_allocation_report(self):
        """Generate a consolidated report of all allocations"""
        # Create a dictionary to store consolidated allocations
        consolidated = {}
        
        # Consolidate allocations by employee and project
        for alloc in self.allocations:
            emp_id = alloc['employee_id']
            project_id = alloc['project_id']
            month_idx = alloc['month_idx']
            
            key = (emp_id, project_id)
            if key not in consolidated:
                consolidated[key] = {
                    'employee_id': emp_id,
                    'employee_name': self.employees[emp_id]['name'],
                    'project_id': project_id,
                    'project_name': self.projects[project_id]['name'],
                    'Jan': 0, 'Feb': 0, 'Mar': 0, 'Apr': 0, 'May': 0, 'Jun': 0,
                    'Jul': 0, 'Aug': 0, 'Sep': 0, 'Oct': 0, 'Nov': 0, 'Dec': 0,
                    'total_cost': 0
                }
            
            month_name = self.months[month_idx]
            consolidated[key][month_name] = alloc['allocation']
            consolidated[key]['total_cost'] += alloc['cost']
        
        # Convert to DataFrame
        report_df = pd.DataFrame(consolidated.values())
        
        # Reorder columns
        columns = ['employee_id', 'employee_name', 'project_id', 'project_name']
        columns.extend(self.months)
        columns.append('total_cost')
        
        # Return the report
        return report_df[columns]
    
    def export_to_excel(self, filename='resource_allocation.xlsx'):
        """Export allocation report to Excel"""
        report = self.generate_allocation_report()
        report.to_excel(filename, index=False)
        print(f"Report exported to {filename}")
        return self

# Example usage
if __name__ == "__main__":
    # Initialize the system
    allocation_system = ResourceAllocationSystem()
    
    # Add employees
    allocation_system.add_employee('E001', 'John Doe', 10000, is_lead=True)
    allocation_system.add_employee('E002', 'Jane Smith', 8000)
    allocation_system.add_employee('E003', 'Bob Johnson', 9000)
    allocation_system.add_employee('E004', 'Alice Brown', 8500, is_lead=True)
    
    # Add projects
    allocation_system.add_project('P001', 'Website Redesign', '2025-01-01', '2025-06-30', 250000)
    allocation_system.add_project('P002', 'Mobile App Development', '2025-03-01', '2025-12-31', 400000)
    allocation_system.add_project('P003', 'Data Migration', '2025-05-01', '2025-08-31', 150000)
    
    # Allocate resources
    allocation_system.allocate_resources(haircut_percentage=5, budget_tolerance_percentage=3)
    
    # Generate and display report
    report = allocation_system.generate_allocation_report()
    print(report)
    
    # Export to Excel
    allocation_system.export_to_excel()