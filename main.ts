// THE WHOLE DAY — Broadsheet Edition (news-image-20261119, entry #2).
// Node 22 entrypoint: renders a fresh entry.png with the Python/PIL renderer
// (daypage.py), validates it (PNG magic, 1024x1024, <= 1 MiB) and copies it to
// the output directory. If python3/PIL is unavailable, it falls back to the
// committed entry.png beside this file.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { execFileSync } from 'node:child_process';
import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const rendered = join(here, 'entry.png');
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

function isValidPng(path) {
  const buf = readFileSync(path);
  if (buf.length > 1024 * 1024) return false;
  const magic = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
  if (!magic.every((b, i) => buf[i] === b)) return false;
  const width = buf.readUInt32BE(16);
  const height = buf.readUInt32BE(20);
  return width === 1024 && height === 1024;
}

let fresh = false;
try {
  execFileSync('python3', [join(here, 'daypage.py')], { stdio: 'inherit' });
  fresh = isValidPng(rendered);
  if (!fresh) console.error('Fresh render failed validation; using committed entry.png');
} catch {
  console.error('python3/PIL unavailable; using committed entry.png');
}

if (!fresh && !isValidPng(rendered)) {
  throw new Error('No valid entry.png available');
}

mkdirSync(outDir, { recursive: true });
copyFileSync(rendered, join(outDir, 'entry.png'));
console.log(`entry.png -> ${join(outDir, 'entry.png')}`);
