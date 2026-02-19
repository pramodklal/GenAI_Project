"""
Validators for Research Laboratory data
"""

import re
from datetime import datetime
from typing import Dict, List, Optional

def validate_compound_formula(formula: str) -> tuple[bool, str]:
    """Validate chemical compound formula"""
    if not formula:
        return False, "Formula cannot be empty"
    
    # Basic chemical formula validation
    pattern = r'^([A-Z][a-z]?\d*)+$'
    if not re.match(pattern, formula):
        return False, "Invalid chemical formula format"
    
    return True, "Valid"

def validate_trial_id(trial_id: str) -> tuple[bool, str]:
    """Validate clinical trial ID format"""
    if not trial_id:
        return False, "Trial ID cannot be empty"
    
    # Example: CT-2024-001
    pattern = r'^CT-\d{4}-\d{3,}$'
    if not re.match(pattern, trial_id):
        return False, "Invalid trial ID format. Use: CT-YYYY-NNN"
    
    return True, "Valid"

def validate_project_data(data: Dict) -> tuple[bool, List[str]]:
    """Validate research project data"""
    errors = []
    
    required_fields = ['project_name', 'principal_investigator', 'start_date', 'status']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate status
    valid_statuses = ['Planning', 'Active', 'On Hold', 'Completed', 'Cancelled']
    if 'status' in data and data['status'] not in valid_statuses:
        errors.append(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    # Validate date format
    if 'start_date' in data:
        try:
            datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        except:
            errors.append("Invalid start_date format. Use ISO format: YYYY-MM-DD")
    
    return len(errors) == 0, errors

def validate_experiment_data(data: Dict) -> tuple[bool, List[str]]:
    """Validate lab experiment data"""
    errors = []
    
    required_fields = ['experiment_name', 'experiment_type', 'date_conducted']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate experiment type
    valid_types = ['In Vitro', 'In Vivo', 'Analytical', 'Synthesis', 'Screening', 'Other']
    if 'experiment_type' in data and data['experiment_type'] not in valid_types:
        errors.append(f"Invalid experiment_type. Must be one of: {', '.join(valid_types)}")
    
    return len(errors) == 0, errors

def validate_candidate_data(data: Dict) -> tuple[bool, List[str]]:
    """Validate drug candidate data"""
    errors = []
    
    required_fields = ['compound_name', 'molecular_formula', 'development_stage']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate development stage
    valid_stages = ['Discovery', 'Preclinical', 'Phase I', 'Phase II', 'Phase III', 'Approval']
    if 'development_stage' in data and data['development_stage'] not in valid_stages:
        errors.append(f"Invalid development_stage. Must be one of: {', '.join(valid_stages)}")
    
    # Validate molecular formula if present
    if 'molecular_formula' in data:
        is_valid, msg = validate_compound_formula(data['molecular_formula'])
        if not is_valid:
            errors.append(f"Molecular formula error: {msg}")
    
    return len(errors) == 0, errors

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    text = text.strip()
    text = re.sub(r'[<>\"\'%;()&+]', '', text)
    
    return text

def validate_date_range(start_date: str, end_date: str) -> tuple[bool, str]:
    """Validate that date range is logical"""
    try:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if end < start:
            return False, "End date cannot be before start date"
        
        return True, "Valid"
        
    except Exception as e:
        return False, f"Invalid date format: {str(e)}"
