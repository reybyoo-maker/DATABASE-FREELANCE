/**
 * DATABASE-FREELANCE Google Sheets receiver.
 * Deploy as a Web App (execute as Me), then set Script Property WEBHOOK_TOKEN.
 * This endpoint stores data only; it never sends outreach messages.
 */
const TZ = "Asia/Jakarta";
const PROSPECT_TAB = "Prospects";
const RUNS_TAB = "Runs";
const HEADERS = [
  ["prospect_id", "Prospect ID"],
  ["company_name", "Company Name"],
  ["country", "Country"],
  ["city", "City / Region"],
  ["industry", "Industry"],
  ["website", "Website"],
  ["whatsapp_url", "WhatsApp URL"],
  ["public_phone", "Public Phone (not assumed WhatsApp)"],
  ["public_email", "Public Email"],
  ["instagram", "Instagram"],
  ["facebook", "Facebook"],
  ["linkedin", "LinkedIn"],
  ["tiktok", "TikTok"],
  ["other_social", "Other Social"],
  ["source_url", "Source URL"],
  ["source_name", "Source Name"],
  ["evidence", "Public Source Evidence"],
  ["discovered_at_utc", "First Discovered (UTC)"],
  ["need_audit", "AI Need Audit"],
  ["recommended_service", "Recommended Service"],
  ["prospect_score", "Prospect Score (0-100)"],
  ["prospect_grade", "Prospect Grade"],
  ["grade_reason", "Grade Reason"],
  ["outreach_language", "Outreach Language"],
  ["outreach_dm", "Copy-Paste Social DM"],
  ["outreach_email_subject", "Copy-Paste Email Subject"],
  ["outreach_email_body", "Copy-Paste Email Body"],
  ["outreach_whatsapp", "Copy-Paste WhatsApp Message"],
  ["outreach_status", "Outreach Status"],
  ["data_quality", "Data Quality"],
  ["added_at_jakarta", "Added At (Jakarta)"],
  ["portfolio_service_match", "Portfolio Service Match"],
  ["relevant_portfolio_url", "Relevant Portfolio Example URL"]
];

function doPost(e) {
  try {
    const body = JSON.parse((e && e.postData && e.postData.contents) || "{}");
    const expected = PropertiesService.getScriptProperties().getProperty("WEBHOOK_TOKEN");
    if (!expected || !body.token || !constantTimeEqual_(String(body.token), String(expected))) {
      return json_({ok: false, error: "Unauthorized"});
    }
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    if (!ss) return json_({ok: false, error: "No active spreadsheet. Create/deploy this script from the target Sheet."});
    const sheets = ensureSheets_(ss);
    if (body.action === "stats") {
      return json_({ok: true, daily_count: countToday_(sheets.prospects), date_jakarta: Utilities.formatDate(new Date(), TZ, "yyyy-MM-dd")});
    }
    if (body.action !== "append") return json_({ok: false, error: "Unknown action"});
    const prospects = Array.isArray(body.prospects) ? body.prospects : [];
    if (prospects.length > 50) return json_({ok: false, error: "Maximum 50 prospects per request"});
    const sh = sheets.prospects;
    const ids = new Set();
    const last = sh.getLastRow();
    if (last > 1) {
      sh.getRange(2, 1, last - 1, 1).getDisplayValues().forEach(row => {
        if (row[0]) ids.add(String(row[0]));
      });
    }
    const rows = [];
    let skipped = 0;
    for (const p of prospects) {
      if (!p || !p.prospect_id || !p.company_name) { skipped++; continue; }
      const social = ["instagram", "facebook", "linkedin", "tiktok", "other_social"].some(k => p[k]);
      if (!p.whatsapp_url && !social) { skipped++; continue; }
      const id = String(p.prospect_id);
      if (ids.has(id)) { skipped++; continue; }
      ids.add(id);
      const row = HEADERS.map(([key]) => {
        if (key === "outreach_status") return "BELUM DIHUBUNGI";
        if (key === "added_at_jakarta") return new Date();
        return safeCell_(p[key]);
      });
      rows.push(row);
    }
    if (rows.length) {
      const startRow = sh.getLastRow() + 1;
      sh.getRange(startRow, 1, rows.length, HEADERS.length).setValues(rows);
      const dateCol = HEADERS.findIndex(x => x[0] === "added_at_jakarta") + 1;
      sh.getRange(startRow, dateCol, rows.length, 1).setNumberFormat("yyyy-mm-dd hh:mm:ss");
      const scoreCol = HEADERS.findIndex(x => x[0] === "prospect_score") + 1;
      sh.getRange(startRow, scoreCol, rows.length, 1).setNumberFormat("0");
    }
    const daily = countToday_(sh);
    sheets.runs.appendRow([
      new Date(),
      String(body.run_id || ""),
      prospects.length,
      rows.length,
      skipped,
      daily,
      Math.max(0, 100 - daily)
    ]);
    return json_({ok: true, inserted: rows.length, skipped_or_duplicate: skipped, received: prospects.length,
      daily_count: daily, target: 100, remaining_to_target: Math.max(0, 100 - daily)});
  } catch (err) {
    return json_({ok: false, error: String(err && err.message ? err.message : err)});
  }
}

function doGet() {
  return json_({ok: true, service: "DATABASE-FREELANCE Google Sheets receiver", message: "POST with configured token required."});
}

function ensureSheets_(ss) {
  let prospects = ss.getSheetByName(PROSPECT_TAB);
  if (!prospects) prospects = ss.insertSheet(PROSPECT_TAB);
  const desired = HEADERS.map(x => x[1]);
  if (prospects.getLastRow() === 0) {
    prospects.getRange(1, 1, 1, desired.length).setValues([desired]);
    prospects.setFrozenRows(1);
    prospects.getRange(1, 1, 1, desired.length).setFontWeight("bold");
    prospects.autoResizeColumns(1, Math.min(desired.length, 12));
  } else {
    // Preserve existing rows and validate every existing column before adding new trailing columns.
    const existingCount = prospects.getLastColumn();
    const compareCount = Math.min(existingCount, desired.length);
    const existing = prospects.getRange(1, 1, 1, compareCount).getDisplayValues()[0];
    for (let i = 0; i < compareCount; i++) {
      if (existing[i] !== desired[i]) {
        throw new Error("Prospects tab schema differs at column " + (i + 1) + ". Rename the tab or reconcile its headers before continuing.");
      }
    }
    if (existingCount < desired.length) {
      const newHeaders = desired.slice(existingCount);
      prospects.getRange(1, existingCount + 1, 1, newHeaders.length).setValues([newHeaders]);
      prospects.getRange(1, existingCount + 1, 1, newHeaders.length).setFontWeight("bold");
      prospects.autoResizeColumns(existingCount + 1, newHeaders.length);
    }
  }
  let runs = ss.getSheetByName(RUNS_TAB);
  if (!runs) runs = ss.insertSheet(RUNS_TAB);
  if (runs.getLastRow() === 0) {
    runs.appendRow(["Run At (Jakarta)", "Run ID", "Received", "Inserted", "Skipped / Duplicate", "Daily Total", "Remaining to Target"]);
    runs.setFrozenRows(1);
    runs.getRange(1, 1, 1, 7).setFontWeight("bold");
  }
  return {prospects: prospects, runs: runs};
}

function countToday_(sh) {
  const last = sh.getLastRow();
  if (last < 2) return 0;
  const col = HEADERS.findIndex(x => x[0] === "added_at_jakarta") + 1;
  const values = sh.getRange(2, col, last - 1, 1).getValues();
  const today = Utilities.formatDate(new Date(), TZ, "yyyy-MM-dd");
  return values.reduce((count, row) => {
    const v = row[0];
    if (!v) return count;
    try {
      const date = Utilities.formatDate(v instanceof Date ? v : new Date(v), TZ, "yyyy-MM-dd");
      return count + (date === today ? 1 : 0);
    } catch (_) { return count; }
  }, 0);
}

function safeCell_(value) {
  if (value === null || value === undefined) return "";
  if (typeof value === "number" || typeof value === "boolean") return value;
  const str = String(value).slice(0, 6000);
  // Prevent scraped text from being evaluated as a spreadsheet formula.
  return /^[=+\-@\t\r]/.test(str) ? "'" + str : str;
}

function constantTimeEqual_(a, b) {
  if (a.length !== b.length) return false;
  let mismatch = 0;
  for (let i = 0; i < a.length; i++) mismatch |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return mismatch === 0;
}

function json_(data) {
  return ContentService.createTextOutput(JSON.stringify(data)).setMimeType(ContentService.MimeType.JSON);
}
