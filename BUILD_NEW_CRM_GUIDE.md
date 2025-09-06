# BUILD NEW CRM TOOL - Customization Guide

## 🎯 Purpose: Create Similar CRM for Any Business Type

### 🔧 CUSTOMIZABLE TEMPLATE STRUCTURE

#### Business Information Template
```python
# CHANGE THESE FOR YOUR BUSINESS
BUSINESS_NAME = "[YOUR_BUSINESS_NAME]"           # e.g., "ABC Dance Academy"
BUSINESS_TYPE = "[YOUR_BUSINESS_TYPE]"           # e.g., "Dance Academy", "Coaching Center", "Gym"
WEBSITE = "[YOUR_WEBSITE]"                       # e.g., "www.abcdance.com"
OWNER_NAME = "[YOUR_FULL_NAME]"                  # e.g., "John Smith"
MANAGING_DIRECTOR = "[YOUR_NAME]"                # e.g., "John S"
CONTACT_PHONE = "[YOUR_PHONE_NUMBER]"            # e.g., "+91-9876543210"
```

#### Payment Details Template
```python
# CHANGE THESE TO YOUR BANK DETAILS
UPI_ID = "[YOUR_UPI_ID]"                        # e.g., "9876543210"
ACCOUNT_NUMBER = "[YOUR_ACCOUNT_NUMBER]"         # e.g., "12345678901"
IFSC_CODE = "[YOUR_IFSC_CODE]"                   # e.g., "HDFC0001234"
BANK_NAME = "[YOUR_BANK_NAME]"                   # e.g., "HDFC Bank"
ACCOUNT_HOLDER = "[YOUR_ACCOUNT_HOLDER_NAME]"    # e.g., "John Smith"
```

#### API Credentials Template
```python
# GET NEW CREDENTIALS FOR YOUR BUSINESS
FAST2SMS_API_KEY = "[GET_NEW_API_KEY]"           # Register at fast2sms.com
REGISTERED_SENDER = "[YOUR_BUSINESS_NUMBER]"     # Your registered business number
SENDER_EMAIL = "[YOUR_BUSINESS_EMAIL]"           # e.g., "info@abcdance.com"
APP_PASSWORD = "[GENERATE_NEW_APP_PASSWORD]"     # Gmail app password
```

---

## 🏗️ BUSINESS TYPE ADAPTATIONS

### 🩰 Dance Academy CRM
```python
# Business Configuration
BUSINESS_NAME = "ABC Dance Academy"
BUSINESS_TYPE = "Dance Academy"
RECEIPT_PREFIX = "ADA"  # ABC Dance Academy
STUDENT_ID_PREFIX = "ADA"

# Services (Replace instruments table)
SERVICES = [
    'Classical Dance', 'Hip-Hop', 'Bharatanatyam', 'Bollywood', 
    'Contemporary', 'Jazz', 'Salsa', 'Ballet'
]

# Plans (Dance-specific)
PLANS = [
    ('1 Month - Beginner', 2500, 1),
    ('1 Month - Intermediate', 3000, 1),
    ('3 Months - Beginner', 7000, 3),
    ('3 Months - Advanced', 8500, 3),
    ('Annual - All Forms', 25000, 12)
]

# WhatsApp Template Content
TEMPLATE_CONTENT = """
Hi {Var1}, Your {Var2} dance classes expire on {Var3}.

💃 Payment Options:
📱 UPI: [YOUR_UPI_ID]
🏦 Bank: [YOUR_BANK_DETAILS]

Keep dancing! - ABC Dance Academy
"""
```

### 📚 Coaching Center CRM
```python
# Business Configuration
BUSINESS_NAME = "Excellence Coaching Center"
BUSINESS_TYPE = "Coaching Center"
RECEIPT_PREFIX = "ECC"
STUDENT_ID_PREFIX = "ECC"

# Services (Replace instruments)
SERVICES = [
    'Mathematics', 'Physics', 'Chemistry', 'Biology',
    'English', 'JEE Preparation', 'NEET Preparation', 'Board Exam Prep'
]

# Plans (Subject-specific)
PLANS = [
    ('Single Subject - 1 Month', 3000, 1),
    ('Two Subjects - 1 Month', 5000, 1),
    ('JEE Complete - 3 Months', 15000, 3),
    ('NEET Complete - 6 Months', 25000, 6),
    ('Board Exam - Annual', 30000, 12)
]

# Additional Tables for Coaching
ADDITIONAL_TABLES = '''
CREATE TABLE batches (
    id INTEGER PRIMARY KEY,
    batch_name TEXT,
    subject TEXT,
    timing TEXT,
    capacity INTEGER,
    current_strength INTEGER DEFAULT 0
);

CREATE TABLE exam_schedules (
    id INTEGER PRIMARY KEY,
    student_id TEXT,
    exam_name TEXT,
    exam_date TEXT,
    syllabus TEXT,
    FOREIGN KEY (student_id) REFERENCES students_enhanced (student_id)
);
'''
```

### 💪 Gym/Fitness Center CRM
```python
# Business Configuration
BUSINESS_NAME = "FitZone Gym"
BUSINESS_TYPE = "Fitness Center"
RECEIPT_PREFIX = "FZG"
STUDENT_ID_PREFIX = "FZG"

# Services (Replace instruments)
SERVICES = [
    'General Fitness', 'Weight Training', 'Cardio', 'Personal Training',
    'Group Classes', 'Yoga', 'Zumba', 'CrossFit'
]

# Plans (Membership-specific)
PLANS = [
    ('Basic Gym - 1 Month', 1500, 1),
    ('Premium + Cardio - 1 Month', 2500, 1),
    ('Personal Training - 1 Month', 5000, 1),
    ('Annual Membership', 15000, 12),
    ('Couple Package - 6 Months', 20000, 6)
]

# Additional Tables for Gym
ADDITIONAL_TABLES = '''
CREATE TABLE trainers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    specialization TEXT,
    contact TEXT,
    experience_years INTEGER
);

CREATE TABLE workout_plans (
    id INTEGER PRIMARY KEY,
    student_id TEXT,
    trainer_id INTEGER,
    plan_details TEXT,
    created_date TEXT,
    FOREIGN KEY (student_id) REFERENCES students_enhanced (student_id),
    FOREIGN KEY (trainer_id) REFERENCES trainers (id)
);
'''
```

### 🎨 Art Classes CRM
```python
# Business Configuration
BUSINESS_NAME = "Creative Art Studio"
BUSINESS_TYPE = "Art Classes"
RECEIPT_PREFIX = "CAS"
STUDENT_ID_PREFIX = "CAS"

# Services (Replace instruments)
SERVICES = [
    'Painting', 'Sketching', 'Digital Art', 'Sculpture',
    'Pottery', 'Calligraphy', 'Watercolor', 'Oil Painting'
]

# Plans (Art-specific)
PLANS = [
    ('Basic Drawing - 1 Month', 2000, 1),
    ('Painting Complete - 3 Months', 8000, 3),
    ('Digital Art - 2 Months', 6000, 2),
    ('All Art Forms - 6 Months', 18000, 6),
    ('Professional Course - 1 Year', 30000, 12)
]

# Additional Tables for Art Classes
ADDITIONAL_TABLES = '''
CREATE TABLE art_supplies (
    id INTEGER PRIMARY KEY,
    item_name TEXT,
    quantity INTEGER,
    cost_per_unit REAL,
    supplier TEXT
);

CREATE TABLE student_portfolios (
    id INTEGER PRIMARY KEY,
    student_id TEXT,
    artwork_name TEXT,
    completion_date TEXT,
    grade TEXT,
    FOREIGN KEY (student_id) REFERENCES students_enhanced (student_id)
);
'''
```

---

## 📋 STEP-BY-STEP CUSTOMIZATION PROCESS

### Phase 1: Business Setup (30 minutes)
1. **Choose Business Type** from templates above
2. **Register Fast2SMS Account** with your business details
3. **Create Gmail Account** for your business
4. **Get Bank Details** ready for payment integration

### Phase 2: API Setup (45 minutes)
1. **Fast2SMS Configuration**
   ```bash
   # Register at fast2sms.com
   # Get API key
   # Register your business phone number
   # Create 3 WhatsApp templates with your business name
   ```

2. **Gmail SMTP Setup**
   ```bash
   # Enable 2-factor authentication
   # Generate app password
   # Test SMTP connection
   ```

### Phase 3: Code Customization (2 hours)
1. **Update Business Constants**
   ```python
   # In all files, replace:
   "Chords Music Academy" → "[Your Business Name]"
   "CMA" → "[Your Business Code]"
   "chords_crm.db" → "[your_business]_crm.db"
   ```

2. **Update Services/Plans**
   ```python
   # In create_database.py, replace instruments and plans
   # with your business-specific services and pricing
   ```

3. **Update Templates**
   ```python
   # In sms_email.py, update template IDs and content
   template_map = {
       "fee_reminder": "[YOUR_TEMPLATE_ID_1]",
       "payment_receipt": "[YOUR_TEMPLATE_ID_2]",
       "installment_reminder": "[YOUR_TEMPLATE_ID_3]"
   }
   ```

### Phase 4: UI Customization (1 hour)
1. **Update Page Titles**
   ```python
   # In app.py
   st.title("[Your Business Name] - CRM System")
   st.sidebar.title("[Your Business] CRM")
   ```

2. **Update Colors** (.streamlit/config.toml)
   ```toml
   [theme]
   primaryColor = "[Your Brand Color]"  # e.g., "#FF6B6B"
   ```

3. **Update Labels**
   ```python
   # Replace "Student" with appropriate term:
   # "Member" for gym, "Participant" for classes, etc.
   ```

### Phase 5: Testing & Deployment (1 hour)
1. **Local Testing**
   ```bash
   python create_database.py
   streamlit run app.py
   ```

2. **Test All Functions**
   - Add new member/student
   - Process payment
   - Send WhatsApp/Email
   - Check due alerts

3. **Deploy to Streamlit Cloud**
   ```bash
   git init
   git add .
   git commit -m "Initial [Business Name] CRM"
   git push origin main
   ```

---

## 🎯 INDUSTRY-SPECIFIC MODIFICATIONS

### Language Learning Institute
```python
SERVICES = ['English', 'Spanish', 'French', 'German', 'Mandarin', 'Japanese']
PLANS = [
    ('Beginner Level - 2 Months', 4000, 2),
    ('Intermediate Level - 3 Months', 6000, 3),
    ('Advanced Level - 4 Months', 8000, 4),
    ('Business English - 6 Months', 12000, 6)
]

# Additional table for proficiency tracking
CREATE TABLE proficiency_levels (
    id INTEGER PRIMARY KEY,
    student_id TEXT,
    language TEXT,
    level TEXT,  -- Beginner, Intermediate, Advanced
    test_score INTEGER,
    test_date TEXT
);
```

### Swimming Academy
```python
SERVICES = ['Beginner Swimming', 'Intermediate Swimming', 'Advanced Swimming', 'Competitive Training', 'Water Aerobics']
PLANS = [
    ('Beginner - 1 Month', 3000, 1),
    ('Intermediate - 2 Months', 5500, 2),
    ('Advanced - 3 Months', 8000, 3),
    ('Competitive Training - 6 Months', 15000, 6)
]

# Additional table for swimming levels
CREATE TABLE swimming_levels (
    id INTEGER PRIMARY KEY,
    student_id TEXT,
    current_level TEXT,
    strokes_learned TEXT,
    distance_capability TEXT,
    last_assessment_date TEXT
);
```

### Driving School
```python
SERVICES = ['Two Wheeler', 'Four Wheeler Manual', 'Four Wheeler Automatic', 'Commercial Vehicle', 'Refresher Course']
PLANS = [
    ('Two Wheeler - 15 Days', 3000, 0.5),
    ('Car Manual - 1 Month', 8000, 1),
    ('Car Automatic - 20 Days', 6000, 0.67),
    ('Commercial Vehicle - 2 Months', 15000, 2)
]

# Additional tables for driving school
CREATE TABLE driving_tests (
    id INTEGER PRIMARY KEY,
    student_id TEXT,
    test_type TEXT,  -- Theory, Practical
    test_date TEXT,
    result TEXT,     -- Pass, Fail
    instructor_name TEXT
);

CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY,
    vehicle_number TEXT,
    vehicle_type TEXT,
    fuel_type TEXT,
    last_service_date TEXT
);
```

---

## 🚨 CRITICAL CUSTOMIZATION CHECKLIST

### ✅ MUST CHANGE (Business-Specific)
- [ ] Business name and contact details
- [ ] Bank/UPI payment details  
- [ ] Fast2SMS API key and templates
- [ ] Gmail credentials
- [ ] Services/courses offered
- [ ] Pricing plans
- [ ] Receipt and student ID prefixes
- [ ] WhatsApp template content

### ✅ SHOULD CHANGE (Branding)
- [ ] Color scheme and theme
- [ ] Logo and branding elements
- [ ] Page titles and labels
- [ ] Email signature
- [ ] Website URL

### ✅ CAN CUSTOMIZE (Optional)
- [ ] Database table names
- [ ] Additional business-specific tables
- [ ] Custom fields for students
- [ ] Reporting metrics
- [ ] UI layout and design

---

## 🔧 ADVANCED CUSTOMIZATIONS

### Multi-Location Support
```python
# Add location table
CREATE TABLE locations (
    id INTEGER PRIMARY KEY,
    location_name TEXT,
    address TEXT,
    contact_number TEXT,
    manager_name TEXT
);

# Add location_id to students table
ALTER TABLE students_enhanced ADD COLUMN location_id INTEGER;
```

### Instructor/Trainer Management
```python
CREATE TABLE instructors (
    id INTEGER PRIMARY KEY,
    name TEXT,
    specialization TEXT,
    contact TEXT,
    salary REAL,
    joining_date TEXT
);

# Link students to instructors
ALTER TABLE students_enhanced ADD COLUMN instructor_id INTEGER;
```

### Advanced Reporting
```python
# Revenue by service
def get_revenue_by_service():
    query = '''
    SELECT s.instrument as service, SUM(p.amount) as revenue
    FROM payments p
    JOIN students_enhanced s ON p.student_id = s.student_id
    GROUP BY s.instrument
    '''
    return pd.read_sql_query(query, conn)

# Monthly growth tracking
def get_monthly_growth():
    query = '''
    SELECT strftime('%Y-%m', payment_date) as month, 
           COUNT(*) as payments, 
           SUM(amount) as revenue
    FROM payments
    GROUP BY strftime('%Y-%m', payment_date)
    ORDER BY month
    '''
    return pd.read_sql_query(query, conn)
```

---

## 📞 SUPPORT & MAINTENANCE

### Regular Maintenance Tasks
- **Weekly**: Database backup, performance check
- **Monthly**: API key validation, template updates
- **Quarterly**: Feature updates, user feedback integration

### Common Issues & Solutions
1. **WhatsApp delivery fails**: Check template approval status
2. **Email not sending**: Verify Gmail app password
3. **Database errors**: Check column count and data types
4. **Payment processing issues**: Validate amount calculations

### Scaling Considerations
- **100+ students**: Consider PostgreSQL migration
- **Multiple locations**: Implement location-based filtering
- **Advanced features**: Add user authentication and roles

---

## 🎯 SUCCESS METRICS

### Key Performance Indicators
- **Student Retention Rate**: Track renewals vs new registrations
- **Payment Collection Efficiency**: On-time payment percentage
- **Communication Effectiveness**: WhatsApp/Email delivery rates
- **Revenue Growth**: Month-over-month revenue increase

### Reporting Dashboard
```python
def create_dashboard():
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Students", get_active_students_count())
    with col2:
        st.metric("Monthly Revenue", f"₹{get_monthly_revenue():,.0f}")
    with col3:
        st.metric("Collection Rate", f"{get_collection_rate():.1f}%")
    with col4:
        st.metric("Renewal Rate", f"{get_renewal_rate():.1f}%")
```

---

*This guide enables creation of customized CRM systems for any service-based business in 4-6 hours with complete functionality.*