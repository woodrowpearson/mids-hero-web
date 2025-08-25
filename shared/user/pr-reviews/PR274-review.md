PR #274 - 2.5.5 project clean up & Epic 2.6 new data source

1. Every note made below if their is a gh issue exists update the issue to align with the note. This includes updating all TDD and other notes to reflect the changes requested below.

# GH Issue: Epic 2.5.5 - Project Cleanup & JSON Migration Preparation (parent epic)

## Review the files in @.claude/state and examine why some files are being updated and used regularly while others have not been used. Determine if the files are still needed and if not delete them and/or update @CLAUDE.md and files in @.claude/workflows to ensure they are incorporated into the new workflow. Specifically

- decisions.log
- @.claude/state/logs/
- @.claude/state/agents/general-purpose-state.json

```
く state
く agents
1) general-purpose-state.json
v logs
() activity.jsonl
() agent-activity.jsonl
v summaries
() agent-activity-2025-07-27.json
agent-coordination-fix-2025-...
documentation-review-2025-...
{} agent-stats.json
= decisions.log
1} progress.json
scratchpad.md
```

## Remove MidsReborn refs and update for epic 2.5.5 and new data source(/Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916)

/Users/w/code/mids-hero-web/.claude/EPIC_2.5.3_UPDATES.md

## Remove MidsReborn and MHD refs and MidsReborn C# parser and update for epic 2.5.5and new data source(/Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916)

/Users/w/code/mids-hero-web/.claude/EPIC_2.5.3_IMPLEMENTATION_PLAN.md

## Update Gemini for epic 2.5.5 and new data source(/Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916)

/Users/w/code/mids-hero-web/.claude/EPIC_2.5.3_GEMINI_UPDATES.md

# GH Issue 253: Epic 2.6 - JSON Data Source Migration (parent epic)

# GH Issue 254: Epic 2.7 - RAG Game Data Integration

## Remove all RAG files added to PR #274

Find and delete all vector files and all retrieval documents and cache files. RAG cache dir: `/Users/w/code/mids-hero-web/backend/.claude/rag/cache`

## Add RAG cache dir to .gitignore

/Users/w/code/mids-hero-web/.gitignore

## Decide if /Users/w/code/mids-hero-web/backend/.env.example should exist or if it can be consolidated with /Users/w/code/mids-hero-web/.env.example

## Update the .claude/context-map.json to reflect the new data source

## Indexing the new data source(/Users/w/code/mids-hero-web/external/city_of_data/raw_data_homecoming-20250617_6916)

/Users/w/code/mids-hero-web/.claude/EPIC_2.7_INDEXING_PLAN.md

## RAG Game Data Integration

/Users/w/code/mids-hero-web/.claude/EPIC_2.7_RAG_GAME_DATA_INTEGRATION.md

## Update Gemini for epic 2.7

/Users/w/code/mids-hero-web/.claude/EPIC_2.7_GEMINI_UPDATES.md
