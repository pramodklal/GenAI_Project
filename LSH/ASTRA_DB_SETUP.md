# Astra DB Setup Guide for Healthcare Digital

## Overview
This guide will help you set up Astra DB for the Healthcare Digital system, including creating all 11 Cassandra tables and 5 vector collections.

## Prerequisites
✅ You have created "healthcare-digital" database on https://astra.datastax.com/  
✅ You have the Database ID and API Endpoint  
✅ Python 3.11+ installed  

---

## Step 1: Download Secure Connect Bundle

1. Go to https://astra.datastax.com/
2. Click on your **"healthcare-digital"** database
3. Click on the **"Connect"** tab
4. Under **"Driver"** section, click **"Download Bundle"**
5. Save the file as `secure-connect-healthcare-digital.zip`
6. Move this file to your project root directory:
   ```
   HealthCareDigital/
   ├── secure-connect-healthcare-digital.zip  ← Place here
   ├── database/
   ├── .env
   └── ...
   ```

---

## Step 2: Generate Application Token

1. In your Astra DB Console, click on your **"healthcare-digital"** database
2. Go to **"Settings"** tab
3. Click **"Application Tokens"**
4. Click **"Generate Token"**
5. Select Role: **"Database Administrator"**
6. Click **"Generate Token"**
7. **IMPORTANT:** Copy the token immediately (starts with `AstraCS:...`)
   - You won't be able to see it again!
   - Save it securely

---

## Step 3: Configure Environment Variables

1. Open the `.env` file in your project root
2. Update it with your credentials:

```env
# Astra DB Configuration
ASTRA_DB_TOKEN=AstraCS:your-token-here  ← Paste your token here
ASTRA_DB_ID=your-database-id  ← Your database ID from console
ASTRA_DB_REGION=us-east1  ← Your database region
ASTRA_DB_KEYSPACE=healthcare_digital
ASTRA_SECURE_BUNDLE_PATH=./secure-connect-healthcare-digital.zip

# OpenAI Configuration (for embeddings)
OPENAI_API_KEY=your-openai-api-key

# Embedding Configuration
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
```

**How to find your Database ID and Region:**
- Database ID: In Astra Console → Database Details → Database ID
- Region: In Astra Console → Database Details → Region (e.g., us-east1, us-west2)

---

## Step 4: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

This installs:
- `cassandra-driver` - For Cassandra database operations
- `astrapy` - For vector search operations
- `python-dotenv` - For environment variable management

---

## Step 5: Create All Tables

Run the table creation script:

```bash
python database/create_astra_tables.py
```

**Expected Output:**
```
============================================================
🏥 Healthcare Digital - Astra DB Table Creation
============================================================

🔌 Connecting to Astra DB...
   Keyspace: healthcare_digital
   Bundle: ./secure-connect-healthcare-digital.zip
✅ Connected successfully!

📝 Creating tables...

   Creating table: patients... ✅
   Creating table: patient_dietary_profiles... ✅
   Creating table: menu_items... ✅
   Creating table: meal_orders... ✅
   Creating table: meal_order_items... ✅
   Creating table: evs_tasks... ✅
   Creating table: evs_staff... ✅
   Creating table: agent_activities... ✅
   Creating table: system_audit_logs... ✅
   Creating table: food_inventory... ✅
   Creating table: production_schedules... ✅

📊 Summary:
   ✅ Successfully created: 11 tables

🔍 Verifying tables...

   Found 11 tables in keyspace 'healthcare_digital':
   ✓ agent_activities
   ✓ evs_staff
   ✓ evs_tasks
   ✓ food_inventory
   ✓ meal_order_items
   ✓ meal_orders
   ✓ menu_items
   ✓ patient_dietary_profiles
   ✓ patients
   ✓ production_schedules
   ✓ system_audit_logs

   ✅ All tables verified successfully!

============================================================
✅ Setup completed successfully!

Next steps:
   1. Run: python database/init_astra_db.py
   2. This will create vector collections and insert sample data
============================================================
```

---

## Step 6: Verify in Astra Console

1. Go to Astra Console → Your database
2. Click **"CQL Console"** tab
3. Run:
   ```sql
   DESCRIBE TABLES;
   ```
4. You should see all 11 tables listed

---

## Database Schema Overview

### Tables Created (11 Total)

1. **patients** - Patient master data with allergies, dietary restrictions, preferences
2. **patient_dietary_profiles** - Nutritional targets, texture modifications, restrictions
3. **menu_items** - Menu catalog with nutritional info, allergens, costs
4. **meal_orders** - Patient meal orders with AI validation status
5. **meal_order_items** - Line items for each meal order
6. **evs_tasks** - Environmental Services tasks with prioritization
7. **evs_staff** - EVS staff profiles, skills, certifications
8. **agent_activities** - Agent execution logs for monitoring
9. **system_audit_logs** - HIPAA-compliant audit trail
10. **food_inventory** - Ingredient inventory with expiration tracking
11. **production_schedules** - AI-forecasted meal production plans

### Key Design Patterns

- **Time-Series Data**: meal_orders, evs_tasks, agent_activities use composite partition keys with timestamp clustering
- **Entity-Centric**: patients, menu_items, evs_staff use simple primary keys
- **Relational Links**: meal_order_items links orders to menu items

---

## Troubleshooting

### Issue: "ASTRA_DB_TOKEN not found"
**Solution:** Make sure your `.env` file has the token and it starts with `AstraCS:`

### Issue: "Secure Connect Bundle not found"
**Solution:** Verify the file path in `.env` matches where you saved the bundle

### Issue: "Authentication failed"
**Solution:** 
- Regenerate your token with "Database Administrator" role
- Make sure you copied the entire token (it's long!)

### Issue: "Connection timeout"
**Solution:**
- Check your internet connection
- Verify your database is in "Active" state in Astra Console
- Try a different region if connection is slow

---

## Next Steps

After tables are created:

1. **Create Vector Collections:**
   ```bash
   python database/init_astra_db.py
   ```
   This creates 5 vector collections for semantic search:
   - meal_embeddings (1536D)
   - patient_preferences (1536D)
   - evs_task_history (768D)
   - agent_conversations (1536D)
   - clinical_documents (1536D)

2. **Test the System:**
   ```bash
   streamlit run ui/app.py
   ```

3. **View Data in Astra Console:**
   - Go to CQL Console
   - Query tables:
     ```sql
     SELECT * FROM patients LIMIT 10;
     SELECT * FROM meal_orders LIMIT 10;
     ```

---

## Support

- **Astra DB Documentation:** https://docs.datastax.com/en/astra/
- **Python Driver Docs:** https://docs.datastax.com/en/developer/python-driver/
- **Vector Search Guide:** https://docs.datastax.com/en/astra-serverless/docs/vector-search/

---

## Security Notes

⚠️ **NEVER commit your `.env` file to Git!**  
⚠️ **Keep your Astra DB token secure** - treat it like a password  
⚠️ **Rotate tokens regularly** for production environments  
⚠️ **Use different tokens** for dev/staging/production  

---

Happy coding! 🚀
