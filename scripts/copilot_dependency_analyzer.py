#!/usr/bin/env python3
"""
Copilot Dependency Analysis Helper

This script provides comprehensive tools for Copilot to systematically analyze
and implement critical dependency updates safely and efficiently.
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('copilot_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CopilotDependencyAnalyzer:
    """
    Comprehensive dependency analysis tool for Copilot
    """
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.analysis_results = {}
        self.test_results = {}
        
    def analyze_dependency_update(self, pr_number: int) -> dict:
        """
        Comprehensive analysis of a dependency update PR
        """
        logger.info(f"Starting analysis of PR #{pr_number}")
        
        # Phase 1: Extract dependency information
        dependency_info = self._extract_dependency_info(pr_number)
        
        # Phase 2: Impact assessment
        impact_assessment = self._assess_impact(dependency_info)
        
        # Phase 3: Breaking changes analysis
        breaking_changes = self._analyze_breaking_changes(dependency_info)
        
        # Phase 4: Security assessment
        security_assessment = self._assess_security_implications(dependency_info)
        
        # Phase 5: Testing strategy
        testing_strategy = self._develop_testing_strategy(dependency_info)
        
        analysis = {
            'pr_number': pr_number,
            'dependency_info': dependency_info,
            'impact_assessment': impact_assessment,
            'breaking_changes': breaking_changes,
            'security_assessment': security_assessment,
            'testing_strategy': testing_strategy,
            'timestamp': datetime.now().isoformat(),
            'status': 'analysis_complete'
        }
        
        self.analysis_results[pr_number] = analysis
        self._save_analysis_report(analysis)
        
        return analysis
    
    def _extract_dependency_info(self, pr_number: int) -> dict:
        """Extract dependency information from PR"""
        logger.info("Extracting dependency information")
        
        try:
            # Get PR details using GitHub CLI
            pr_info = self._run_command(f"gh pr view {pr_number} --json title,body,files")
            pr_data = json.loads(pr_info)
            
            title = pr_data.get('title', '')
            
            # Parse dependency from title (Dependabot format)
            dep_match = re.search(r'bump (.+?) from ([\d.]+) to ([\d.]+)', title)
            if dep_match:
                package_name = dep_match.group(1)
                from_version = dep_match.group(2)
                to_version = dep_match.group(3)
            else:
                # Fallback parsing
                package_name = self._extract_package_name(title)
                from_version = "unknown"
                to_version = "unknown"
            
            # Determine ecosystem
            ecosystem = self._determine_ecosystem(pr_data.get('files', []))
            
            # Determine update type
            update_type = self._determine_update_type(from_version, to_version)
            
            return {
                'package_name': package_name,
                'from_version': from_version,
                'to_version': to_version,
                'ecosystem': ecosystem,
                'update_type': update_type,
                'pr_title': title,
                'files_changed': [f['path'] for f in pr_data.get('files', [])]
            }
            
        except Exception as e:
            logger.error(f"Error extracting dependency info: {e}")
            return {'error': str(e)}
    
    def _assess_impact(self, dependency_info: dict) -> dict:
        """Assess the impact of the dependency update"""
        logger.info("Assessing dependency impact")
        
        package_name = dependency_info.get('package_name', '')
        ecosystem = dependency_info.get('ecosystem', '')
        
        # Critical dependencies list
        critical_dependencies = {
            'python': ['flask', 'django', 'sqlalchemy', 'requests', 'pytest'],
            'javascript': ['react', 'express', 'webpack', 'babel', 'typescript', 'vite'],
            'docker': ['node', 'python', 'nginx'],
            'github-actions': ['actions/checkout', 'actions/setup-node', 'actions/setup-python']
        }
        
        is_critical = any(
            package_name.lower() in critical_dependencies.get(ecosystem, [])
            for eco in critical_dependencies
        )
        
        # Assess usage in codebase
        usage_analysis = self._analyze_package_usage(package_name)
        
        impact_level = 'low'
        if is_critical:
            impact_level = 'critical'
        elif dependency_info.get('update_type') == 'major':
            impact_level = 'high'
        elif usage_analysis.get('usage_count', 0) > 10:
            impact_level = 'medium'
        
        return {
            'impact_level': impact_level,
            'is_critical_dependency': is_critical,
            'usage_analysis': usage_analysis,
            'potential_affected_areas': self._identify_affected_areas(package_name)
        }
    
    def _analyze_breaking_changes(self, dependency_info: dict) -> dict:
        """Analyze potential breaking changes"""
        logger.info("Analyzing breaking changes")
        
        package_name = dependency_info.get('package_name', '')
        from_version = dependency_info.get('from_version', '')
        to_version = dependency_info.get('to_version', '')
        
        # Try to fetch changelog/release notes
        changelog = self._fetch_changelog(package_name, from_version, to_version)
        
        # Analyze for breaking change indicators
        breaking_indicators = [
            'breaking change', 'breaking', 'removes', 'deprecated',
            'no longer supported', 'major version', 'incompatible'
        ]
        
        potential_breaks = []
        if changelog:
            for indicator in breaking_indicators:
                if indicator.lower() in changelog.lower():
                    potential_breaks.append(indicator)
        
        return {
            'potential_breaking_changes': potential_breaks,
            'changelog_available': bool(changelog),
            'changelog_excerpt': changelog[:500] if changelog else None,
            'risk_level': 'high' if potential_breaks else 'medium' if dependency_info.get('update_type') == 'major' else 'low'
        }
    
    def _assess_security_implications(self, dependency_info: dict) -> dict:
        """Assess security implications of the update"""
        logger.info("Assessing security implications")
        
        # Check for security advisories
        security_check = self._check_security_advisories(dependency_info.get('package_name', ''))
        
        # Check for known vulnerabilities in current version
        vuln_check = self._check_vulnerabilities()
        
        return {
            'security_advisories': security_check,
            'vulnerability_scan': vuln_check,
            'security_impact': 'positive' if security_check.get('fixes_vulnerabilities') else 'neutral'
        }
    
    def _develop_testing_strategy(self, dependency_info: dict) -> dict:
        """Develop comprehensive testing strategy"""
        logger.info("Developing testing strategy")
        
        impact_level = self.analysis_results.get('impact_assessment', {}).get('impact_level', 'medium')
        
        base_tests = [
            'run_existing_test_suite',
            'check_application_startup',
            'validate_core_functionality'
        ]
        
        if impact_level in ['critical', 'high']:
            base_tests.extend([
                'integration_testing',
                'performance_testing',
                'security_testing',
                'compatibility_testing'
            ])
        
        return {
            'test_phases': base_tests,
            'estimated_time': self._estimate_testing_time(impact_level),
            'test_environments': ['development', 'staging'],
            'rollback_plan': self._create_rollback_plan()
        }
    
    def run_comprehensive_tests(self) -> dict:
        """Run comprehensive test suite"""
        logger.info("Running comprehensive test suite")
        
        results = {}
        
        # Backend tests
        logger.info("Running backend tests")
        try:
            backend_result = self._run_command("make backend-test", timeout=300)
            results['backend_tests'] = {
                'status': 'passed',
                'output': backend_result[-1000:]  # Last 1000 chars
            }
        except subprocess.CalledProcessError as e:
            results['backend_tests'] = {
                'status': 'failed',
                'error': str(e),
                'output': e.output[-1000:] if hasattr(e, 'output') else ''
            }
        
        # Frontend tests
        logger.info("Running frontend tests")
        try:
            frontend_result = self._run_command("cd frontend && npm run test:vitest:run", timeout=120)
            results['frontend_tests'] = {
                'status': 'passed',
                'output': frontend_result[-1000:]
            }
        except subprocess.CalledProcessError as e:
            results['frontend_tests'] = {
                'status': 'failed',
                'error': str(e),
                'output': e.output[-1000:] if hasattr(e, 'output') else ''
            }
        
        # Build tests
        logger.info("Running build tests")
        try:
            build_result = self._run_command("make build", timeout=180)
            results['build_tests'] = {
                'status': 'passed',
                'output': build_result[-500:]
            }
        except subprocess.CalledProcessError as e:
            results['build_tests'] = {
                'status': 'failed',
                'error': str(e),
                'output': e.output[-500:] if hasattr(e, 'output') else ''
            }
        
        # Linting
        logger.info("Running linting")
        try:
            lint_result = self._run_command("make lint", timeout=60)
            results['linting'] = {
                'status': 'passed',
                'output': lint_result[-500:]
            }
        except subprocess.CalledProcessError as e:
            results['linting'] = {
                'status': 'failed',
                'error': str(e),
                'output': e.output[-500:] if hasattr(e, 'output') else ''
            }
        
        # Calculate overall status
        failed_tests = [k for k, v in results.items() if v.get('status') == 'failed']
        results['overall_status'] = 'failed' if failed_tests else 'passed'
        results['failed_categories'] = failed_tests
        
        self.test_results = results
        logger.info(f"Test suite complete. Overall status: {results['overall_status']}")
        
        return results
    
    def create_implementation_plan(self, analysis: dict) -> dict:
        """Create detailed implementation plan"""
        logger.info("Creating implementation plan")
        
        impact_level = analysis.get('impact_assessment', {}).get('impact_level', 'medium')
        breaking_changes = analysis.get('breaking_changes', {})
        
        phases = []
        
        # Phase 1: Preparation
        phases.append({
            'phase': 'preparation',
            'tasks': [
                'backup_current_state',
                'document_current_functionality',
                'prepare_rollback_plan',
                'set_up_test_environment'
            ],
            'estimated_time': '30 minutes'
        })
        
        # Phase 2: Implementation
        impl_tasks = ['apply_dependency_update']
        
        if breaking_changes.get('risk_level') == 'high':
            impl_tasks.extend([
                'update_deprecated_apis',
                'fix_breaking_changes',
                'update_configuration'
            ])
        
        phases.append({
            'phase': 'implementation',
            'tasks': impl_tasks,
            'estimated_time': '1-3 hours' if impact_level in ['critical', 'high'] else '30-60 minutes'
        })
        
        # Phase 3: Testing
        phases.append({
            'phase': 'testing',
            'tasks': [
                'run_unit_tests',
                'run_integration_tests',
                'manual_functionality_testing',
                'performance_validation'
            ],
            'estimated_time': '1-2 hours' if impact_level in ['critical', 'high'] else '30 minutes'
        })
        
        # Phase 4: Validation
        phases.append({
            'phase': 'validation',
            'tasks': [
                'security_validation',
                'documentation_update',
                'deployment_preparation',
                'final_approval'
            ],
            'estimated_time': '30 minutes'
        })
        
        return {
            'phases': phases,
            'total_estimated_time': self._calculate_total_time(phases),
            'risk_level': impact_level,
            'success_criteria': self._define_success_criteria(analysis)
        }
    
    def generate_progress_report(self, issue_number: int) -> str:
        """Generate comprehensive progress report"""
        
        analysis = self.analysis_results.get(issue_number, {})
        tests = self.test_results
        
        report = f"""
# 📊 Copilot Analysis Progress Report

**Issue:** #{issue_number}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** {analysis.get('status', 'in_progress')}

## 🔍 Analysis Summary
- **Dependency:** {analysis.get('dependency_info', {}).get('package_name', 'N/A')}
- **Update Type:** {analysis.get('dependency_info', {}).get('update_type', 'N/A')}
- **Impact Level:** {analysis.get('impact_assessment', {}).get('impact_level', 'N/A')}
- **Risk Level:** {analysis.get('breaking_changes', {}).get('risk_level', 'N/A')}

## 🧪 Test Results
"""
        
        if tests:
            for test_type, result in tests.items():
                if test_type != 'overall_status' and test_type != 'failed_categories':
                    status_emoji = "✅" if result.get('status') == 'passed' else "❌"
                    report += f"- {status_emoji} **{test_type.replace('_', ' ').title()}:** {result.get('status', 'unknown')}\n"
            
            report += f"\n**Overall Test Status:** {'✅ PASSED' if tests.get('overall_status') == 'passed' else '❌ FAILED'}\n"
        else:
            report += "- No test results available yet\n"
        
        report += f"""
## 📋 Next Steps
{self._generate_next_steps(analysis, tests)}

## ⚠️ Risks & Mitigations
{self._generate_risk_summary(analysis)}

---
*This report was automatically generated by Copilot Dependency Analyzer*
"""
        
        return report
    
    # Helper methods
    def _run_command(self, command: str, timeout: int = 120) -> str:
        """Run shell command with timeout"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.repo_path
            )
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, command, result.stdout, result.stderr)
            
            return result.stdout
        except subprocess.TimeoutExpired:
            raise subprocess.CalledProcessError(1, command, "", f"Command timed out after {timeout} seconds")
    
    def _determine_ecosystem(self, files: list[dict]) -> str:
        """Determine package ecosystem from changed files"""
        for file_info in files:
            path = file_info.get('path', '')
            if 'requirements' in path or path.endswith('.txt'):
                return 'python'
            if 'package.json' in path or path.endswith('.json'):
                return 'javascript'
            if 'Dockerfile' in path:
                return 'docker'
            if '.github/workflows' in path:
                return 'github-actions'
        return 'unknown'
    
    def _determine_update_type(self, from_version: str, to_version: str) -> str:
        """Determine semantic version update type"""
        try:
            from_parts = [int(x) for x in from_version.split('.')]
            to_parts = [int(x) for x in to_version.split('.')]
            
            if from_parts[0] != to_parts[0]:
                return 'major'
            if from_parts[1] != to_parts[1]:
                return 'minor'
            return 'patch'
        except (ValueError, IndexError):
            return 'unknown'
    
    def _analyze_package_usage(self, package_name: str) -> dict:
        """Analyze how the package is used in the codebase"""
        usage_count = 0
        files_using = []
        
        try:
            # Search for imports and references
            for file_path in self.repo_path.rglob("*.py"):
                try:
                    content = file_path.read_text()
                    if package_name.lower() in content.lower():
                        usage_count += content.lower().count(package_name.lower())
                        files_using.append(str(file_path))
                except:
                    continue
                    
            for file_path in self.repo_path.rglob("*.js"):
                try:
                    content = file_path.read_text()
                    if package_name.lower() in content.lower():
                        usage_count += content.lower().count(package_name.lower())
                        files_using.append(str(file_path))
                except:
                    continue
        except Exception as e:
            logger.warning(f"Error analyzing package usage: {e}")
        
        return {
            'usage_count': usage_count,
            'files_using_package': files_using[:10]  # Limit to first 10
        }
    
    def _save_analysis_report(self, analysis: dict):
        """Save analysis report to file"""
        report_dir = self.repo_path / 'reports' / 'dependency_analysis'
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f"analysis_{analysis['pr_number']}_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        logger.info(f"Analysis report saved to {report_file}")
    
    def _generate_next_steps(self, analysis: dict, tests: dict) -> str:
        """Generate next steps based on current status"""
        if not analysis:
            return "- Complete dependency analysis\n- Run comprehensive tests\n- Create implementation plan"
        
        if not tests:
            return "- Run comprehensive test suite\n- Analyze test results\n- Proceed with implementation if tests pass"
        
        if tests.get('overall_status') == 'failed':
            failed = tests.get('failed_categories', [])
            return f"- Fix failing tests: {', '.join(failed)}\n- Re-run test suite\n- Investigate test failures"
        
        return "- Review successful test results\n- Proceed with PR approval\n- Monitor post-merge health"
    
    def _generate_risk_summary(self, analysis: dict) -> str:
        """Generate risk summary"""
        impact = analysis.get('impact_assessment', {}).get('impact_level', 'unknown')
        breaking = analysis.get('breaking_changes', {}).get('risk_level', 'unknown')
        
        if impact == 'critical' or breaking == 'high':
            return "- HIGH RISK: Extensive testing and validation required\n- Consider staging deployment first\n- Have rollback plan ready"
        if impact == 'high' or breaking == 'medium':
            return "- MEDIUM RISK: Standard testing protocols apply\n- Monitor application health after merge"
        return "- LOW RISK: Standard dependency update\n- Routine testing sufficient"
    
    # Additional placeholder methods for full functionality
    def _extract_package_name(self, title: str) -> str:
        """Extract package name from PR title"""
        # Simple extraction - can be enhanced
        words = title.split()
        for i, word in enumerate(words):
            if word.lower() == 'bump' and i + 1 < len(words):
                return words[i + 1]
        return 'unknown'
    
    def _identify_affected_areas(self, package_name: str) -> list[str]:
        """Identify areas of code potentially affected by the update"""
        return ["To be implemented"]
    
    def _fetch_changelog(self, package_name: str, from_version: str, to_version: str) -> Optional[str]:
        """Fetch changelog for the package update"""
        return None  # To be implemented
    
    def _check_security_advisories(self, package_name: str) -> dict:
        """Check for security advisories"""
        return {"fixes_vulnerabilities": False}  # To be implemented
    
    def _check_vulnerabilities(self) -> dict:
        """Check for known vulnerabilities"""
        return {"vulnerabilities_found": False}  # To be implemented
    
    def _estimate_testing_time(self, impact_level: str) -> str:
        """Estimate testing time"""
        times = {
            'low': '30 minutes',
            'medium': '1 hour',
            'high': '2 hours',
            'critical': '3-4 hours'
        }
        return times.get(impact_level, '1 hour')
    
    def _create_rollback_plan(self) -> dict:
        """Create rollback plan"""
        return {
            "steps": ["git checkout previous_version", "redeploy", "verify_functionality"],
            "estimated_time": "15 minutes"
        }
    
    def _calculate_total_time(self, phases: list[dict]) -> str:
        """Calculate total estimated time"""
        return "2-6 hours depending on complexity"
    
    def _define_success_criteria(self, analysis: dict) -> list[str]:
        """Define success criteria"""
        return [
            "All tests pass",
            "Application starts successfully",
            "Core functionality works",
            "No security regressions"
        ]


def main():
    """Main CLI interface for Copilot dependency analyzer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Copilot Dependency Analysis Helper')
    parser.add_argument('command', choices=['analyze', 'test', 'plan', 'report'], 
                       help='Command to execute')
    parser.add_argument('--pr', type=int, help='PR number to analyze')
    parser.add_argument('--issue', type=int, help='Issue number for reporting')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    analyzer = CopilotDependencyAnalyzer()
    
    try:
        if args.command == 'analyze':
            if not args.pr:
                print("Error: --pr required for analyze command")
                sys.exit(1)
            
            result = analyzer.analyze_dependency_update(args.pr)
            print(json.dumps(result, indent=2))
            
        elif args.command == 'test':
            result = analyzer.run_comprehensive_tests()
            print(json.dumps(result, indent=2))
            
        elif args.command == 'plan':
            if not args.pr:
                print("Error: --pr required for plan command")
                sys.exit(1)
            
            analysis = analyzer.analyze_dependency_update(args.pr)
            plan = analyzer.create_implementation_plan(analysis)
            print(json.dumps(plan, indent=2))
            
        elif args.command == 'report':
            if not args.issue:
                print("Error: --issue required for report command")
                sys.exit(1)
            
            report = analyzer.generate_progress_report(args.issue)
            print(report)
            
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()