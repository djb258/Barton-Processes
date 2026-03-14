/*
 * CTB Metadata
 * ctb_id: CTB-6DF5A22CE337
 * ctb_branch: ui
 * ctb_path: ui/api/test.js
 * ctb_version: 1.0.0
 * created: 2025-10-23T16:37:01.291265
 * checksum: dc044c85
 */

export default function handler(req, res) {
  res.status(200).json({ 
    message: 'API is working!', 
    method: req.method,
    timestamp: new Date().toISOString()
  });
}