const $a = (id) => document.getElementById(id);
const statusLabels = {
  confirmed: "已确认官方",
  candidate: "候选待验证",
  unverified: "未验证",
  excluded: "已排除",
  reachable: "可访问",
  unknown: "未知",
  access_error: "访问异常",
  integrated: "已接入",
  analyzing: "分析中",
  not_integrated: "未接入",
  blocked: "已阻断",
  high: "高质量",
  medium: "中质量",
  low: "低质量",
};
const reasonLabels = {
  detail_url_unresolved: "具体详情链接未确认",
  concrete_detail_url_unresolved: "具体详情链接未确认",
  bounded_probe_timeout: "受控探查超时",
  no_concrete_job_list_observed: "未观察到具体岗位列表",
  concrete_job_objects_not_captured: "未捕获具体岗位对象",
  no_public_positions_observed: "未观察到公开岗位",
  duplicate_url_variant_replaced_by_papegames_adapter: "重复入口，已由专用适配器替代",
};
function status(value) { return statusLabels[value] || value || "—"; }
function reason(value) { return reasonLabels[value] || value || "—"; }
function renderSources(sources) {
  const body = $a("sourceRows"); body.replaceChildren();
  for (const source of sources || []) {
    const row = document.createElement("tr");
    for (const value of [source.company_name || "-", source.ats_type || "unknown", status(source.official_status), status(source.access_status), status(source.integration_status || "not_integrated"), status(source.quality_level || "low"), `P${source.integration_priority ?? 4}`, source.last_success_at || "—", source.next_run_at || "—", reason(source.paused_reason)]) { const cell = document.createElement("td"); cell.textContent = value; row.appendChild(cell); }
    const cell = document.createElement("td"); const link = document.createElement("a"); link.href = source.url; link.target = "_blank"; link.rel = "noopener noreferrer"; link.textContent = "查看入口"; cell.appendChild(link); row.appendChild(cell); body.appendChild(row);
  }
}
function renderList(container, rows, format) { container.replaceChildren(); if (!rows.length) { container.textContent = "暂无记录"; return; } for (const row of rows) { const item = document.createElement("div"); item.className = "admin-list-item"; item.textContent = format(row); container.appendChild(item); } }
function sourceFilterParams() {
  const params = new URLSearchParams();
  for (const id of ["filterCompany", "filterAts", "filterOfficial", "filterAccess", "filterIntegration", "filterQuality"]) {
    const value = $a(id).value.trim();
    if (value) params.set({filterCompany:"company", filterAts:"ats_type", filterOfficial:"official_status", filterAccess:"access_status", filterIntegration:"integration_status", filterQuality:"quality_level"}[id], value);
  }
  params.set("limit", "200");
  return params;
}
async function loadSources(filters = false) {
  const query = filters ? `?${sourceFilterParams().toString()}` : "?limit=200";
  const response = await fetch(`/api/company-sources${query}`);
  if (!response.ok) throw new Error(`来源查询失败（HTTP ${response.status}）`);
  const sources = await response.json();
  renderSources(sources);
  $a("sourceResultCount").textContent = `当前筛选结果：${sources.length} 条入口`;
  return sources;
}
async function loadAdmin() {
  const [stats, queue, quality, runs, quarantine] = await Promise.all([
    fetch("/api/company-source-stats").then(r => r.json()), fetch("/api/ingestion-queue?limit=20").then(r => r.json()), fetch("/api/job-quality").then(r => r.json()), fetch("/api/crawl-runs?limit=10").then(r => r.json()), fetch("/api/job-quarantine?limit=20").then(r => r.json()),
  ]);
  $a("sourceCompanies").textContent = stats.companies || 0; $a("sourceCount").textContent = stats.sources || 0; const qualityLevels = Object.fromEntries((stats.by_quality_level || []).map(item => [item.value, item.count])); $a("highQuality").textContent = qualityLevels.high || 0; $a("blockedSources").textContent = qualityLevels.blocked || 0; $a("sourceSummary").textContent = `${stats.reachable_sources || 0} 条可访问，${stats.confirmed_official_sources || 0} 条已确认官方归属；此页不自动触发采集`;
  await loadSources(); renderList($a("ingestionQueue"), queue, row => `${row.company_name || "未知企业"} · ${row.source_name || row.source_key || "入口"} · ${row.adapter || row.ats_type || "待识别"} · P${row.integration_priority ?? 4} · ${reason(row.paused_reason)}`); $a("jobQuality").textContent = JSON.stringify(quality, null, 2); renderList($a("crawlRuns"), runs, row => `#${row.id} ${row.source_id} · ${status(row.status)} · 发现 ${row.jobs_found ?? 0} · 新增 ${row.jobs_created ?? 0}`); renderList($a("jobQuarantine"), quarantine, row => `${row.company_name || row.source_id} · ${row.source_job_id} · ${row.title || "未命名岗位"} · ${reason(row.reason)}`);
}
$a("sourceFilters").addEventListener("submit", async event => { event.preventDefault(); try { await loadSources(true); } catch (error) { $a("sourceSummary").textContent = `筛选失败：${error.message}；已保留当前表格`; } });
$a("resetSourceFilters").addEventListener("click", async () => { $a("sourceFilters").reset(); try { await loadSources(); } catch (error) { $a("sourceSummary").textContent = `重置失败：${error.message}；已保留当前表格`; } });
$a("filterCompany").addEventListener("keydown", event => { if (event.key === "Enter") $a("sourceFilters").requestSubmit(); });
loadAdmin().catch(error => { $a("sourceSummary").textContent = `加载失败：${error.message}`; });
