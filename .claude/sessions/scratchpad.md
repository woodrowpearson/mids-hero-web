# Claude Session Scratchpad - Calculation Endpoints Development

## Session Start: 2025-07-20

### Context
- Working on feature branch: `feature/issue-44-epic-3-calculation-endpoints`
- PR #208 is open for this work
- Calculation analysis report identified 5 GitHub issues (#221-#225) for remaining calculation work
- System is 75-80% complete with core calculation engine functional

### Issues to Implement (Priority Order)

1. **#221 - Healing calculations** (HIGH) ✅ COMPLETED
   - Created `app/calc/healing.py` module with:
     - `calc_base_heal()` - Base healing from heal scale
     - `calc_final_healing()` - Enhanced healing with ED
     - `calc_heal_over_time()` - HoT calculations
   - Added healing to PowerStatBlock and EnhancementValues schemas
   - Integrated healing into calculator.py service
   - Created comprehensive unit tests (9 passing)
   - Created integration tests (3 passing)
   - Supports archetype-specific heal modifiers
   - Enhancement values extracted from `other_bonuses` field

2. **#222 - Complete ToHit/Accuracy system** (HIGH) - NEXT UP
   - Only basic accuracy implemented
   - No tohit buff calculations
   - No defense debuff support

3. **#223 - Buff/debuff effects (non-defense)** (MEDIUM)
   - No buff power effects
   - No debuff calculations
   - No buff/debuff enhancements

4. **#224 - Movement speed enhancements** (MEDIUM)
   - Only base values
   - No travel power support
   - No speed buff calculations

5. **#225 - Basic mez protection/resistance** (LOW)
   - No hold/stun/sleep/immobilize protection
   - No mez duration calculations
   - No mez enhancement support

### Development Approach
- TDD with pytest for all new features
- Follow existing code patterns from calculator.py
- Reference MidsReborn source for implementation details
- Integrate with existing enhancement diversification system

### Current Status
- Health check passed
- PR #208 is open and ready for new commits
- Issue #221 (Healing) completed with full test coverage
- Ready to commit changes and move to Issue #222

### Implementation Notes - Healing
- Healing uses Schedule A for ED calculations
- Power.effects JSON field stores `heal_scale`
- Enhancement.other_bonuses JSON field stores `heal` bonus
- GlobalBuffs schema extended with `healing` field
- Archetype heal modifiers stored in constants.py
- Base heal values by level in HEAL_BASE_BY_LEVEL constant

### Next Steps
1. Commit healing calculation changes
2. Start with Issue #222 (ToHit/Accuracy system)
3. Research existing accuracy implementation
4. Plan tohit buff/debuff architecture