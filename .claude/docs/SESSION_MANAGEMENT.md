# Session Management System
Last Updated: 2025-08-25 00:00:00 UTC

## Overview

The Session Management System provides intelligent context management for Claude conversations, automatically summarizing long sessions, maintaining continuity between sessions, and ensuring optimal token usage.

## Features

### 1. Session Summarization (#176)
- **Automatic summarization** when token thresholds are reached
- **Key information extraction** (files, commands, TODOs, errors)
- **Progressive context pruning** to stay within token limits
- **OpenAI integration** for high-quality summaries

### 2. Session Continuity (#232)
- **Session tracking** across conversations
- **Context restoration** when resuming work
- **Related session linking** for project continuity
- **Git branch awareness** for context switching

### 3. Configurable Thresholds (#233)
- **Dynamic threshold management** via configuration files
- **Environment variable overrides** for flexibility
- **Adaptive thresholds** based on performance metrics
- **Per-session customization** options

### 4. Summary Quality Validation
- **Multi-metric quality assessment** (completeness, coherence, relevance)
- **Automatic summary improvement** for low-quality outputs
- **Configurable quality thresholds**
- **Issue detection and reporting**

### 5. Automatic Summary Injection
- **Background monitoring** of conversation progress
- **Seamless context injection** without user intervention
- **Conversation hooks** for integration
- **Real-time status tracking**

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AutoSummarizer                        │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Monitor    │  │  Validator   │  │   Injector    │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────┘
           │                │                  │
┌──────────┴────────┐ ┌─────┴──────┐ ┌────────┴──────────┐
│ SessionSummarizer │ │  Quality   │ │    Continuity     │
│                   │ │ Validator  │ │     Manager       │
└───────────────────┘ └────────────┘ └───────────────────┘
           │                              │
┌──────────┴────────────────────────────────┴─────────────┐
│              Threshold Configuration                     │
└──────────────────────────────────────────────────────────┘
```

## Usage

### Command Line Interface

```bash
# Generate session summary
just session-summarize

# Check session status
just session-status

# Continue previous session
just session-continue [session_id]

# List recent sessions
just session-list

# Configure thresholds
just threshold-config
just threshold-set max_context_tokens 100000
```

### Python API

```python
from scripts.context.auto_summarizer import AutoSummarizer

# Create auto-summarizer
summarizer = AutoSummarizer()

# Add messages
summarizer.add_message("user", "Help me create an API")
summarizer.add_message("assistant", "I'll help you create an API...")

# Start monitoring
summarizer.start_monitoring()

# Get status
status = summarizer.get_status()
print(f"Tokens: {status['total_tokens']}/{status['token_threshold']}")
```

### Integration with Claude

```python
from scripts.context.auto_summarizer import ConversationHook

# Create hook
hook = ConversationHook(auto_summarizer)

# On conversation start
context = hook.on_conversation_start()
if context:
    print(f"Resuming: {context}")

# During conversation
hook.on_user_message("user message")
hook.on_assistant_message("assistant response")
```

## Configuration

### Threshold Settings

Create or modify `.claude/thresholds.json` in your project:

```json
{
  "max_context_tokens": 90000,
  "summary_trigger_percent": 0.8,
  "critical_token_percent": 0.95,
  "checkpoint_interval": 50,
  "min_messages_for_summary": 20,
  "session_timeout_hours": 24,
  "min_summary_quality_score": 0.7
}
```

### Environment Variables

```bash
export CLAUDE_MAX_CONTEXT_TOKENS=100000
export CLAUDE_SUMMARY_TRIGGER_PERCENT=0.75
export CLAUDE_SESSION_TIMEOUT_HOURS=48
export OPENAI_API_KEY=your-api-key
```

## Quality Metrics

The system evaluates summaries on five dimensions:

1. **Completeness** (30%): Coverage of key information
2. **Coherence** (20%): Logical flow and structure
3. **Relevance** (20%): Focus on important content
4. **Conciseness** (15%): Appropriate brevity
5. **Accuracy** (15%): Factual correctness

Summaries scoring below the threshold are automatically improved.

## Session State

Session state is stored in the project's `.claude/sessions/` directory with the following structure:

```
.claude/sessions/
├── session_metadata.json          # Session registry
├── session_001_state.json        # Session summaries
├── session_001_checkpoint_50.json # Conversation checkpoints
├── session_001_auto_state.json   # Auto-summarizer state
├── scratchpad.md                 # Manual notes (optional)
└── scratchpad/                   # Additional notes (optional)
```

This ensures that:
- Session data is project-specific
- Sessions are included in version control (if desired)
- Multiple projects maintain separate session histories
- Team members can share session context

## Performance Considerations

- **Token counting** is performed using tiktoken for accuracy
- **Summaries are cached** to avoid redundant API calls
- **Adaptive thresholds** optimize based on actual performance
- **Background monitoring** runs in a separate thread
- **State persistence** ensures continuity across restarts

## Troubleshooting

### Common Issues

1. **"OpenAI API key required"**
   - Set `OPENAI_API_KEY` environment variable
   - Or pass `api_key` parameter to SessionSummarizer

2. **"Summary quality too low"**
   - Adjust `min_summary_quality_score` threshold
   - Increase `summary_model_temperature` for more creative summaries

3. **"Session not found"**
   - Check session ID is correct
   - Verify session hasn't exceeded timeout
   - Use `just session-list` to see available sessions

4. **"Token limit exceeded"**
   - Lower `summary_trigger_percent` to summarize earlier
   - Reduce `max_messages_to_keep` for more aggressive pruning

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Testing

Run the test suite:

```bash
python scripts/context/test_session_management.py test
```

Individual component tests:

```bash
python scripts/context/session_summarizer.py test
python scripts/context/session_continuity.py test
python scripts/context/threshold_config.py test
python scripts/context/summary_validator.py test
python scripts/context/auto_summarizer.py test
```

## Future Enhancements

- **Multi-model support** for summarization
- **Custom summarization templates**
- **Session export/import** functionality
- **Team session sharing** capabilities
- **Advanced analytics** on session patterns
- **Integration with IDE extensions**

## Related Documentation

- [Epic 2.5 Status](./EPIC_2.5_STATUS.md)
- [Claude Context Management](./epic_2-5_claude_context_mgmt_refactor_072625.md)
- [Claude Workflow](./CLAUDE_WORKFLOW.md)

---

🤖 Generated with [Claude Code](https://claude.ai/code)