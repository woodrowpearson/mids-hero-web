# Claude Code Project Setup Prompt

Use this prompt to have Claude Code help you set up a new project or refactor an existing one using this template.

## For New Projects

```
I want to create a new project using Claude Code best practices for context management. I have a template in the `shared/claude/new-project/` directory.

Please help me:
1. Copy the template to a new project directory called [PROJECT_NAME]
2. Customize the CLAUDE.md file for my project, which is [PROJECT_DESCRIPTION]
3. Set up the initial project structure for a [PROJECT_TYPE] application
4. Configure the justfile with appropriate commands for my tech stack: [TECH_STACK]
5. Create initial agent templates for my specific use cases

My project requirements:
- [REQUIREMENT_1]
- [REQUIREMENT_2]
- [REQUIREMENT_3]

Please ensure all context management best practices are followed, keeping CLAUDE.md under 5k tokens and setting up proper modular documentation.
```

## For Existing Projects

```
I have an existing project that I want to refactor to use Claude Code best practices. I have a template in the `shared/claude/new-project/` directory.

Please help me:
1. Analyze my current project structure and identify what needs to be organized
2. Create a CLAUDE.md file that captures the essential project context (under 5k tokens)
3. Set up the .claude/ directory structure with modular documentation
4. Migrate relevant documentation to the appropriate locations
5. Integrate the justfile commands with my existing workflow
6. Set up context management scripts for token monitoring

Current project details:
- Tech stack: [CURRENT_TECH_STACK]
- Main functionality: [PROJECT_DESCRIPTION]
- Current documentation locations: [DOC_LOCATIONS]

Please preserve all existing functionality while adding the context management layer.
```

## For Specialized Setups

### Backend API Project

```
Using the Claude Code template in `shared/claude/new-project/`, help me set up a backend API project with:
- RESTful endpoints
- Database integration
- Authentication
- Testing setup
- API documentation

Customize the agent templates for backend-specific tasks like database migrations, API testing, and performance optimization.
```

### Frontend Application

```
Using the Claude Code template in `shared/claude/new-project/`, help me set up a frontend application with:
- Component architecture
- State management
- Build tooling
- Testing setup
- Accessibility standards

Create specialized agents for component development, styling, and performance optimization.
```

### Full-Stack Project

```
Using the Claude Code template in `shared/claude/new-project/`, help me set up a full-stack project with:
- Separate frontend and backend directories
- Shared types/interfaces
- Unified testing strategy
- Deployment configuration

Set up agents for both frontend and backend work, with clear handoff procedures between them.
```

## Context Management Focus

When using any of these prompts, emphasize:

1. **Token Efficiency**: Keep all context files optimized
2. **Modular Structure**: Split large documents appropriately
3. **Progress Tracking**: Set up multi-session coordination
4. **Agent Specialization**: Create focused agents for specific tasks
5. **Automation**: Configure just recipes for common workflows

## GitHub Workflows Setup

### Enabling AI Workflows

```
I want to set up the AI-powered GitHub workflows from the template. Please help me:

1. Copy all workflows from `.github/workflows/` to my project
2. Set up the required GitHub secrets (I'll add ANTHROPIC_API_KEY)
3. Configure `.new-project/workflows/config.yaml` for my project
4. Customize the workflows for my specific needs:
   - Review criteria
   - Documentation targets
   - Coverage requirements
   - Custom checks

My project specifics:
- Language: [LANGUAGE]
- Testing framework: [TEST_FRAMEWORK]
- Documentation format: [DOC_FORMAT]
- Coverage target: [COVERAGE_PERCENT]%
```

### Workflow Customization

```
Help me customize the AI workflows for my project:

1. Update the Claude Code integration to understand my project context
2. Configure PR review to check for my coding standards
3. Set up documentation synthesis for my doc structure
4. Add custom checks for [SPECIFIC_REQUIREMENTS]
5. Configure context health monitoring thresholds

Current workflow needs:
- [WORKFLOW_NEED_1]
- [WORKFLOW_NEED_2]
- [WORKFLOW_NEED_3]
```

## Tips for Best Results

1. Be specific about your project requirements
2. Mention any existing tools or frameworks you're using
3. Specify any naming conventions or standards to follow
4. Include examples of complex tasks that might need agent coordination
5. Request validation that all files follow the token limit guidelines
6. Configure GitHub secrets before enabling workflows
7. Test workflows in a feature branch first
