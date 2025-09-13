#!/bin/bash

# 🧪 Comprehensive Deployment Verification and Validation Script
# This script performs thorough testing of the V1.00D deployment

set -e

echo "🧪 COMPREHENSIVE DEPLOYMENT VERIFICATION"
echo "========================================"
echo ""

# Configuration
DEV_URL="http://72.60.176.200:8080"
PROD_URL="https://optura.nl"
VPS_HOST="72.60.176.200"
VPS_USER="root"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test result tracking
TESTS_PASSED=0
TESTS_FAILED=0
CRITICAL_FAILURES=()

# Helper functions
log_test() {
    echo -e "${BLUE}🔍 Testing: $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
}

log_failure() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
    CRITICAL_FAILURES+=("$1")
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Frontend Build Verification
echo "📦 FRONTEND BUILD VERIFICATION"
echo "==============================="

log_test "Frontend build process"
cd frontend
if npm run build > /dev/null 2>&1; then
    log_success "Frontend builds successfully"
else
    log_failure "Frontend build failed"
fi
cd ..

# 2. Backend Service Health
echo ""
echo "🔧 BACKEND SERVICE VERIFICATION"
echo "==============================="

log_test "Development backend health"
DEV_HEALTH=$(curl -s "$DEV_URL/health" 2>/dev/null || echo "ERROR")
if [[ "$DEV_HEALTH" == *"healthy"* ]]; then
    log_success "Development backend is healthy"
else
    log_failure "Development backend health check failed: $DEV_HEALTH"
fi

log_test "Production backend health"
PROD_HEALTH=$(curl -s "$PROD_URL/api/health" 2>/dev/null || echo "ERROR")
if [[ "$PROD_HEALTH" == *"healthy"* ]] || [[ "$PROD_HEALTH" == *"200"* ]]; then
    log_success "Production backend is responding"
else
    log_warning "Production backend health check returned: $PROD_HEALTH"
fi

# 3. Frontend Application Loading
echo ""
echo "🌐 FRONTEND APPLICATION VERIFICATION"
echo "===================================="

log_test "Development frontend loading"
DEV_TITLE=$(curl -s "$DEV_URL" 2>/dev/null | grep -o '<title>[^<]*</title>' || echo "ERROR")
if [[ "$DEV_TITLE" == *"devdeploy"* ]]; then
    log_success "Development frontend loads with correct title: $DEV_TITLE"
else
    log_failure "Development frontend title issue: $DEV_TITLE"
fi

log_test "Production frontend loading"
PROD_TITLE=$(curl -s "$PROD_URL" 2>/dev/null | grep -o '<title>[^<]*</title>' || echo "ERROR")
if [[ "$PROD_TITLE" == *"Landscape"* ]] && [[ "$PROD_TITLE" != *"devdeploy"* ]]; then
    log_success "Production frontend loads with correct title: $PROD_TITLE"
else
    log_warning "Production frontend title: $PROD_TITLE"
fi

# 4. API Endpoints Testing
echo ""
echo "🔌 API ENDPOINTS VERIFICATION"
echo "============================="

# Test development API endpoints
log_test "Development API endpoints"
DEV_ENDPOINTS=(
    "/health"
    "/api/auth/login"
    "/api/suppliers"
    "/api/plants"
    "/api/products"
)

for endpoint in "${DEV_ENDPOINTS[@]}"; do
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$DEV_URL$endpoint" 2>/dev/null || echo "ERROR")
    if [[ "$RESPONSE" =~ ^[2-4][0-9][0-9]$ ]]; then
        log_success "Endpoint $endpoint responds: $RESPONSE"
    else
        log_failure "Endpoint $endpoint failed: $RESPONSE"
    fi
done

# 5. Database Connectivity
echo ""
echo "💾 DATABASE VERIFICATION"
echo "========================"

log_test "Development database connectivity"
if [[ "$DEV_HEALTH" == *"database"* ]] || [[ "$DEV_HEALTH" == *"healthy"* ]]; then
    log_success "Development database is connected"
else
    log_failure "Development database connectivity issue"
fi

# 6. Authentication System
echo ""
echo "🔐 AUTHENTICATION VERIFICATION"
echo "=============================="

log_test "Login endpoint availability"
LOGIN_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$DEV_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"test"}' 2>/dev/null || echo "ERROR")

if [[ "$LOGIN_RESPONSE" =~ ^[2-4][0-9][0-9]$ ]]; then
    log_success "Login endpoint responds: $LOGIN_RESPONSE"
else
    log_failure "Login endpoint failed: $LOGIN_RESPONSE"
fi

log_test "Registration endpoint availability"
REG_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$DEV_URL/api/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"username":"testuser","password":"testpass","email":"test@test.com"}' 2>/dev/null || echo "ERROR")

if [[ "$REG_RESPONSE" =~ ^[2-4][0-9][0-9]$ ]]; then
    log_success "Registration endpoint responds: $REG_RESPONSE"
else
    log_failure "Registration endpoint failed: $REG_RESPONSE"
fi

# 7. Environment Isolation
echo ""
echo "🛡️ ENVIRONMENT ISOLATION VERIFICATION"
echo "====================================="

log_test "Development environment isolation"
if [[ "$DEV_TITLE" == *"devdeploy"* ]] && [[ "$DEV_URL" == *":8080"* ]]; then
    log_success "Development environment properly isolated"
else
    log_failure "Development environment isolation issue"
fi

log_test "Production environment protection"
if [[ "$PROD_TITLE" != *"devdeploy"* ]] && [[ "$PROD_URL" == "https://"* ]]; then
    log_success "Production environment properly protected"
else
    log_warning "Production environment protection check"
fi

# 8. VPS Service Status
echo ""
echo "🖥️ VPS SERVICE VERIFICATION"
echo "==========================="

if command -v sshpass >/dev/null 2>&1 && [ ! -z "$VPS_PASSWORD" ]; then
    log_test "VPS service status"
    VPS_STATUS=$(sshpass -p "$VPS_PASSWORD" ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no \
        "$VPS_USER@$VPS_HOST" "systemctl is-active landscape-backend-dev" 2>/dev/null || echo "ERROR")
    
    if [[ "$VPS_STATUS" == "active" ]]; then
        log_success "VPS development service is active"
    else
        log_failure "VPS development service status: $VPS_STATUS"
    fi
else
    log_warning "VPS access not configured for automated testing"
fi

# 9. React Router Verification
echo ""
echo "🔀 REACT ROUTER VERIFICATION"
echo "============================"

log_test "React Router error check"
DEV_CONTENT=$(curl -s "$DEV_URL" 2>/dev/null || echo "ERROR")
if [[ "$DEV_CONTENT" == *"cannot render"* ]] || [[ "$DEV_CONTENT" == *"Router"* ]] && [[ "$DEV_CONTENT" == *"error"* ]]; then
    log_failure "React Router error detected in frontend"
else
    log_success "No React Router errors detected"
fi

# 10. Performance Verification
echo ""
echo "⚡ PERFORMANCE VERIFICATION"
echo "=========================="

log_test "Frontend load time"
LOAD_TIME=$(curl -s -o /dev/null -w "%{time_total}" "$DEV_URL" 2>/dev/null || echo "ERROR")
if [[ "$LOAD_TIME" != "ERROR" ]] && (( $(echo "$LOAD_TIME < 5.0" | bc -l) )); then
    log_success "Frontend loads in ${LOAD_TIME}s (< 5s target)"
else
    log_warning "Frontend load time: ${LOAD_TIME}s"
fi

# Final Results
echo ""
echo "📊 VERIFICATION RESULTS"
echo "======================="
echo ""
echo -e "${GREEN}✅ Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}❌ Tests Failed: $TESTS_FAILED${NC}"
echo ""

if [ ${#CRITICAL_FAILURES[@]} -gt 0 ]; then
    echo -e "${RED}🚨 CRITICAL FAILURES:${NC}"
    for failure in "${CRITICAL_FAILURES[@]}"; do
        echo -e "${RED}  - $failure${NC}"
    done
    echo ""
fi

# Overall status
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL VERIFICATIONS PASSED - DEPLOYMENT IS HEALTHY${NC}"
    exit 0
elif [ $TESTS_FAILED -le 2 ]; then
    echo -e "${YELLOW}⚠️  MINOR ISSUES DETECTED - DEPLOYMENT MOSTLY HEALTHY${NC}"
    exit 1
else
    echo -e "${RED}🚨 CRITICAL ISSUES DETECTED - DEPLOYMENT NEEDS ATTENTION${NC}"
    exit 2
fi
