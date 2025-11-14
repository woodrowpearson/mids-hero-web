# Update Changelog

Update CHANGELOG.md with new version entry.

## Usage

Tell Claude: "Update changelog for version X.Y.Z" or "Add changelog entry for [feature]"

## Format

Follow [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format:

**Version Entry**:
```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Modifications to existing features

### Deprecated
- Features being phased out

### Removed
- Deleted features

### Fixed
- Bug fixes

### Security
- Security fixes
```

## Semantic Versioning

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

## Guidelines

- Write in **present tense** ("Added," "Fixed," "Changed")
- Use **backticks** for code/commands
- Include **links** to PRs or issues when relevant
- Keep **entries concise** (one line per change)
- **Technical details** in sub-bullets if needed
- Move items from **[Unreleased]** to version section on release

## Example Entry

```markdown
## [1.0.0] - 2025-12-01

### Added
- User authentication with JWT tokens
- Build sharing via unique URLs
- Real-time build validation

### Changed
- Migrated from Create React App to Next.js 14
- Improved API response time by 40%

### Fixed
- Power calculation accuracy for damage bonuses
- Enhancement set bonus stacking rules

### Security
- Fixed XSS vulnerability in build name input ([#123](link))
```
