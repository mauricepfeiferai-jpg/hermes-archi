# BuilderIO Agent Native Integration Plan

## Source
https://github.com/BuilderIO/agent-native.git

## Purpose
Integrate BuilderIO's agent-native approach into the AI Empire/Hermes agent system.
Potential use cases:
- Native mobile/desktop agent runtime
- UI generation from natural language
- Cross-platform agent deployment
- Visual editing powered by agents

## Integration Targets

### 1. Hermes Runtime
- Evaluate if agent-native patterns can replace or augment Hermes CLI dispatch
- Check compatibility with existing `ops/cron/run_agent.py`

### 2. One-Person AI Agent Company Template
- Add a "UI Agent" role if BuilderIO provides agent-driven UI generation
- Wire UI generation into writer/engineer workflow

### 3. Product Factory
- Use agent-native to generate landing pages or product UIs automatically
- Connect to existing Netlify deploy pipeline

## Safety Rules
1. Evaluate in isolated directory first
2. No production code changes until compatibility verified
3. Do not replace existing deployment pipeline without approval
4. Document all dependencies and licenses

## Evaluation Plan
1. Clone repo into `~/ai-empire/projects/hermes-archi/integrations/builderio-agent-native/repo/`
2. Read README + architecture
3. Identify entry points and APIs
4. Run minimal example if available
5. Document integration decision: adopt / adapt / skip

## Status
STAGED — NOT CLONED — NOT IN PRODUCTION

## Next Approval
APPROVE BUILDERIO AGENT-NATIVE ISOLATED EVALUATION ONLY
