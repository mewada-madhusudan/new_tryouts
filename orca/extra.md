instructions/ loads first, silently, based on file glob match — this is baseline context on every single message, no selection needed.
You (or a handoff) select an agent from agents/ — that becomes the active persona + tool scope for the session.
Mid-task, if the request matches a skill's description, Copilot pulls it in automatically — e.g. firm-ops agent gets a Jira question, playwright-auth-bridge's SKILL.md description matches, its scripts become available to run via terminal.
hooks/ run silently around all of this — e.g. intercepting an edit attempt on a path listed in BOUNDARIES.md before it happens, as a hard backstop below the "please don't" instruction-level enforcement I wrote into firm-ops.agent.md.
prompts/ and workflows/ sit outside this live loop entirely — prompts wait for someone to type /command, workflows only run when GitHub Actions triggers them (a push, a PR, a schedule).
plugin/ isn't read at runtime at all — it's just packaging, for when you want to hand this whole setup to a teammate as one install command instead of them copying folders.



Atlassian (Jira, Confluence, Compass)
Microsoft 365 (SharePoint, Teams, Outlook, OneDrive)
Bitbucket
Docker
Databricks
Figma
ServiceNow
