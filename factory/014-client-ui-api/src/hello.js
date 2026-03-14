/*
 * CTB Metadata
 * ctb_id: CTB-5F9DA8B68024
 * ctb_branch: ui
 * ctb_path: ui/api/hello.js
 * ctb_version: 1.0.0
 * created: 2025-10-23T16:37:01.264383
 * checksum: 4be03931
 */

export default function handler(request, response) {
  response.status(200).json({
    message: 'Hello from API!',
    url: request.url,
    method: request.method
  });
}