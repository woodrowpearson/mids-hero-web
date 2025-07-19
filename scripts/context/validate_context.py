#!/usr/bin/env python3
"""
Validate Claude context structure against defined limits.
"""

import json
import os
from pathlib import Path
import tiktoken

# Initialize tokenizer
encoding = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken."""
    return len(encoding.encode(text))

def load_context_map():
    """Load context-map.json configuration."""
    context_map_path = Path(".claude/context-map.json")
    if not context_map_path.exists():
        print("❌ context-map.json not found!")
        return None
    return json.loads(context_map_path.read_text())

def validate_file_sizes(context_map):
    """Validate all files against size limits."""
    print("\n📏 Validating File Sizes...")
    print("=" * 60)
    
    max_sizes = context_map['file_health_checks']['max_file_sizes']
    issues = []
    
    # Check CLAUDE.md
    claude_path = Path("CLAUDE.md")
    if claude_path.exists():
        tokens = count_tokens(claude_path.read_text())
        limit = max_sizes.get('CLAUDE.md', 5000)
        status = "✅" if tokens <= limit else "❌"
        print(f"{status} CLAUDE.md: {tokens:,} tokens (limit: {limit:,})")
        if tokens > limit:
            issues.append(f"CLAUDE.md exceeds limit by {tokens - limit:,} tokens")
    
    # Check module guides
    modules_dir = Path(".claude/modules")
    if modules_dir.exists():
        for module_dir in modules_dir.iterdir():
            if module_dir.is_dir():
                guide_path = module_dir / "guide.md"
                if guide_path.exists():
                    tokens = count_tokens(guide_path.read_text())
                    limit = max_sizes.get('module_guide', 10000)
                    status = "✅" if tokens <= limit else "❌"
                    print(f"{status} {guide_path}: {tokens:,} tokens (limit: {limit:,})")
                    if tokens > limit:
                        issues.append(f"{guide_path} exceeds limit by {tokens - limit:,} tokens")
    
    # Check workflow files
    workflows_dir = Path(".claude/workflows")
    if workflows_dir.exists():
        for workflow_file in workflows_dir.glob("*.md"):
            tokens = count_tokens(workflow_file.read_text())
            limit = max_sizes.get('workflow', 5000)
            status = "✅" if tokens <= limit else "❌"
            print(f"{status} {workflow_file}: {tokens:,} tokens (limit: {limit:,})")
            if tokens > limit:
                issues.append(f"{workflow_file} exceeds limit by {tokens - limit:,} tokens")
    
    return issues

def validate_required_files(context_map):
    """Check that all required files exist."""
    print("\n📂 Checking Required Files...")
    print("=" * 60)
    
    required = context_map['file_health_checks']['required_files']
    missing = []
    
    for file_path in required:
        path = Path(file_path)
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        if not exists:
            missing.append(file_path)
    
    return missing

def calculate_module_sizes(context_map):
    """Calculate total token size for each module."""
    print("\n📦 Module Sizes...")
    print("=" * 60)
    
    modules_dir = Path(".claude/modules")
    if not modules_dir.exists():
        print("No modules directory found")
        return {}
    
    module_sizes = {}
    
    for module_dir in modules_dir.iterdir():
        if module_dir.is_dir():
            total_tokens = 0
            file_count = 0
            
            for md_file in module_dir.glob("*.md"):
                tokens = count_tokens(md_file.read_text())
                total_tokens += tokens
                file_count += 1
            
            module_sizes[module_dir.name] = {
                'tokens': total_tokens,
                'files': file_count
            }
            
            status = "✅" if total_tokens <= 15000 else "⚠️"
            print(f"{status} {module_dir.name}: {total_tokens:,} tokens ({file_count} files)")
    
    return module_sizes

def calculate_context_scenarios(context_map, module_sizes):
    """Calculate token usage for different scenarios."""
    print("\n🎯 Context Loading Scenarios...")
    print("=" * 60)
    
    # Base context
    base_tokens = 0
    for file_path in context_map['loading_rules']['always_load']['files']:
        path = Path(file_path)
        if path.exists():
            base_tokens += count_tokens(path.read_text())
    
    print(f"Base context: {base_tokens:,} tokens")
    
    # Task scenarios
    task_configs = context_map['loading_rules']['task_based_loading']['triggers']
    
    for task, config in task_configs.items():
        task_tokens = base_tokens
        module_name = task
        
        if module_name in module_sizes:
            task_tokens += module_sizes[module_name]['tokens']
        
        percentage = (task_tokens / 128000) * 100
        status = "✅" if task_tokens <= 50000 else "⚠️"
        
        print(f"{status} {task.capitalize()} work: {task_tokens:,} tokens ({percentage:.1f}% of context)")

def generate_report(issues, missing, module_sizes):
    """Generate validation report."""
    print("\n📋 Validation Report")
    print("=" * 60)
    
    if not issues and not missing:
        print("✅ All validations passed!")
    else:
        if issues:
            print("\n❌ Size Issues:")
            for issue in issues:
                print(f"  - {issue}")
        
        if missing:
            print("\n❌ Missing Files:")
            for file in missing:
                print(f"  - {file}")
    
    # Recommendations
    print("\n💡 Recommendations:")
    
    total_modules_size = sum(m['tokens'] for m in module_sizes.values())
    if total_modules_size > 60000:
        print("  - Consider splitting large modules into sub-modules")
    
    for module, data in module_sizes.items():
        if data['tokens'] > 15000:
            print(f"  - {module} module is large ({data['tokens']:,} tokens), consider splitting")
    
    print("\n📊 Summary:")
    print(f"  - Total modules: {len(module_sizes)}")
    print(f"  - Total module tokens: {total_modules_size:,}")
    print(f"  - Average module size: {total_modules_size // max(len(module_sizes), 1):,} tokens")

def main():
    """Run context validation."""
    print("🔍 Claude Context Validation")
    print("=" * 60)
    
    # Load configuration
    context_map = load_context_map()
    if not context_map:
        return
    
    # Run validations
    size_issues = validate_file_sizes(context_map)
    missing_files = validate_required_files(context_map)
    module_sizes = calculate_module_sizes(context_map)
    
    # Calculate scenarios
    calculate_context_scenarios(context_map, module_sizes)
    
    # Generate report
    generate_report(size_issues, missing_files, module_sizes)

if __name__ == "__main__":
    main()