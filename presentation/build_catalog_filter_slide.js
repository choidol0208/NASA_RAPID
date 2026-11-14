// AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps
// Challenge 2026 hackathon (2026-11-14). Builds one explainer slide for the catalog filter.
// Usage: NODE_PATH=$(npm root -g) node presentation/build_catalog_filter_slide.js <path-to-apply_theme.js>
const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const { TbFlame, TbAdjustmentsHorizontal, TbCircleCheck } = require("react-icons/tb"); // Tabler Icons, MIT

const THEME = {
  name: "Flame in Freefall",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "14213D", lt1: "FFFFFF", dk2: "33415C", lt2: "EEF2F7",
    accent1: "E8590C", accent2: "1D4E89", accent3: "2A9D8F", accent4: "F2A541",
    accent5: "6C7A93", accent6: "9AA5B8", hlink: "1D4E89", folHlink: "6C7A93",
  },
};
const HEX = THEME.colors;

async function icon(Comp, color) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: 256 }));
  const buf = await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

async function main() {
  const applyThemePath = process.argv[2];
  const out = path.join(__dirname, "catalog_filter_slide.pptx");
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.title = "Catalog filter";
  const C = pres.SchemeColor;

  pres.defineSlideMaster({
    title: "TITLE_ONLY",
    background: { color: "FFFFFF" },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 12.33, h: 0.75,
        fontSize: 34, bold: true, color: C.text1, valign: "middle", align: "left", margin: 0 }, text: "" } },
      { text: { text: "Data: NASA Physical Sciences Informatics, 24 combustion investigations (CC0-1.0). Scores and classifications are the team's method, not NASA conclusions. Built with AI assistance (Claude).",
        options: { x: 0.5, y: 7.0, w: 12.33, h: 0.3, fontSize: 10, color: C.accent5, margin: 0, isTextBox: true } } },
    ],
  });

  const s = pres.addSlide({ masterName: "TITLE_ONLY" });
  s.addText("Catalog filter: ranking PSI evidence for a habitat scenario", { placeholder: "title" });
  s.addText("A combustion-based similarity score, computed in code and explained on screen", {
    x: 0.5, y: 1.05, w: 12.33, h: 0.35, fontSize: 15, italic: true, color: C.accent5, margin: 0, isTextBox: true, objectName: "subtitle" });

  // ---- pipeline strip
  const steps = [
    ["Rough input", "\"ISS\", \"moon base cotton\" (EN/KO), or exact values"],
    ["Interpret", "presets, keywords, numbers; assumptions shown"],
    ["Score 41 test configurations", "similarity 0–1 on 7 dimensions"],
    ["Gate × evidence quality", "no compensation for wrong fuel or O2"],
    ["Top 3 + warnings", "one per investigation, linked to PSI"],
  ];
  const sx = 0.5, sw = 2.25, gap = 0.27, sy = 1.6, sh = 0.95;
  steps.forEach(([h, d], i) => {
    const x = sx + i * (sw + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: sy, w: sw, h: sh, rectRadius: 0.08,
      fill: { color: i === 4 ? HEX.accent1 : HEX.lt2 }, line: { color: i === 4 ? HEX.accent1 : HEX.lt2 }, objectName: `step-${i + 1}` });
    s.addText([
      { text: h, options: { bold: true, fontSize: 14, color: i === 4 ? "FFFFFF" : HEX.dk1, breakLine: true } },
      { text: d, options: { fontSize: 11, color: i === 4 ? "FFFFFF" : HEX.dk2 } },
    ], { x: x + 0.1, y: sy + 0.05, w: sw - 0.2, h: sh - 0.1, valign: "middle", margin: 0, isTextBox: true, objectName: `step-text-${i + 1}` });
    if (i < steps.length - 1) {
      s.addShape(pres.shapes.RIGHT_ARROW, { x: x + sw + 0.04, y: sy + sh / 2 - 0.1, w: 0.19, h: 0.2,
        fill: { color: HEX.accent6 }, line: { color: HEX.accent6 }, objectName: `arrow-${i + 1}` });
    }
  });

  // ---- three cards
  const cy = 2.85, ch = 3.95, cw = 3.9, cg = 0.315;
  const cards = [
    { title: "Combustion concepts", icon: await icon(TbFlame, HEX.accent1), items: [
      ["O2 mole fraction ", "drives flammability. Above the tested O2 the real fire may be worse, so the score drops faster above the range than below it."],
      ["No buoyancy in μg: ", "fans supply the oxygen. Flames die at very low flow (radiative loss) and very high flow (blow-off, low Damköhler number), so flow is compared on a log scale; opposed and concurrent spread differ."],
      ["Fuel and thickness: ", "phase, melting vs charring, thermally thin vs thick change how a flame spreads."],
      ["Pressure ", "matters less; compared as a ratio."],
    ] },
    { title: "Mechanism", icon: await icon(TbAdjustmentsHorizontal, HEX.accent2), formula: true, items: [
      ["Sᵢ ", "similarity 0–1: O2, pressure, flow, fuel, shape, research purpose, diluent"],
      ["wᵢ ", "weights by question. Prevention: O2 .25, fuel .25, flow .20, pressure .10, shape .10, purpose .10"],
      ["G ", "gate 0.5–1 when fuel or O2 similarity is below 0.2"],
      ["M ", "evidence quality 0.7–1.0: raw data, flight time, human check"],
      ["\"ISS\" alone ", "→ 21% O2, 101.3 kPa, ventilated, each listed as an assumption"],
    ] },
    { title: "Validation", icon: await icon(TbCircleCheck, HEX.accent3), stat: true, items: [
      ["Traps: ", "spacesuit 100% O2 → extrapolation warning (PSI max 85%); Mars → no partial-gravity data; rockets → out of scope"],
      ["Stable: ", "rank 1 unchanged when any weight moves by ±0.05"],
      ["Example: ", "lunar base + cotton fabric → SAFFIRE-II, BASS-II (tested ≤22% O2, flagged) + ACME-BRE (21–40% O2)"],
    ] },
  ];
  for (let i = 0; i < cards.length; i++) {
    const cd = cards[i];
    const x = 0.5 + i * (cw + cg);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: cy, w: cw, h: ch, rectRadius: 0.06,
      fill: { color: "F7F9FC" }, line: { color: "DCE3EE", width: 1 }, objectName: `card-${i + 1}` });
    s.addShape(pres.shapes.OVAL, { x: x + 0.22, y: cy + 0.2, w: 0.5, h: 0.5, fill: { color: "FFFFFF" }, line: { color: "DCE3EE" }, objectName: `icon-bg-${i + 1}` });
    s.addImage({ data: cd.icon, x: x + 0.32, y: cy + 0.3, w: 0.3, h: 0.3, altText: cd.title + " icon" });
    s.addText(cd.title, { x: x + 0.85, y: cy + 0.2, w: cw - 1.0, h: 0.5, fontSize: 20, bold: true, color: HEX.dk1, valign: "middle", margin: 0, isTextBox: true });
    let y = cy + 0.85;
    if (cd.formula) {
      s.addText("Score = 100 × M × G × Σ wᵢ·Sᵢ", { x: x + 0.22, y, w: cw - 0.44, h: 0.42, fontSize: 16, bold: true,
        color: HEX.accent2, fill: { color: "FFFFFF" }, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "formula" });
      y += 0.52;
    }
    if (cd.stat) {
      s.addText([{ text: "22/22", options: { fontSize: 36, bold: true, color: HEX.accent3 } }],
        { x: x + 0.22, y: y - 0.05, w: 1.5, h: 0.6, margin: 0, valign: "middle", isTextBox: true, objectName: "stat" });
      s.addText("scenarios pass: rough and Korean inputs, prevention, detection, suppression, liquids, traps", {
        x: x + 1.72, y: y - 0.05, w: cw - 1.94, h: 0.6, fontSize: 11, color: HEX.dk2, margin: 0, valign: "middle", isTextBox: true });
      y += 0.65;
    }
    const runs = [];
    cd.items.forEach(([b, t], k) => {
      runs.push({ text: b, options: { bold: true, color: HEX.dk1, bullet: true } });
      runs.push({ text: t, options: { color: HEX.dk2, breakLine: k < cd.items.length - 1 } });
    });
    s.addText(runs, { x: x + 0.22, y, w: cw - 0.44, h: cy + ch - y - (cd.stat ? 0.5 : 0.15), fontSize: 12, valign: "top",
      paraSpaceAfter: 5, margin: 0, isTextBox: true, objectName: `card-body-${i + 1}` });
    if (cd.stat) {
      s.addText("Expected answers are team judgement from combustion reasoning; expert review pending.", {
        x: x + 0.22, y: cy + ch - 0.48, w: cw - 0.44, h: 0.38, fontSize: 10, italic: true, color: HEX.accent5, margin: 0, isTextBox: true });
    }
  }

  s.addNotes([
    "Speaker notes",
    "1) Concept: in microgravity there is no buoyancy, so the fan's airflow supplies the oxygen. If the flow is too weak, the flame goes out from radiative heat loss and lack of oxygen; if it is too strong, there is too little time to react (the Damköhler number falls). So the flammability limit is U-shaped on the plane of oxygen concentration and flow speed, and we weigh these two axes and the fuel most. Oxygen above the tested range could mean a worse real fire (non-conservative), so a departure upwards costs more points.",
    "2) Implementation: even a single word such as 'ISS' is read as a preset (21% O2, 101.3 kPa, ventilated), and every assumed value is shown on screen. The 24 investigations are split into 41 test configurations; similarity is computed on 7 dimensions and combined with weights for the kind of question (prevention, detection, suppression). A gate keeps other scores from making up for a very different fuel or oxygen level, and the total is multiplied by 0.7 to 1.0 for data quality. For each investigation only the most similar configuration is shown.",
    "3) Validation: 22 scenarios, whose expected answers the team set first from combustion reasoning, run automatically. A 100% oxygen spacesuit is above the PSI maximum (the 85% oxidizer stream of the inverse flames), so it gets an extrapolation warning; Mars is handled as having no partial-gravity data, and a rocket as out of scope. We checked that rank 1 stays the same when the weights change by ±0.05. We say plainly that the expected answers are the team's judgement and still await expert review.",
    "(These notes describe the first version, 14 Nov 2026, 10:30 KST. Since then: 35 validation scenarios; oxygen above the range is measured against the highest surrounding-atmosphere oxygen tested, 40%, and the 85% burner stream is no longer compared with a habitat atmosphere; weight sensitivity is checked at x0.5 and x1.5 of each weight.)",
  ].join("\n\n"));

  await pres.writeFile({ fileName: out });
  if (applyThemePath) {
    const { applyTheme } = require(applyThemePath);
    await applyTheme(out, THEME);
  }
  console.log("wrote", out);
}
main().catch((e) => { console.error(e); process.exit(1); });
