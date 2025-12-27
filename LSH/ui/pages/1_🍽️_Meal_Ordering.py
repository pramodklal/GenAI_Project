"""
Meal Ordering Page - Streamlit UI

Patient meal ordering with AI-powered validation and recommendations.
"""

import streamlit as st
import asyncio
from datetime import datetime, timedelta
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from database.astra_helper import get_db_helper
from agents import NutritionValidationAgent

# Initialize services
@st.cache_resource
@st.cache_resource
def get_services():
    db = get_db_helper()
    nutrition_agent = NutritionValidationAgent()
    return db, nutrition_agent

db, nutrition_agent = get_services()

# Page header
st.markdown("# 🍽️ Patient Meal Ordering")
st.markdown("### AI-Powered Meal Validation & Ordering System")

# Tabs
tab1, tab2, tab3 = st.tabs(["📝 New Order", "📋 Order History", "💡 Recommendations"])

with tab1:
    st.markdown("## Create New Meal Order")
    
    # Patient information
    # Get database helper
    db, nutrition_agent = get_services()
    
    # Load real patients from database
    with st.spinner("Loading patients..."):
        patients = db.get_all_patients(limit=100)
    
    if not patients:
        st.error("No patients found in database. Please add patients first.")
        st.stop()
    
    # Create patient selection dropdown
    patient_options = {f"{p['name']} - Room {p['room_number']}": p['patient_id'] for p in patients}
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_patient_display = st.selectbox(
            "Select Patient",
            options=list(patient_options.keys()),
            help="Select the patient to create an order for"
        )
        patient_id = patient_options[selected_patient_display]
    
    with col2:
        meal_time = st.selectbox(
            "Meal Time",
            ["Breakfast", "Lunch", "Dinner", "Snack"],
            index=1
        )
    
    # Load patient details from database
    patient = db.get_patient(patient_id)
    dietary_profile = db.get_patient_dietary_profile(patient_id)
    
    # Display patient information
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            allergies = patient.get('allergies', [])
            allergy_text = ", ".join(allergies) if allergies else "None"
            st.warning(f"🚫 **Allergies:** {allergy_text}")
        
        with col2:
            restrictions = patient.get('dietary_restrictions', [])
            restrictions_text = ", ".join(restrictions) if restrictions else "None"
            st.info(f"⚕️ **Restrictions:** {restrictions_text}")
        
        with col3:
            if dietary_profile:
                dietary_type = dietary_profile.get('dietary_type', 'Standard')
                st.success(f"🥗 **Diet Type:** {dietary_type}")
    
    # Store restrictions in session state
    st.session_state["restrictions"] = {
        "allergies": allergies,
        "dietary_restrictions": restrictions,
        "dietary_type": dietary_profile.get('dietary_type', 'Standard') if dietary_profile else 'Standard'
    }
    
    # Scheduled delivery time
    col1, col2 = st.columns(2)
    with col1:
        delivery_date = st.date_input(
            "Delivery Date",
            value=datetime.now().date()
        )
    with col2:
        delivery_time = st.time_input(
            "Delivery Time",
            value=(datetime.now() + timedelta(hours=1)).time()
        )
    
    st.markdown("---")
    
    # Meal selection
    st.markdown("## Select Meal Items")
    
    # Load real menu items from database
    with st.spinner("Loading menu..."):
        categories = ["Entree", "Soup", "Salad", "Breakfast", "Dessert", "Beverage", "Side"]
        menu_by_category = {}
        for category in categories:
            items = db.get_menu_items_by_category(category, limit=20)
            if items:
                menu_by_category[category] = items
    
    # Initialize selected items in session state
    if "selected_meal_items" not in st.session_state:
        st.session_state.selected_meal_items = []
    
    # Display menu items by category
    for category, items in menu_by_category.items():
        with st.expander(f"📦 {category}", expanded=(category in ["Entree", "Breakfast"])):
            for item in items:
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"**{item['name']}**")
                    st.caption(item.get('description', 'No description'))
                
                with col2:
                    st.caption(f"🔥 {item['calories']} cal | 🥩 {item['protein_g']}g protein")
                    
                    # Show dietary tags
                    dietary_tags = item.get('dietary_tags', [])
                    if dietary_tags:
                        tags_display = " ".join([f"`{tag}`" for tag in dietary_tags[:3]])
                        st.markdown(tags_display)
                
                with col3:
                    item_id = item['item_id']
                    is_selected = item_id in st.session_state.selected_meal_items
                    
                    if st.button("➕" if not is_selected else "➖", 
                               key=f"select_{item_id}",
                               help="Add to order" if not is_selected else "Remove from order"):
                        if is_selected:
                            st.session_state.selected_meal_items.remove(item_id)
                        else:
                            st.session_state.selected_meal_items.append(item_id)
                        st.rerun()
    
    selected_items = st.session_state.selected_meal_items
    
    # Show selected items
    if selected_items:
        st.markdown("### 🛒 Selected Items")
        
        # Load full item details
        selected_item_details = []
        total_calories = 0
        total_protein = 0
        
        for item_id in selected_items:
            item = db.get_menu_item(item_id)
            if item:
                selected_item_details.append(item)
                total_calories += item.get('calories', 0)
                total_protein += item.get('protein_g', 0)
        
        # Display selected items
        cols = st.columns(min(len(selected_item_details), 4))
        for idx, item in enumerate(selected_item_details):
            with cols[idx % 4]:
                st.markdown(f"**{item['name']}**")
                st.caption(f"{item['calories']} cal")
        
        # Show totals
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Items", len(selected_items))
        with col2:
            st.metric("Total Calories", f"{total_calories} kcal")
        with col3:
            st.metric("Total Protein", f"{total_protein}g")
    
    st.markdown("---")
    
    # Validate and submit
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Validate Order", type="secondary", use_container_width=True, disabled=len(selected_items) == 0):
            with st.spinner("🤖 AI Agent validating meal selection..."):
                # Run validation with real database data
                async def validate():
                    return await nutrition_agent.process({
                        "patient_id": patient_id,
                        "meal_item_ids": selected_items,  # Use item IDs
                        "validation_type": "full"
                    })
                
                validation_result = asyncio.run(validate())
                st.session_state["validation_result"] = validation_result
                
                if validation_result.get("valid"):
                    st.markdown("""
                        <div class="success-box">
                            <h4>✅ Validation Passed!</h4>
                            <p>Meal selection meets all dietary and nutritional requirements.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Show nutrition summary
                    nutrition = validation_result.get("nutrition_summary", {})
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Calories", f"{nutrition.get('total_calories', 0)} kcal")
                    with col2:
                        st.metric("Protein", f"{nutrition.get('total_protein_g', 0)} g")
                    with col3:
                        st.metric("Carbs", f"{nutrition.get('total_carbohydrates_g', 0)} g")
                    with col4:
                        st.metric("Sodium", f"{nutrition.get('total_sodium_mg', 0)} mg")
                    
                    # Show warnings if any
                    warnings = validation_result.get("warnings", [])
                    if warnings:
                        st.markdown("**⚠️ Warnings:**")
                        for warning in warnings:
                            st.warning(f"• {warning.get('reason')}")
                            if warning.get('recommendation'):
                                st.info(f"  💡 {warning.get('recommendation')}")
                    
                else:
                    st.markdown("""
                        <div class="error-box">
                            <h4>❌ Validation Failed</h4>
                            <p>Meal selection has critical issues that must be resolved.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    issues = validation_result.get("issues", [])
                    for issue in issues:
                        st.error(f"🚫 {issue.get('reason')}")
                    
                    # Show recommendations
                    recommendations = validation_result.get("recommendations", [])
                    if recommendations:
                        st.markdown("### 💡 Alternative Recommendations")
                        for rec in recommendations:
                            with st.container():
                                st.markdown(f"**{rec['name']}**")
                                st.markdown(f"_{rec['description']}_")
                                st.markdown(f"Match Score: {rec['match_score'] * 100:.0f}%")
                                st.markdown(f"Reason: {rec['reason']}")
                                st.markdown("---")
    
    with col2:
        validation_result = st.session_state.get("validation_result", {})
        can_submit = validation_result.get("valid", False)
        
        if st.button("📤 Submit Order", type="primary", use_container_width=True, disabled=not can_submit):
            with st.spinner("Submitting order..."):
                # Submit order to database
                scheduled_time = datetime.combine(delivery_date, delivery_time).isoformat()
                
                try:
                    order_data = {
                        'patient_id': patient_id,
                        'meal_items': selected_items,
                        'meal_time': meal_time.lower(),
                        'meal_type': meal_time.lower(),
                        'order_date': delivery_date.isoformat(),
                        'delivery_time': delivery_time.strftime('%H:%M:%S'),
                        'scheduled_delivery_time': scheduled_time,
                        'status': 'pending',
                        'validated_by_ai': True,
                        'validation_notes': validation_result.get('summary', 'Order validated successfully'),
                        'total_calories': validation_result.get('nutritional_summary', {}).get('total_calories', 0),
                        'warnings': validation_result.get('warnings', []),
                        'patient_name': patient.get('name'),
                        'room_number': patient.get('room_number')
                    }
                    order_id = db.create_meal_order(order_data)
                    
                    if order_id:
                        st.markdown(f"""
                            <div class="success-box">
                                <h3>🎉 Order Submitted Successfully!</h3>
                                <p><strong>Order ID:</strong> {order_id}</p>
                                <p><strong>Patient:</strong> {patient['name']} ({patient_id})</p>
                                <p><strong>Room:</strong> {patient['room_number']}</p>
                                <p><strong>Scheduled:</strong> {scheduled_time}</p>
                                <p><strong>Status:</strong> Pending</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Clear selected items
                        st.session_state.selected_meal_items = []
                        st.session_state.validation_result = {}
                        
                        st.balloons()
                        st.success("Order has been sent to food production team!")
                    else:
                        st.error("❌ Failed to create order. Please try again.")
                
                except Exception as e:
                    st.error(f"❌ Error submitting order: {str(e)}")

with tab2:
    st.markdown("## Order History")
    
    # Use same patient selection
    history_patient_id = patient_id if 'patient_id' in locals() else "P001"
    
    col1, col2 = st.columns(2)
    with col1:
        # Optionally change patient
        all_patients = db.get_all_patients(limit=100)
        history_patient_options = {f"{p['name']} - Room {p['room_number']}": p['patient_id'] for p in all_patients}
        
        selected_history_patient = st.selectbox(
            "Select Patient",
            options=list(history_patient_options.keys()),
            key="history_patient_select"
        )
        history_patient_id = history_patient_options[selected_history_patient]
    
    with col2:
        status_filter = st.multiselect(
            "Filter by Status",
            ["pending", "preparing", "ready", "delivered", "cancelled"],
            default=["pending", "preparing", "ready", "delivered"]
        )
    
    # Load order history from database
    with st.spinner("Loading order history..."):
        orders = db.get_patient_orders(history_patient_id)
        
        # Filter by status
        if status_filter:
            orders = [o for o in orders if o.get('status') in status_filter]
    
    if orders:
        st.success(f"Found {len(orders)} orders for {selected_history_patient}")
        
        # Display statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Orders", len(orders))
        with col2:
            delivered = len([o for o in orders if o.get('status') == 'delivered'])
            st.metric("Delivered", delivered)
        with col3:
            pending = len([o for o in orders if o.get('status') in ['pending', 'preparing']])
            st.metric("Pending", pending)
        
        st.markdown("---")
        
        # Display orders
        for order in orders:
            status_emoji = {
                "pending": "⏳",
                "preparing": "👨‍🍳",
                "ready": "✅",
                "delivered": "🚚",
                "cancelled": "❌"
            }.get(order.get('status', 'pending'), "📦")
            
            with st.expander(
                f"{status_emoji} Order {order['order_id']} - {order.get('meal_time', 'N/A').title()} - {order.get('status', 'unknown').upper()}",
                expanded=False
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Order ID:** {order['order_id']}")
                    st.markdown(f"**Date:** {order.get('order_date', 'N/A')}")
                    st.markdown(f"**Meal Time:** {order.get('meal_time', 'N/A')}")
                
                with col2:
                    st.markdown(f"**Status:** {order.get('status', 'unknown').upper()}")
                    st.markdown(f"**Delivery Time:** {order.get('scheduled_delivery_time', 'N/A')}")
                    if order.get('delivered_time'):
                        st.markdown(f"**Delivered:** {order['delivered_time']}")
                
                # Show meal items
                meal_items = order.get('meal_items', [])
                if meal_items:
                    st.markdown("**Items:**")
                    for item_id in meal_items:
                        item = db.get_menu_item(item_id)
                        if item:
                            st.markdown(f"- {item['name']} ({item['calories']} cal)")
                        else:
                            st.markdown(f"- Item ID: {item_id}")
                
                # Show notes if any
                if order.get('special_instructions'):
                    st.markdown(f"**Special Instructions:** {order['special_instructions']}")
    else:
        st.info(f"No orders found for {selected_history_patient}")

with tab3:
    st.markdown("## 💡 Personalized Meal Recommendations")
    st.markdown("Get AI-powered meal recommendations based on patient preferences and dietary needs.")
    
    col1, col2 = st.columns(2)
    with col1:
        # Use patient selection
        rec_patients = db.get_all_patients(limit=100)
        rec_patient_options = {f"{p['name']} - Room {p['room_number']}": p['patient_id'] for p in rec_patients}
        
        selected_rec_patient = st.selectbox(
            "Select Patient",
            options=list(rec_patient_options.keys()),
            key="rec_patient_select"
        )
        rec_patient_id = rec_patient_options[selected_rec_patient]
    
    with col2:
        rec_meal_type = st.selectbox(
            "Meal Type",
            ["Breakfast", "Lunch", "Dinner", "Snack"],
            index=1,
            key="rec_meal_type"
        )
    
    if st.button("🤖 Generate Recommendations", use_container_width=True):
        with st.spinner("AI Agent generating personalized recommendations..."):
            # Get patient details
            rec_patient = db.get_patient(rec_patient_id)
            rec_dietary_profile = db.get_patient_dietary_profile(rec_patient_id)
            
            # Get patient allergies and restrictions
            patient_allergies = rec_patient.get('allergies', [])
            patient_restrictions = rec_patient.get('dietary_restrictions', [])
            
            # Show what recommendations are based on
            with st.expander("ℹ️ Recommendation Criteria", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Patient:** {rec_patient['name']}")
                    st.markdown(f"**Allergies:** {', '.join(patient_allergies) if patient_allergies else 'None'}")
                with col2:
                    dietary_type = rec_dietary_profile.get('dietary_type', 'Standard') if rec_dietary_profile else 'Standard'
                    st.markdown(f"**Diet Type:** {dietary_type}")
                    st.markdown(f"**Restrictions:** {', '.join(patient_restrictions) if patient_restrictions else 'None'}")
            
            st.markdown("---")
            
            # Get menu items that match dietary requirements
            category_map = {
                "Breakfast": "Breakfast",
                "Lunch": "Entree",
                "Dinner": "Entree",
                "Snack": "Dessert"
            }
            category = category_map.get(rec_meal_type, "Entree")
            
            menu_items = db.get_menu_items_by_category(category, limit=50)
            
            # Filter safe items (no allergens)
            safe_items = []
            for item in menu_items:
                item_allergens = item.get('allergens', [])
                # Check if any patient allergen is in item allergens
                has_allergen = any(allergy.lower() in [a.lower() for a in item_allergens] for allergy in patient_allergies)
                if not has_allergen:
                    safe_items.append(item)
            
            # Score items based on dietary profile
            scored_items = []
            for item in safe_items:
                score = 0.5  # Base score
                
                # Boost score for dietary tags match
                item_tags = item.get('dietary_tags', [])
                if rec_dietary_profile:
                    dietary_type = rec_dietary_profile.get('dietary_type', '').lower()
                    if dietary_type in [tag.lower() for tag in item_tags]:
                        score += 0.3
                
                # Boost for low-sodium if needed
                if 'low-sodium' in patient_restrictions:
                    if item.get('sodium_mg', 1000) < 500:
                        score += 0.2
                
                # Boost for diabetic-friendly
                if 'diabetic' in patient_restrictions:
                    if item.get('sugar_g', 20) < 10:
                        score += 0.2
                
                scored_items.append((item, min(score, 1.0)))
            
            # Sort by score
            scored_items.sort(key=lambda x: x[1], reverse=True)
            recommendations = scored_items[:5]  # Top 5
            
            if recommendations:
                st.success(f"✨ Generated {len(recommendations)} safe recommendations")
                
                # Display recommendations
                for idx, (item, score) in enumerate(recommendations, 1):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"### {idx}. {item['name']}")
                            st.markdown(f"_{item.get('description', 'Delicious and nutritious')}_")
                            st.markdown(f"**Category:** {item['category']} | **Calories:** {item['calories']} kcal")
                            
                            # Show nutritional info
                            st.caption(f"Protein: {item['protein_g']}g | Carbs: {item['carbs_g']}g | Fat: {item['fat_g']}g | Sodium: {item['sodium_mg']}mg")
                            
                            # Show dietary tags
                            if item.get('dietary_tags'):
                                tags_display = " ".join([f"`{tag}`" for tag in item['dietary_tags']])
                                st.markdown(f"**Tags:** {tags_display}")
                        
                        with col2:
                            st.metric("Match Score", f"{score * 100:.0f}%")
                            if st.button(f"Add to Order", key=f"add_rec_{idx}"):
                                if 'selected_meal_items' not in st.session_state:
                                    st.session_state.selected_meal_items = []
                                st.session_state.selected_meal_items.append(item['item_id'])
                                st.success("Added! Go to 'New Order' tab")
                        
                        st.markdown("---")
            else:
                st.warning("No safe recommendations found for this patient's dietary restrictions.")

# Add a help section at the bottom
with st.expander("❓ Help & Instructions"):
    st.markdown("""
    ### How to Use the Meal Ordering System
    
    **Creating a New Order:**
    1. Enter the Patient ID
    2. Select meal time and delivery schedule
    3. Click "Load Patient Restrictions" to see dietary requirements
    4. Select meal items from available categories
    5. Click "Validate Order" to check for dietary compliance
    6. If validation passes, click "Submit Order"
    
    **Understanding Validation Results:**
    - ✅ **Green Box:** Order is approved and safe to submit
    - ⚠️ **Yellow Warnings:** Order is acceptable but has minor concerns
    - ❌ **Red Errors:** Order has critical issues and cannot be submitted
    
    **AI-Powered Features:**
    - Real-time nutrition validation
    - Allergy and dietary restriction checking
    - Personalized meal recommendations
    - Automatic compliance verification
    
    **Need Help?**
    Contact the nutrition team or system administrator.
    """)
