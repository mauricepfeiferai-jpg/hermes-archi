# Agent Reach Security Gates

## Hard Stops (Never Without Explicit Approval)

1. Extracting browser cookies from Chrome/Safari/Firefox.
2. Installing any binary that hooks into the browser.
3. Storing social-media credentials in plain text.
4. Running on the Hermes/OpenClaw production gateway.
5. Enabling Facebook/Instagram/LinkedIn scraping without legal review.
6. Using a server proxy with embedded credentials.

## Privacy Rules

- Cookies must stay local to the machine where they were extracted.
- No uploading session tokens to GitHub, cloud, or shared state.
- No scraping private profiles, DMs, or non-public data.

## Network Rules

- Prefer local execution.
- If server deployment needed, use a dedicated isolated VM/container.
- No exposing agent-reach ports to the public internet.
