"""
AI Data Mapping Service for Intelligent Excel Import

This service provides AI-powered data mapping functionality for Excel imports,
helping users automatically map columns to database fields and validate data.
"""

import openai
import json
import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
from src.utils.error_handlers import handle_business_logic_error

logger = logging.getLogger(__name__)

class AIDataMappingService:
    """AI-powered service for intelligent data mapping during Excel imports."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the AI data mapping service."""
        self.openai_api_key = openai_api_key
        if openai_api_key:
            openai.api_key = openai_api_key
    
    @handle_business_logic_error
    def suggest_column_mapping(
        self, 
        excel_columns: List[str], 
        target_schema: Dict[str, str],
        data_type: str = "suppliers"
    ) -> Dict[str, Dict[str, float]]:
        """
        Suggest mapping between Excel columns and database fields using AI.
        
        Args:
            excel_columns: List of column names from Excel file
            target_schema: Dict of field_name -> field_description for target schema
            data_type: Type of data being imported (suppliers, plants, products, clients)
            
        Returns:
            Dict mapping excel_column -> {field_name: confidence_score}
        """
        if not self.openai_api_key:
            return self._fallback_mapping(excel_columns, target_schema)
        
        try:
            # Create prompt for GPT
            prompt = self._create_mapping_prompt(excel_columns, target_schema, data_type)
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert data mapping assistant for Dutch landscape architecture business data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            # Parse AI response
            mapping_suggestions = self._parse_ai_response(response.choices[0].message.content)
            return mapping_suggestions
            
        except Exception as e:
            logger.warning(f"AI mapping failed, using fallback: {e}")
            return self._fallback_mapping(excel_columns, target_schema)
    
    @handle_business_logic_error
    def validate_data_quality(
        self, 
        data: pd.DataFrame, 
        column_mapping: Dict[str, str],
        data_type: str = "suppliers"
    ) -> Dict[str, List[str]]:
        """
        Use AI to validate data quality and suggest corrections.
        
        Args:
            data: DataFrame with the imported data
            column_mapping: Mapping from excel_column -> db_field
            data_type: Type of data being imported
            
        Returns:
            Dict with validation results and suggestions
        """
        if not self.openai_api_key:
            return self._fallback_validation(data, column_mapping)
        
        try:
            # Sample first few rows for AI analysis
            sample_data = data.head(3).to_dict('records')
            
            prompt = self._create_validation_prompt(sample_data, column_mapping, data_type)
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a data quality expert for Dutch landscape architecture businesses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            return self._parse_validation_response(response.choices[0].message.content)
            
        except Exception as e:
            logger.warning(f"AI validation failed, using fallback: {e}")
            return self._fallback_validation(data, column_mapping)
    
    def _create_mapping_prompt(
        self, 
        excel_columns: List[str], 
        target_schema: Dict[str, str], 
        data_type: str
    ) -> str:
        """Create a prompt for AI column mapping."""
        return f"""
Analyze these Excel column names and suggest the best mapping to our database schema.

Data Type: {data_type} (Dutch landscape architecture business)

Excel Columns:
{', '.join(excel_columns)}

Target Database Schema:
{json.dumps(target_schema, indent=2, ensure_ascii=False)}

Please provide a JSON response with confidence scores (0.0-1.0) for each mapping:
{{
  "excel_column_name": {{
    "suggested_field": "confidence_score",
    "alternative_field": "confidence_score"
  }}
}}

Consider:
- Dutch language variations (leverancier = supplier)
- Common business terminology
- Partial matches and abbreviations
- Context of landscape architecture industry
"""
    
    def _create_validation_prompt(
        self, 
        sample_data: List[Dict], 
        column_mapping: Dict[str, str], 
        data_type: str
    ) -> str:
        """Create a prompt for AI data validation."""
        return f"""
Analyze this sample data for quality issues and suggest improvements.

Data Type: {data_type} (Dutch landscape architecture business)
Column Mapping: {json.dumps(column_mapping, ensure_ascii=False)}

Sample Data:
{json.dumps(sample_data, indent=2, ensure_ascii=False)}

Please provide a JSON response with validation results:
{{
  "issues": [
    {{
      "type": "missing_data",
      "column": "column_name", 
      "suggestion": "what to do"
    }}
  ],
  "recommendations": [
    "general improvement suggestions"
  ],
  "quality_score": 0.85
}}

Check for:
- Missing required fields
- Invalid formats (email, phone, postal codes)
- Inconsistent naming conventions
- Dutch address/postal code formats
- Reasonable business values
"""
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Dict[str, float]]:
        """Parse AI response for column mapping suggestions."""
        try:
            # Try to extract JSON from the response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text.strip()
            
            return json.loads(json_text)
        except Exception as e:
            logger.warning(f"Failed to parse AI response: {e}")
            return {}
    
    def _parse_validation_response(self, response_text: str) -> Dict[str, List[str]]:
        """Parse AI response for data validation."""
        try:
            # Try to extract JSON from the response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text.strip()
            
            return json.loads(json_text)
        except Exception as e:
            logger.warning(f"Failed to parse AI validation response: {e}")
            return {"issues": [], "recommendations": [], "quality_score": 0.5}
    
    def _fallback_mapping(
        self, 
        excel_columns: List[str], 
        target_schema: Dict[str, str]
    ) -> Dict[str, Dict[str, float]]:
        """Fallback column mapping without AI."""
        mapping = {}
        
        # Simple keyword-based matching
        mapping_rules = {
            'name': ['naam', 'name', 'bedrijf', 'company', 'leverancier'],
            'email': ['email', 'e-mail', 'mail'],
            'phone': ['telefoon', 'phone', 'tel', 'gsm', 'mobiel'],
            'address': ['adres', 'address', 'straat', 'street'],
            'city': ['stad', 'city', 'plaats', 'woonplaats'],
            'postal_code': ['postcode', 'postal', 'zip'],
            'country': ['land', 'country'],
            'contact_person': ['contact', 'contactpersoon', 'persoon'],
            'description': ['beschrijving', 'description', 'omschrijving'],
            'price': ['prijs', 'price', 'cost', 'kosten'],
            'category': ['categorie', 'category', 'type'],
        }
        
        for excel_col in excel_columns:
            excel_lower = excel_col.lower().strip()
            suggestions = {}
            
            for field, keywords in mapping_rules.items():
                if field in target_schema:
                    for keyword in keywords:
                        if keyword in excel_lower:
                            confidence = 1.0 if keyword == excel_lower else 0.7
                            suggestions[field] = confidence
                            break
            
            if suggestions:
                mapping[excel_col] = suggestions
            else:
                # Default low-confidence mapping to first available field
                first_field = list(target_schema.keys())[0]
                mapping[excel_col] = {first_field: 0.3}
        
        return mapping
    
    def _fallback_validation(
        self, 
        data: pd.DataFrame, 
        column_mapping: Dict[str, str]
    ) -> Dict[str, List[str]]:
        """Fallback data validation without AI."""
        issues = []
        recommendations = []
        
        # Basic validation checks
        for col, field in column_mapping.items():
            if col in data.columns:
                null_count = data[col].isnull().sum()
                if null_count > 0:
                    issues.append({
                        "type": "missing_data",
                        "column": col,
                        "suggestion": f"{null_count} empty values found in {col}"
                    })
        
        # Email validation
        email_cols = [col for col, field in column_mapping.items() if 'email' in field.lower()]
        for col in email_cols:
            if col in data.columns:
                invalid_emails = data[~data[col].str.contains('@', na=False)][col].count()
                if invalid_emails > 0:
                    issues.append({
                        "type": "invalid_format",
                        "column": col,
                        "suggestion": f"{invalid_emails} invalid email formats in {col}"
                    })
        
        recommendations.append("Consider reviewing data for completeness")
        recommendations.append("Verify email addresses and contact information")
        
        return {
            "issues": issues,
            "recommendations": recommendations,
            "quality_score": 0.7
        }

# Singleton instance
ai_mapping_service = AIDataMappingService()