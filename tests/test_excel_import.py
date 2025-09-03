import pytest
import io
import tempfile
import pandas as pd
from tests.fixtures.database import DatabaseTestMixin

@pytest.mark.api
class TestExcelImport(DatabaseTestMixin):
    """Test Excel import functionality"""

    def test_get_import_status(self, client, app_context):
        """Test getting import status"""
        response = client.get('/api/import/status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'current_counts' in data
        assert 'import_types' in data
        assert 'supported_formats' in data
        assert 'max_file_size' in data
        
        # Check import types
        expected_types = ['suppliers', 'plants', 'products', 'clients']
        assert data['import_types'] == expected_types
        
        # Check supported formats
        expected_formats = {'csv', 'xls', 'xlsx'}
        assert set(data['supported_formats']) == expected_formats

    def test_download_suppliers_template(self, client, app_context):
        """Test downloading Excel template for suppliers"""
        response = client.get('/api/import/template/suppliers')
        assert response.status_code == 200
        
        # Check headers
        assert response.headers['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert 'suppliers_import_template.xlsx' in response.headers['Content-Disposition']

    def test_download_plants_template(self, client, app_context):
        """Test downloading Excel template for plants"""
        response = client.get('/api/import/template/plants')
        assert response.status_code == 200
        
        # Check headers
        assert response.headers['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert 'plants_import_template.xlsx' in response.headers['Content-Disposition']

    def test_download_invalid_template(self, client, app_context):
        """Test downloading template for invalid type"""
        response = client.get('/api/import/template/invalid_type')
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data

    def test_validate_empty_file_upload(self, client, app_context):
        """Test validation with no file uploaded"""
        response = client.post('/api/import/validate-file', data={
            'type': 'suppliers'
        })
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert 'Geen bestand geselecteerd' in data['error']

    def test_validate_invalid_file_type(self, client, app_context):
        """Test validation with invalid file type"""
        # Create a text file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'Invalid content')
            tmp.flush()
            
            with open(tmp.name, 'rb') as f:
                response = client.post('/api/import/validate-file', data={
                    'type': 'suppliers',
                    'file': (f, 'test.txt')
                })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Ongeldig bestandsformaat' in data['error']

    def test_validate_valid_suppliers_csv(self, client, app_context):
        """Test validation with valid suppliers CSV"""
        # Create valid CSV content
        csv_content = """name,contact_person,email,phone,address,city,postal_code,country
Test Supplier,Jan Test,test@example.com,+31 20 1234567,Test Street 1,Amsterdam,1000 AB,Nederland
Another Supplier,Marie Test,marie@example.com,+31 30 9876543,Another Street 2,Utrecht,3000 CD,Nederland"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post('/api/import/validate-file', data={
            'type': 'suppliers',
            'file': (csv_file, 'suppliers.csv')
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['valid'] == True
        assert data['total_rows'] == 2
        assert len(data['missing_columns']) == 0
        assert len(data['sample_data']) == 2
        assert data['sample_data'][0]['name'] == 'Test Supplier'

    def test_validate_suppliers_csv_missing_columns(self, client, app_context):
        """Test validation with missing required columns"""
        # Create CSV with missing columns
        csv_content = """name,email
Test Supplier,test@example.com
Another Supplier,marie@example.com"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post('/api/import/validate-file', data={
            'type': 'suppliers',
            'file': (csv_file, 'suppliers.csv')
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['valid'] == False
        assert len(data['missing_columns']) > 0
        assert 'contact_person' in data['missing_columns']
        assert 'phone' in data['missing_columns']

    def test_validate_plants_csv_with_invalid_supplier_id(self, client, app_context):
        """Test validation with invalid supplier IDs"""
        # Create CSV with invalid supplier ID
        csv_content = """name,common_name,category,sun_requirements,water_needs,hardiness_zone,height_max,width_max,bloom_time,bloom_color,maintenance,supplier_id
Test Plant,Test Common,Tree,Sun,Low,5,10.0,8.0,Spring,White,Low,99999"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post('/api/import/validate-file', data={
            'type': 'plants',
            'file': (csv_file, 'plants.csv')
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Should have recommendations about missing supplier IDs
        assert len(data['recommendations']) > 0
        assert any('Leverancier IDs niet gevonden' in rec for rec in data['recommendations'])

    def test_process_import_without_validation(self, client, app_context):
        """Test processing import without prior validation"""
        response = client.post('/api/import/process', data={
            'type': 'suppliers'
        })
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data

    def test_process_import_invalid_file(self, client, app_context):
        """Test processing import with invalid file"""
        # Create invalid CSV
        csv_content = """name
Test Supplier Without Required Fields"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post('/api/import/process', data={
            'type': 'suppliers',
            'file': (csv_file, 'suppliers.csv'),
            'update_existing': 'false'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'validatie gefaald' in data['error']

    def test_process_suppliers_import_success(self, client, app_context):
        """Test successful suppliers import"""
        # Create valid CSV content
        csv_content = """name,contact_person,email,phone,address,city,postal_code,country
Import Test Supplier,Jan Import,import@test.com,+31 20 1111111,Import Street 1,Amsterdam,1100 AB,Nederland"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post('/api/import/process', data={
            'type': 'suppliers',
            'file': (csv_file, 'suppliers.csv'),
            'update_existing': 'false'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] == True
        assert data['total_rows'] == 1
        assert data['successful_imports'] == 1
        assert data['failed_imports'] == 0

    def test_process_products_import_with_missing_supplier(self, client, app_context):
        """Test products import with non-existent supplier ID"""
        # Create CSV with non-existent supplier ID
        csv_content = """name,category,description,price,unit,supplier_id
Test Product,Test Category,Test Description,10.50,piece,99999"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post('/api/import/process', data={
            'type': 'products',
            'file': (csv_file, 'products.csv'),
            'update_existing': 'false'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Should have some failures due to missing supplier
        assert data['failed_imports'] > 0
        assert len(data['errors']) > 0

    def test_process_clients_import_success(self, client, app_context):
        """Test successful clients import"""
        csv_content = """name,email,phone,address,city,postal_code,country,client_type
Import Test Client,client@test.com,+31 6 12345678,Client Street 1,Utrecht,3300 AB,Nederland,Particulier"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post('/api/import/process', data={
            'type': 'clients',
            'file': (csv_file, 'clients.csv'),
            'update_existing': 'false'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] == True
        assert data['total_rows'] == 1
        assert data['successful_imports'] == 1

    def test_process_import_with_update_existing(self, client, app_context):
        """Test import with update existing option"""
        # First import
        csv_content = """name,contact_person,email,phone,address,city,postal_code,country
Update Test Supplier,Jan Update,update@test.com,+31 20 2222222,Update Street 1,Amsterdam,1200 AB,Nederland"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        # First import
        response = client.post('/api/import/process', data={
            'type': 'suppliers',
            'file': (csv_file, 'suppliers.csv'),
            'update_existing': 'false'
        })
        
        assert response.status_code == 200
        first_data = response.get_json()
        assert first_data['successful_imports'] == 1
        
        # Second import with update
        csv_content_updated = """name,contact_person,email,phone,address,city,postal_code,country
Update Test Supplier,Jane Updated,update@test.com,+31 20 3333333,Updated Street 2,Rotterdam,3000 AB,Nederland"""
        
        csv_file_updated = io.BytesIO(csv_content_updated.encode('utf-8'))
        
        response = client.post('/api/import/process', data={
            'type': 'suppliers',
            'file': (csv_file_updated, 'suppliers_updated.csv'),
            'update_existing': 'true'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] == True
        assert data['updated_records'] == 1
        assert data['successful_imports'] == 0  # No new records, only updated

    def test_large_file_recommendation(self, client, app_context):
        """Test that large files get appropriate recommendations"""
        # Create a large CSV (simulate with many rows)
        rows = ['Test Supplier ' + str(i) + ',Jan,test' + str(i) + '@example.com,+31 20 1234567,Street ' + str(i) + ',Amsterdam,1000 AB,Nederland' 
                for i in range(1500)]  # Simulate large file
        csv_content = 'name,contact_person,email,phone,address,city,postal_code,country\n' + '\n'.join(rows)
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        response = client.post('/api/import/validate-file', data={
            'type': 'suppliers',
            'file': (csv_file, 'large_suppliers.csv')
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Should recommend splitting large files
        assert any('Groot bestand gedetecteerd' in rec for rec in data['recommendations'])