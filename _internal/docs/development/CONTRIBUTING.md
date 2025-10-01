# Contributing to Landscape Architecture Tool

Thank you for your interest in contributing to the Landscape Architecture Tool! This guide will help you get started with contributing to our project.

## 🌟 Ways to Contribute

- **🐛 Bug Reports**: Help us identify and fix issues
- **✨ Feature Requests**: Suggest new features or improvements
- **💻 Code Contributions**: Submit bug fixes or new features
- **📚 Documentation**: Improve our documentation
- **🧪 Testing**: Help us improve test coverage
- **🌱 Domain Expertise**: Share landscape architecture knowledge

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **Node.js 20+**
- **PostgreSQL** (for production-like testing)
- **Git**

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/landscape-architecture-tool.git
   cd landscape-architecture-tool
   ```

2. **Choose Your Development Environment**

   **Option A: GitHub Codespaces (Recommended)**
   - Click the "Code" button and select "Open with Codespaces"
   - Everything is pre-configured and ready to use

   **Option B: Local Development with Docker**
   ```bash
   docker-compose up --build
   ```

   **Option C: Manual Setup**
   ```bash
   # Backend
   pip install -r requirements-dev.txt
   export PYTHONPATH=.
   python src/main.py

   # Frontend (new terminal)
   cd frontend
   npm install
   npm run dev
   ```

## 📝 Development Guidelines

### Code Style

**Python (Backend)**
- Follow PEP 8 style guidelines
- Use `black` for code formatting
- Use `isort` for import sorting
- Use `ruff` for linting
- Maximum line length: 88 characters

**JavaScript (Frontend)**
- Follow ESLint configuration
- Use Prettier for formatting
- Use meaningful variable names
- Prefer functional components with hooks

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(plants): add plant recommendation system
fix(api): resolve supplier deletion cascade issue
docs(readme): update installation instructions
test(backend): add integration tests for projects API
```

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

## 🧪 Testing

### Running Tests

```bash
# Backend tests
pytest

# Frontend tests
cd frontend && npm test

# All tests with coverage
make test
```

### Test Requirements

- **Unit Tests**: All new functions and methods should have unit tests
- **Integration Tests**: API endpoints should have integration tests
- **Frontend Tests**: Components should have React Testing Library tests
- **Coverage**: Maintain >90% test coverage

### Writing Tests

**Backend Example:**
```python
def test_create_supplier():
    """Test supplier creation with valid data."""
    supplier_data = {
        "name": "Test Supplier",
        "contact_email": "test@example.com"
    }
    response = client.post("/api/suppliers", json=supplier_data)
    assert response.status_code == 201
    assert response.json["name"] == "Test Supplier"
```

**Frontend Example:**
```javascript
test('renders supplier list', async () => {
  render(<SupplierList />);
  expect(screen.getByText('Suppliers')).toBeInTheDocument();
});
```

## 🔄 Pull Request Process

### Before Submitting

1. **Create an Issue**: For significant changes, create an issue first to discuss
2. **Branch**: Create a feature branch from `main`
3. **Code**: Implement your changes following our guidelines
4. **Test**: Ensure all tests pass and add new tests for your changes
5. **Document**: Update documentation if needed

### Submitting a PR

1. **Push** your branch to your fork
2. **Create** a pull request against the `main` branch
3. **Fill** out the PR template completely
4. **Link** related issues using "Fixes #123" or "Closes #123"

### PR Requirements

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] PR template is filled out
- [ ] Commits follow conventional commit format
- [ ] No merge conflicts

### Review Process

1. **Automated Checks**: CI/CD pipeline runs automatically
2. **Code Review**: Maintainers will review your code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, your PR will be merged

## 🌱 Landscape Architecture Contributions

We especially welcome contributions from landscape architects and related professionals:

### Domain Knowledge
- **Plant Data**: Accurate plant information and growing requirements
- **Design Workflows**: Real-world landscape architecture processes
- **Industry Standards**: Professional standards and best practices
- **Vectorworks Integration**: Expertise with Vectorworks workflows

### Feature Ideas
- **Plant Selection Tools**: Advanced plant recommendation algorithms
- **Project Management**: Landscape-specific project tracking
- **Client Presentations**: Professional presentation templates
- **Cost Estimation**: Accurate pricing and material calculations

## 🐛 Bug Reports

When reporting bugs, please include:

- **Environment**: OS, browser, Python/Node versions
- **Steps to Reproduce**: Clear step-by-step instructions
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Screenshots**: If applicable
- **Error Messages**: Full error messages and stack traces

## ✨ Feature Requests

For feature requests, please provide:

- **Problem Statement**: What problem does this solve?
- **Proposed Solution**: How should it work?
- **Use Cases**: Who would use this feature?
- **Alternatives**: What alternatives have you considered?
- **Landscape Architecture Context**: How does this relate to professional workflows?

## 📚 Documentation

We use several documentation formats:

- **README.md**: Project overview and quick start
- **API Documentation**: Auto-generated from code
- **User Guides**: Step-by-step tutorials
- **Developer Docs**: Technical implementation details

### Documentation Standards

- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Keep documentation up-to-date with code changes

## 🔒 Security

If you discover a security vulnerability:

1. **Do NOT** create a public issue
2. **Email** the maintainers privately
3. **Include** detailed information about the vulnerability
4. **Wait** for a response before disclosing publicly

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Review**: Ask questions in PR comments

## 🏆 Recognition

Contributors are recognized in:

- **README.md**: Contributors section
- **Release Notes**: Major contributions highlighted
- **GitHub**: Contributor statistics and badges

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to the Landscape Architecture Tool! Your contributions help make landscape architecture workflows more efficient and effective. 🌱
