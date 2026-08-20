const $ = (id) => document.getElementById(id);

const fields = {
  keyword: $("keyword"),
  company: $("company"),
  country: $("country"),
  province: $("province"),
  city: $("city"),
  category: $("category"),
  major: $("major"),
  job_nature: $("jobNature"),
  degree: $("degree"),
};

function optionize(select, values) {
  const first = select.options[0];
  select.replaceChildren(first);
  for (const value of values || []) {
    const opt = document.createElement("option");
    opt.value = typeof value === "object" ? value.value : value;
    opt.textContent = typeof value === "object" ? value.label : value;
    select.appendChild(opt);
  }
}

function text(v) {
  return (v || "").toString().replace(/\s+/g, " ").trim();
}

function listValue(value) {
  if (Array.isArray(value)) return value.map(text).filter(Boolean);
  return text(value).split(/\n|\/|；|;/).map(item => item.trim()).filter(Boolean);
}

let currentJobs = [];
let actionState = { favorite: new Set(), ignore: new Set(), applied: new Set() };
let pendingResumeProfile = null;
let currentOffset = 0;
let currentTotal = 0;
let locationHierarchy = [];
const pageSize = 100;
const poolLabels = {
  main: "主攻方向",
  target_company: "目标企业",
  adjacent: "相邻方向",
  exploration: "探索岗位",
};
const statusLabels = {
  matched: "已匹配",
  review: "需要确认",
  unconfirmed: "待确认",
  direct: "直接匹配",
  adjacent: "相邻匹配",
  unknown: "暂无证据",
};
const riskLabels = { high: "较高", medium: "中等", low: "较低" };
const categoryLabels = { "算法/AI": "算法与人工智能" };

function unique(values) {
  return [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b, "zh-CN"));
}

function refreshLocationOptions(level) {
  if (level === "country") {
    fields.province.value = "";
    fields.city.value = "";
  } else if (level === "province") {
    fields.city.value = "";
  }
  const byCountry = locationHierarchy.filter(item => !fields.country.value || item.country === fields.country.value);
  if (level !== "province") {
    optionize(fields.province, unique(byCountry.map(item => item.province)));
  }
  const byProvince = byCountry.filter(item => !fields.province.value || item.province === fields.province.value);
  optionize(fields.city, unique(byProvince.map(item => item.city)));
}

function renderJobs(jobs) {
  const container = $("jobs");
  container.innerHTML = "";
  if ($("recommendationHint")) $("recommendationHint").hidden = true;
  $("resultCount").textContent = `${jobs.length} 个结果`;
  $("empty").hidden = jobs.length > 0;

  const template = $("jobTemplate");
  for (const job of jobs) {
    const node = template.content.cloneNode(true);
    node.querySelector(".company").textContent = job.company || "未知公司";
    node.querySelector(".title").textContent = job.title || "未命名岗位";

    const cat = node.querySelector(".category");
    if (job.category) cat.textContent = categoryLabels[job.category] || job.category;
    else cat.remove();

    const chips = node.querySelector(".chips");
    for (const item of [
      listValue(job.work_locations || job.city).join(" / "),
      job.job_nature,
      job.degree,
      job.graduate_year,
      poolLabels[job.recommendation_pool] || "",
      job.competition_risk ? `竞争信号：${riskLabels[job.competition_risk] || job.competition_risk}` : "",
    ].filter(Boolean)) {
      const chip = document.createElement("span");
      chip.className = "chip";
      chip.textContent = item;
      chips.appendChild(chip);
    }

    if (job.adjacent_explanation || job.competition_risk_basis) {
      const note = document.createElement("div");
      note.className = "job-analysis-note";
      note.textContent = [job.adjacent_explanation, job.competition_risk_basis ? `依据：${job.competition_risk_basis.join("；")}` : ""].filter(Boolean).join(" ");
      chips.appendChild(note);
    }

    const matchSummary = node.querySelector(".match-summary");
    const dimensions = job.match_dimensions || {};
    const dimensionLabels = {
      basic_qualification: "基本资格",
      ability_match: "能力匹配",
      job_seeking_intent: "求职意愿",
      company_preference: "企业偏好",
      transition_distance: "转型距离",
      confidence: "证据置信度",
    };
    const dimensionText = Object.entries(dimensionLabels)
      .filter(([key]) => dimensions[key])
      .map(([key, label]) => `${label}：${statusLabels[dimensions[key].status] || dimensions[key].status}`)
      .join(" · ");
    if (dimensionText) matchSummary.textContent = dimensionText;
    else matchSummary.remove();

    const description = text(job.responsibilities || job.description);
    const requirements = text(job.qualifications || job.requirements);
    const majors = listValue(job.major_requirements);
    const normalizedMajors = majors;
    const majorSection = node.querySelector(".major-section");
    const majorContainer = node.querySelector(".major-requirements");
    if (normalizedMajors.length) {
      for (const major of normalizedMajors) {
        const item = document.createElement("span");
        item.className = "major-tag";
        item.textContent = major;
        majorContainer.appendChild(item);
      }
    } else {
      majorSection.remove();
    }
    const descriptionSection = node.querySelector(".description-section");
    const requirementsSection = node.querySelector(".requirements-section");
    if (description) node.querySelector(".description").textContent = description;
    else descriptionSection.remove();
    if (requirements) node.querySelector(".requirements").textContent = requirements;
    else requirementsSection.remove();
    if (!description && !requirements && !normalizedMajors.length) {
      node.querySelector(".job-details").remove();
    }
    node.querySelector(".updated").textContent = `最近发现：${(job.last_seen_at || "").slice(0, 10) || "—"}`;

    const apply = node.querySelector(".apply");
    apply.href = job.apply_url || job.source_url;
    const favorite = node.querySelector(".favorite");
    const favoriteSaved = actionState.favorite.has(Number(job.id));
    favorite.dataset.saved = String(favoriteSaved);
    favorite.textContent = favoriteSaved ? "已收藏" : "收藏";
    favorite.addEventListener("click", async () => {
      const enabled = favorite.dataset.saved !== "true";
      await fetch(`/api/jobs/${job.id}/action`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "favorite", enabled }),
      });
      favorite.dataset.saved = String(enabled);
      favorite.textContent = enabled ? "已收藏" : "收藏";
      if (enabled) actionState.favorite.add(Number(job.id)); else actionState.favorite.delete(Number(job.id));
    });
    for (const actionButton of node.querySelectorAll(".job-action")) {
      const action = actionButton.dataset.action;
      const enabled = actionState[action].has(Number(job.id));
      actionButton.textContent = enabled ? (action === "ignore" ? "已忽略" : "已投递") : (action === "ignore" ? "不感兴趣" : "已投递");
      actionButton.classList.toggle("selected", enabled);
      actionButton.addEventListener("click", async () => {
        const nextEnabled = !actionState[action].has(Number(job.id));
        await fetch(`/api/jobs/${job.id}/action`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ action, enabled: nextEnabled }),
        });
        if (nextEnabled) actionState[action].add(Number(job.id)); else actionState[action].delete(Number(job.id));
        actionButton.textContent = nextEnabled ? (action === "ignore" ? "已忽略" : "已投递") : (action === "ignore" ? "不感兴趣" : "已投递");
        actionButton.classList.toggle("selected", nextEnabled);
      });
    }
    container.appendChild(node);
  }
}

async function loadFacets() {
  const [data, coverage] = await Promise.all([
    fetch("/api/facets").then(r => r.json()),
    fetch("/api/coverage-summary").then(r => r.json()),
  ]);
  $("total").textContent = data.total || 0;
  $("companyCount").textContent = coverage.registered_companies ?? (data.companies || []).length;
  $("sourceCountHome").textContent = coverage.integrated_sources || 0;
  optionize(fields.company, data.companies);
  locationHierarchy = data.locations || [];
  optionize(fields.country, unique(locationHierarchy.map(item => item.country)));
  refreshLocationOptions();
  optionize(fields.category, (data.categories || []).map(value => ({ value, label: categoryLabels[value] || value })));
  optionize(fields.major, data.majors || []);
  optionize(fields.job_nature, data.job_natures);
  optionize(fields.degree, data.degrees);
}

async function loadCompanyDirectory() {
  const companies = await fetch("/api/company-job-directory?limit=100").then(r => r.json());
  const list = $("companyDirectoryList");
  if (!list) return;
  const syncedCompanies = companies.filter(company => Number(company.active_job_count || 0) > 0);
  $("directoryCount").textContent = `${syncedCompanies.length} 家有岗位`;
  list.replaceChildren();
  for (const company of syncedCompanies) {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "company-directory-item";
    const name = document.createElement("strong");
    name.textContent = company.brand_name || company.canonical_name || "未命名企业";
    const meta = document.createElement("span");
    const jobs = Number(company.active_job_count || 0);
    meta.textContent = `${jobs} 个具体岗位 · ${company.source_count || 0} 个招聘入口`;
    item.append(name, meta);
    item.addEventListener("click", () => {
      const preferred = company.canonical_name || company.brand_name || "";
      const matching = [...fields.company.options].find(option => option.value === preferred);
      fields.company.value = matching ? matching.value : (company.brand_name || preferred);
      document.querySelector('[data-view="all"]')?.click();
      loadJobs();
    });
    list.appendChild(item);
  }
}

async function loadJobs() {
  currentOffset = 0;
  const params = new URLSearchParams();
  for (const [key, input] of Object.entries(fields)) {
    if (input.value) params.set(key, input.value);
  }
  params.set("offset", "0");
  params.set("limit", String(pageSize));
  const data = await fetch(`/api/jobs?${params}`).then(r => r.json());
  currentJobs = data.items || data;
  currentTotal = data.total ?? currentJobs.length;
  renderJobs(currentJobs);
  updateLoadMore();
}

async function loadMoreJobs() {
  if (currentJobs.length >= currentTotal) return;
  const params = new URLSearchParams();
  for (const [key, input] of Object.entries(fields)) if (input.value) params.set(key, input.value);
  currentOffset = currentJobs.length;
  params.set("offset", String(currentOffset));
  params.set("limit", String(pageSize));
  const data = await fetch(`/api/jobs?${params}`).then(r => r.json());
  const existing = new Set(currentJobs.map(job => Number(job.id)));
  currentJobs = currentJobs.concat((data.items || []).filter(job => !existing.has(Number(job.id))));
  currentTotal = data.total ?? currentTotal;
  renderJobs(currentJobs);
  updateLoadMore();
}

function updateLoadMore() {
  const button = $("loadMore");
  const status = $("loadMoreStatus");
  if (!button || !status) return;
  button.hidden = currentJobs.length >= currentTotal;
  status.textContent = `已显示 ${currentJobs.length} / ${currentTotal}`;
}

async function loadActionState() {
  const rows = await fetch("/api/job-actions").then(r => r.json());
  actionState = { favorite: new Set(), ignore: new Set(), applied: new Set() };
  for (const row of rows) if (actionState[row.action]) actionState[row.action].add(Number(row.job_id));
}

async function loadActionView(action) {
  if (action === "all") return loadJobs();
  const ids = new Set((await fetch(`/api/job-actions?action=${action}`).then(r => r.json())).map(row => Number(row.job_id)));
  renderJobs(currentJobs.filter(job => ids.has(Number(job.id))));
  $("resultCount").textContent = `${ids.size} 个结果`;
}

async function loadRecommendations() {
  const result = await fetch("/api/recommendations?limit=100").then(r => r.json());
  if (result.needs_profile) {
    renderJobs([]);
    $("recommendationHint").hidden = false;
    $("resultCount").textContent = "尚未建立画像";
    $("loadMore").hidden = true;
    $("loadMoreStatus").textContent = "先确认能力证据和求职意愿，再生成推荐";
    return;
  }
  renderJobs(result.items || []);
  $("resultCount").textContent = `${(result.items || []).length} 个推荐结果（保留全部岗位入口）`;
  $("loadMore").hidden = true;
  $("loadMoreStatus").textContent = "推荐按岗位池展示；全部岗位仍可分页查看";
}

function renderSources(sources) {
  const body = $("sourceRows");
  body.replaceChildren();
  for (const source of sources || []) {
    const row = document.createElement("tr");
    const cells = [
      source.company_name || "-",
      source.ats_type || "unknown",
      source.official_status || "unknown",
      source.quality_level || "low",
      `P${source.integration_priority ?? 4}`,
    ];
    for (const value of cells) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.appendChild(cell);
    }
    const linkCell = document.createElement("td");
    const link = document.createElement("a");
    link.href = source.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "查看入口";
    linkCell.appendChild(link);
    row.appendChild(linkCell);
    body.appendChild(row);
  }
}

async function loadDirectory() {
  const [stats, sources] = await Promise.all([
    fetch("/api/company-source-stats").then(r => r.json()),
    fetch("/api/company-sources?limit=60").then(r => r.json()),
  ]);
  $("sourceCompanies").textContent = stats.companies || 0;
  $("sourceCount").textContent = stats.sources || 0;
  const quality = Object.fromEntries((stats.by_quality_level || []).map(item => [item.value, item.count]));
  $("highQuality").textContent = quality.high || 0;
  $("blockedSources").textContent = quality.blocked || 0;
  $("sourceSummary").textContent = `${stats.reachable_sources || 0} 条可访问，${stats.confirmed_official_sources || 0} 条已确认官方归属`;
  renderSources(sources);
}

const profileFields = {
  education: $("profileEducation"),
  graduation_year: $("profileYear"),
  major: $("profileMajor"),
  skills: $("profileSkills"),
  target_roles: $("profileTargetRoles"),
  adjacent_roles: $("profileAdjacentRoles"),
  target_companies: $("profileCompanies"),
  target_cities: $("profileCities"),
  excluded_roles: $("profileExcludedRoles"),
};

function addProfileGroupLabels() {
  if (!$('profileSkills')) return;
  const grid = $("profileSkills").closest(".profile-grid");
  if (!grid || grid.querySelector(".profile-group-label")) return;
  const evidence = document.createElement("div");
  evidence.className = "profile-group-label";
  evidence.textContent = "能力证据（简历可以辅助，最终由你确认）";
  grid.insertBefore(evidence, grid.firstElementChild);
  const intent = document.createElement("div");
  intent.className = "profile-group-label intent-label";
  intent.textContent = "求职意愿（必须由你自己填写）";
  grid.insertBefore(intent, $("profileTargetRoles").closest("label"));
}

addProfileGroupLabels();

function splitProfileValue(value) {
  return (value || "").split(/[，,]/).map(item => item.trim()).filter(Boolean);
}

function profileListKeys() {
  return ["skills", "target_roles", "adjacent_roles", "target_companies", "target_cities", "excluded_roles"];
}

function fillProfile(profile) {
  for (const [key, field] of Object.entries(profileFields)) {
    const value = profile[key];
    field.value = Array.isArray(value) ? value.join(", ") : (value || "");
  }
}

async function loadProfile() {
  const data = await fetch("/api/profile").then(r => r.json());
  if (data.saved !== false) fillProfile(data);
}

async function saveProfile() {
  const payload = { save_profile: $("profileSave").checked };
  for (const [key, field] of Object.entries(profileFields)) {
    payload[key] = profileListKeys().includes(key)
      ? splitProfileValue(field.value) : field.value.trim();
  }
  const result = await fetch("/api/profile", {
    method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
  }).then(r => r.json());
  $("profileStatus").textContent = result.saved ? "已保存结构化画像" : "本次仅在当前会话使用";
}

$("saveProfile")?.addEventListener("click", saveProfile);
$("clearProfile")?.addEventListener("click", async () => {
  await fetch("/api/profile", { method: "DELETE" });
  fillProfile({});
  $("profileStatus").textContent = "已删除保存的结构化画像";
});

$("previewResume")?.addEventListener("click", async () => {
  const file = $("resumeFile").files[0];
  if (!file) return;
  const encoded = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(",")[1] || "");
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
  const result = await fetch("/api/resume/preview", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename: file.name, content_base64: encoded }),
  }).then(r => r.json());
  $("resumePreview").hidden = false;
  $("resumePreview").textContent = result.profile
    ? `候选画像预览（需要你确认）\n${JSON.stringify(result.profile, null, 2)}\n\n文本片段：\n${result.text_preview || ""}`
    : (result.detail || "解析失败");
});

$("analyzeResume")?.addEventListener("click", async () => {
  const file = $("resumeFile").files[0];
  if (!file) return;
  const encoded = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(",")[1] || "");
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
  const result = await fetch("/api/resume/analyze", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      filename: file.name, content_base64: encoded,
      external_ai_consent: $("externalAiConsent").checked,
    }),
  }).then(r => r.json());
  $("resumePreview").hidden = false;
  pendingResumeProfile = result.profile || null;
  $("applyResumeProfile").hidden = !pendingResumeProfile;
  $("resumePreview").textContent = result.profile
    ? `结构化分析结果（需要你确认）\n${JSON.stringify(result.profile, null, 2)}`
    : (result.detail || "分析失败");
});

$("applyResumeProfile")?.addEventListener("click", () => {
  if (!pendingResumeProfile) return;
  if (pendingResumeProfile.education) $("profileEducation").value = pendingResumeProfile.education;
  const years = pendingResumeProfile.graduation_year_candidates || [];
  if (years.length) $("profileYear").value = years[0];
  if (Array.isArray(pendingResumeProfile.skills)) $("profileSkills").value = pendingResumeProfile.skills.join(", ");
  $("profileStatus").textContent = "已应用到能力画像，请检查后保存";
  $("profileSave").checked = true;
});

$("searchBtn").addEventListener("click", loadJobs);
$("loadMore")?.addEventListener("click", loadMoreJobs);
$("recommendBtn").addEventListener("click", loadRecommendations);
for (const tab of document.querySelectorAll(".view-tab")) {
  tab.addEventListener("click", async () => {
    document.querySelectorAll(".view-tab").forEach(item => item.classList.toggle("active", item === tab));
    await loadActionView(tab.dataset.view);
  });
}
$("keyword").addEventListener("keydown", e => { if (e.key === "Enter") loadJobs(); });
for (const [key, field] of Object.entries(fields)) {
  if (key !== "keyword" && !["country", "province"].includes(key)) field.addEventListener("change", loadJobs);
}
fields.country.addEventListener("change", () => { refreshLocationOptions("country"); loadJobs(); });
fields.province.addEventListener("change", () => { refreshLocationOptions("province"); loadJobs(); });
$("resetBtn").addEventListener("click", () => {
  for (const field of Object.values(fields)) field.value = "";
  loadJobs();
});

Promise.all([loadFacets(), loadCompanyDirectory(), loadActionState()]).then(() => loadJobs());
