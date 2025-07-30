# GitHub Scripts - Custom Claude Integration

This directory contains custom scripts for integrating Claude AI into GitHub Actions workflows.

## Background

The workflows were originally designed to use `anthropics/claude-code-action@v1.2.0`, but this action does not exist. To maintain the AI-powered features, we've implemented a custom integration that calls the Anthropic API directly.

## Scripts

### claude_action.py
Main Python script that handles Claude API interactions. Features:
- Direct API calls to Claude using the Anthropic Python SDK
- Support for PR context and commenting
- Error handling and timeout management
- Response saving for workflow integration

### claude_wrapper.sh
Bash wrapper script for easy use in GitHub Actions. Features:
- Simple command-line interface
- Automatic dependency installation
- Environment variable handling
- GitHub event data processing

### test_claude_local.py
Local testing script to verify setup. Use this to:
- Test API key validity
- Verify Claude connectivity
- Check script permissions

## Usage in Workflows

Replace the non-existent action:
```yaml
# OLD (doesn't work)
- name: Claude Review
  uses: anthropics/claude-code-action@v1.2.0
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    timeout_minutes: "10"
    direct_prompt: "Your prompt here"
```

With our custom implementation:
```yaml
# NEW (working)
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'

- name: Claude Review
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    bash .github/scripts/claude_wrapper.sh \
      --prompt "Your prompt here" \
      --timeout 10 \
      --pr ${{ github.event.pull_request.number }} \
      --post-comment
```

## Testing Locally

1. Set your API key:
   ```bash
   export ANTHROPIC_API_KEY='your-key-here'
   ```

2. Run the test script:
   ```bash
   python .github/scripts/test_claude_local.py
   ```

3. Test the wrapper directly:
   ```bash
   bash .github/scripts/claude_wrapper.sh --prompt "Test prompt" --timeout 5
   ```

## Environment Variables

- `ANTHROPIC_API_KEY`: Required. Your Anthropic API key
- `GITHUB_TOKEN`: Required for posting comments. Provided automatically in workflows
- `GITHUB_WORKSPACE`: Set automatically by GitHub Actions
- `GITHUB_EVENT_PATH`: Path to GitHub event data (automatic)

## Options

The wrapper script supports:
- `--prompt`: The prompt to send to Claude (required)
- `--timeout`: Timeout in minutes (default: 10)
- `--pr`: PR number for context (optional)
- `--post-comment`: Post response as GitHub comment

## Troubleshooting

### "API key not set" error
Ensure `ANTHROPIC_API_KEY` is set in repository secrets.

### "Command not found" error
The scripts need Python 3.11+ and pip. The workflows handle this automatically.

### "Permission denied" error
Make sure scripts are executable:
```bash
chmod +x .github/scripts/claude_wrapper.sh
chmod +x .github/scripts/test_claude_local.py
```

### Rate limiting
The Anthropic API has rate limits. Consider adding retry logic for production use.

## Future Improvements

1. **Response Caching**: Cache responses for identical prompts
2. **Retry Logic**: Add automatic retries for transient failures
3. **File Modifications**: Implement actual file editing capabilities
4. **Streaming Responses**: Support for longer responses
5. **Multiple Models**: Add support for different Claude models

## Security Notes

- Never commit API keys to the repository
- Use GitHub secrets for sensitive data
- Validate and sanitize all inputs
- Be cautious with automated file modifications

---

*Created to resolve failing GitHub Actions that referenced non-existent anthropics/claude-code-action*