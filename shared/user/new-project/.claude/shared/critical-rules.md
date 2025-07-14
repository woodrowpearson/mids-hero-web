# Critical Rules - MUST FOLLOW

## Command Usage

### NEVER Use These Commands
- **NEVER use `find`** - Always use `fd` instead
- **NEVER use `rm -rf`** - Always use `trash` instead
- **NEVER use `grep`** - Always use `rg` (ripgrep) instead

### Correct Usage Examples

#### File Search
```bash
# WRONG - NEVER DO THIS
find . -name "*.py"

# CORRECT
fd "\.py$"
fd -e py
```

#### File Deletion
```bash
# WRONG - NEVER DO THIS
rm -rf directory/
rm file.txt

# CORRECT
trash directory/
trash file.txt
```

#### Text Search
```bash
# WRONG - NEVER DO THIS
grep "pattern" file.txt
find . -name "*.py" | xargs grep "pattern"

# CORRECT
rg "pattern" file.txt
rg "pattern" -t py
```

## Why These Rules Exist

1. **`fd` over `find`**: 
   - Faster and more intuitive
   - Better defaults (ignores .git, node_modules)
   - Simpler syntax

2. **`trash` over `rm -rf`**:
   - Recoverable deletions
   - Prevents accidental data loss
   - Safer for development

3. **`rg` over `grep`**:
   - Much faster
   - Respects .gitignore
   - Better Unicode support

## Enforcement

These rules are non-negotiable and must be followed in:
- All scripts
- All justfile recipes
- All command suggestions
- All documentation examples

Memory references:
- [[memory:905944]] - fd usage
- [[memory:648882]] - trash usage