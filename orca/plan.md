your-repo/
├── .github/
│   │
│   ├── agents/                          ← personas, selectable in chat, can hand off to each other
│   │   ├── orchestrator.agent.md
│   │   ├── planner.agent.md
│   │   ├── designer.agent.md
│   │   ├── developer.agent.md
│   │   └── firm-ops.agent.md
│   │
│   ├── skills/                          ← auto-triggered capabilities, ANY agent above can use these
│   │   └── playwright-auth-bridge/
│   │       ├── SKILL.md
│   │       └── scripts/                 ← the actual executable code a skill runs
│   │           ├── common/
│   │           │   └── auth-session.js
│   │           ├── jira-auth.js
│   │           ├── confluence-auth.js
│   │           ├── bitbucket-auth.js
│   │           └── sharepoint-auth.js
│   │
│   ├── instructions/                    ← passive, always-on context — not a persona, just rules
│   │   ├── copilot-instructions.md      ← (this one specific filename applies repo-wide, no frontmatter needed)
│   │   └── typescript.instructions.md   ← (applyTo: "**/*.ts" in frontmatter — scoped by glob)
│   │
│   ├── prompts/                         ← legacy/optional — explicit /command templates, mostly superseded by skills+agents now
│   │   └── (skip this folder unless you want a one-off /slash-command someone types deliberately)
│   │
│   ├── hooks/                           ← event-triggered guardrails, fire automatically on session events
│   │   ├── hooks.json                   ← declares which events trigger which script
│   │   └── scripts/
│   │       └── block-protected-paths.sh ← e.g. hard-enforce BOUNDARIES.md at the tool-call level, not just prompt level
│   │
│   ├── workflows/                       ← real GitHub Actions YAML/MD, runs in CI not in your chat session
│   │   └── nightly-doc-sync.md          ← e.g. "keep docs/DEVELOPMENT_STATUS.md synced with closed PRs, every night"
│   │
│   └── plugin/
│       └── plugin.json                 ← optional — bundles everything above into one installable unit for other repos
│
├── .vscode/
│   └── mcp.json                         ← MCP servers (github, playwright, internal-docs) — VS Code side
│
├── docs/
│   ├── README.md
│   ├── DEVELOPMENT_STATUS.md
│   ├── SUGGESTIONS.md
│   ├── BUGS_ISSUES.md
│   ├── BRD.md
│   ├── GUIDELINES.md
│   ├── plan.md                          ← written by Planner
│   └── design.md                        ← written by Designer
│
├── .auth/                                ← gitignored, live session cookies from playwright-auth-bridge
├── firm-tools.config.json
├── BOUNDARIES.md
└── .gitignore
