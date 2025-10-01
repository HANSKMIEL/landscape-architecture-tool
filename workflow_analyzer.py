#!/usr/bin/env python3
"""
GitHub Actions Workflow Analyzer
Analyzes deployment workflows and VPS automation
"""

import json
import os
import yaml
from pathlib import Path
from typing import Dict, List

class WorkflowAnalyzer:
    def __init__(self):
        self.workflows_dir = Path(".github/workflows")
        self.analysis_results = {
            "deployment_workflows": [],
            "vps_related_workflows": [],
            "automation_features": [],
            "secrets_required": set(),
            "deployment_targets": {},
            "workflow_summary": {}
        }
        
    def analyze_workflow(self, workflow_file: Path) -> Dict:
        """Analyze a single workflow file"""
        try:
            with open(workflow_file, 'r') as f:
                workflow_content = yaml.safe_load(f)
                
            analysis = {
                "name": workflow_file.name,
                "workflow_name": workflow_content.get("name", "Unnamed"),
                "triggers": workflow_content.get("on", {}),
                "jobs": list(workflow_content.get("jobs", {}).keys()),
                "environment_urls": [],
                "secrets_used": [],
                "vps_related": False,
                "deployment_steps": []
            }
            
            # Analyze jobs for deployment and VPS-related content
            jobs = workflow_content.get("jobs", {})
            for job_name, job_config in jobs.items():
                steps = job_config.get("steps", [])
                for step in steps:
                    step_name = step.get("name", "")
                    step_run = step.get("run", "")
                    
                    # Check for VPS-related content
                    if any(term in step_name.lower() or term in step_run.lower() 
                           for term in ["vps", "deploy", "ssh", "72.60.176.200"]):
                        analysis["vps_related"] = True
                        analysis["deployment_steps"].append({
                            "job": job_name,
                            "step": step_name,
                            "type": "deployment"
                        })
                    
                    # Extract secrets
                    if "${{ secrets." in step_run:
                        import re
                        secrets = re.findall(r'\$\{\{\s*secrets\.([A-Z_]+)\s*\}\}', step_run)
                        analysis["secrets_used"].extend(secrets)
                        
                # Check for environment URLs
                if "environment" in job_config:
                    env_config = job_config["environment"]
                    if isinstance(env_config, dict) and "url" in env_config:
                        analysis["environment_urls"].append(env_config["url"])
                        
            return analysis
            
        except Exception as e:
            return {
                "name": workflow_file.name,
                "error": str(e),
                "analysis_failed": True
            }
    
    def analyze_all_workflows(self):
        """Analyze all workflow files"""
        if not self.workflows_dir.exists():
            print("❌ No .github/workflows directory found")
            return
            
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))
        
        print(f"🔍 Analyzing {len(workflow_files)} workflow files...")
        
        for workflow_file in workflow_files:
            analysis = self.analyze_workflow(workflow_file)
            
            # Categorize workflows
            if analysis.get("vps_related") or "deploy" in workflow_file.name.lower():
                self.analysis_results["deployment_workflows"].append(analysis)
                
            if analysis.get("vps_related"):
                self.analysis_results["vps_related_workflows"].append(analysis)
                
            # Collect secrets and URLs
            self.analysis_results["secrets_required"].update(analysis.get("secrets_used", []))
            
            for url in analysis.get("environment_urls", []):
                if "72.60.176.200" in url or "vps" in url.lower():
                    self.analysis_results["deployment_targets"]["vps"] = url
                    
        # Convert set to list for JSON serialization
        self.analysis_results["secrets_required"] = list(self.analysis_results["secrets_required"])
        
    def generate_report(self) -> str:
        """Generate a comprehensive analysis report"""
        report = []
        report.append("🔍 GITHUB ACTIONS WORKFLOW ANALYSIS REPORT")
        report.append("=" * 60)
        
        # Deployment Workflows Summary
        report.append(f"\n📦 DEPLOYMENT WORKFLOWS ({len(self.analysis_results['deployment_workflows'])})")
        report.append("-" * 40)
        
        for workflow in self.analysis_results["deployment_workflows"]:
            if not workflow.get("analysis_failed"):
                report.append(f"✅ {workflow['workflow_name']} ({workflow['name']})")
                report.append(f"   Jobs: {', '.join(workflow['jobs'])}")
                if workflow.get("environment_urls"):
                    report.append(f"   URLs: {', '.join(workflow['environment_urls'])}")
                if workflow.get("deployment_steps"):
                    report.append(f"   Deployment steps: {len(workflow['deployment_steps'])}")
            else:
                report.append(f"❌ {workflow['name']} - Analysis failed: {workflow.get('error')}")
                
        # VPS-Specific Analysis
        report.append(f"\n🌐 VPS-RELATED WORKFLOWS ({len(self.analysis_results['vps_related_workflows'])})")
        report.append("-" * 40)
        
        for workflow in self.analysis_results["vps_related_workflows"]:
            if not workflow.get("analysis_failed"):
                report.append(f"🚀 {workflow['workflow_name']}")
                report.append(f"   File: {workflow['name']}")
                report.append(f"   Triggers: {list(workflow.get('triggers', {}).keys())}")
                if workflow.get("secrets_used"):
                    report.append(f"   Secrets: {', '.join(workflow['secrets_used'])}")
                    
        # Secrets Analysis
        report.append(f"\n🔐 REQUIRED SECRETS ({len(self.analysis_results['secrets_required'])})")
        report.append("-" * 40)
        
        if self.analysis_results["secrets_required"]:
            for secret in sorted(self.analysis_results["secrets_required"]):
                report.append(f"🔑 {secret}")
        else:
            report.append("ℹ️ No secrets found in workflow analysis")
            
        # Deployment Targets
        report.append(f"\n🎯 DEPLOYMENT TARGETS")
        report.append("-" * 40)
        
        if self.analysis_results["deployment_targets"]:
            for target, url in self.analysis_results["deployment_targets"].items():
                report.append(f"🌐 {target.upper()}: {url}")
        else:
            report.append("ℹ️ No deployment targets identified")
            
        # Automation Features
        report.append(f"\n🤖 AUTOMATION ANALYSIS")
        report.append("-" * 40)
        
        # Count different types of automation
        total_workflows = len([f for f in self.workflows_dir.glob("*.yml")]) + len([f for f in self.workflows_dir.glob("*.yaml")])
        deployment_count = len(self.analysis_results["deployment_workflows"])
        vps_count = len(self.analysis_results["vps_related_workflows"])
        
        report.append(f"📊 Total Workflows: {total_workflows}")
        report.append(f"📦 Deployment Workflows: {deployment_count}")
        report.append(f"🌐 VPS-Related Workflows: {vps_count}")
        
        automation_score = (deployment_count / max(total_workflows, 1)) * 100
        report.append(f"🎯 Automation Score: {automation_score:.1f}%")
        
        if automation_score >= 80:
            report.append("✅ AUTOMATION STATUS: EXCELLENT")
        elif automation_score >= 60:
            report.append("⚠️ AUTOMATION STATUS: GOOD")
        else:
            report.append("❌ AUTOMATION STATUS: NEEDS IMPROVEMENT")
            
        return "\n".join(report)
        
    def check_vps_connectivity(self, vps_url: str = "http://72.60.176.200:8080") -> Dict:
        """Check VPS connectivity and basic functionality"""
        import requests
        
        connectivity_report = {
            "vps_url": vps_url,
            "connection_status": "unknown",
            "response_time": None,
            "status_code": None,
            "has_devdeploy_title": False,
            "api_health": "unknown"
        }
        
        try:
            print(f"🌐 Testing VPS connectivity: {vps_url}")
            
            # Test basic connectivity
            response = requests.get(vps_url, timeout=10)
            connectivity_report["status_code"] = response.status_code
            connectivity_report["connection_status"] = "connected" if response.status_code == 200 else "error"
            
            # Check for devdeploy title
            if response.status_code == 200:
                if "devdeploy" in response.text.lower():
                    connectivity_report["has_devdeploy_title"] = True
                    
            # Test API health
            try:
                health_response = requests.get(f"{vps_url}/health", timeout=5)
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    if health_data.get("status") == "healthy":
                        connectivity_report["api_health"] = "healthy"
                    else:
                        connectivity_report["api_health"] = "unhealthy"
                else:
                    connectivity_report["api_health"] = f"error_{health_response.status_code}"
            except:
                connectivity_report["api_health"] = "unreachable"
                
        except requests.exceptions.Timeout:
            connectivity_report["connection_status"] = "timeout"
        except requests.exceptions.ConnectionError:
            connectivity_report["connection_status"] = "refused"
        except Exception as e:
            connectivity_report["connection_status"] = f"error: {str(e)}"
            
        return connectivity_report

def main():
    print("🚀 WORKFLOW AND VPS DEPLOYMENT ANALYZER")
    print("=" * 60)
    
    analyzer = WorkflowAnalyzer()
    analyzer.analyze_all_workflows()
    
    # Generate and display report
    report = analyzer.generate_report()
    print(report)
    
    # Test VPS connectivity
    print(f"\n🌐 VPS CONNECTIVITY TEST")
    print("-" * 40)
    
    connectivity = analyzer.check_vps_connectivity()
    print(f"🎯 VPS URL: {connectivity['vps_url']}")
    print(f"🔗 Connection: {connectivity['connection_status']}")
    print(f"📊 Status Code: {connectivity['status_code']}")
    print(f"🏷️ DevDeploy Title: {'✅' if connectivity['has_devdeploy_title'] else '❌'}")
    print(f"💚 API Health: {connectivity['api_health']}")
    
    # Overall assessment
    print(f"\n🎯 OVERALL DEPLOYMENT ANALYSIS")
    print("-" * 40)
    
    workflow_count = len(analyzer.analysis_results["vps_related_workflows"])
    secrets_count = len(analyzer.analysis_results["secrets_required"])
    
    if workflow_count > 0 and connectivity["connection_status"] == "connected":
        print("✅ VPS DEPLOYMENT: FULLY OPERATIONAL")
        print("✅ AUTOMATION: CONFIGURED AND WORKING")
    elif workflow_count > 0:
        print("⚠️ VPS DEPLOYMENT: CONFIGURED BUT CONNECTION ISSUES")
        print("⚠️ AUTOMATION: NEEDS CONNECTIVITY FIX")
    else:
        print("❌ VPS DEPLOYMENT: NOT CONFIGURED")
        print("❌ AUTOMATION: MISSING")
        
    # Save results
    results = {
        "workflow_analysis": analyzer.analysis_results,
        "vps_connectivity": connectivity,
        "timestamp": str(datetime.now())
    }
    
    with open("workflow_analysis_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"\n📁 Detailed analysis saved to: workflow_analysis_results.json")

if __name__ == "__main__":
    from datetime import datetime
    main()