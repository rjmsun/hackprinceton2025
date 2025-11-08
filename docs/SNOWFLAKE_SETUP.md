# ❄️ Snowflake Setup Guide

## What is Snowflake?

Snowflake is a cloud data warehouse that can store your conversation transcripts, tasks, and summaries for long-term analytics and retrieval.

## 🆓 Get Free Snowflake Account

### Step 1: Sign Up for Free Trial

1. Go to **https://signup.snowflake.com/**
2. Click **"Start for free"**
3. Fill out the form:
   - Email address
   - Company name (can be personal)
   - Choose **"Standard"** edition (free trial)
   - Select a cloud provider (AWS, Azure, or GCP) and region
4. Verify your email

### Step 2: Get Your Account Details

After signing up, you'll get:
- **Account URL**: Something like `https://xy12345.us-east-1.snowflakecomputing.com`
- **Account identifier**: The part before `.snowflakecomputing.com` (e.g., `xy12345.us-east-1`)

### Step 3: Create Your First Database

1. Log into Snowflake web interface
2. Go to **Worksheets** tab
3. Run these SQL commands:

```sql
-- Create a database
CREATE DATABASE IF NOT EXISTS EVE_DB;

-- Create a schema
CREATE SCHEMA IF NOT EXISTS EVE_DB.EVE_SCHEMA;

-- Create a warehouse (for compute)
CREATE WAREHOUSE IF NOT EXISTS EVE_WH
  WITH WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;

-- Use the warehouse
USE WAREHOUSE EVE_WH;
```

### Step 4: Get Your Credentials

You'll need:
- **Account**: The account identifier (e.g., `xy12345.us-east-1`)
- **Username**: Your login username (usually your email)
- **Password**: Your login password
- **Database**: `EVE_DB` (or whatever you named it)
- **Schema**: `EVE_SCHEMA` (or whatever you named it)
- **Warehouse**: `EVE_WH` (or whatever you named it)

## 🔧 Add to `.env`

Edit your `.env` file:

```bash
SNOWFLAKE_ACCOUNT=xy12345.us-east-1
SNOWFLAKE_USER=your_email@example.com
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=EVE_DB
SNOWFLAKE_SCHEMA=EVE_SCHEMA
SNOWFLAKE_WAREHOUSE=EVE_WH
```

**Important:** 
- Account format: `account_identifier.region` (e.g., `xy12345.us-east-1`)
- No `https://` or `.snowflakecomputing.com` in the account field
- Use the exact database/schema/warehouse names you created

## 🧪 Test Connection

### Install Snowflake Connector

```bash
cd backend
source venv/bin/activate
pip install snowflake-connector-python
```

### Test via API

Start your backend and visit:
```
http://localhost:8000/snowflake/test
```

Should return:
```json
{
  "connected": true,
  "status": "success"
}
```

### Test via Python

```bash
cd backend
source venv/bin/activate
python3 -c "
from services.snowflake_service import SnowflakeService
import os
from dotenv import load_dotenv
load_dotenv('../.env')

service = SnowflakeService()
if service.test_connection():
    print('✅ Snowflake connected!')
else:
    print('❌ Connection failed - check credentials')
"
```

## 📊 What Gets Stored

When you call `/snowflake/store`, EVE stores:
- Full transcript text
- Generated summary (short + detailed)
- Extracted tasks (with dates, owners, priorities)
- User ID
- Timestamp

## 🔍 Retrieve Data

Get conversation history:
```
GET /snowflake/conversations/{user_id}?limit=10
```

Returns:
```json
{
  "conversations": [
    {
      "id": "uuid",
      "transcript": "...",
      "summary": {...},
      "tasks": [...],
      "created_at": "2025-11-08T..."
    }
  ]
}
```

## 🎯 Use Cases

1. **Long-term Analytics**: Track productivity over time
2. **Search History**: Find past conversations
3. **Multi-session Consolidation**: Combine tasks across meetings
4. **Learning**: Train models on your conversation patterns

## 🐛 Troubleshooting

### "Connection failed"
- Check account format: `xy12345.us-east-1` (not full URL)
- Verify username/password are correct
- Make sure warehouse is running (it auto-resumes)

### "Database does not exist"
- Run the CREATE DATABASE command in Snowflake
- Check database name matches `.env`

### "Warehouse not found"
- Create warehouse in Snowflake
- Make sure it's not suspended

### "Access denied"
- Check user has permissions on database/schema
- Run: `GRANT ALL ON DATABASE EVE_DB TO ROLE PUBLIC;`

## 💰 Free Tier Limits

- **30-day free trial** with $400 credit
- **X-Small warehouse** is free (auto-suspends after 60s idle)
- **Storage**: First 10GB free, then pay-as-you-go
- Perfect for hackathon demo!

## 📝 Example Account Format

```
Account: xy12345.us-east-1
User: john@example.com
Password: MySecurePass123!
Database: EVE_DB
Schema: EVE_SCHEMA
Warehouse: EVE_WH
```

## ✅ Quick Checklist

- [ ] Signed up at https://signup.snowflake.com/
- [ ] Created database and schema
- [ ] Created warehouse
- [ ] Added credentials to `.env`
- [ ] Installed `snowflake-connector-python`
- [ ] Tested connection at `/snowflake/test`
- [ ] Stored first transcript at `/snowflake/store`

---

**Need help?** Check Snowflake docs: https://docs.snowflake.com/

