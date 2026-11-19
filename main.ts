import { execFileSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const entry = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

let rendered = false;
try {
  execFileSync("python3", [join(here, "broadsheet.py")], { stdio: "inherit" });
  rendered = existsSync(entry);
} catch {
  rendered = false;
}
if (!rendered && !existsSync(entry)) {
  throw new Error("entry.png missing and renderer unavailable");
}
const buf = readFileSync(entry);
const isPng = buf.length > 8 && buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e && buf[3] === 0x47;
if (!isPng) throw new Error("entry.png is not a PNG");
const w = buf.readUInt32BE(16);
const h = buf.readUInt32BE(20);
if (w !== 1024 || h !== 1024) throw new Error(`bad size ${w}x${h}`);
if (buf.length > 1024 * 1024) throw new Error(`too large ${buf.length}`);
mkdirSync(outDir, { recursive: true });
copyFileSync(entry, join(outDir, "entry.png"));
console.log(`OK entry.png ${w}x${h} ${buf.length} bytes -> ${outDir}`);
