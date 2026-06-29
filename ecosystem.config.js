// pm2 ecosystem — hermes-archi Core4
// Start: pm2 start ecosystem.config.js
// Stop:  pm2 stop hermes-archi
// Logs:  pm2 logs

const ENV = {
  OLLAMA_URL: 'http://localhost:11434',
  JARVIS_MODEL: 'north-mini-code-1.0:q4_K_M',
  OPENCLAW_MODEL: 'north-mini-code-1.0:q4_K_M',
  HARVEY_MODEL: 'north-mini-code-1.0:q4_K_M',
  HARVEY_FALLBACK_MODEL: 'qwen3:8b',
  HERMES_KG_DB: `${process.env.HOME}/.hermes/knowledge_graph.db`,
  JARVIS_MEMORY_DB: `${process.env.HOME}/.hermes/jarvis_memory.db`,
  GOALS_DIR: `${process.env.HOME}/.hermes/goals`,
  HARVEY_USAGE_DIR: `${process.env.HOME}/.hermes/legal_usage`,
  REDIS_URL: 'redis://localhost:6379/0',
  LOG_LEVEL: 'INFO',
};

module.exports = {
  apps: [
    {
      name: 'core4-hermes',
      cwd: `${process.env.HOME}/ai-empire/projects/hermes-archi`,
      script: '.venv/bin/python',
      args: 'control-plane/hermes/runtime/main.py',
      interpreter: 'none',
      env: { ...ENV, HERMES_PORT: '18890' },
      autorestart: true,
      max_restarts: 10,
      restart_delay: 3000,
    },
    {
      name: 'core4-jarvis',
      cwd: `${process.env.HOME}/ai-empire/projects/hermes-archi`,
      script: '.venv/bin/python',
      args: 'control-plane/jarvis/runtime/main.py',
      interpreter: 'none',
      env: {
        ...ENV,
        JARVIS_PORT: '18891',
        AGENT_PORT: '18891',
        HERMES_URL: 'http://127.0.0.1:18890',
        JARVIS_URL: 'http://127.0.0.1:18891',
        AGENT_URL: 'http://127.0.0.1:18891',
      },
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
    },
    {
      name: 'core4-openclaw',
      cwd: `${process.env.HOME}/ai-empire/projects/hermes-archi`,
      script: '.venv/bin/python',
      args: 'control-plane/openclaw/runtime/main.py',
      interpreter: 'none',
      env: {
        ...ENV,
        OPENCLAW_PORT: '18892',
        AGENT_PORT: '18892',
        HERMES_URL: 'http://127.0.0.1:18890',
        OPENCLAW_URL: 'http://127.0.0.1:18892',
        AGENT_URL: 'http://127.0.0.1:18892',
      },
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
    },
    {
      name: 'core4-harvey',
      cwd: `${process.env.HOME}/ai-empire/projects/hermes-archi`,
      script: '.venv/bin/python',
      args: 'control-plane/harvey/runtime/main.py',
      interpreter: 'none',
      env: {
        ...ENV,
        HARVEY_PORT: '18893',
        AGENT_PORT: '18893',
        HERMES_URL: 'http://127.0.0.1:18890',
        HARVEY_URL: 'http://127.0.0.1:18893',
        AGENT_URL: 'http://127.0.0.1:18893',
      },
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
    },
  ],
};
