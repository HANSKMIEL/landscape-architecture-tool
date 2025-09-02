# Setting Up Copilot Space for Landscape Architecture Tool

This guide walks you through creating a **real Copilot Space** in the Copilot UI that will appear in the Spaces panel and provide AI-assisted development guidance for this repository.

## What is a Copilot Space?

A Copilot Space is a feature in GitHub Copilot that allows you to create custom AI assistants with specialized knowledge about your repository. Unlike GitHub Actions workflows (which automate tasks), Copilot Spaces provide interactive AI assistance directly in your development environment.

## Benefits of Using Copilot Spaces

- **Appears in Copilot Spaces UI panel** - Easy access from your IDE
- **Repository-aware assistance** - AI understands your codebase patterns
- **Custom instructions** - Tailored guidance for your development workflow
- **Interactive help** - Ask questions and get contextual responses
- **Enhanced productivity** - Faster onboarding and development

## Step-by-Step Setup

### 1. Access Copilot Spaces

1. Open **GitHub Copilot** in your IDE (VS Code, JetBrains, etc.)
2. Look for the **Spaces** panel or icon in the Copilot interface
3. Click **"Create Space"** or **"New Space"**

### 2. Configure the Space

**Space Name:** `Landscape Architecture Tool`

**Space Description:**
```
AI assistant for the Landscape Architecture Tool - a Flask/React application for managing landscape projects, suppliers, plants, and clients. Specialized in Python/Flask backend patterns, React frontend, and comprehensive development workflows.
```

### 3. Attach Repository

1. **Repository:** Select or enter `HANSKMIEL/landscape-architecture-tool`
2. **Branch:** `main` (or your default branch)
3. **Access Level:** Full repository access

### 4. Add Instruction Files

Add these key files to provide context to the AI:

#### Primary Instructions
- **`.github/copilot-instructions.md`** - Main development guide with patterns, workflows, and best practices

#### Architecture Documentation  
- **`docs/ARCHITECTURE.md`** - Detailed system architecture and component relationships
- **`docs/SPACE_OVERVIEW.md`** - Space overview and usage guidelines

#### Development Guidelines
- **`documentation/development/DEVELOPER_GUIDELINES.md`** - Code standards and development practices
- **`documentation/pipeline/PIPELINE_TROUBLESHOOTING.md`** - CI/CD guidance and troubleshooting

#### Additional Context Files (Optional)
- **`README.md`** - Project overview
- **`pyproject.toml`** - Python configuration and tool settings
- **`frontend/package.json`** - Frontend dependencies and scripts

### 5. Configure Space Settings

**Response Style:** Professional and detailed
**Code Examples:** Include working code snippets
**Context Awareness:** High - reference specific files and patterns
**Update Frequency:** Sync with repository changes

### 6. Test the Space

Once created, test your Space with these validation prompts:

#### Architecture Testing
```
Explain the database transaction isolation pattern with code examples
```

#### Development Workflow Testing
```
Show me how to add a new API route following our conventions
```

#### Testing Strategy
```
What's our current testing strategy and how do I add tests?
```

#### Organization Testing
```
How should I organize generated reports and prevent clutter?
```

#### Service Layer Testing
```
Create a new service following our transaction patterns
```

### 7. Verify Space Functionality

You should see:

✅ **Space appears in Copilot Spaces panel**
✅ **AI responses reference specific files from the repository**
✅ **Code examples match your actual patterns**
✅ **Responses include file paths and line numbers**
✅ **Architecture explanations are accurate**

## Expected AI Capabilities

When properly configured, your Copilot Space should provide:

### Code Assistance
- Generate Flask routes following your patterns
- Create SQLAlchemy models with proper relationships
- Write tests using your testing conventions
- Suggest React components matching your style

### Architecture Guidance
- Explain service layer patterns
- Database transaction handling
- Error handling conventions
- File organization principles

### Development Workflow
- Bootstrap commands (`make install`, `make build`)
- Testing procedures (`make backend-test`)
- Validation scenarios (5 key scenarios documented)
- Clutter management rules

### Troubleshooting Help
- Common build/test failures
- Environment setup issues
- Docker configuration problems
- CI/CD pipeline debugging

## Relationship to GitHub Actions Automation

**Important:** Copilot Spaces and GitHub Actions serve different purposes:

- **Copilot Space (UI):** Interactive AI assistant for development guidance
- **GitHub Actions:** Automated workflows for CI/CD, issue management, and maintenance

Both complement each other:
- Use **Copilot Space** for: Development questions, code generation, architecture guidance
- Use **GitHub Actions** for: Automated testing, issue management, deployment

## Maintenance and Updates

### Keeping the Space Current

1. **Regular Updates:** The Space syncs with repository changes automatically
2. **Instruction Updates:** Update `.github/copilot-instructions.md` when patterns change
3. **Architecture Changes:** Update `docs/ARCHITECTURE.md` when architecture evolves
4. **Testing:** Periodically test with validation prompts to ensure effectiveness

### Monitoring Space Effectiveness

Use these indicators to monitor Space quality:

- **Response Accuracy:** AI references correct files and patterns
- **Code Quality:** Generated code follows your conventions
- **Context Awareness:** AI understands your project structure
- **Developer Feedback:** Team finds responses helpful and accurate

## Troubleshooting

### Space Not Appearing
- Check GitHub Copilot subscription status
- Verify repository access permissions
- Refresh Copilot interface

### Poor Response Quality
- Verify instruction files are properly loaded
- Check that files contain current, accurate information
- Test with simpler, more specific prompts

### Outdated Information
- Force refresh the Space configuration
- Update instruction files with current patterns
- Verify branch synchronization

## Advanced Configuration

### Custom Prompts for Common Tasks

Create shortcuts for frequent operations:

**Add New Feature:**
```
Create a new [feature name] following our full-stack pattern: Flask route, service layer, SQLAlchemy model, React component, and tests
```

**Debug Issue:**
```
Help me debug [issue description] - check our common patterns and suggest solutions
```

**Code Review:**
```
Review this code against our standards: [paste code]
```

### Integration with Development Tools

- **VS Code:** Space appears in Copilot sidebar
- **JetBrains:** Available in Copilot panel
- **CLI:** Use GitHub CLI with Copilot extensions

## Success Criteria

Your Copilot Space is successfully configured when:

✅ Space appears in Copilot UI Spaces panel
✅ AI provides repository-specific guidance
✅ Code examples match your actual patterns
✅ Responses include accurate file references
✅ Development workflow questions are answered correctly
✅ Architecture explanations are detailed and accurate

---

**Need Help?**
- Check [SPACE_OVERVIEW.md](./SPACE_OVERVIEW.md) for usage guidelines
- Review [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details
- Test with validation prompts to verify functionality
- Update instruction files if responses seem outdated