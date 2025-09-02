# Real Copilot Spaces Integration Guide

This guide explains how to set up real GitHub Copilot Spaces that integrate with the MotherSpace orchestration system and appear in the Copilot UI.

## What are GitHub Copilot Spaces?

GitHub Copilot Spaces are AI-powered development environments that provide contextual assistance for specific projects or workflows. They appear in the GitHub Copilot chat interface and can be customized with project-specific knowledge and patterns.

## MotherSpace Integration

The MotherSpace orchestration system now provides real Copilot Spaces integration instead of just workflow automation. This creates actual Copilot Spaces that developers can interact with through the GitHub UI.

## Setting Up Real Copilot Spaces

### 1. Create Space Configuration Files

Create the following files in your repository to define Copilot Spaces:

#### `.github/copilot-spaces/motherspace.yml`
```yaml
name: "MotherSpace Orchestrator"
description: "Master coordination space for landscape architecture tool development"
version: "1.2.0"
context:
  type: "orchestration"
  scope: "repository"
  harmony_threshold: 85
  
knowledge_sources:
  - path: ".github/copilot-instructions.md"
    type: "instructions"
    priority: "high"
  - path: "docs/ARCHITECTURE.md"
    type: "documentation"
    priority: "medium"
  - path: "docs/MOTHERSPACE_OVERVIEW.md"
    type: "overview"
    priority: "high"

capabilities:
  - name: "Issue Management"
    description: "Analyze and manage automated issues with deduplication"
    commands:
      - "analyze issues for duplicates"
      - "create tracking issue for fingerprint"
      - "check harmony score"
  
  - name: "Task Delegation"
    description: "Delegate tasks to appropriate spaces or developers"
    commands:
      - "delegate routine task to copilot"
      - "assign task to daughter space"
      - "create integration manager task"

safety_features:
  - "fingerprint_deduplication"
  - "concurrency_control"
  - "bot_loop_prevention"
  - "pr_interference_check"

patterns:
  - name: "Single Tracking Issue"
    description: "Use fingerprint-based tracking to avoid duplicate issues"
    example: "Instead of creating multiple similar issues, update existing tracking issue"
  
  - name: "Quiet Operations"
    description: "Minimize noise while maintaining functionality"
    example: "Use update-existing rather than create-new patterns"
```

#### `.github/copilot-spaces/daughter.yml`
```yaml
name: "Daughter Space - UI/UX Manager"
description: "Specialized space for UI/UX analysis and improvement"
version: "1.0.0"
context:
  type: "ui_ux"
  scope: "frontend"
  
knowledge_sources:
  - path: "frontend/src/"
    type: "source_code"
    priority: "high"
  - path: "docs/UI_GUIDELINES.md"
    type: "guidelines"
    priority: "high"

capabilities:
  - name: "Visual Analysis"
    description: "Analyze UI/UX and provide improvement recommendations"
    commands:
      - "analyze ui accessibility"
      - "review user workflow"
      - "suggest visual improvements"
  
  - name: "User Experience"
    description: "Optimize user workflows and interactions"
    commands:
      - "map user journey"
      - "identify workflow friction"
      - "recommend ux improvements"

reporting:
  format: "comprehensive_analysis"
  includes_screenshots: true
  targets:
    - "motherspace"
    - "issue_comments"
```

#### `.github/copilot-spaces/integration-manager.yml`
```yaml
name: "IntegrationManager Space"
description: "External system integration and module development"
version: "1.0.0"
context:
  type: "integration"
  scope: "cross_system"
  
knowledge_sources:
  - path: "src/integrations/"
    type: "source_code"
    priority: "high"
  - path: "docs/API_DOCUMENTATION.md"
    type: "api_docs"
    priority: "high"

capabilities:
  - name: "Module Development"
    description: "Create and manage integration modules"
    commands:
      - "create integration module"
      - "test api connections"
      - "validate cross-system compatibility"
  
  - name: "External Integration"
    description: "Integrate with external systems and APIs"
    commands:
      - "connect to vectorworks api"
      - "setup crm integration"
      - "configure ai service"

external_systems:
  - "Vectorworks"
  - "CRM Systems"
  - "AI Services"
  - "Planning APIs"
```

### 2. Enable Copilot Spaces in Repository Settings

1. Go to your repository settings
2. Navigate to "Code security and analysis"
3. Enable "GitHub Copilot" if not already enabled
4. Look for "Copilot Spaces" section
5. Enable "Custom Spaces" and point to `.github/copilot-spaces/`

### 3. Configure Space Activation Triggers

Create `.github/workflows/copilot-spaces-activation.yml`:

```yaml
name: Copilot Spaces Activation

on:
  issues:
    types: [opened, labeled]
  pull_request:
    types: [opened, labeled]
  workflow_dispatch:
    inputs:
      space:
        description: 'Space to activate'
        required: true
        type: choice
        options:
        - motherspace
        - daughter
        - integration-manager

jobs:
  activate_space:
    runs-on: ubuntu-latest
    permissions:
      issues: write
      pull-requests: write
      contents: read
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Determine Space Activation
        id: space_detection
        uses: actions/github-script@v7
        with:
          script: |
            const issue = context.payload.issue || context.payload.pull_request;
            const labels = (issue?.labels || []).map(l => l.name);
            const title = issue?.title || '';
            
            let targetSpace = '${{ github.event.inputs.space }}';
            
            if (!targetSpace) {
              // Auto-detect based on labels and content
              if (labels.includes('ui-ux') || title.toLowerCase().includes('ui') || title.toLowerCase().includes('ux')) {
                targetSpace = 'daughter';
              } else if (labels.includes('integration') || title.toLowerCase().includes('api') || title.toLowerCase().includes('integration')) {
                targetSpace = 'integration-manager';
              } else if (labels.includes('motherspace') || labels.includes('orchestration')) {
                targetSpace = 'motherspace';
              } else {
                targetSpace = 'motherspace'; // Default
              }
            }
            
            core.setOutput('space', targetSpace);
            console.log(`Activating space: ${targetSpace}`);
      
      - name: Activate Copilot Space
        uses: actions/github-script@v7
        with:
          script: |
            const space = '${{ steps.space_detection.outputs.space }}';
            const issue = context.payload.issue || context.payload.pull_request;
            
            // Add space activation comment
            const spaceInfo = {
              'motherspace': {
                emoji: '🎯',
                name: 'MotherSpace Orchestrator',
                description: 'Master coordination and harmony management'
              },
              'daughter': {
                emoji: '👩‍💻',
                name: 'Daughter Space - UI/UX Manager',
                description: 'Visual appeal and user experience optimization'
              },
              'integration-manager': {
                emoji: '🔗',
                name: 'IntegrationManager Space',
                description: 'External system integration and module development'
              }
            };
            
            const info = spaceInfo[space];
            
            if (issue) {
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: issue.number,
                body: [
                  `## ${info.emoji} Copilot Space Activated: ${info.name}`,
                  ``,
                  `**Description:** ${info.description}`,
                  `**Space Type:** ${space}`,
                  `**Activation Time:** ${new Date().toISOString()}`,
                  ``,
                  `### How to Use This Space`,
                  ``,
                  `You can now interact with this specialized Copilot Space through:`,
                  `- GitHub Copilot chat interface`,
                  `- @copilot mentions in comments`,
                  `- Direct space commands in the Copilot UI`,
                  ``,
                  `### Available Commands`,
                  space === 'motherspace' ? [
                    `- \`@copilot analyze issues for duplicates\``,
                    `- \`@copilot check harmony score\``,
                    `- \`@copilot create tracking issue for pattern\``,
                    `- \`@copilot delegate routine task\``
                  ].join('\n') : space === 'daughter' ? [
                    `- \`@copilot analyze ui accessibility\``,
                    `- \`@copilot review user workflow\``,
                    `- \`@copilot suggest visual improvements\``,
                    `- \`@copilot map user journey\``
                  ].join('\n') : [
                    `- \`@copilot create integration module\``,
                    `- \`@copilot test api connections\``,
                    `- \`@copilot setup external integration\``,
                    `- \`@copilot validate compatibility\``
                  ].join('\n'),
                  ``,
                  `### Space Integration`,
                  `This space is integrated with the MotherSpace orchestration system and will:`,
                  `- Coordinate with other spaces for optimal harmony`,
                  `- Use fingerprint-based deduplication to prevent spam`,
                  `- Apply safety features and quality controls`,
                  `- Report back to MotherSpace for system-wide coordination`,
                  ``,
                  `---`,
                  `*Real Copilot Space integration - appears in GitHub Copilot UI*`
                ].join('\n')
              });
              
              // Add space label
              const currentLabels = issue.labels?.map(l => l.name) || [];
              if (!currentLabels.includes(space)) {
                await github.rest.issues.update({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  issue_number: issue.number,
                  labels: [...currentLabels, space, 'copilot-space-active']
                });
              }
            }
```

### 4. Using Copilot Spaces

Once set up, developers can:

1. **Access spaces through GitHub Copilot UI:**
   - Open GitHub Copilot chat
   - See available spaces in the space selector
   - Choose the appropriate space for their task

2. **Use space-specific commands:**
   ```
   @copilot [space-name] [command]
   
   Examples:
   @copilot motherspace analyze issues for duplicates
   @copilot daughter review user workflow for dashboard
   @copilot integration-manager create vectorworks module
   ```

3. **Get space-specific context:**
   - Each space has access to relevant files and documentation
   - Responses are tailored to the space's specialization
   - Coordination with MotherSpace for system harmony

### 5. Space Coordination Patterns

The spaces coordinate through:

1. **MotherSpace as orchestrator:**
   - Monitors all space activities
   - Resolves conflicts between spaces
   - Maintains system harmony

2. **Cross-space communication:**
   - Daughter → MotherSpace: UI/UX analysis results
   - IntegrationManager → MotherSpace: Module development updates
   - MotherSpace → All: Coordination decisions

3. **Safety features:**
   - Fingerprint-based deduplication across all spaces
   - Concurrency controls to prevent conflicts
   - Automatic issue consolidation

### 6. Verification

To verify your Copilot Spaces are working:

1. Check the GitHub Copilot UI for available spaces
2. Create an issue with appropriate labels
3. Verify space activation comments appear
4. Test space-specific commands in Copilot chat
5. Confirm coordination with MotherSpace orchestration

## Benefits

- **Real GitHub integration:** Appears in actual Copilot UI
- **Specialized assistance:** Each space provides focused help
- **Coordinated development:** MotherSpace ensures harmony
- **Reduced noise:** Fingerprint deduplication prevents spam
- **Safety features:** Multiple safeguards prevent issues
- **Quiet operation:** Updates existing issues instead of creating new ones

## Troubleshooting

If spaces don't appear:
1. Verify repository has Copilot enabled
2. Check `.github/copilot-spaces/` directory exists
3. Validate YAML configuration files
4. Ensure appropriate permissions are set
5. Check workflow activation logs

For coordination issues:
1. Check MotherSpace harmony score
2. Verify safety system is operational
3. Review fingerprint tracking logs
4. Check for concurrency conflicts