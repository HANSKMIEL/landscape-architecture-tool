# Systematic Debugging Guide

## Philosophy

> "Debugging is a science, not an art. A systematic approach transforms frustrating troubleshooting into efficient problem-solving."

This guide provides a repeatable framework for diagnosing and fixing issues in the Landscape Architecture Tool. Following this process will dramatically reduce debugging time and prevent recurring problems.

---

## Table of Contents

1. [The 5-Step Debugging Process](#the-5-step-debugging-process)
2. [Backend Debugging](#backend-debugging)
3. [Frontend Debugging](#frontend-debugging)
4. [Database Debugging](#database-debugging)
5. [Integration Debugging](#integration-debugging)
6. [Common Issues & Solutions](#common-issues--solutions)
7. [Debugging Tools Reference](#debugging-tools-reference)
8. [Prevention Strategies](#prevention-strategies)

---

## The 5-Step Debugging Process

Every debugging session should follow this systematic process:

### Step 1: Identify the Problem

**Goal**: Define the issue with precision.

**Bad Description**:
- "It doesn't work"
- "The page is broken"
- "Something is wrong with suppliers"

**Good Description**:
```
Issue: Supplier creation returns 500 error
Expected: POST /api/suppliers with valid data returns 201 Created
Actual: POST /api/suppliers returns 500 Internal Server Error
Context: Happens with email "test@example.com", not with "admin@company.nl"
Environment: Development (docker-compose)
```

**Template**:
```markdown
## Issue Description
- **What should happen**: [Expected behavior]
- **What actually happens**: [Actual behavior]
- **When does it occur**: [Specific conditions]
- **Environment**: [Dev/Staging/Production]
- **First noticed**: [Date/commit if known]
```

### Step 2: Reproduce Consistently

**Goal**: Create minimal, repeatable steps that trigger the bug.

**Process**:

1. **Document exact steps**:
   ```
   1. Navigate to http://localhost:3000/suppliers/new
   2. Fill in form:
      - Name: "Test Supplier"
      - Email: "test@example.com"
      - Phone: "+31 20 1234567"
   3. Click "Save" button
   4. Observe network tab in DevTools
   5. Result: 500 error, no supplier created
   ```

2. **Simplify to minimal case**:
   - Remove unnecessary steps
   - Use direct API calls if possible
   - Isolate the failing component

3. **Test in isolation**:
   ```bash
   # Direct API test
   curl -X POST http://localhost:5000/api/suppliers \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test Supplier",
       "email": "test@example.com"
     }'
   ```

4. **Verify consistency**:
   - Does it fail every time?
   - Does it fail on other machines?
   - Does it fail in different environments?

**Reproduction Checklist**:
- [ ] Steps documented clearly
- [ ] Reproduced multiple times
- [ ] Reproduced in clean environment
- [ ] Minimal test case created
- [ ] Screenshots/recordings captured (if UI issue)

### Step 3: Isolate the Root Cause

**Goal**: Identify the exact source of the problem.

**Strategy**: Binary search through the stack.

#### Full-Stack Isolation Process

```
User Action → Frontend → API Call → Backend → Database
                ↓          ↓          ↓          ↓
              Check     Check      Check     Check
              Here      Here       Here      Here
```

**Questions to Answer**:

1. **Is the request reaching the backend?**
   ```bash
   # Check backend logs
   docker-compose logs -f backend | grep POST
   
   # Or add logging
   # src/routes/suppliers.py
   import logging
   logger = logging.getLogger(__name__)
   
   @bp.route('/suppliers', methods=['POST'])
   def create_supplier():
       logger.info(f"Received request: {request.json}")
       # ...
   ```

2. **Is the data valid?**
   ```python
   # Add validation logging
   @bp.route('/suppliers', methods=['POST'])
   def create_supplier():
       data = request.json
       logger.info(f"Request data: {data}")
       
       try:
           schema = SupplierSchema()
           validated = schema.load(data)
           logger.info(f"Validated data: {validated}")
       except ValidationError as e:
           logger.error(f"Validation failed: {e.messages}")
           return jsonify({"error": e.messages}), 422
   ```

3. **Is the database operation failing?**
   ```python
   # Add database logging
   try:
       new_supplier = SupplierService.create(validated)
       logger.info(f"Created supplier with ID: {new_supplier.id}")
   except SQLAlchemyError as e:
       logger.error(f"Database error: {str(e)}", exc_info=True)
       raise
   ```

4. **Is the response being sent correctly?**
   ```python
   response = jsonify(new_supplier.to_dict())
   logger.info(f"Sending response: {response.status_code}")
   return response, 201
   ```

**Isolation Tools**:

- **Breakpoints**: Pause execution at specific lines
- **Logging**: Strategic log statements at each layer
- **Unit tests**: Test components in isolation
- **Direct calls**: Bypass layers to test specific functions

### Step 4: Fix the Issue

**Goal**: Make minimal, targeted changes to resolve the root cause.

**Principles**:

1. **Fix one thing at a time**
   - Don't refactor while debugging
   - Don't fix multiple issues in one commit
   - Focus on the specific root cause

2. **Make minimal changes**
   ```python
   # ❌ Bad: Large refactor while fixing bug
   def create_supplier(data):
       # Restructure entire function
       # Add new features
       # Change variable names
       # Fix the bug somewhere in there
   
   # ✅ Good: Minimal fix
   def create_supplier(data):
       # ... existing code ...
       
       # Fix: Validate email before database insert
       if not validate_email(data['email']):
           raise ValidationError("Invalid email format")
       
       # ... rest of existing code ...
   ```

3. **Document the fix**
   ```python
   # Fix for issue #123: Validate email format before database insert
   # Previously, invalid emails would cause database constraint violation
   # which returned 500 instead of 422
   if not validate_email(data['email']):
       raise ValidationError("Invalid email format")
   ```

### Step 5: Verify the Fix

**Goal**: Ensure the bug is fixed and no new bugs were introduced.

**Verification Checklist**:

1. **Test the specific issue**:
   ```bash
   # Does the original reproduction case now work?
   curl -X POST http://localhost:5000/api/suppliers \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test Supplier",
       "email": "test@example.com"
     }'
   # Should return 201 Created
   ```

2. **Test edge cases**:
   ```bash
   # Test invalid email (should return 422, not 500)
   curl -X POST http://localhost:5000/api/suppliers \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test Supplier",
       "email": "not-an-email"
     }'
   # Should return 422 Unprocessable Entity
   ```

3. **Run automated tests**:
   ```bash
   make backend-test
   make frontend-test
   ```

4. **Test in production-like environment**:
   ```bash
   docker-compose down
   docker-compose up --build
   # Test again in fresh environment
   ```

5. **Write regression test**:
   ```python
   # tests/test_suppliers.py
   def test_create_supplier_with_invalid_email_returns_422():
       """Regression test for issue #123"""
       response = client.post('/api/suppliers', json={
           'name': 'Test Supplier',
           'email': 'not-an-email'
       })
       
       assert response.status_code == 422
       assert 'email' in response.json['error']['details']
   ```

**Final Verification**:
- [ ] Original issue resolved
- [ ] Edge cases handled
- [ ] All tests passing
- [ ] No new errors introduced
- [ ] Regression test added
- [ ] Documentation updated if needed

---

## Backend Debugging

### Flask Application Debugging

#### Enable Debug Mode (Development Only)

```python
# .env
FLASK_ENV=development
FLASK_DEBUG=1
```

**⚠️ Never enable debug mode in production!**

#### Strategic Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use throughout code
@bp.route('/suppliers', methods=['POST'])
def create_supplier():
    logger.info("=== CREATE SUPPLIER START ===")
    logger.info(f"Request data: {request.json}")
    
    try:
        result = SupplierService.create(request.json)
        logger.info(f"Supplier created: ID={result.id}")
        return jsonify(result.to_dict()), 201
    except Exception as e:
        logger.error(f"Failed to create supplier: {e}", exc_info=True)
        raise
    finally:
        logger.info("=== CREATE SUPPLIER END ===")
```

#### Using Python Debugger (pdb)

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()
```

**Common pdb commands**:
- `n` - Next line
- `s` - Step into function
- `c` - Continue execution
- `p variable_name` - Print variable
- `pp variable_name` - Pretty print variable
- `l` - List code around current line
- `q` - Quit debugger

#### Testing Individual Routes

```python
# tests/test_suppliers.py
def test_create_supplier(client):
    """Test supplier creation"""
    response = client.post('/api/suppliers', json={
        'name': 'Test Supplier',
        'email': 'test@example.com'
    })
    
    assert response.status_code == 201
    assert response.json['data']['name'] == 'Test Supplier'
```

#### Checking Service Layer

```python
# Test services directly
from src.services.supplier_service import SupplierService

# In Python shell or test
supplier = SupplierService.create({
    'name': 'Test Supplier',
    'email': 'test@example.com'
})
print(f"Created: {supplier.id}")
```

### Common Backend Issues

#### Issue: 500 Internal Server Error

**Symptoms**:
- API returns 500
- No clear error message
- Vague "Internal Server Error"

**Debug Process**:

1. **Check logs**:
   ```bash
   docker-compose logs -f backend
   # or
   tail -f logs/application.log
   ```

2. **Look for stack trace**:
   ```
   Traceback (most recent call last):
     File "src/routes/suppliers.py", line 45, in create_supplier
       supplier = SupplierService.create(data)
     File "src/services/supplier_service.py", line 23, in create
       db.session.commit()
   IntegrityError: UNIQUE constraint failed: suppliers.email
   ```

3. **Identify the actual error** (in this case: duplicate email)

4. **Fix with proper error handling**:
   ```python
   try:
       supplier = SupplierService.create(data)
   except IntegrityError as e:
       if 'email' in str(e):
           return jsonify({
               'error': 'Supplier with this email already exists'
           }), 409
       raise
   ```

#### Issue: Database Connection Errors

**Symptoms**:
- "Could not connect to database"
- "Connection refused"
- "Database does not exist"

**Debug Process**:

1. **Check database is running**:
   ```bash
   docker-compose ps
   # db service should be "Up"
   ```

2. **Check connection string**:
   ```bash
   echo $DATABASE_URL
   # Should be: postgresql://user:pass@host:port/dbname
   ```

3. **Test connection directly**:
   ```bash
   docker-compose exec db psql -U landscape_user -d landscape_architecture_prod
   ```

4. **Check migrations**:
   ```bash
   flask db current
   flask db upgrade
   ```

#### Issue: Validation Errors Not Clear

**Symptoms**:
- 400 errors with vague messages
- Missing field details in errors

**Fix**:
```python
# Use proper schema validation
from marshmallow import Schema, fields, ValidationError

class SupplierSchema(Schema):
    name = fields.Str(required=True, error_messages={
        'required': 'Supplier name is required'
    })
    email = fields.Email(required=True, error_messages={
        'required': 'Email is required',
        'invalid': 'Invalid email format'
    })

@bp.route('/suppliers', methods=['POST'])
def create_supplier():
    try:
        data = SupplierSchema().load(request.json)
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Validation failed',
                'details': e.messages
            }
        }), 422
```

---

## Frontend Debugging

### Browser DevTools

#### Console Tab

**Always have console open during development**:
- Shows JavaScript errors
- Displays console.log output
- Shows network request summaries

**Strategic console logging**:
```javascript
// Add contextual logging
console.log('📤 Sending supplier data:', formData);

fetch('/api/suppliers', {
  method: 'POST',
  body: JSON.stringify(formData)
})
.then(res => {
  console.log('📥 Response status:', res.status);
  return res.json();
})
.then(data => {
  console.log('✅ Success:', data);
})
.catch(error => {
  console.error('❌ Error:', error);
});
```

#### Network Tab

**Most important tool for API debugging**:

1. **Open Network tab** before reproducing issue
2. **Filter to XHR/Fetch** to see API calls
3. **Click on request** to see:
   - Request headers
   - Request payload
   - Response headers
   - Response body
   - Timing information

**What to check**:
- Is the request sent to correct URL?
- Are headers correct (Content-Type)?
- Is request body formatted correctly?
- What is response status code?
- What is response body?

#### Sources Tab (Debugger)

**Set breakpoints in code**:

1. Open Sources tab
2. Find your file (Ctrl+P)
3. Click line number to set breakpoint
4. Trigger the action
5. Execution pauses at breakpoint

**Breakpoint features**:
- Inspect variables in scope
- Step through code line by line
- Watch specific variables
- Conditional breakpoints

```javascript
// Or add debugger statement in code
function handleSubmit(formData) {
  debugger;  // Execution pauses here
  
  fetch('/api/suppliers', {
    method: 'POST',
    body: JSON.stringify(formData)
  });
}
```

### React DevTools

Install React DevTools browser extension.

**Features**:
- Inspect component hierarchy
- View component props and state
- Track component updates
- Identify performance issues

**Common use cases**:

1. **Check if data is reaching component**:
   ```jsx
   function SupplierList({ suppliers }) {
     // In React DevTools, inspect props
     // Is suppliers array populated?
     // Are values correct?
     
     return suppliers.map(s => <SupplierCard key={s.id} {...s} />);
   }
   ```

2. **Check state updates**:
   ```jsx
   function SupplierForm() {
     const [formData, setFormData] = useState({});
     
     // In React DevTools, watch formData state
     // Does it update when typing?
     // Are values correct?
     
     return <form>...</form>;
   }
   ```

### Common Frontend Issues

#### Issue: API Calls Fail with CORS Errors

**Symptoms**:
```
Access to fetch at 'http://localhost:5000/api/suppliers' from origin 
'http://localhost:3000' has been blocked by CORS policy
```

**Fix**: Configure CORS in backend
```python
# src/main.py
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})
```

#### Issue: Data Not Updating in UI

**Debug process**:

1. **Check if API call succeeds**:
   ```javascript
   console.log('Before API call');
   const response = await fetch('/api/suppliers');
   console.log('API response:', response.status);
   const data = await response.json();
   console.log('API data:', data);
   ```

2. **Check if state updates**:
   ```javascript
   const [suppliers, setSuppliers] = useState([]);
   
   useEffect(() => {
     fetchSuppliers().then(data => {
       console.log('Setting suppliers:', data);
       setSuppliers(data);
     });
   }, []);
   
   console.log('Current suppliers state:', suppliers);
   ```

3. **Check if component re-renders**:
   ```javascript
   function SupplierList({ suppliers }) {
     console.log('SupplierList render, count:', suppliers.length);
     return ...;
   }
   ```

#### Issue: Form Submission Not Working

**Debug checklist**:

- [ ] Is form `onSubmit` handler attached?
- [ ] Is `event.preventDefault()` called?
- [ ] Is form data collected correctly?
- [ ] Is API call made?
- [ ] Does API return success?
- [ ] Is success state updated?

```javascript
function SupplierForm() {
  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('1. Form submitted');
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData);
    console.log('2. Form data:', data);
    
    try {
      const response = await fetch('/api/suppliers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      console.log('3. API response:', response.status);
      
      if (response.ok) {
        const result = await response.json();
        console.log('4. Success:', result);
      }
    } catch (error) {
      console.error('5. Error:', error);
    }
  };
  
  return <form onSubmit={handleSubmit}>...</form>;
}
```

---

## Database Debugging

### Flask-Migrate / Alembic

#### Check Current Migration

```bash
flask db current
# Shows current migration version
```

#### View Migration History

```bash
flask db history
# Shows all migrations
```

#### Upgrade Database

```bash
flask db upgrade
# Apply all pending migrations
```

#### Downgrade Database

```bash
flask db downgrade -1
# Rollback one migration
```

#### Create New Migration

```bash
flask db migrate -m "Add supplier category field"
# Auto-generate migration from model changes

# Always review generated migration!
cat migrations/versions/xxxx_add_supplier_category.py
```

### SQL Query Debugging

#### Enable SQLAlchemy Logging

```python
# src/config.py
SQLALCHEMY_ECHO = True  # Logs all SQL queries
```

#### Manual Query Testing

```bash
# Connect to database
docker-compose exec db psql -U landscape_user -d landscape_architecture_prod

# Run queries
SELECT * FROM suppliers WHERE email = 'test@example.com';

# Check constraints
\d suppliers

# View indexes
\di
```

### Common Database Issues

#### Issue: Migration Conflicts

**Symptoms**:
```
Multiple head revisions are present
```

**Fix**:
```bash
# Merge the heads
flask db merge heads -m "Merge migrations"
flask db upgrade
```

#### Issue: Table Doesn't Exist

**Symptoms**:
```
sqlalchemy.exc.ProgrammingError: relation "suppliers" does not exist
```

**Fix**:
```bash
# Run migrations
flask db upgrade

# Or create all tables
python -c "from src.main import app, db; 
           with app.app_context(): db.create_all()"
```

#### Issue: Data Migration Needed

When adding NOT NULL column to existing table:

```python
# migrations/versions/xxxx_add_required_field.py
def upgrade():
    # Step 1: Add column as nullable
    op.add_column('suppliers', 
        sa.Column('category', sa.String(100), nullable=True))
    
    # Step 2: Set default value for existing rows
    op.execute("UPDATE suppliers SET category = 'General' WHERE category IS NULL")
    
    # Step 3: Make column NOT NULL
    op.alter_column('suppliers', 'category', nullable=False)

def downgrade():
    op.drop_column('suppliers', 'category')
```

---

## Integration Debugging

### Full-Stack Request Tracing

Add correlation IDs to track requests through the stack:

**Backend**:
```python
import uuid

@app.before_request
def before_request():
    request.id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
    logger.info(f"[{request.id}] {request.method} {request.path}")

@app.after_request
def after_request(response):
    logger.info(f"[{request.id}] Response: {response.status_code}")
    response.headers['X-Request-ID'] = request.id
    return response
```

**Frontend**:
```javascript
const requestId = crypto.randomUUID();

fetch('/api/suppliers', {
  headers: {
    'X-Request-ID': requestId
  }
}).then(response => {
  console.log(`Request ${requestId}: ${response.status}`);
});
```

### Docker Debugging

#### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

#### Execute Commands in Container

```bash
# Open shell in backend container
docker-compose exec backend bash

# Run Python in container
docker-compose exec backend python
>>> from src.models import Supplier
>>> Supplier.query.all()

# Run tests in container
docker-compose exec backend pytest
```

#### Rebuild After Changes

```bash
# Rebuild specific service
docker-compose up --build backend

# Rebuild all
docker-compose down
docker-compose up --build
```

---

## Common Issues & Solutions

### Quick Reference

| Symptom | Likely Cause | Quick Fix |
|---------|--------------|-----------|
| 500 error | Unhandled exception | Check backend logs |
| 404 error | Wrong URL/route | Verify endpoint exists |
| 422 error | Validation failure | Check request data format |
| CORS error | Missing CORS config | Configure Flask-CORS |
| Connection refused | Service not running | `docker-compose up` |
| Import errors | Missing dependency | `pip install -r requirements.txt` |
| Module not found | PYTHONPATH not set | `export PYTHONPATH=.` |
| Database locked | Transaction not committed | Check db.session.commit() |
| Frontend blank page | JavaScript error | Check browser console |
| Stale data in UI | Cache issue | Hard refresh (Ctrl+Shift+R) |

---

## Debugging Tools Reference

### Backend Tools

| Tool | Purpose | Command |
|------|---------|---------|
| pdb | Interactive debugger | `python -m pdb script.py` |
| pytest | Test runner | `pytest -v tests/` |
| Flask shell | Interactive Python | `flask shell` |
| SQLAlchemy | ORM debugging | Set `SQLALCHEMY_ECHO=True` |
| Bandit | Security scanning | `bandit -r src/` |

### Frontend Tools

| Tool | Purpose | Access |
|------|---------|--------|
| Chrome DevTools | Browser debugger | F12 |
| React DevTools | Component inspector | Browser extension |
| Network Monitor | API debugging | DevTools → Network |
| Console | Log output | DevTools → Console |
| Vitest | Test runner | `npm run test` |

### Database Tools

| Tool | Purpose | Command |
|------|---------|---------|
| psql | PostgreSQL CLI | `psql -U user -d db` |
| pgAdmin | PostgreSQL GUI | Web interface |
| Flask-Migrate | Migrations | `flask db` commands |

---

## Prevention Strategies

### Write Tests First (TDD)

```python
# 1. Write failing test
def test_duplicate_email_returns_409():
    client.post('/api/suppliers', json={'email': 'test@example.com'})
    response = client.post('/api/suppliers', json={'email': 'test@example.com'})
    assert response.status_code == 409

# 2. Run test - it fails
pytest tests/test_suppliers.py::test_duplicate_email_returns_409

# 3. Implement fix
# 4. Test passes
```

### Add Comprehensive Logging

```python
# Strategic logging at entry/exit points
logger.info(f"Function called with: {params}")
logger.info(f"Function returned: {result}")
logger.error(f"Function failed: {error}", exc_info=True)
```

### Use Type Hints

```python
from typing import Dict, List, Optional

def create_supplier(data: Dict[str, str]) -> Supplier:
    """Create a new supplier"""
    pass

# Catch type errors early with mypy
# mypy src/
```

### Document Assumptions

```python
def process_supplier(supplier_id: int) -> bool:
    """
    Process supplier data.
    
    Assumptions:
    - supplier_id exists in database
    - Supplier has valid email
    - Database connection is active
    
    Returns:
        True if processed successfully, False otherwise
    
    Raises:
        ValueError: If supplier_id is invalid
        DatabaseError: If database operation fails
    """
```

---

## Debugging Workflow Checklist

When encountering a bug:

- [ ] Clearly define the problem
- [ ] Create minimal reproduction steps
- [ ] Check recent changes (git log)
- [ ] Verify environment (dependencies, config)
- [ ] Add logging at each layer
- [ ] Isolate the failing component
- [ ] Make minimal fix
- [ ] Write regression test
- [ ] Run full test suite
- [ ] Test in production-like environment
- [ ] Document the issue and fix
- [ ] Update documentation if needed

---

## Getting Help

If stuck after following this guide:

1. **Document everything you've tried**
2. **Create a minimal reproduction**
3. **Check existing issues** on GitHub
4. **Ask for help** with:
   - Problem description
   - Reproduction steps
   - What you've tried
   - Relevant logs/errors

---

## Conclusion

Systematic debugging is about:
- **Process over panic** - Follow the 5 steps
- **Tools over guessing** - Use debuggers and logs
- **Testing over hoping** - Write tests to verify fixes
- **Prevention over cure** - Add tests to prevent regressions

With practice, this framework becomes second nature, transforming debugging from a frustrating mystery into an efficient, repeatable process.
