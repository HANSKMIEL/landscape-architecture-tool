"""
Enhanced Vectorworks Integration Service
Provides comprehensive integration with Vectorworks 2024 for landscape architecture workflows.
"""

import json
import logging
import os
import subprocess
import tempfile
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class VectorworksProject:
    """Vectorworks project information"""
    file_path: str
    project_name: str
    last_modified: datetime
    layers: List[str]
    classes: List[str]
    plant_objects: List[Dict]
    material_objects: List[Dict]

@dataclass
class PlantObject:
    """Plant object in Vectorworks"""
    object_id: str
    name: str
    scientific_name: str
    quantity: int
    x_coordinate: float
    y_coordinate: float
    layer: str
    class_name: str
    symbol_name: str
    custom_data: Dict[str, Any]

@dataclass
class MaterialSpecification:
    """Material specification for Vectorworks"""
    material_id: str
    name: str
    category: str
    unit: str
    quantity: float
    unit_price: float
    supplier: str
    specifications: Dict[str, str]

class VectorworksSDKInterface:
    """Interface for Vectorworks SDK operations"""
    
    def __init__(self, vectorworks_path: str = None):
        self.vectorworks_path = vectorworks_path or self._find_vectorworks_installation()
        self.sdk_path = self._find_sdk_path()
        self.temp_dir = tempfile.mkdtemp(prefix="vw_integration_")
        
    def _find_vectorworks_installation(self) -> str:
        """Find Vectorworks installation path"""
        common_paths = [
            r"C:\Program Files\Vectorworks 2024",
            r"C:\Program Files (x86)\Vectorworks 2024",
            "/Applications/Vectorworks 2024",
            "/opt/vectorworks2024"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        logger.warning("Vectorworks installation not found in common paths")
        return ""
    
    def _find_sdk_path(self) -> str:
        """Find Vectorworks SDK path"""
        if self.vectorworks_path:
            sdk_path = os.path.join(self.vectorworks_path, "SDK")
            if os.path.exists(sdk_path):
                return sdk_path
        return ""
    
    def is_available(self) -> bool:
        """Check if Vectorworks SDK is available"""
        return bool(self.vectorworks_path and self.sdk_path)

class VectorworksDataExtractor:
    """Extract data from Vectorworks files"""
    
    def __init__(self, sdk_interface: VectorworksSDKInterface):
        self.sdk = sdk_interface
        
    def extract_project_info(self, vwx_file_path: str) -> VectorworksProject:
        """Extract project information from Vectorworks file"""
        try:
            # Generate extraction script
            script_content = self._generate_extraction_script(vwx_file_path)
            script_path = os.path.join(self.sdk.temp_dir, "extract_data.vss")
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Execute script via Vectorworks
            result = self._execute_vectorscript(script_path, vwx_file_path)
            
            if result:
                return self._parse_extraction_result(result)
            
        except Exception as e:
            logger.error(f"Error extracting project info: {e}")
        
        return VectorworksProject(
            file_path=vwx_file_path,
            project_name=Path(vwx_file_path).stem,
            last_modified=datetime.now(),
            layers=[],
            classes=[],
            plant_objects=[],
            material_objects=[]
        )
    
    def _generate_extraction_script(self, vwx_file_path: str) -> str:
        """Generate Vectorscript for data extraction"""
        # Define output filename as constant to avoid duplication
        OUTPUT_FILENAME = "extraction_output.json"
        output_path = f"{self.sdk.temp_dir}/{OUTPUT_FILENAME}"
        
        return f"""
        {{ Vectorscript for extracting landscape architecture data }}
        PROCEDURE ExtractLandscapeData;
        VAR
            h: HANDLE;
            layerName: STRING;
            className: STRING;
            objName: STRING;
            objType: INTEGER;
            x, y: REAL;
            recordHandle: HANDLE;
            fieldValue: STRING;
            outputFile: STRING;
            
        BEGIN
            outputFile := '{output_path}';
            
            {{ Initialize JSON output }}
            WriteToFile(outputFile, '{{"layers": [');
            
            {{ Extract layer information }}
            h := FLayer;
            WHILE h <> NIL DO BEGIN
                layerName := GetLName(h);
                WriteToFile(outputFile, Concat('"', layerName, '",'));
                h := NextLayer(h);
            END;
            
            WriteToFile(outputFile, '], "classes": [');
            
            {{ Extract class information }}
            h := FClass;
            WHILE h <> NIL DO BEGIN
                className := GetName(h);
                WriteToFile(outputFile, Concat('"', className, '",'));
                h := NextClass(h);
            END;
            
            WriteToFile(outputFile, '], "objects": [');
            
            {{ Extract plant and material objects }}
            h := FSActLayer;
            WHILE h <> NIL DO BEGIN
                objType := GetType(h);
                objName := GetName(h);
                
                {{ Check if object is a plant symbol or material }}
                IF (objType = 86) OR (objType = 15) THEN BEGIN {{ Symbol or Group }}
                    GetSymLoc(h, x, y);
                    
                    WriteToFile(outputFile, '{');
                    WriteToFile(outputFile, Concat('"name": "', objName, '",'));
                    WriteToFile(outputFile, Concat('"type": ', Num2Str(0, objType), ','));
                    WriteToFile(outputFile, Concat('"x": ', Num2Str(2, x), ','));
                    WriteToFile(outputFile, Concat('"y": ', Num2Str(2, y), ','));
                    WriteToFile(outputFile, Concat('"layer": "', GetLName(GetLayer(h)), '",'));
                    WriteToFile(outputFile, Concat('"class": "', GetClass(h), '"'));
                    
                    {{ Extract custom data from records }}
                    recordHandle := GetRecord(h, 1);
                    IF recordHandle <> NIL THEN BEGIN
                        WriteToFile(outputFile, ', "data": {');
                        {{ Add record field extraction here }}
                        WriteToFile(outputFile, '}');
                    END;
                    
                    WriteToFile(outputFile, '},');
                END;
                
                h := NextSObj(h);
            END;
            
            WriteToFile(outputFile, ']}');
            
        END;
        
        RUN(ExtractLandscapeData);
        """
    
    def _execute_vectorscript(self, script_path: str, vwx_file_path: str) -> Optional[Dict]:
        """Execute Vectorscript and return results"""
        if not self.sdk.is_available():
            logger.warning("Vectorworks SDK not available, using mock data")
            return self._generate_mock_data()
        
        try:
            # Command to execute Vectorworks with script
            cmd = [
                os.path.join(self.sdk.vectorworks_path, "Vectorworks.exe"),
                "-script", script_path,
                "-file", vwx_file_path,
                "-batch"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                OUTPUT_FILENAME = "extraction_output.json"
                output_file = os.path.join(self.sdk.temp_dir, OUTPUT_FILENAME)
                if os.path.exists(output_file):
                    with open(output_file, 'r') as f:
                        return json.load(f)
            else:
                logger.error(f"Vectorscript execution failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("Vectorscript execution timed out")
        except Exception as e:
            logger.error(f"Error executing Vectorscript: {e}")
        
        return None
    
    def _generate_mock_data(self) -> Dict:
        """Generate mock data for testing when Vectorworks is not available"""
        return {
            "layers": ["Site Plan", "Planting Plan", "Hardscape", "Utilities"],
            "classes": ["Trees", "Shrubs", "Perennials", "Hardscape", "Irrigation"],
            "objects": [
                {
                    "name": "Acer platanoides",
                    "type": 86,
                    "x": 10.5,
                    "y": 15.2,
                    "layer": "Planting Plan",
                    "class": "Trees",
                    "data": {
                        "quantity": "3",
                        "size": "8-10cm caliper",
                        "supplier": "Local Nursery"
                    }
                },
                {
                    "name": "Buxus sempervirens",
                    "type": 86,
                    "x": 5.0,
                    "y": 8.0,
                    "layer": "Planting Plan",
                    "class": "Shrubs",
                    "data": {
                        "quantity": "25",
                        "size": "30-40cm",
                        "supplier": "Hedge Specialists"
                    }
                }
            ]
        }
    
    def _parse_extraction_result(self, result: Dict) -> VectorworksProject:
        """Parse extraction result into VectorworksProject"""
        plant_objects = []
        material_objects = []
        
        for obj in result.get("objects", []):
            if obj.get("class") in ["Trees", "Shrubs", "Perennials", "Grasses"]:
                plant_objects.append(obj)
            elif obj.get("class") in ["Hardscape", "Materials", "Irrigation"]:
                material_objects.append(obj)
        
        return VectorworksProject(
            file_path="",
            project_name="Extracted Project",
            last_modified=datetime.now(),
            layers=result.get("layers", []),
            classes=result.get("classes", []),
            plant_objects=plant_objects,
            material_objects=material_objects
        )

class VectorworksDataExporter:
    """Export data to Vectorworks format"""
    
    def __init__(self, sdk_interface: VectorworksSDKInterface):
        self.sdk = sdk_interface
    
    def export_plant_list(self, plants: List[Dict], output_path: str) -> bool:
        """Export plant list to Vectorworks-compatible format"""
        try:
            # Generate Vectorscript for plant placement
            script_content = self._generate_plant_placement_script(plants)
            script_path = os.path.join(self.sdk.temp_dir, "place_plants.vss")
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Also create CSV for manual import
            csv_path = output_path.replace('.vwx', '_plants.csv')
            self._export_plants_csv(plants, csv_path)
            
            logger.info(f"Plant list exported to {csv_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting plant list: {e}")
            return False
    
    def _generate_plant_placement_script(self, plants: List[Dict]) -> str:
        """Generate Vectorscript for automated plant placement"""
        script_lines = [
            "{ Automated Plant Placement Script }",
            "PROCEDURE PlacePlants;",
            "VAR",
            "    h: HANDLE;",
            "    x, y: REAL;",
            "    symbolName: STRING;",
            "BEGIN"
        ]
        
        for i, plant in enumerate(plants):
            x = plant.get('x_coordinate', 0)
            y = plant.get('y_coordinate', 0)
            symbol_name = plant.get('symbol_name', plant.get('name', 'Plant'))
            
            script_lines.extend([
                f"    {{ Place {plant.get('name', 'Plant')} }}",
                f"    symbolName := '{symbol_name}';",
                f"    x := {x};",
                f"    y := {y};",
                f"    h := CreateSymbol(symbolName, x, y, 0);",
                f"    IF h <> NIL THEN BEGIN",
                f"        SetClass(h, '{plant.get('class_name', 'Plants')}');",
                f"        SetLayer(h, '{plant.get('layer', 'Planting Plan')}');",
                f"    END;",
                ""
            ])
        
        script_lines.extend([
            "END;",
            "",
            "RUN(PlacePlants);"
        ])
        
        return "\n".join(script_lines)
    
    def _export_plants_csv(self, plants: List[Dict], csv_path: str) -> None:
        """Export plants to CSV format for manual import"""
        import csv
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Name', 'Scientific_Name', 'Quantity', 'Size', 'Unit_Price',
                'Total_Price', 'Supplier', 'X_Coordinate', 'Y_Coordinate',
                'Layer', 'Class', 'Notes'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for plant in plants:
                writer.writerow({
                    'Name': plant.get('name', ''),
                    'Scientific_Name': plant.get('scientific_name', ''),
                    'Quantity': plant.get('quantity', 1),
                    'Size': plant.get('size', ''),
                    'Unit_Price': plant.get('unit_price', 0),
                    'Total_Price': plant.get('total_price', 0),
                    'Supplier': plant.get('supplier', ''),
                    'X_Coordinate': plant.get('x_coordinate', 0),
                    'Y_Coordinate': plant.get('y_coordinate', 0),
                    'Layer': plant.get('layer', 'Planting Plan'),
                    'Class': plant.get('class_name', 'Plants'),
                    'Notes': plant.get('notes', '')
                })

class VectorworksReportGenerator:
    """Generate professional reports for Vectorworks projects"""
    
    def __init__(self, sdk_interface: VectorworksSDKInterface):
        self.sdk = sdk_interface
    
    def generate_plant_schedule(self, project: VectorworksProject, 
                              output_path: str, language: str = "nl") -> bool:
        """Generate professional plant schedule report"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import cm
            
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            
            title_text = "Plantenlijst" if language == "nl" else "Plant Schedule"
            story.append(Paragraph(title_text, title_style))
            story.append(Spacer(1, 20))
            
            # Project information
            project_info = [
                ["Project:", project.project_name],
                ["Datum:", datetime.now().strftime("%d-%m-%Y")],
                ["Bestand:", os.path.basename(project.file_path)]
            ]
            
            project_table = Table(project_info, colWidths=[4*cm, 10*cm])
            project_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(project_table)
            story.append(Spacer(1, 30))
            
            # Plant schedule table
            if language == "nl":
                headers = ["Naam", "Wetenschappelijke naam", "Aantal", "Maat", "Prijs/st", "Totaal", "Leverancier"]
            else:
                headers = ["Name", "Scientific Name", "Quantity", "Size", "Unit Price", "Total", "Supplier"]
            
            data = [headers]
            total_cost = 0
            
            for plant_obj in project.plant_objects:
                plant_data = plant_obj.get('data', {})
                quantity = int(plant_data.get('quantity', 1))
                unit_price = float(plant_data.get('unit_price', 0))
                total_price = quantity * unit_price
                total_cost += total_price
                
                row = [
                    plant_obj.get('name', ''),
                    plant_data.get('scientific_name', ''),
                    str(quantity),
                    plant_data.get('size', ''),
                    f"€{unit_price:.2f}",
                    f"€{total_price:.2f}",
                    plant_data.get('supplier', '')
                ]
                data.append(row)
            
            # Add total row
            total_label = "Totaal:" if language == "nl" else "Total:"
            data.append(['', '', '', '', '', f"€{total_cost:.2f}", total_label])
            
            table = Table(data, colWidths=[3*cm, 4*cm, 1.5*cm, 2*cm, 2*cm, 2*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ]))
            
            story.append(table)
            
            # Build PDF
            doc.build(story)
            logger.info(f"Plant schedule generated: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating plant schedule: {e}")
            return False

class VectorworksIntegrationService:
    """Main service for Vectorworks integration"""
    
    def __init__(self, vectorworks_path: str = None):
        self.sdk = VectorworksSDKInterface(vectorworks_path)
        self.extractor = VectorworksDataExtractor(self.sdk)
        self.exporter = VectorworksDataExporter(self.sdk)
        self.report_generator = VectorworksReportGenerator(self.sdk)
    
    def import_project_data(self, vwx_file_path: str) -> VectorworksProject:
        """Import data from Vectorworks project file"""
        return self.extractor.extract_project_info(vwx_file_path)
    
    def export_plant_data(self, plants: List[Dict], output_path: str) -> bool:
        """Export plant data to Vectorworks format"""
        return self.exporter.export_plant_list(plants, output_path)
    
    def generate_reports(self, project: VectorworksProject, 
                        output_dir: str, language: str = "nl") -> List[str]:
        """Generate all project reports"""
        generated_files = []
        
        # Plant schedule
        plant_schedule_path = os.path.join(output_dir, "plant_schedule.pdf")
        if self.report_generator.generate_plant_schedule(project, plant_schedule_path, language):
            generated_files.append(plant_schedule_path)
        
        return generated_files
    
    def sync_project_data(self, project_id: int, vwx_file_path: str) -> Dict:
        """Synchronize project data between database and Vectorworks"""
        try:
            # Import current Vectorworks data
            vw_project = self.import_project_data(vwx_file_path)
            
            # Update database with Vectorworks data
            # This would integrate with your existing database models
            
            # Export updated data back to Vectorworks
            # This would use your plant recommendation data
            
            return {
                "success": True,
                "imported_plants": len(vw_project.plant_objects),
                "imported_materials": len(vw_project.material_objects),
                "layers": vw_project.layers,
                "classes": vw_project.classes
            }
            
        except Exception as e:
            logger.error(f"Error syncing project data: {e}")
            return {"success": False, "error": str(e)}

# Factory function
def create_vectorworks_service(vectorworks_path: str = None) -> VectorworksIntegrationService:
    """Create Vectorworks integration service"""
    return VectorworksIntegrationService(vectorworks_path)
