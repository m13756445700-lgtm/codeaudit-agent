#!/usr/bin/env node
import { defineService, runServiceMain } from '@chaitin-ai/octobus-sdk';
import { spawn } from 'node:child_process';

const methods = ['InventoryRepository', 'ScanCandidates', 'ReadCodeSlice', 'HashEvidence', 'RunValidation'];
let busy = false;
function handler(method) {
  return async (ctx) => {
    if (busy) throw new Error('SERVICE_BUSY');
    const request = JSON.parse(ctx.request.requestJson);
    busy = true;
    try {
      return await new Promise((resolve, reject) => {
        const p = spawn(ctx.config.pythonPath, ['-m', 'agent.service'], {
          cwd: ctx.config.applicationRoot,
          env: { PATH: process.env.PATH, HOME: process.env.HOME,
            CODEAUDIT_REPOSITORY_ROOT: ctx.config.repositoryRoot,
            CODEAUDIT_OUTPUT_ROOT: ctx.config.outputRoot },
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
        p.stdin.end(JSON.stringify({method, request}));
      });
    } finally { busy = false; }
  };
}
runServiceMain(defineService({handlers: Object.fromEntries(methods.map(m => [`codeaudit.v1.CodeAuditService/${m}`, handler(m)]))}));
