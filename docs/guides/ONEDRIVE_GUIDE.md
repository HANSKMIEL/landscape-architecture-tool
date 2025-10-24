# OneDrive Integration Guide

This guide provides comprehensive instructions for integrating Microsoft OneDrive with the Landscape Architecture Tool for cloud storage, backup, and collaboration features.

## 🌐 Overview

OneDrive integration enables:
- **Cloud Backup** - Automatic backup of project files and databases
- **File Sharing** - Share landscape plans and documents with clients
- **Collaboration** - Real-time collaboration on project documents
- **Cross-Device Sync** - Access your work from any device
- **Version Control** - Track changes to project files

## 🔧 Prerequisites

Before setting up OneDrive integration:

1. **Microsoft Account**: Valid Microsoft 365 or OneDrive account
2. **API Access**: Microsoft Graph API access (free tier available)
3. **Application Registration**: Azure AD app registration
4. **Storage Plan**: Sufficient OneDrive storage for your projects

## 📱 Setup Options

### Option 1: Basic OneDrive Sync (Recommended for Individual Use)

This setup syncs your project directory with OneDrive for basic backup and access.

#### 1. Install OneDrive Client

**Windows (Built-in):**
- OneDrive is pre-installed on Windows 10/11
- Sign in with your Microsoft account

**macOS:**
```bash
# Download from Mac App Store or Microsoft website
# Or install via Homebrew
brew install --cask onedrive
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install onedrive

# CentOS/RHEL
sudo yum install onedrive

# Arch Linux
sudo pacman -S onedrive
```

#### 2. Configure OneDrive Sync

1. **Create Project Directory in OneDrive**
   ```bash
   mkdir ~/OneDrive/LandscapeArchitectureTool
   cd ~/OneDrive/LandscapeArchitectureTool
   ```

2. **Clone Repository to OneDrive**
   ```bash
   git clone https://github.com/HANSKMIEL/landscape-architecture-tool.git
   cd landscape-architecture-tool
   ```

3. **Configure Selective Sync**
   - Exclude large directories from sync:
     - `node_modules/`
     - `__pycache__/`
     - `.git/` (optional)
     - `dist/`
     - `logs/`

#### 3. Set Up .onedriveignore

Create a `.onedriveignore` file to exclude unnecessary files:

```
# Dependencies
node_modules/
venv/
env/

# Build outputs
dist/
build/
frontend/dist/

# Cache and logs
__pycache__/
.pytest_cache/
*.log
logs/

# Database files (optional - backup separately)
*.db
*.sqlite

# Environment files with secrets
.env
.env.local
.env.production

# Git files (optional)
.git/

# IDE files
.vscode/settings.json
.idea/

# OS files
.DS_Store
Thumbs.db
```

### Option 2: Advanced OneDrive Integration (Enterprise/Team Use)

This setup provides full API integration for automated backup, file sharing, and collaboration.

#### 1. Azure AD App Registration

1. **Go to Azure Portal**
   - Visit [Azure Portal](https://portal.azure.com)
   - Navigate to "Azure Active Directory" > "App registrations"

2. **Create New Registration**
   ```
   Name: Landscape Architecture Tool
   Supported account types: Single tenant
   Redirect URI: http://localhost:5000/auth/callback
   ```

3. **Configure API Permissions**
   - Microsoft Graph > Application permissions:
     - `Files.Read.All`
     - `Files.ReadWrite.All`
     - `Sites.Read.All`
     - `Sites.ReadWrite.All`
   - Grant admin consent

4. **Create Client Secret**
   - Go to "Certificates & secrets"
   - Create new client secret
   - Copy the value immediately

#### 2. Environment Configuration

Add OneDrive configuration to your `.env` file:

```bash
# OneDrive Integration
ONEDRIVE_ENABLED=true
AZURE_CLIENT_ID=your-azure-client-id
AZURE_CLIENT_SECRET=your-azure-client-secret
AZURE_TENANT_ID=your-azure-tenant-id
ONEDRIVE_REDIRECT_URI=http://localhost:5000/auth/callback

# OneDrive Settings
ONEDRIVE_BACKUP_ENABLED=true
ONEDRIVE_BACKUP_INTERVAL=daily
ONEDRIVE_PROJECT_FOLDER=LandscapeArchitectureTool
ONEDRIVE_BACKUP_FOLDER=Backups

# File Sharing
ONEDRIVE_SHARING_ENABLED=true
ONEDRIVE_DEFAULT_PERMISSIONS=read
```

#### 3. Install Additional Dependencies

Add OneDrive-specific dependencies to `requirements.txt`:

```bash
# OneDrive integration
msal==1.24.0
msgraph-core==0.2.2
azure-identity==1.15.0
azure-storage-file-datalake==12.14.0
```

Install the dependencies:
```bash
pip install -r requirements.txt
```

#### 4. OneDrive Service Implementation

Create `src/services/onedrive_service.py`:

```python
import os
import msal
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from datetime import datetime, timedelta
import json
import zipfile
import tempfile

class OneDriveService:
    def __init__(self):
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.tenant_id = os.getenv('AZURE_TENANT_ID')
        self.enabled = os.getenv('ONEDRIVE_ENABLED', 'false').lower() == 'true'
        
        if self.enabled:
            self.credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            self.graph_client = GraphServiceClient(
                credentials=self.credential,
                scopes=['https://graph.microsoft.com/.default']
            )
    
    async def upload_file(self, file_path, onedrive_path):
        """Upload a file to OneDrive"""
        if not self.enabled:
            return False
            
        try:
            with open(file_path, 'rb') as file:
                await self.graph_client.me.drive.root.item_with_path(
                    onedrive_path
                ).content.put(file.read())
            return True
        except Exception as e:
            print(f"OneDrive upload error: {e}")
            return False
    
    async def download_file(self, onedrive_path, local_path):
        """Download a file from OneDrive"""
        if not self.enabled:
            return False
            
        try:
            content = await self.graph_client.me.drive.root.item_with_path(
                onedrive_path
            ).content.get()
            
            with open(local_path, 'wb') as file:
                file.write(content)
            return True
        except Exception as e:
            print(f"OneDrive download error: {e}")
            return False
    
    async def create_backup(self):
        """Create a backup of the application"""
        if not self.enabled:
            return False
            
        try:
            backup_name = f"landscape_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
                with zipfile.ZipFile(tmp_file.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # Add database
                    if os.path.exists('landscape_architecture.db'):
                        zip_file.write('landscape_architecture.db')
                    
                    # Add configuration files
                    for config_file in ['.env.example', 'requirements.txt']:
                        if os.path.exists(config_file):
                            zip_file.write(config_file)
                    
                    # Add key source files
                    for root, dirs, files in os.walk('src'):
                        # Skip __pycache__
                        dirs[:] = [d for d in dirs if d != '__pycache__']
                        
                        for file in files:
                            if file.endswith('.py'):
                                file_path = os.path.join(root, file)
                                zip_file.write(file_path)
                
                # Upload backup to OneDrive
                backup_path = f"Backups/{backup_name}"
                return await self.upload_file(tmp_file.name, backup_path)
                
        except Exception as e:
            print(f"Backup creation error: {e}")
            return False
    
    async def share_file(self, onedrive_path, permission_type='read'):
        """Create a sharing link for a file"""
        if not self.enabled:
            return None
            
        try:
            sharing_link = await self.graph_client.me.drive.root.item_with_path(
                onedrive_path
            ).create_link.post({
                "type": "view" if permission_type == 'read' else "edit",
                "scope": "anonymous"
            })
            
            return sharing_link.link.web_url
        except Exception as e:
            print(f"File sharing error: {e}")
            return None
```

#### 5. Add OneDrive Routes

Create `src/routes/onedrive.py`:

```python
from flask import Blueprint, request, jsonify, current_app
from src.services.onedrive_service import OneDriveService
import asyncio

onedrive_bp = Blueprint('onedrive', __name__)
onedrive_service = OneDriveService()

@onedrive_bp.route('/api/onedrive/backup', methods=['POST'])
async def create_backup():
    """Create a backup and upload to OneDrive"""
    try:
        success = await onedrive_service.create_backup()
        if success:
            return jsonify({'message': 'Backup created successfully'}), 200
        else:
            return jsonify({'error': 'Backup creation failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@onedrive_bp.route('/api/onedrive/share', methods=['POST'])
async def share_file():
    """Create a sharing link for a file"""
    data = request.get_json()
    file_path = data.get('file_path')
    permission = data.get('permission', 'read')
    
    if not file_path:
        return jsonify({'error': 'File path required'}), 400
    
    try:
        share_link = await onedrive_service.share_file(file_path, permission)
        if share_link:
            return jsonify({'share_link': share_link}), 200
        else:
            return jsonify({'error': 'File sharing failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@onedrive_bp.route('/api/onedrive/status', methods=['GET'])
def get_status():
    """Get OneDrive integration status"""
    return jsonify({
        'enabled': onedrive_service.enabled,
        'configured': bool(onedrive_service.client_id and onedrive_service.client_secret)
    })
```

## 🔄 Automated Backup Configuration

### 1. Scheduled Backups

Add to your cron jobs for automatic backups:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/landscape-architecture-tool && python -c "
import asyncio
from src.services.onedrive_service import OneDriveService
async def main():
    service = OneDriveService()
    await service.create_backup()
asyncio.run(main())
"
```

### 2. GitHub Actions Integration

Add to `.github/workflows/backup.yml`:

```yaml
name: OneDrive Backup

on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM
  workflow_dispatch:

jobs:
  backup:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Create OneDrive backup
      env:
        AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
        AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
        AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
        ONEDRIVE_ENABLED: true
      run: |
        python -c "
        import asyncio
        from src.services.onedrive_service import OneDriveService
        async def main():
            service = OneDriveService()
            success = await service.create_backup()
            print(f'Backup successful: {success}')
        asyncio.run(main())
        "
```

## 📁 File Organization

### Recommended OneDrive Structure

```
OneDrive/
└── LandscapeArchitectureTool/
    ├── Active-Projects/
    │   ├── Project-A/
    │   │   ├── plans/
    │   │   ├── documents/
    │   │   └── photos/
    │   └── Project-B/
    ├── Templates/
    │   ├── project-templates/
    │   ├── report-templates/
    │   └── plan-templates/
    ├── Backups/
    │   ├── daily/
    │   ├── weekly/
    │   └── monthly/
    ├── Shared/
    │   ├── client-files/
    │   └── public-resources/
    └── Archive/
        └── completed-projects/
```

## 🔗 Client Integration

### Frontend OneDrive Features

Add OneDrive features to your React frontend:

```javascript
// src/services/onedriveApi.js
export class OneDriveAPI {
  static async createBackup() {
    const response = await fetch('/api/onedrive/backup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    return response.json();
  }
  
  static async shareFile(filePath, permission = 'read') {
    const response = await fetch('/api/onedrive/share', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_path: filePath, permission })
    });
    return response.json();
  }
  
  static async getStatus() {
    const response = await fetch('/api/onedrive/status');
    return response.json();
  }
}
```

## 🔐 Security Best Practices

### 1. Client Secret Protection

- Store client secrets in environment variables
- Use Azure Key Vault for production
- Rotate secrets regularly
- Never commit secrets to version control

### 2. Permission Management

- Use least privilege principle
- Separate read/write permissions
- Regular permission audits
- User-specific access controls

### 3. Data Encryption

- Enable OneDrive encryption at rest
- Use HTTPS for all API calls
- Encrypt sensitive data before upload
- Regular security assessments

## 📊 Monitoring and Analytics

### OneDrive Usage Tracking

```python
class OneDriveAnalytics:
    def __init__(self):
        self.usage_stats = {
            'uploads': 0,
            'downloads': 0,
            'backups': 0,
            'shares': 0,
            'storage_used': 0
        }
    
    def track_upload(self, file_size):
        self.usage_stats['uploads'] += 1
        self.usage_stats['storage_used'] += file_size
    
    def track_download(self):
        self.usage_stats['downloads'] += 1
    
    def track_backup(self):
        self.usage_stats['backups'] += 1
    
    def track_share(self):
        self.usage_stats['shares'] += 1
    
    def get_report(self):
        return {
            'total_operations': sum(self.usage_stats.values()) - self.usage_stats['storage_used'],
            'storage_gb': self.usage_stats['storage_used'] / (1024**3),
            'breakdown': self.usage_stats
        }
```

## 🆘 Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Check credentials
   echo $AZURE_CLIENT_ID
   echo $AZURE_TENANT_ID
   # Client secret should not be echoed
   ```

2. **Permission Denied**
   - Verify API permissions in Azure AD
   - Check admin consent status
   - Validate redirect URI

3. **Upload Failures**
   - Check file size limits (250GB max)
   - Verify network connectivity
   - Check OneDrive storage quota

4. **Sync Issues**
   ```bash
   # Reset OneDrive sync
   onedrive --resync
   
   # Check sync status
   onedrive --display-config
   ```

### Diagnostic Commands

```bash
# Test OneDrive connectivity
python -c "
import asyncio
from src.services.onedrive_service import OneDriveService
async def test():
    service = OneDriveService()
    print(f'OneDrive enabled: {service.enabled}')
    if service.enabled:
        status = await service.graph_client.me.get()
        print(f'Connected as: {status.display_name}')
asyncio.run(test())
"
```

## 📞 Support

For OneDrive integration support:

1. **Microsoft Documentation**: [OneDrive Developer Center](https://docs.microsoft.com/en-us/onedrive/developer/)
2. **Azure Support**: [Azure Portal Support](https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade)
3. **Community**: [Microsoft Graph Community](https://docs.microsoft.com/en-us/graph/overview)
4. **Project Issues**: [GitHub Issues](https://github.com/HANSKMIEL/landscape-architecture-tool/issues)

## 🚀 Advanced Features

### Future Enhancements

- **Real-time Collaboration**: Live document editing
- **AI-Powered Organization**: Automatic file categorization
- **Version History**: Track document changes
- **Mobile App Integration**: OneDrive mobile access
- **Offline Sync**: Work without internet connection

### Integration with Other Services

- **SharePoint**: Team collaboration spaces
- **Microsoft Teams**: Chat and video integration
- **Power BI**: Analytics dashboards
- **Azure Functions**: Serverless processing

---

For more setup options, return to [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md)