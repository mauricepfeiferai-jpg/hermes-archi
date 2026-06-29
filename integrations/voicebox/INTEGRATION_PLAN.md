# Voicebox Integration Plan

## Source
https://github.com/jamiepine/voicebox.git

## Purpose
Add voice interaction to the one-person AI agent company. Voicebox turns the agent system into a voice-controlled assistant that can:
- Accept voice commands
- Read agent outputs aloud
- Trigger cron jobs by voice
- Dictate content drafts

## Integration Targets

### 1. CEO Agent
- Voice input for daily priorities
- Reads `ceo/outputs/daily_goals_*.md` aloud

### 2. Writer Agent
- Voice dictation for content drafts
- Converts draft to markdown in `writer/outputs/`

### 3. Loop Agent
- Voice summary of daily review
- Reads patch proposals aloud

### 4. Dashboard
- Add "Mic" button to trigger Voicebox
- Live transcription status

## Safety Rules

1. Voicebox runs in isolated subprocess / container
2. No always-on microphone without explicit user approval
3. All voice-triggered actions must route through approval gate
4. No production deploy until isolated evaluation passes

## Evaluation Plan

1. Clone repo into `~/ai-empire/projects/hermes-archi/integrations/voicebox/repo/`
2. Read README + requirements
3. Install dependencies in isolated venv
4. Run a single voice command test
5. Document success/failure

## Status
STAGED — NOT INSTALLED — NOT IN PRODUCTION

## Next Approval
APPROVE VOICEBOX ISOLATED EVALUATION ONLY
