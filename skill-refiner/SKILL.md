---
name: skill-refiner
description: Evolve and optimize agent skills. Use when improving skill capabilities, optimizing triggers, diagnosing skill issues, analyzing skill gaps, merging skills, or discovering similar skills. Performs skill discovery, analysis, learning, and fusion with local and external discovery.
---

# Skill Refiner

Evolve skills through systematic diagnosis, analysis, and improvement.

## When to Use

Use this skill when the user wants to:

- Improve an existing skill's capabilities or trigger rate
- Diagnose skill issues or gaps
- Merge multiple related skills
- Find similar skills (local or external via `npx skills`)
- Add academic depth or engineering rigor to a skill
- Optimize skill structure or tooling

## Workflow

### Phase 1: Diagnose

Analyze the target skill's current state:

```bash
# Scan local skill ecosystem
python3 scripts/skill_discovery.py --target <skill-name> --find-similar

# Check skill health
python3 scripts/local_skill_analyzer.py --skill <skill-name>

# Search external skills
npx skills find <keywords>
```

**Checklist:**
- [ ] Identify skill purpose and target scenarios
- [ ] Analyze trigger effectiveness (description clarity, keyword coverage)
- [ ] Review structure (completeness, organization, references)
- [ ] Check for similar skills (overlap/merge opportunities)
- [ ] Assess tooling (scripts, templates, automation)

### Phase 2: Analyze

Compare and identify improvement opportunities:

| Analysis Type | Tool | Output |
|--------------|------|--------|
| Local discovery | `skill_discovery.py` | Similar skills in `~/.claude/skills/` |
| External discovery | `npx skills find` | Skills from skills.sh ecosystem |
| Local analysis | `local_skill_analyzer.py` | Health score, improvement suggestions |
| Multi-skill compare | `local_skill_analyzer.py --compare` | Gap analysis, fusion recommendations |

**Key questions:**
1. What capabilities are missing?
2. What content is outdated or redundant?
3. Which similar skills could be merged?
4. What tools would improve usability?

### Phase 3: Improve

Execute improvements based on analysis:

**Description optimization:**
- Follow pattern: `<What>. Use when <triggers>. <Capabilities>.`
- Include action verbs and domain keywords
- Keep under 200 words

**Structure improvements:**
- Move deep content to `references/`
- Keep SKILL.md under 500 lines
- Use progressive disclosure (metadata → body → bundled resources)

**Tooling additions:**
- Add scripts only for non-trivial, multi-step operations
- Place templates in `assets/`, deep docs in `references/`

**Research enhancement:**
- Use WebSearch/WebFetch for latest practices
- Add academic sources to `references/research.md`

### Phase 4: Validate

Verify improvements:

- [ ] SKILL.md parses correctly
- [ ] Description covers what/when/capabilities
- [ ] All referenced files exist
- [ ] Scripts are executable and tested
- [ ] No duplication with other skills (post-merge)

## Quick Commands

```bash
# Analyze single skill
python3 scripts/local_skill_analyzer.py --skill <name> [--output report.json]

# Compare multiple skills
python3 scripts/local_skill_analyzer.py --compare skill-a skill-b skill-c

# Discover similar skills locally
python3 scripts/skill_discovery.py --target <skill-name> --find-similar --top-k 5

# Search external skill ecosystem
npx skills find <query>

# Scan all local skills
python3 scripts/skill_discovery.py --scan-all
```

## Scripts

| Script | Purpose |
|--------|---------|
| `skill_discovery.py` | Scan local skill ecosystem, find similar skills |
| `local_skill_analyzer.py` | Analyze skill health, compare skills, suggest improvements |
| `desc_optimizer.py` | Optimize skill description for trigger coverage |
| `skill_doctor.sh` | Comprehensive skill diagnostic |

## References

- `references/official_best_practices.md` - Claude skill creation standards
- `references/skill_examples.md` - Concrete skill patterns
- `references/research_expander.py` - Academic resource retrieval

## Anti-Patterns to Avoid

| Pattern | Why Avoid | Alternative |
|---------|-----------|-------------|
| Keyword stuffing in description | Reduces clarity | Natural language with key terms |
| Duplicating Claude's built-in knowledge | Wasted tokens | Reference external docs |
| Wrapper scripts for single commands | Unnecessary abstraction | Document the command directly |
| Deep nesting (>3 levels) | Hard to follow | Flatten structure, use references |
| Creating README/CHANGELOG/INSTALL | Unnecessary files | Keep info in SKILL.md or references/ |
| No clear trigger conditions | Skill won't activate | Explicit "Use when" in description |

## Checklist: Quality Skill

- [ ] Frontmatter: name, description (what+when+capabilities)
- [ ] Description < 200 words, includes trigger phrases
- [ ] SKILL.md < 500 lines
- [ ] Scripts/ only for complex, multi-step operations
- [ ] References/ for docs loaded on demand
- [ ] Assets/ for templates/images (not loaded into context)
- [ ] All file references from SKILL.md (so Claude discovers them)
- [ ] Clear workflow with actionable steps
- [ ] Tool scripts executable and tested

## Relationships

```
skill-creator: Create new skills (adjacent capability)
skill-refiner (this): Improve existing skills, merge skills, discover skills
```

Use skill-creator for "create new skill", skill-refiner for "improve existing skill".

## Recent Changes

caf7271 refactor(skill-refiner): remove NotebookLM dependency, use local analyzer instead
4fe08fa feat(skill-refiner): integrate find-skills and local analyzer for skill discovery
5378a8c fix(build): fix ARM cross-compilation and QEMU virt boot
