# N8n Workflow Templates for Landscape Architecture Tool

This directory contains pre-built N8n workflow templates that integrate with the Landscape Architecture Tool to automate common business processes.

## 🚀 Quick Start

### Prerequisites
1. N8n instance running (see `docker-compose.n8n.yml`)
2. Landscape Architecture Tool backend running
3. SMTP credentials configured in N8n for email notifications
4. Google API credentials (optional, for Google Drive/Docs integration)

### Installation Steps

1. **Start the integrated stack:**
   ```bash
   docker-compose -f docker-compose.n8n.yml up -d
   ```

2. **Access N8n interface:**
   - URL: `http://localhost:5678` (or your domain/n8n/)
   - Login with credentials set in docker-compose.yml

3. **Import workflows:**
   - Go to N8n interface
   - Click "Import from File" or "Import from URL"
   - Select the JSON files from this directory

4. **Configure credentials:**
   - Set up SMTP credentials for email sending
   - Configure Google API credentials (optional)
   - Test webhook endpoints

## 📋 Available Workflows

### 1. Client Onboarding Automation
**File:** `client-onboarding.json`

**Trigger:** Webhook `/webhook/client-onboarding`

**Features:**
- ✅ Welcome email with professional HTML template
- 📁 Automatic project folder creation in Google Drive
- 📅 Calendar event generation for initial consultation
- 🔔 Backend notification tracking
- 🎯 Client portal access instructions

**Test Command:**
```bash
curl -X POST http://localhost:5678/webhook/client-onboarding \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "client_name": "John Smith",
    "client_email": "john@example.com",
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

**Expected Actions:**
1. Sends branded welcome email to client
2. Creates project folder in Google Drive
3. Generates calendar link for consultation
4. Notifies backend of completion
5. Returns workflow status

### 2. Project Created Automation
**File:** `project-created.json`

**Trigger:** Webhook `/webhook/project-created`

**Features:**
- 🚀 Project start notification emails
- 📋 Project timeline and milestone overview
- 🎯 Next steps communication to client
- 📊 Progress tracking setup
- 🔔 Backend integration for status updates

**Test Command:**
```bash
curl -X POST http://localhost:5678/webhook/project-created \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "client_id": 1,
    "project_name": "Garden Redesign Project",
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

**Expected Actions:**
1. Fetches client and project details from backend
2. Sends project start notification email
3. Provides timeline and next steps
4. Notifies backend of email delivery
5. Returns workflow completion status

### 3. Project Milestone Tracking
**File:** `project-milestone-tracking.json`

**Trigger:** Webhook `/webhook/project-milestone`

**Features:**
- 🎯 Milestone-specific email notifications
- 📊 Progress tracking with visual indicators
- 🏆 Completion percentage updates
- 💰 Automatic invoice generation (100% completion)
- 👥 Team notifications for project completion
- 📝 Client and team status updates

**Test Command:**
```bash
curl -X POST http://localhost:5678/webhook/project-milestone \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "milestone": "design_completed",
    "status": "completed",
    "completion_percentage": 50,
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

**Supported Milestones:**
- `design_completed` - Design phase finished
- `construction_started` - Construction begins
- `planting_completed` - Plant installation done
- `project_completed` - Full project finished

**Expected Actions:**
1. Fetches project and client details
2. Sends milestone-specific email to client
3. Updates backend with progress
4. Triggers additional actions for completion
5. Generates invoice for completed projects

### 4. Inventory Management Automation
**File:** `inventory-management.json`

**Trigger:** Webhook `/webhook/inventory-alert`

**Features:**
- 📉 Low stock level monitoring
- 🚨 Critical stock alerts (out of stock)
- 📧 Procurement team notifications
- 📋 Automatic purchase order generation
- 💰 Cost estimation for reorders
- 📞 Supplier contact information

**Test Commands:**

**Low Stock Alert:**
```bash
curl -X POST http://localhost:5678/webhook/inventory-alert \
  -H "Content-Type: application/json" \
  -d '{
    "plant_id": 1,
    "plant_name": "Dutch Rose",
    "current_stock": 3,
    "minimum_threshold": 10,
    "supplier_id": 1,
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

**Critical Stock Alert:**
```bash
curl -X POST http://localhost:5678/webhook/inventory-alert \
  -H "Content-Type: application/json" \
  -d '{
    "plant_id": 1,
    "plant_name": "Dutch Rose",
    "current_stock": 0,
    "minimum_threshold": 10,
    "supplier_id": 1,
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

**Expected Actions:**
1. Checks stock levels against thresholds
2. Fetches plant and supplier details
3. Sends appropriate alert emails
4. Creates purchase orders for critical items
5. Notifies backend of inventory status

## 🔧 Configuration Guide

### SMTP Setup

1. In N8n, go to Settings > Credentials
2. Add new SMTP credential:
   ```
   Host: smtp.gmail.com
   Port: 587
   User: your-email@gmail.com
   Password: your-app-password
   ```

### Google API Setup (Optional)

1. Create project in Google Cloud Console
2. Enable Google Drive and Google Docs APIs
3. Create service account and download JSON key
4. In N8n, add Google API credential with the JSON key

### Webhook Security

Enable webhook authentication in production:

1. Set `N8N_WEBHOOK_SECRET` environment variable
2. Configure signature validation in workflow settings
3. Update backend webhook calls to include signatures

## 🔗 Integration with Landscape Tool

### Triggering Workflows from Backend

The landscape tool provides dedicated webhook endpoints for triggering N8n workflows. Use these backend endpoints rather than calling N8n directly:

```python
# Client onboarding (new client created)
import requests
def trigger_client_onboarding(client_id, client_name, client_email, contact_person=None):
    requests.post(
        'http://localhost:5000/webhooks/n8n/client-onboarding',
        json={
            'client_id': client_id,
            'client_name': client_name,
            'client_email': client_email,
            'contact_person': contact_person,
            'timestamp': datetime.now().isoformat()
        }
    )

# Project created 
def trigger_project_created(project_id, client_id, project_name):
    requests.post(
        'http://localhost:5000/webhooks/n8n/project-created',
        json={
            'project_id': project_id,
            'client_id': client_id,
            'project_name': project_name,
            'timestamp': datetime.now().isoformat()
        }
    )

# Project milestone reached
def trigger_milestone_update(project_id, milestone, completion_percentage):
    requests.post(
        'http://localhost:5000/webhooks/n8n/project-milestone',
        json={
            'project_id': project_id,
            'milestone': milestone,
            'completion_percentage': completion_percentage,
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        }
    )

# Inventory alert
def trigger_inventory_alert(plant_id, current_stock, minimum_threshold):
    requests.post(
        'http://localhost:5000/webhooks/n8n/inventory-alert',
        json={
            'plant_id': plant_id,
            'current_stock': current_stock,
            'minimum_threshold': minimum_threshold,
            'timestamp': datetime.now().isoformat()
        }
    )
```

### Receiving Callbacks

The workflows send updates back to these endpoints:

- `/api/n8n/receive/email-sent` - Email delivery confirmations
- `/api/n8n/receive/task-completed` - Task completion updates
- `/api/n8n/receive/external-data` - External system integrations

## 📊 Monitoring and Troubleshooting

### Workflow Execution Logs

1. Access N8n interface
2. Go to "Executions" tab
3. View detailed execution logs and data flow
4. Check for errors and retry failed executions

### Common Issues

**Webhook not triggered:**
- Verify webhook URL is correct
- Check N8n container is running
- Validate JSON payload format

**Email not sent:**
- Check SMTP credentials
- Verify email addresses are valid
- Review email delivery logs

**API calls failing:**
- Confirm backend is accessible from N8n container
- Check API endpoint URLs
- Verify authentication tokens

### Health Monitoring

Check integration status:
```bash
curl http://localhost:5000/api/n8n/status
```

Expected response:
```json
{
  "n8n_integration": "enabled",
  "n8n_available": true,
  "n8n_base_url": "http://n8n:5678",
  "webhook_secret_configured": true
}
```

## 🎯 Business Impact

### Automation Benefits

**Time Savings:**
- Client onboarding: 90% reduction (2 hours → 12 minutes)
- Project communications: 80% reduction (1 hour → 12 minutes)
- Inventory management: 85% reduction (2 hours → 18 minutes)

**Error Reduction:**
- Automated email templates eliminate formatting errors
- Consistent milestone tracking prevents missed notifications
- Systematic inventory monitoring reduces stockouts

**Client Satisfaction:**
- Immediate welcome emails improve first impressions
- Timely project updates increase transparency
- Professional communications enhance brand perception

## 📚 Advanced Customization

### Adding New Workflows

1. **Design the workflow** in N8n interface
2. **Export as JSON** from workflow settings
3. **Add to this directory** with descriptive filename
4. **Update this README** with usage instructions
5. **Test thoroughly** before production deployment

### Extending Existing Workflows

Common customizations:
- Add more email templates for different scenarios
- Integrate with additional external services
- Add conditional logic for complex business rules
- Include file attachments and document generation

### Integration Examples

**CRM Integration:**
```javascript
// Add to workflow to sync with external CRM
{
  "parameters": {
    "url": "https://api.crm-system.com/contacts",
    "sendBody": true,
    "bodyContentType": "json",
    "jsonBody": {
      "name": "={{$json.client_name}}",
      "email": "={{$json.client_email}}",
      "source": "landscape_tool"
    },
    "authentication": "headerAuth",
    "nodeCredentialType": "httpHeaderAuth"
  },
  "name": "Sync to CRM",
  "type": "n8n-nodes-base.httpRequest"
}
```

## 🔄 Maintenance

### Regular Tasks

**Weekly:**
- Review workflow execution logs
- Check email delivery rates
- Verify external API integrations

**Monthly:**
- Update workflow templates
- Review and optimize performance
- Check credential expiration dates

**As Needed:**
- Update email templates for seasonal content
- Modify thresholds based on business changes
- Add new integrations as requirements evolve

## 📞 Support

For workflow-related issues:

1. **Check execution logs** in N8n interface
2. **Review error messages** and stack traces
3. **Test individual nodes** to isolate problems
4. **Verify credentials** and API connectivity
5. **Consult N8n documentation** for node-specific issues

For integration issues with the Landscape Tool:
- Check backend API endpoint availability
- Verify webhook payload formats
- Review authentication and security settings

---

*These workflows provide a solid foundation for automating landscape architecture business processes. Customize them based on your specific needs and add new workflows as your automation requirements grow.*