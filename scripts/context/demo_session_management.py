#!/usr/bin/env python3
"""Demo script showing session management in action."""

import time
from auto_summarizer import AutoSummarizer, ConversationHook
from threshold_config import ThresholdManager

def demo():
    """Demonstrate session management features."""
    print("🚀 Session Management Demo\n")
    
    # Configure thresholds for demo (lower for testing)
    thresholds = ThresholdManager()
    thresholds.set("min_messages_for_summary", 5)
    thresholds.set("summary_trigger_percent", 0.1)  # Very low for demo
    print("✅ Configured thresholds for demo\n")
    
    # Create auto-summarizer
    def on_summary(summary):
        print(f"\n📝 SUMMARY GENERATED:\n{summary}\n")
    
    auto_summarizer = AutoSummarizer(
        session_id="demo_session",
        callback=on_summary
    )
    
    # Create conversation hook
    hook = ConversationHook(auto_summarizer)
    
    # Check for previous context
    context = hook.on_conversation_start()
    if context:
        print(f"📚 Previous context restored:\n{context}\n")
    
    # Simulate a conversation
    conversation = [
        ("user", "I need help creating a user authentication system"),
        ("assistant", "I'll help you create a user authentication system. Let me start by creating the user model in models.py"),
        ("user", "Great! Make sure to include email verification"),
        ("assistant", "I've added email verification to the User model. The system now includes a verification token field and an is_verified boolean."),
        ("user", "Now let's add the authentication endpoints"),
        ("assistant", "I've created the authentication endpoints in auth.py:\n- POST /api/auth/register\n- POST /api/auth/login\n- POST /api/auth/verify-email\n- POST /api/auth/forgot-password"),
        ("user", "Add rate limiting to prevent brute force attacks"),
        ("assistant", "I've added rate limiting using Flask-Limiter. The login endpoint now has a limit of 5 attempts per minute per IP address."),
    ]
    
    print("💬 Starting conversation simulation...\n")
    
    for i, (role, message) in enumerate(conversation):
        print(f"{role.upper()}: {message}")
        
        if role == "user":
            hook.on_user_message(message)
        else:
            hook.on_assistant_message(message)
        
        # Show status periodically
        if i % 3 == 2:
            status = auto_summarizer.get_status()
            print(f"\n📊 Status: {status['buffer_size']} messages, {status['total_tokens']} tokens")
            print(f"   Should summarize: {status['should_summarize']} ({status['reason']})\n")
        
        time.sleep(0.5)  # Simulate typing delay
    
    # Final status
    print("\n📊 Final Status:")
    status = auto_summarizer.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    demo()