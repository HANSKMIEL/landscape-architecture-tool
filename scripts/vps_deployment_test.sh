#!/bin/bash
# VPS Deployment Testing Script
# This script tests the VPS deployment to ensure everything is working correctly
# Can be run locally (with external access) or on the VPS itself

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
VPS_HOST="${VPS_HOST:-72.60.176.200}"
VPS_PORT="${VPS_PORT:-8080}"
INTERNAL_PORT="${INTERNAL_PORT:-5000}"

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TEST_RESULTS=()

# Function to display banner
display_banner() {
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${BLUE}🧪 VPS Deployment Testing Script${NC}"
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${CYAN}VPS Host: ${VPS_HOST}${NC}"
    echo -e "${CYAN}VPS Port: ${VPS_PORT}${NC}"
    echo -e "${BLUE}================================================================${NC}"
}

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected="$3"
    
    echo -e "${YELLOW}Testing: ${test_name}...${NC}"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASS: ${test_name}${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        TEST_RESULTS+=("✅ $test_name")
        return 0
    else
        echo -e "${RED}❌ FAIL: ${test_name}${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        TEST_RESULTS+=("❌ $test_name")
        return 1
    fi
}

# Test 1: Check if running on VPS
test_service_running() {
    echo -e "${BLUE}=== Test 1: Service Status ===${NC}"
    
    if [ -f "/etc/systemd/system/landscape-backend.service" ]; then
        # Running on VPS
        run_test "Backend service exists" "systemctl status landscape-backend >/dev/null 2>&1" ""
        run_test "Backend service is active" "systemctl is-active --quiet landscape-backend" ""
        run_test "Backend service is enabled" "systemctl is-enabled --quiet landscape-backend" ""
    else
        echo -e "${YELLOW}⚠️ Not running on VPS, skipping service tests${NC}"
        TEST_RESULTS+=("⚠️ Service tests skipped (not on VPS)")
    fi
}

# Test 2: Health endpoint (internal)
test_health_internal() {
    echo -e "${BLUE}=== Test 2: Internal Health Endpoint ===${NC}"
    
    if command -v curl >/dev/null 2>&1; then
        run_test "Internal health endpoint responds" \
            "curl -f -s -m 10 http://localhost:${INTERNAL_PORT}/health >/dev/null 2>&1" ""
        
        if curl -f -s -m 10 "http://localhost:${INTERNAL_PORT}/health" 2>/dev/null | grep -q "status"; then
            echo -e "${GREEN}Health endpoint JSON response:${NC}"
            curl -s "http://localhost:${INTERNAL_PORT}/health" 2>/dev/null | head -10
        fi
    else
        echo -e "${YELLOW}⚠️ curl not available, skipping internal health test${NC}"
        TEST_RESULTS+=("⚠️ Internal health test skipped (no curl)")
    fi
}

# Test 3: Health endpoint (external)
test_health_external() {
    echo -e "${BLUE}=== Test 3: External Health Endpoint ===${NC}"
    
    if command -v curl >/dev/null 2>&1; then
        run_test "External health endpoint responds" \
            "curl -f -s -m 10 http://${VPS_HOST}:${VPS_PORT}/health >/dev/null 2>&1" ""
        
        if curl -f -s -m 10 "http://${VPS_HOST}:${VPS_PORT}/health" 2>/dev/null | grep -q "status"; then
            echo -e "${GREEN}External health JSON response:${NC}"
            curl -s "http://${VPS_HOST}:${VPS_PORT}/health" 2>/dev/null | head -10
        fi
    else
        echo -e "${YELLOW}⚠️ curl not available, skipping external health test${NC}"
        TEST_RESULTS+=("⚠️ External health test skipped (no curl)")
    fi
}

# Test 4: Frontend files
test_frontend_files() {
    echo -e "${BLUE}=== Test 4: Frontend Build ===${NC}"
    
    if [ -f "/var/www/landscape-architecture-tool/frontend/dist/index.html" ]; then
        run_test "Frontend dist folder exists" "test -d /var/www/landscape-architecture-tool/frontend/dist" ""
        run_test "Frontend index.html exists" "test -f /var/www/landscape-architecture-tool/frontend/dist/index.html" ""
    elif [ -f "/var/www/landscape-architecture-tool/frontend/build/index.html" ]; then
        run_test "Frontend build folder exists" "test -d /var/www/landscape-architecture-tool/frontend/build" ""
        run_test "Frontend index.html exists" "test -f /var/www/landscape-architecture-tool/frontend/build/index.html" ""
    else
        echo -e "${YELLOW}⚠️ Not running on VPS, skipping frontend file tests${NC}"
        TEST_RESULTS+=("⚠️ Frontend file tests skipped (not on VPS)")
    fi
}

# Test 5: API endpoints
test_api_endpoints() {
    echo -e "${BLUE}=== Test 5: API Endpoints ===${NC}"
    
    if command -v curl >/dev/null 2>&1; then
        # Test suppliers endpoint
        run_test "Suppliers API endpoint responds" \
            "curl -f -s -m 10 http://localhost:${INTERNAL_PORT}/api/suppliers >/dev/null 2>&1" ""
        
        # Test dashboard stats endpoint
        run_test "Dashboard stats endpoint responds" \
            "curl -f -s -m 10 http://localhost:${INTERNAL_PORT}/api/dashboard/stats >/dev/null 2>&1" ""
    else
        echo -e "${YELLOW}⚠️ curl not available, skipping API endpoint tests${NC}"
        TEST_RESULTS+=("⚠️ API endpoint tests skipped (no curl)")
    fi
}

# Test 6: Database access
test_database() {
    echo -e "${BLUE}=== Test 6: Database ===${NC}"
    
    if [ -f "/var/www/landscape-architecture-tool/landscape_architecture_prod.db" ]; then
        run_test "Production database file exists" \
            "test -f /var/www/landscape-architecture-tool/landscape_architecture_prod.db" ""
        
        run_test "Production database is readable" \
            "test -r /var/www/landscape-architecture-tool/landscape_architecture_prod.db" ""
    else
        echo -e "${YELLOW}⚠️ Not running on VPS, skipping database tests${NC}"
        TEST_RESULTS+=("⚠️ Database tests skipped (not on VPS)")
    fi
}

# Test 7: Application files
test_application_files() {
    echo -e "${BLUE}=== Test 7: Application Files ===${NC}"
    
    if [ -d "/var/www/landscape-architecture-tool" ]; then
        run_test "Application directory exists" \
            "test -d /var/www/landscape-architecture-tool" ""
        
        run_test "Backend source code exists" \
            "test -d /var/www/landscape-architecture-tool/src" ""
        
        run_test "Virtual environment exists" \
            "test -d /var/www/landscape-architecture-tool/venv" ""
        
        run_test "wsgi.py exists" \
            "test -f /var/www/landscape-architecture-tool/wsgi.py" ""
        
        run_test "requirements.txt exists" \
            "test -f /var/www/landscape-architecture-tool/requirements.txt" ""
    else
        echo -e "${YELLOW}⚠️ Not running on VPS, skipping application file tests${NC}"
        TEST_RESULTS+=("⚠️ Application file tests skipped (not on VPS)")
    fi
}

# Test 8: Git repository
test_git_repository() {
    echo -e "${BLUE}=== Test 8: Git Repository ===${NC}"
    
    if [ -d "/var/www/landscape-architecture-tool/.git" ]; then
        cd /var/www/landscape-architecture-tool
        
        run_test "Git repository exists" \
            "test -d .git" ""
        
        run_test "On V1.00D branch" \
            "[[ $(git branch --show-current) == \"V1.00D\" ]]" ""
        
        echo -e "${CYAN}Current commit:${NC} $(git rev-parse --short HEAD)"
        echo -e "${CYAN}Current branch:${NC} $(git branch --show-current)"
    else
        echo -e "${YELLOW}⚠️ Not running on VPS, skipping git repository tests${NC}"
        TEST_RESULTS+=("⚠️ Git repository tests skipped (not on VPS)")
    fi
}

# Test 9: Logs and monitoring
test_logs() {
    echo -e "${BLUE}=== Test 9: Logs ===${NC}"
    
    if command -v journalctl >/dev/null 2>&1; then
        run_test "Service logs accessible" \
            "journalctl -u landscape-backend -n 1 >/dev/null 2>&1" ""
        
        echo -e "${CYAN}Recent log entries:${NC}"
        journalctl -u landscape-backend -n 10 --no-pager 2>/dev/null | tail -5 || echo "No logs available"
    else
        echo -e "${YELLOW}⚠️ journalctl not available, skipping log tests${NC}"
        TEST_RESULTS+=("⚠️ Log tests skipped (no journalctl)")
    fi
}

# Test 10: Port listening
test_ports() {
    echo -e "${BLUE}=== Test 10: Network Ports ===${NC}"
    
    if command -v netstat >/dev/null 2>&1; then
        run_test "Internal port ${INTERNAL_PORT} listening" \
            "netstat -tlnp | grep -q :${INTERNAL_PORT}" ""
    elif command -v ss >/dev/null 2>&1; then
        run_test "Internal port ${INTERNAL_PORT} listening" \
            "ss -tlnp | grep -q :${INTERNAL_PORT}" ""
    else
        echo -e "${YELLOW}⚠️ Neither netstat nor ss available, skipping port tests${NC}"
        TEST_RESULTS+=("⚠️ Port tests skipped (no netstat/ss)")
    fi
}

# Test 11: SSH and User Configuration
test_ssh_and_users() {
    echo -e "${BLUE}=== Test 11: SSH and User Configuration ===${NC}"
    
    # Test SSH service
    if command -v systemctl >/dev/null 2>&1; then
        if systemctl is-active --quiet sshd || systemctl is-active --quiet ssh; then
            run_test "SSH service is running" "true" ""
        else
            run_test "SSH service is running" "false" ""
        fi
    else
        echo -e "${YELLOW}⚠️ systemctl not available, skipping SSH service test${NC}"
        TEST_RESULTS+=("⚠️ SSH service test skipped")
    fi
    
    # Test www-data user exists
    if id -u www-data >/dev/null 2>&1; then
        run_test "www-data user exists" "true" ""
    else
        run_test "www-data user exists" "false" ""
    fi
    
    # Test SSH key authentication setup
    if [ -d "/root/.ssh" ]; then
        run_test "/root/.ssh directory exists" "test -d /root/.ssh" ""
        
        if [ -f "/root/.ssh/authorized_keys" ]; then
            KEY_COUNT=$(grep -c "^ssh-" /root/.ssh/authorized_keys 2>/dev/null || echo "0")
            run_test "SSH authorized_keys configured ($KEY_COUNT keys)" "test -f /root/.ssh/authorized_keys" ""
        else
            echo -e "${YELLOW}⚠️ No authorized_keys file - SSH key auth not configured${NC}"
            TEST_RESULTS+=("⚠️ SSH key authentication not configured")
        fi
    else
        echo -e "${YELLOW}⚠️ /root/.ssh not found${NC}"
        TEST_RESULTS+=("⚠️ /root/.ssh directory not found")
    fi
}

# Test 12: Secrets and Configuration Security
test_secrets_security() {
    echo -e "${BLUE}=== Test 12: Secrets and Configuration Security ===${NC}"
    
    # Test .env file exists and has proper permissions
    if [ -f "/var/www/landscape-architecture-tool/.env" ]; then
        run_test ".env file exists" "test -f /var/www/landscape-architecture-tool/.env" ""
        
        PERMS=$(stat -c "%a" "/var/www/landscape-architecture-tool/.env" 2>/dev/null)
        if [ "$PERMS" = "600" ] || [ "$PERMS" = "400" ]; then
            run_test ".env file has secure permissions ($PERMS)" "true" ""
        else
            run_test ".env file has secure permissions" "false" ""
            echo -e "${YELLOW}⚠️ Current permissions: $PERMS (should be 600)${NC}"
        fi
        
        # Check for critical secrets
        if grep -q "^SECRET_KEY=" "/var/www/landscape-architecture-tool/.env" 2>/dev/null; then
            if ! grep -q "^SECRET_KEY=your-" "/var/www/landscape-architecture-tool/.env"; then
                run_test "SECRET_KEY is configured" "true" ""
            else
                run_test "SECRET_KEY is configured (not default)" "false" ""
            fi
        else
            echo -e "${YELLOW}⚠️ SECRET_KEY not found in .env${NC}"
            TEST_RESULTS+=("⚠️ SECRET_KEY not configured")
        fi
    else
        echo -e "${YELLOW}⚠️ .env file not found${NC}"
        TEST_RESULTS+=("⚠️ .env file not found")
    fi
    
    # Check secrets backup directory
    if [ -d "/root/.secrets" ]; then
        run_test "Secrets backup directory exists" "test -d /root/.secrets" ""
    else
        echo -e "${YELLOW}⚠️ /root/.secrets directory not found${NC}"
        TEST_RESULTS+=("⚠️ Secrets backup not configured")
    fi
}

# Display summary
display_summary() {
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${BLUE}📊 Test Summary${NC}"
    echo -e "${BLUE}================================================================${NC}"
    
    echo -e "${CYAN}Test Results:${NC}"
    for result in "${TEST_RESULTS[@]}"; do
        echo "  $result"
    done
    
    echo ""
    echo -e "${CYAN}Total Tests: $((TESTS_PASSED + TESTS_FAILED))${NC}"
    echo -e "${GREEN}Passed: ${TESTS_PASSED}${NC}"
    echo -e "${RED}Failed: ${TESTS_FAILED}${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed!${NC}"
        echo -e "${BLUE}================================================================${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ Some tests failed. Review the output above.${NC}"
        echo -e "${BLUE}================================================================${NC}"
        return 1
    fi
}

# Main execution
main() {
    display_banner
    
    test_service_running
    test_health_internal
    test_health_external
    test_frontend_files
    test_api_endpoints
    test_database
    test_application_files
    test_git_repository
    test_logs
    test_ports
    test_ssh_and_users
    test_secrets_security
    
    display_summary
}

# Run main function
main "$@"
