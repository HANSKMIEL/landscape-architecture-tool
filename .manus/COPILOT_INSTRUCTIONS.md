# 🤖 GitHub Copilot Instructions

## 📋 **How to Work with Manus Handoffs**

### 🎯 **When You Receive an Issue Assignment**

1. **Read the Issue Completely**
   - Review all requirements and context
   - Note the completion trigger format
   - Understand success criteria

2. **Review .manus Context Files**
   **MANDATORY**: Always read these files first:
   - `.manus/handoff/copilot_context_[timestamp].md` - Complete project overview
   - `.manus/handoff/copilot_assignment_[timestamp].md` - Detailed requirements
   - `.manus/CONTINUATION_INSTRUCTIONS.md` - Project guidelines
   - `.manus/TASK_CONTINUATION.md` - Current priorities

3. **Understand the Environment**
   - **Development**: V1.00D branch, DevDeploy (http://72.60.176.200:8080)
   - **Production**: main branch, Production (https://optura.nl)
   - **NEVER touch production** - work only on V1.00D

### 🔧 **Development Workflow**

#### **Step 1: Checkout the Correct Branch**
```bash
git checkout feature/comprehensive-error-handling-enhancement
# Or create new feature branch if specified
```

#### **Step 2: Make Your Changes**
- Follow the requirements in the issue
- Reference .manus context files for patterns
- Ensure code quality and consistency

#### **Step 3: Test Your Changes**
```bash
cd frontend
npm run build  # Must complete without warnings
npm test       # Run any existing tests
```

#### **Step 4: Commit and Push**
```bash
git add .
git commit -m "🤖 [Copilot] [Description of changes]"
git push origin [branch-name]
```

#### **Step 5: Update PR or Create New One**
- Update existing PR if one exists
- Create new PR if specified in issue

#### **Step 6: Trigger Manus Review**
**CRITICAL**: Add this exact comment to the PR:
```
@HANSKMIEL Copilot optimization complete - ready for Manus review
```

### 🧪 **Testing Requirements**

**Always verify:**
- [ ] Build completes without warnings
- [ ] All JSX syntax is valid
- [ ] Error handling works correctly
- [ ] Accessibility features function
- [ ] Code follows project patterns

### 📋 **Code Quality Standards**

- **Consistent Patterns**: Follow existing component structures
- **Error Handling**: Use established error handling patterns
- **Accessibility**: Include ARIA labels and keyboard support
- **Documentation**: Add comments for complex logic
- **Testing**: Include unit tests where specified

### 🚨 **Critical Rules**

1. **NEVER work on main branch** - Only V1.00D and feature branches
2. **ALWAYS read .manus files** - They contain essential context
3. **FOLLOW completion trigger** - Use exact comment format
4. **TEST thoroughly** - Ensure build and functionality work
5. **MAINTAIN quality** - Follow established patterns and standards

### 🔔 **Communication Protocol**

**Progress Updates**: Not required - work independently
**Questions**: Ask in issue comments if clarification needed
**Completion**: Use the exact trigger comment format
**Problems**: Document any issues encountered in PR description

### 📊 **Success Criteria**

Your work is complete when:
- [ ] All issue requirements are met
- [ ] Build completes successfully
- [ ] Tests pass (if applicable)
- [ ] Code follows project standards
- [ ] Completion trigger comment is posted

---

**Remember**: You're working with Manus in an AI-to-AI development pipeline. Quality and communication are essential for seamless handoffs.
