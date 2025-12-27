"""
Add Patient Page - Streamlit UI

Add new patients to the Healthcare Digital database.
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from database.astra_helper import get_db_helper

# Page configuration
st.set_page_config(
    page_title="Add Patient - Healthcare Digital",
    page_icon="👤",
    layout="wide"
)

# Initialize database
@st.cache_resource
def get_db():
    return get_db_helper()

db = get_db()

# Custom CSS
st.markdown("""
    <style>
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Page header
st.markdown("# 👤 Add New Patient")
st.markdown("### Register new patients in the Healthcare Digital system")

# Create tabs
tab1, tab2 = st.tabs(["➕ Add Patient", "📋 Sample Patients"])

with tab1:
    st.markdown("## Patient Registration Form")
    
    with st.form("add_patient_form"):
        st.markdown("### Basic Information")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Patient Name *",
                placeholder="John Doe",
                help="Full name of the patient"
            )
            age = st.number_input(
                "Age *",
                min_value=0,
                max_value=120,
                value=65,
                help="Patient's age"
            )
            room_number = st.text_input(
                "Room Number *",
                placeholder="301",
                help="Hospital room number"
            )
        
        with col2:
            diet_type = st.selectbox(
                "Diet Type",
                ["regular", "diabetic", "renal", "cardiac", "vegetarian", "vegan", "gluten-free"],
                help="Primary diet classification"
            )
            fluid_restriction = st.checkbox(
                "Fluid Restriction",
                help="Check if patient has fluid intake restrictions"
            )
            texture_modification = st.selectbox(
                "Texture Modification",
                ["None", "soft", "minced", "pureed"],
                help="Food texture requirements"
            )
        
        st.markdown("---")
        st.markdown("### Dietary Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dietary_restrictions_input = st.text_area(
                "Dietary Restrictions",
                placeholder="low-sodium\nlow-sugar\nlow-fat\nhigh-fiber",
                help="Enter one restriction per line"
            )
            
            allergies_input = st.text_area(
                "Food Allergies",
                placeholder="peanuts\nshellfish\ndairy\neggs",
                help="Enter one allergy per line"
            )
        
        with col2:
            medical_conditions_input = st.text_area(
                "Medical Conditions",
                placeholder="diabetes\nhypertension\nkidney disease\nheart disease",
                help="Enter one condition per line"
            )
            
            preferences_input = st.text_area(
                "Food Preferences (Optional)",
                placeholder="likes: chicken, rice, vegetables\ndislikes: fish, spicy food",
                help="Patient food likes and dislikes"
            )
        
        st.markdown("---")
        
        # Submit button
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            submitted = st.form_submit_button("➕ Add Patient", use_container_width=True, type="primary")
        
        if submitted:
            # Validate required fields
            if not name or not room_number:
                st.error("❌ Please fill in all required fields (marked with *)")
            else:
                # Parse inputs
                dietary_restrictions = [r.strip() for r in dietary_restrictions_input.split('\n') if r.strip()]
                allergies = [a.strip() for a in allergies_input.split('\n') if a.strip()]
                medical_conditions = [c.strip() for c in medical_conditions_input.split('\n') if c.strip()]
                
                # Parse preferences
                preferences = {}
                if preferences_input:
                    for line in preferences_input.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            preferences[key.strip()] = value.strip()
                
                # Build patient data
                patient_data = {
                    "name": name,
                    "age": age,
                    "room_number": room_number,
                    "dietary_restrictions": dietary_restrictions,
                    "allergies": allergies,
                    "medical_conditions": medical_conditions,
                    "preferences": preferences,
                    "diet_type": diet_type,
                    "fluid_restriction": fluid_restriction,
                    "texture_modification": None if texture_modification == "None" else texture_modification,
                    "admission_date": datetime.now().isoformat(),
                    "status": "active"
                }
                
                try:
                    # Create patient
                    patient_id = db.create_patient(patient_data)
                    
                    # Success message
                    st.markdown(f"""
                        <div class="success-box">
                            <h3>✅ Patient Added Successfully!</h3>
                            <p><strong>Patient ID:</strong> {patient_id}</p>
                            <p><strong>Name:</strong> {name}</p>
                            <p><strong>Room:</strong> {room_number}</p>
                            <p><strong>Diet Type:</strong> {diet_type.title()}</p>
                            <p><strong>Status:</strong> Active</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.balloons()
                    
                    # Show summary
                    with st.expander("📋 Patient Details", expanded=False):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Basic Info:**")
                            st.write(f"- Age: {age}")
                            st.write(f"- Room: {room_number}")
                            st.write(f"- Diet: {diet_type}")
                            if dietary_restrictions:
                                st.write(f"**Dietary Restrictions:**")
                                for r in dietary_restrictions:
                                    st.write(f"- {r}")
                        
                        with col2:
                            if allergies:
                                st.write("**Allergies:**")
                                for a in allergies:
                                    st.write(f"- {a}")
                            if medical_conditions:
                                st.write("**Medical Conditions:**")
                                for c in medical_conditions:
                                    st.write(f"- {c}")
                            if fluid_restriction:
                                st.write("**⚠️ Fluid Restriction: Yes**")
                
                except Exception as e:
                    st.error(f"❌ Error adding patient: {str(e)}")

with tab2:
    st.markdown("## Add Sample Patients for Testing")
    
    st.markdown("""
        <div class="info-box">
            <strong>ℹ️ Sample Patients</strong><br>
            Click the button below to add 5 sample patients with various dietary needs and conditions.
            This is useful for testing the meal ordering and production systems.
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("➕ Add 5 Sample Patients", use_container_width=True, type="primary"):
        sample_patients = [
            {
                "name": "John Smith",
                "age": 65,
                "room_number": "301",
                "dietary_restrictions": ["low-sodium", "low-sugar"],
                "allergies": [],
                "medical_conditions": ["diabetes", "hypertension"],
                "preferences": {"likes": "chicken, vegetables", "dislikes": "fish"},
                "diet_type": "diabetic",
                "fluid_restriction": True,
                "texture_modification": None,
                "admission_date": datetime.now().isoformat(),
                "status": "active"
            },
            {
                "name": "Mary Johnson",
                "age": 72,
                "room_number": "305",
                "dietary_restrictions": ["renal-diet"],
                "allergies": ["shellfish"],
                "medical_conditions": ["kidney disease"],
                "preferences": {"likes": "mild flavors", "dislikes": "spicy"},
                "diet_type": "renal",
                "fluid_restriction": True,
                "texture_modification": None,
                "admission_date": datetime.now().isoformat(),
                "status": "active"
            },
            {
                "name": "Robert Williams",
                "age": 58,
                "room_number": "310",
                "dietary_restrictions": ["low-fat", "low-cholesterol"],
                "allergies": [],
                "medical_conditions": ["heart disease"],
                "preferences": {"likes": "grilled food", "dislikes": "fried"},
                "diet_type": "cardiac",
                "fluid_restriction": False,
                "texture_modification": None,
                "admission_date": datetime.now().isoformat(),
                "status": "active"
            },
            {
                "name": "Patricia Brown",
                "age": 45,
                "room_number": "315",
                "dietary_restrictions": [],
                "allergies": ["dairy", "eggs"],
                "medical_conditions": [],
                "preferences": {"likes": "fruits, vegetables", "dislikes": "meat"},
                "diet_type": "vegan",
                "fluid_restriction": False,
                "texture_modification": None,
                "admission_date": datetime.now().isoformat(),
                "status": "active"
            },
            {
                "name": "Michael Davis",
                "age": 80,
                "room_number": "320",
                "dietary_restrictions": ["soft-diet"],
                "allergies": [],
                "medical_conditions": ["dysphagia"],
                "preferences": {"likes": "soft foods", "dislikes": "hard foods"},
                "diet_type": "regular",
                "fluid_restriction": False,
                "texture_modification": "soft",
                "admission_date": datetime.now().isoformat(),
                "status": "active"
            }
        ]
        
        success_count = 0
        with st.spinner("Adding sample patients..."):
            for patient in sample_patients:
                try:
                    patient_id = db.create_patient(patient)
                    success_count += 1
                except Exception as e:
                    st.warning(f"⚠️ Could not add {patient['name']}: {str(e)}")
        
        if success_count == len(sample_patients):
            st.success(f"✅ Successfully added all {success_count} sample patients!")
            st.balloons()
        else:
            st.info(f"ℹ️ Added {success_count} out of {len(sample_patients)} sample patients")
        
        # Show added patients
        with st.expander("📋 View Added Patients"):
            for patient in sample_patients:
                st.markdown(f"""
                    **{patient['name']}** - Room {patient['room_number']}
                    - Age: {patient['age']}, Diet: {patient['diet_type']}
                    - Allergies: {', '.join(patient['allergies']) if patient['allergies'] else 'None'}
                    - Medical: {', '.join(patient['medical_conditions']) if patient['medical_conditions'] else 'None'}
                """)

# Sidebar info
with st.sidebar:
    st.markdown("---")
    st.markdown("### 👤 Add Patient")
    st.info("""
    **Quick Guide:**
    
    1. Fill in patient information
    2. Add dietary restrictions/allergies
    3. Specify diet type and preferences
    4. Click 'Add Patient'
    
    **Or use Sample Patients** tab to quickly add test data.
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Current Status")
    try:
        # Get patient count
        patients = db.get_all_patients()
        st.metric("Total Patients", len(patients))
    except:
        st.caption("Unable to fetch patient count")
