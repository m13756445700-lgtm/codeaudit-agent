const express = require('express');
const app = express();
const cp = require('child_process');
app.get('/echo', (req, res) => {
  const name = req.query.name;
  cp.execFile('/bin/echo', ['--', name], (err, stdout) => res.send(stdout));
});
