#!/usr/bin/env python3
"""
Pipeline Health Monitor
Comprehensive monitoring tool for CI/CD pipeline health and performance analysis
Based on recommendations from the comprehensive handover document
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple


class PipelineHealthMonitor:
    """Monitor and analyze CI/CD pipeline health metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.health_thresholds = {
            'excellent': 100,
            'good': 80,
            'fair': 60,
            'poor': 0
        }
    
    def assess_pipeline_health(self, success_rate: float) -> str:
        """Assess pipeline health based on success rate"""
        if success_rate >= self.health_thresholds['excellent']:
            return 'EXCELLENT'
        elif success_rate >= self.health_thresholds['good']:
            return 'GOOD'
        elif success_rate >= self.health_thresholds['fair']:
            return 'FAIR'
        else:
            return 'POOR'
    
    def calculate_success_rate(self, job_results: Dict[str, str]) -> Tuple[float, int, int]:
        """Calculate success rate from job results"""
        total_jobs = len(job_results)
        successful_jobs = sum(1 for result in job_results.values() if result == 'success')
        success_rate = (successful_jobs / total_jobs * 100) if total_jobs > 0 else 0
        return success_rate, successful_jobs, total_jobs
    
    def identify_failed_jobs(self, job_results: Dict[str, str]) -> List[str]:
        """Identify which jobs failed and their status"""
        failed_jobs = []
        for job_name, result in job_results.items():
            if result != 'success':
                failed_jobs.append(f"{job_name}({result})")
        return failed_jobs
    
    def generate_health_report(self, job_results: Dict[str, str], 
                             workflow_info: Optional[Dict] = None) -> Dict:
        """Generate comprehensive pipeline health report"""
        success_rate, successful_jobs, total_jobs = self.calculate_success_rate(job_results)
        health_status = self.assess_pipeline_health(success_rate)
        failed_jobs = self.identify_failed_jobs(job_results)
        
        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'pipeline_health': health_status,
            'success_rate': success_rate,
            'total_jobs': total_jobs,
            'successful_jobs': successful_jobs,
            'failed_jobs_count': len(failed_jobs),
            'failed_jobs': failed_jobs,
            'job_results': job_results
        }
        
        if workflow_info:
            report.update(workflow_info)
        
        return report
    
    def get_health_recommendations(self, health_status: str, failed_jobs: List[str]) -> List[str]:
        """Get recommendations based on pipeline health"""
        recommendations = []
        
        if health_status == 'EXCELLENT':
            recommendations.extend([
                "✅ All pipeline jobs completed successfully!",
                "🚀 Pipeline ready for deployment",
                "📈 Continue monitoring for performance trends"
            ])
        elif health_status == 'GOOD':
            recommendations.extend([
                "⚠️ Pipeline mostly successful with minor issues",
                "📊 Review failed jobs before deployment",
                "🔍 Investigate patterns in failing jobs"
            ])
        elif health_status == 'FAIR':
            recommendations.extend([
                "⚠️ Pipeline has moderate failures",
                "🔍 Investigation required for failed jobs",
                "📋 Review recent changes and dependencies"
            ])
        else:  # POOR
            recommendations.extend([
                "❌ Pipeline has significant failures",
                "🔧 Address failing jobs before proceeding",
                "🚨 Consider reverting recent changes if needed"
            ])
        
        # Job-specific recommendations
        if failed_jobs:
            if any('test-backend' in job for job in failed_jobs):
                recommendations.append("🔧 Backend tests failing: Check database connectivity and migrations")
            
            if any('test-frontend' in job for job in failed_jobs):
                recommendations.append("🔧 Frontend tests failing: Check dependencies and build configuration")
            
            if any('code-quality' in job for job in failed_jobs):
                recommendations.append("🔧 Code quality issues: Run linting tools locally and fix violations")
            
            if any('integration-tests' in job for job in failed_jobs):
                recommendations.append("🔧 Integration tests failing: Check service orchestration and API endpoints")
        
        return recommendations
    
    def export_metrics_for_github(self, report: Dict) -> None:
        """Export metrics in GitHub Actions output format"""
        github_output = os.environ.get('GITHUB_OUTPUT')
        if not github_output:
            print("Warning: GITHUB_OUTPUT not set, metrics will be printed to stdout")
            github_output = '/dev/stdout'
        
        try:
            with open(github_output, 'a') as f:
                f.write(f"success_rate={report['success_rate']}\n")
                f.write(f"pipeline_health={report['pipeline_health']}\n")
                f.write(f"total_jobs={report['total_jobs']}\n")
                f.write(f"successful_jobs={report['successful_jobs']}\n")
                f.write(f"failed_jobs_count={report['failed_jobs_count']}\n")
                f.write(f"timestamp={report['timestamp']}\n")
        except Exception as e:
            print(f"Warning: Could not write to GitHub output: {e}")
    
    def print_detailed_report(self, report: Dict) -> None:
        """Print detailed health report to console"""
        print("=== CI/CD Pipeline Health Report ===")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Pipeline Health: {report['pipeline_health']}")
        print(f"Success Rate: {report['success_rate']:.1f}% ({report['successful_jobs']}/{report['total_jobs']})")
        
        if 'workflow' in report:
            print(f"Workflow: {report['workflow']}")
        if 'repository' in report:
            print(f"Repository: {report['repository']}")
        if 'branch' in report:
            print(f"Branch: {report['branch']}")
        if 'commit' in report:
            print(f"Commit: {report['commit']}")
        
        print("\nJob Results:")
        for job_name, result in report['job_results'].items():
            status_emoji = "✅" if result == 'success' else "❌"
            print(f"  {status_emoji} {job_name}: {result}")
        
        if report['failed_jobs']:
            print(f"\nFailed Jobs: {', '.join(report['failed_jobs'])}")
        
        # Get and display recommendations
        recommendations = self.get_health_recommendations(
            report['pipeline_health'], 
            report['failed_jobs']
        )
        
        print("\nRecommendations:")
        for rec in recommendations:
            print(f"  {rec}")
        
        print("\n=== End Pipeline Health Report ===")
    
    def save_report_to_file(self, report: Dict, filename: Optional[str] = None) -> str:
        """Save detailed report to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pipeline_health_report_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"📁 Detailed report saved to: {filename}")
            return filename
        except Exception as e:
            print(f"Warning: Could not save report to file: {e}")
            return ""


def main():
    """Main function for command-line usage"""
    monitor = PipelineHealthMonitor()
    
    # Example usage with environment variables (as used in GitHub Actions)
    job_results = {
        'test-backend': os.environ.get('TEST_BACKEND_RESULT', 'success'),
        'test-frontend': os.environ.get('TEST_FRONTEND_RESULT', 'success'),
        'code-quality': os.environ.get('CODE_QUALITY_RESULT', 'success'),
        'integration-tests': os.environ.get('INTEGRATION_TESTS_RESULT', 'success'),
        'deepsource': os.environ.get('DEEPSOURCE_RESULT', 'success')
    }
    
    workflow_info = {
        'repository': os.environ.get('GITHUB_REPOSITORY', 'unknown'),
        'workflow': os.environ.get('GITHUB_WORKFLOW', 'unknown'),
        'branch': os.environ.get('GITHUB_REF_NAME', 'unknown'),
        'commit': os.environ.get('GITHUB_SHA', 'unknown'),
        'run_id': os.environ.get('GITHUB_RUN_ID', 'unknown'),
        'run_number': os.environ.get('GITHUB_RUN_NUMBER', 'unknown'),
        'actor': os.environ.get('GITHUB_ACTOR', 'unknown'),
        'event': os.environ.get('GITHUB_EVENT_NAME', 'unknown')
    }
    
    # Generate comprehensive report
    report = monitor.generate_health_report(job_results, workflow_info)
    
    # Output report
    monitor.print_detailed_report(report)
    monitor.export_metrics_for_github(report)
    
    # Save detailed report for analysis
    if os.environ.get('SAVE_DETAILED_REPORT', 'false').lower() == 'true':
        monitor.save_report_to_file(report)
    
    # Exit with appropriate code based on health
    health_exit_codes = {
        'EXCELLENT': 0,
        'GOOD': 0,
        'FAIR': 1,
        'POOR': 2
    }
    
    exit_code = health_exit_codes.get(report['pipeline_health'], 2)
    print(f"\n📊 Monitoring completed (exit code: {exit_code})")
    return exit_code


if __name__ == '__main__':
    sys.exit(main())