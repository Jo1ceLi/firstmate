# T3 rename validation

Real Firstmate CLI calls used disposable loopback T3 servers and a disposable Git project. Official stable 0.1.3 and old nightly downloads matched GitHub release SHA-256 digests. Final server runs isolated HOME, CODEX_HOME, and CLAUDE_CONFIG_DIR inside the worktree.

The forwarding proxy recorded actual MCP calls. Fault injection removed advertised tools only. It did not synthesize successful product responses. All three versions passed idle launch, binding read-back, empty question query, refusal of a nonexistent question response, and confirmed archive. Removing the pending-request capability blocked launch before any tool call. Removing both configuration names blocked status.

The old nightly advertised both configuration names. Calling its newer name without modelSelection rejected missing modelSelection, while Firstmate successfully used the older read-only name. Baseline code reproduced capability_gate on the current nightly.

The targeted tests/fm-t3-mcp.test.sh passed against its fake server. They cover merged question list/read/respond, complete families, and preference with both pending-request generations. They are not live question-lifecycle evidence.

A real pending-question lifecycle remains untested. Isolated Codex login status reported Not logged in. No credentials were copied, normal provider login was not used, and no model turn was started. Provide a disposable authenticated provider environment or explicitly authorize normal Claude login to generate and answer real questions. This does not establish that normal machine login is unavailable.

The recording proxy may be reported as telemetry on because its process lacks the T3 environment flag. Actual final T3 servers ran with T3CODE_TELEMETRY_ENABLED=false.

This CLI-only change has no rendered UI evidence. All three servers stopped and ports closed before removing the disposable lab. No source files changed.
