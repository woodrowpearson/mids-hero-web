#!/usr/bin/env python3
"""
Custom Claude integration for GitHub Actions
Replaces the non-existent anthropics/claude-code-action
"""

import os
import sys
import json
import time
from typing import Optional, Dict, Any
import anthropic

def get_pr_context(pr_number: Optional[int] = None) -> str:
    """Get PR context for Claude"""
    context = []
    
    if pr_number:
        context.append(f"PR #{pr_number}")
    
    # Add repository context
    repo = os.environ.get('GITHUB_REPOSITORY', 'mids-hero-web')
    context.append(f"Repository: {repo}")
    
    # Add event context
    event_name = os.environ.get('GITHUB_EVENT_NAME', 'unknown')
    context.append(f"Event: {event_name}")
    
    return "\n".join(context)

def interact_with_claude(
    prompt: str,
    api_key: str,
    timeout_minutes: int = 10,
    pr_number: Optional[int] = None
) -> str:
    """
    Interact with Claude API
    
    Args:
        prompt: The prompt to send to Claude
        api_key: Anthropic API key
        timeout_minutes: Timeout in minutes
        pr_number: Optional PR number for context
    
    Returns:
        Claude's response
    """
    client = anthropic.Anthropic(api_key=api_key)
    
    # Add PR context if available
    full_prompt = prompt
    if pr_number:
        context = get_pr_context(pr_number)
        full_prompt = f"{context}\n\n{prompt}"
    
    try:
        # Create message with appropriate timeout
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            timeout=timeout_minutes * 60  # Convert to seconds
        )
        
        # Extract text from response
        return message.content[0].text if message.content else "No response from Claude"
        
    except anthropic.APIError as e:
        return f"Error calling Claude API: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

def post_github_comment(comment_body: str, pr_number: int, token: str) -> bool:
    """
    Post a comment to a GitHub PR
    
    Args:
        comment_body: The comment text
        pr_number: PR number
        token: GitHub token
    
    Returns:
        Success status
    """
    try:
        import requests
        
        repo = os.environ.get('GITHUB_REPOSITORY', '')
        if not repo:
            print("Error: GITHUB_REPOSITORY not set")
            return False
        
        url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.post(url, json={"body": comment_body}, headers=headers)
        
        if response.status_code == 201:
            print(f"Successfully posted comment to PR #{pr_number}")
            return True
        else:
            print(f"Failed to post comment: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error posting comment: {str(e)}")
        return False

def main():
    """Main entry point for the Claude action"""
    # Get environment variables
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    github_token = os.environ.get('GITHUB_TOKEN')
    
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)
    
    # Get action inputs from environment
    prompt = os.environ.get('INPUT_DIRECT_PROMPT', '')
    timeout_str = os.environ.get('INPUT_TIMEOUT_MINUTES', '10')
    pr_number_str = os.environ.get('INPUT_PR_NUMBER', '')
    post_comment = os.environ.get('INPUT_POST_COMMENT', 'false').lower() == 'true'
    
    if not prompt:
        print("Error: No prompt provided")
        sys.exit(1)
    
    # Parse inputs
    try:
        timeout_minutes = int(timeout_str)
    except ValueError:
        timeout_minutes = 10
    
    pr_number = None
    if pr_number_str:
        try:
            pr_number = int(pr_number_str)
        except ValueError:
            pass
    
    # Get PR number from event if not provided
    if not pr_number and os.path.exists('github_event.json'):
        try:
            with open('github_event.json', 'r') as f:
                event = json.load(f)
                pr_number = event.get('pull_request', {}).get('number') or \
                           event.get('issue', {}).get('number')
        except:
            pass
    
    print(f"Calling Claude with timeout of {timeout_minutes} minutes...")
    if pr_number:
        print(f"Context: PR #{pr_number}")
    
    # Call Claude
    response = interact_with_claude(
        prompt=prompt,
        api_key=api_key,
        timeout_minutes=timeout_minutes,
        pr_number=pr_number
    )
    
    print("\nClaude Response:")
    print("-" * 50)
    print(response)
    print("-" * 50)
    
    # Post as GitHub comment if requested
    if post_comment and pr_number and github_token:
        success = post_github_comment(response, pr_number, github_token)
        if not success:
            print("Warning: Failed to post comment, but Claude interaction succeeded")
    
    # Save response to file for other steps to use
    with open('claude_response.txt', 'w') as f:
        f.write(response)
    
    print("\nResponse saved to claude_response.txt")

if __name__ == "__main__":
    main()