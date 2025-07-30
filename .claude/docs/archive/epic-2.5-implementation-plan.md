# Epic 2.5: Claude Code Context Management Refactor

## 🎯 Executive Summary

Based on comprehensive analysis of the current Claude Code configuration, we have a solid foundation with automated hooks, token management, and activity logging. This epic focuses on implementing the remaining advanced features: session summarization, context quarantine, and RAG indexing.

## 📊 Current State Analysis

### ✅ What's Working (95% Complete)
- **Automated Hook System**: UserPromptSubmit, PreToolUse, PostToolUse, Stop hooks active
- **Token Management**: Real-time enforcement with configurable limits per file type  
- **Activity Logging**: Comprehensive tool usage tracking in JSONL format
- **Context Validation**: Automatic structure and size validation
- **Progressive Loading**: Task-based module loading with tool loadouts

### 🔄 Gaps to Address (5% Remaining)
1. **Session Summarization**: Manual tracking exists, need automated summarization
2. **Context Quarantine**: No agent isolation for parallel work streams
3. **RAG Documentation**: No semantic search or intelligent retrieval

## 🛠️ Implementation Strategy

### Phase 1: Session Summarization Mechanism (Task 2.5.1)

**Goal**: Automatically generate session summaries and maintain session continuity

**Approach**: Leverage uv script recipes for Python-based summarization

```just
[script]
session-summarize:
  # /// script
  # requires-python = ">=3.11"
  # dependencies = ["tiktoken", "openai", "jinja2"]
  # ///
  # Session summarization logic using existing activity logs
```

**Components**:
- **2.5.1.1**: Session Activity Aggregator
- **2.5.1.2**: Intelligent Summary Generator  
- **2.5.1.3**: Session Continuity Manager
- **2.5.1.4**: Summary Template Engine

### Phase 2: Context Quarantine via Native Sub-Agents (Task 2.5.2)

**Goal**: Isolate contexts for different work streams using Anthropic's native sub-agents

**Approach**: Leverage Claude Code's built-in sub-agent feature with automatic delegation

**Implementation**: Create specialized sub-agents using `/agents` command:
- `database-specialist`: Database operations and migrations
- `frontend-specialist`: React components and UI development
- `import-specialist`: I12/MHD data import operations
- `api-specialist`: FastAPI endpoint development

**Components**:
- **2.5.2.1**: Native Sub-Agent Configuration
- **2.5.2.2**: Automatic Task Delegation
- **2.5.2.3**: Tool Restriction per Agent
- **2.5.2.4**: Context Window Isolation

### Phase 3: RAG Documentation Indexing (Task 2.5.3)

**Goal**: Semantic search and intelligent documentation retrieval

**Approach**: Vector indexing with uv-managed dependencies

```just
[script]
rag-index:
  # /// script  
  # requires-python = ">=3.11"
  # dependencies = ["chromadb", "sentence-transformers", "tiktoken"]
  # ///
  # RAG indexing and retrieval system
```

**Components**:
- **2.5.3.1**: Documentation Vector Index Builder
- **2.5.3.2**: Semantic Search Engine
- **2.5.3.3**: Context-Aware Retrieval
- **2.5.3.4**: Dynamic Context Injection

## 📋 Detailed Task Breakdown

### Task 2.5.1: Session Summarization Mechanism

#### Subtask 2.5.1.1: Session Activity Aggregator
**Deliverable**: Python script that processes activity logs
**Approach**: Use uv script with jinja2 for templating
```python
# Read from .claude/state/logs/activity.jsonl
# Aggregate tool usage, file changes, time patterns
# Generate structured session data
```

#### Subtask 2.5.1.2: Intelligent Summary Generator  
**Deliverable**: AI-powered summarization using OpenAI API
**Dependencies**: `openai`, `tiktoken`
```python
# Analyze session patterns and generate natural language summaries
# Identify key achievements, blockers, next steps
# Maintain consistent summary format
```

#### Subtask 2.5.1.3: Session Continuity Manager
**Deliverable**: Session state persistence and restoration
```python
# Save session context between Claude sessions
# Restore previous session state and context
# Handle session transitions and handoffs
```

#### Subtask 2.5.1.4: Summary Template Engine
**Deliverable**: Configurable summary templates
**Dependencies**: `jinja2`
```python
# Different summary formats (brief, detailed, technical)
# Custom templates per project or user preference
# Export to multiple formats (markdown, JSON, plain text)
```

### Task 2.5.2: Context Quarantine via Native Sub-Agents

#### Subtask 2.5.2.1: Native Sub-Agent Configuration
**Deliverable**: Four specialized sub-agents using Claude Code's `/agents` command
```yaml
# Example: database-specialist.md
---
name: database-specialist
description: Database operations, migrations, and PostgreSQL management
tools: [Read, Write, Edit, MultiEdit, Bash, LS, Grep]
---
You are a database specialist for the Mids Hero Web project...
```

#### Subtask 2.5.2.2: Automatic Task Delegation
**Deliverable**: Claude automatically delegates to appropriate sub-agents
- Database queries → database-specialist
- React components → frontend-specialist
- Data imports → import-specialist
- API endpoints → api-specialist

#### Subtask 2.5.2.3: Tool Restriction per Agent
**Deliverable**: Each agent has specific tool access
- Database: No WebFetch/WebSearch
- Frontend: Includes NotebookRead/Edit
- Import: Focus on file operations
- API: Includes WebFetch for API testing

#### Subtask 2.5.2.4: Context Window Isolation
**Deliverable**: Each sub-agent maintains separate context
- Independent context windows
- No cross-contamination between agents
- Automatic context management by Claude Code

### Task 2.5.3: RAG Documentation Indexing

#### Subtask 2.5.3.1: Documentation Vector Index Builder
**Deliverable**: Vector database of all documentation
**Dependencies**: `chromadb`, `sentence-transformers`
```python
# Index all .claude/ documentation
# Chunk documents intelligently  
# Generate embeddings for semantic search
```

#### Subtask 2.5.3.2: Semantic Search Engine
**Deliverable**: Natural language query interface
```python
# Query documentation using natural language
# Rank results by relevance and recency
# Return contextually appropriate chunks
```

#### Subtask 2.5.3.3: Context-Aware Retrieval
**Deliverable**: Smart document selection based on current task
```python
# Analyze current session context
# Automatically retrieve relevant documentation
# Inject into context at optimal times
```

#### Subtask 2.5.3.4: Dynamic Context Injection
**Deliverable**: Automatic context enhancement
```python
# Real-time context enhancement based on user queries
# Proactive document suggestions
# Context size optimization with relevance scoring
```

## 🔧 uv + justfile Integration Strategy

### Python Script Management Pattern
```just
set unstable
set script-interpreter := ['uv', 'run', '--script']

[script]
rag-query query:
  # /// script
  # requires-python = ">=3.11"
  # dependencies = ["chromadb>=0.4.0", "sentence-transformers", "click"]
  # ///
  import click
  @click.command()
  @click.argument('query')
  def search_docs(query):
      # RAG search implementation
      pass
```

### Dependency Management
- Use uv's `# /// script` metadata for dependency specification
- Version pinning for stability
- Isolated environments per script to prevent conflicts

### Integration Points
```just
# Session management
session-start topic:
  uv run --script .claude/scripts/session-manager.py start {{topic}}

session-summarize:
  uv run --script .claude/scripts/session-summarizer.py

# RAG operations  
rag-index:
  uv run --script .claude/scripts/rag-indexer.py

rag-query query:
  uv run --script .claude/scripts/rag-search.py "{{query}}"

# Native sub-agents (no just commands needed)
# Claude automatically delegates to appropriate agents
```

### Using Native Sub-Agents

Anthropic's Claude Code now includes built-in sub-agents that automatically handle task delegation:

1. **Create sub-agents**: Use `/agents` command in Claude Code
2. **Automatic delegation**: Claude detects task type and delegates
3. **Manual invocation**: Mention agent name explicitly if needed

Example interactions:
- "Update the user schema" → Automatically uses database-specialist
- "Create a login component" → Automatically uses frontend-specialist
- "Import this I12 file" → Automatically uses import-specialist
- "Add a new API endpoint" → Automatically uses api-specialist

No manual commands or scripts needed - Claude Code handles agent selection and context isolation automatically.
## 📅 Implementation Timeline

### Week 1: Session Summarization Foundation
- Implement activity aggregator and basic summary generation
- Create session continuity management
- Add summary templates

### Week 2: Native Sub-Agent Implementation
- Create four specialized sub-agents using `/agents`
- Configure tool restrictions and system prompts
- Test automatic delegation functionality

### Week 3: RAG System Development
- Build vector indexing system
- Implement semantic search
- Create context injection mechanisms

### Week 4: Integration and Testing
- Integrate all systems with existing hooks
- Performance optimization
- Documentation and testing

## 🎯 Success Metrics

1. **Session Summarization**: 90% of sessions auto-summarized with relevant insights
2. **Context Quarantine**: Zero cross-agent context contamination
3. **RAG Indexing**: Sub-second semantic search with 95% relevance
4. **Overall**: Context management requires zero manual intervention

## 🚨 Risks and Mitigations

**Risk**: Performance impact from additional processing
**Mitigation**: Background processing, lazy loading, configurable features

**Risk**: Complexity overwhelming simple use cases  
**Mitigation**: Progressive enhancement, feature flags, simple defaults

**Risk**: Dependency management complexity
**Mitigation**: uv's isolated environments, pinned dependencies

## 🔗 Dependencies

- OpenAI API for intelligent summarization
- ChromaDB for vector storage
- sentence-transformers for embeddings
- tiktoken for token counting
- jinja2 for templating

## 📈 Future Enhancements

- Multi-language RAG support
- Agent learning and adaptation
- Cross-project session insights
- Real-time collaboration features

---

*This plan leverages the existing solid foundation to add advanced AI-powered context management capabilities while maintaining simplicity and performance.*