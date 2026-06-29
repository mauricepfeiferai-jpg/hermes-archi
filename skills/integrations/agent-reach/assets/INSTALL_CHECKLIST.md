# Agent Reach Install Checklist

## Before Install

- [ ] Isolated venv created (`~/.venvs/agent-reach`)
- [ ] `pip install -e . --dry-run` reviewed
- [ ] No conflicts with existing Hermes/OpenClaw dependencies
- [ ] `agent-reach doctor --dry-run` reviewed
- [ ] Maurice explicitly approved install

## Install

- [ ] Install in isolated venv
- [ ] Run `agent-reach doctor`
- [ ] Confirm zero-config channels work:
  - [ ] web reader
  - [ ] YouTube
  - [ ] RSS
  - [ ] V2EX
- [ ] Test one cookie-required channel only after approval

## Post-Install

- [ ] Add channel commands to relevant agent roles (researcher, content, writer)
- [ ] Document which channels are enabled
- [ ] Update `~/.hermes/model-policy.env` if needed
- [ ] Run 100x self-improvement loop retro
