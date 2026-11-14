// AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
// Challenge 2026 hackathon (2026-11-14).
// Node side of the parity check: reads queries (JSON array) on stdin, prints the JS
// scorer's output for each as JSON. Called by web/parity_check.py.
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createScorer } from "./scorer.js";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const scorer = createScorer({
  config: JSON.parse(readFileSync(join(root, "scoring/scoring_config.json"), "utf8")),
  investigationsCsv: readFileSync(join(root, "data/catalog/investigations.csv"), "utf8"),
  configurationsCsv: readFileSync(join(root, "data/catalog/configurations.csv"), "utf8"),
});
const queries = JSON.parse(readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(queries.map((q) => scorer.rank(q))));
