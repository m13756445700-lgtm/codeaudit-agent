const express = require('express');
const app = express();
const Database = require('better-sqlite3');
const db = new Database('app.db');
app.get('/lookup', (req, res) => {
  const q = req.query.name;
  res.json(db.prepare('SELECT name FROM users WHERE name=?').all(q));
});
