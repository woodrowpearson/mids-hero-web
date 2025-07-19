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

### Phase 2: Context Quarantine via Agents (Task 2.5.2)

**Goal**: Isolate contexts for different work streams to prevent contamination

**Approach**: Agent-specific context environments using uv virtual environments

```just
[script]
agent-database:
  # /// script
  # requires-python = ">=3.11"
  # dependencies = ["sqlalchemy", "alembic"]
  # ///
  # Database-focused agent with isolated context
```

**Components**:
- **2.5.2.1**: Agent Context Isolation System
- **2.5.2.2**: Cross-Agent Communication Protocol
- **2.5.2.3**: Agent-Specific Tool Loadouts
- **2.5.2.4**: Context Merge Strategies

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

### Task 2.5.2: Context Quarantine via Agents

#### Subtask 2.5.2.1: Agent Context Isolation System
**Deliverable**: Isolated context environments per agent
```bash
# Use uv to create agent-specific environments
# Separate .claude/agents/{agent-name}/ directories
# Isolated state and logging per agent
```

#### Subtask 2.5.2.2: Cross-Agent Communication Protocol
**Deliverable**: Agent coordination and data sharing
```python
# Message passing between agents
# Shared state management
# Conflict resolution protocols
```

#### Subtask 2.5.2.3: Agent-Specific Tool Loadouts
**Deliverable**: Customized tool sets per agent type
```json
// Enhanced context-map.json with agent configurations
{
  "agents": {
    "database": {
      "tools": ["Read", "Edit", "Bash(alembic:*)"],
      "modules": [".claude/modules/database/"],
      "context_limit": 40000
    }
  }
}
```

#### Subtask 2.5.2.4: Context Merge Strategies
**Deliverable**: Smart context combining when agents collaborate
```python
# Automatic context deduplication
# Priority-based context merging
# Conflict detection and resolution
```

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

# Agent operations
agent-database cmd:
  uv run --script .claude/scripts/database-agent.py "{{cmd}}"
```

## 📅 Implementation Timeline

### Week 1: Session Summarization Foundation
- Implement activity aggregator and basic summary generation
- Create session continuity management
- Add summary templates

### Week 2: Context Quarantine Setup  
- Design agent isolation architecture
- Implement basic agent environments
- Create communication protocols

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