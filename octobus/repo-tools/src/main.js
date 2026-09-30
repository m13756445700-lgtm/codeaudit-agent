#!/usr/bin/env node
import { defineService, runServiceMain } from '@chaitin-ai/octobus-sdk';
import { spawn } from 'node:child_process';

const methods = ['ExecuteTool'];
let busy = false;
function handler(method) {
  return async (ctx) => {
    if (busy) return { resultJson: JSON.stringify({error: 'SERVICE_BUSY'}) };
    const request = JSON.parse(ctx.request.requestJson);
    busy = true;
    try {
      if (ctx.config.repoEndpoint && ctx.config.staticEndpoint) {
        const endpoint = request.tool === 'static.semgrep' ? ctx.config.staticEndpoint : ctx.config.repoEndpoint;
        const response = await fetch(endpoint + '/execute', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(request), signal: AbortSignal.timeout(150000), redirect: 'error',
        });
        if (!response.ok) throw new Error('CAPABILITY_HTTP_' + response.status);
        const reader = response.body.getReader();
        let size = 0; const chunks = [];
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          size += value.byteLength;
          if (size > 1048576) { await reader.cancel(); throw new Error('OUTPUT_LIMIT'); }
          chunks.push(value);
        }
        const output = Buffer.concat(chunks).toString('utf8');
        JSON.parse(output);
        return { resultJson: output };
      }
      return await new Promise((resolve, reject) => {
        const p = spawn(ctx.config.pythonPath, ['-m', 'agent.v2.tools'], {
          cwd: ctx.config.applicationRoot,
          env: { PATH: process.env.PATH, HOME: process.env.HOME,
            CODEAUDIT_WORKSPACES: ctx.config.workspaces },
          stdio: ['pipe', 'pipe', 'pipe'],
        });
        let output = '';
        const timer = setTimeout(() => { p.kill('SIGKILL'); reject(new Error('VALIDATION_TIMEOUT')); }, 150000);
        p.stdout.on('data', data => {
          output += data;
          if (output.length > 1048576) { p.kill('SIGKILL'); reject(new Error('OUTPUT_LIMIT')); }
        });
        p.stderr.resume();
        p.on('error', () => { clearTimeout(timer); reject(new Error('WORKER_START_FAILED')); });
        p.on('close', code => {
          clearTimeout(timer);
          if (code !== 0) return reject(new Error('CONTROLLED_METHOD_FAILED'));
          try { JSON.parse(output); resolve({ resultJson: output }); }
          catch { reject(new Error('INVALID_WORKER_RESPONSE')); }
        });
        p.stdin.on('error', () => {});
        p.stdin.end(JSON.stringify(request));
      });
    } catch (error) {
      const code = String(error?.message || 'CAPABILITY_FAILED');
      const safe = /^(CAPABILITY_HTTP_[0-9]{3}|OUTPUT_LIMIT|VALIDATION_TIMEOUT|WORKER_START_FAILED|CONTROLLED_METHOD_FAILED|INVALID_WORKER_RESPONSE)$/.test(code) ? code : 'CAPABILITY_FAILED';
      return { resultJson: JSON.stringify({error: safe}) };
    } finally { busy = false; }
  };
}
runServiceMain(defineService({handlers: Object.fromEntries(methods.map(m => [`codeaudit.v2.RepositoryTools/${m}`, handler(m)]))}));
