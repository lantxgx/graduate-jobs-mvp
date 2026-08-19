const $p = (id) => document.getElementById(id);
const listKeys = new Set(["skills", "target_roles", "adjacent_roles", "target_companies", "target_cities", "excluded_roles"]);
const profileFields = {
  education: $p("profileEducation"), graduation_year: $p("profileYear"), major: $p("profileMajor"), skills: $p("profileSkills"),
  target_roles: $p("profileTargetRoles"), adjacent_roles: $p("profileAdjacentRoles"), target_companies: $p("profileCompanies"),
  target_cities: $p("profileCities"), excluded_roles: $p("profileExcludedRoles"),
};
let pendingResumeProfile = null;
function splitValue(value) { return (value || "").split(/[，,]/).map(v => v.trim()).filter(Boolean); }
function fillProfile(profile) { for (const [key, field] of Object.entries(profileFields)) { const value = profile[key]; field.value = Array.isArray(value) ? value.join(", ") : (value || ""); } }
function fillPreferences(profile) {
  $p("profileCityMode").value = profile.city_preference_mode || "preference";
  const mix = profile.recommendation_mix || { main: 50, target_company: 25, adjacent: 20, exploration: 5 };
  $p("mixMain").value = mix.main ?? 50; $p("mixCompany").value = mix.target_company ?? 25; $p("mixAdjacent").value = mix.adjacent ?? 20; $p("mixExplore").value = mix.exploration ?? 5;
}
async function loadProfile() { const data = await fetch("/api/profile").then(r => r.json()); if (data.saved !== false) { fillProfile(data); fillPreferences(data); } }
async function encodeFile() {
  const file = $p("resumeFile").files[0];
  if (!file) { $p("resumePreview").hidden = false; $p("resumePreview").textContent = "请先选择 PDF 或 DOCX 简历。"; return null; }
  const content_base64 = await new Promise((resolve, reject) => { const reader = new FileReader(); reader.onload = () => resolve(String(reader.result).split(",")[1] || ""); reader.onerror = reject; reader.readAsDataURL(file); });
  return { file, content_base64 };
}
async function saveProfile() {
  const payload = { save_profile: $p("profileSave").checked };
  for (const [key, field] of Object.entries(profileFields)) payload[key] = listKeys.has(key) ? splitValue(field.value) : field.value.trim();
  const mix = { main: Number($p("mixMain").value), target_company: Number($p("mixCompany").value), adjacent: Number($p("mixAdjacent").value), exploration: Number($p("mixExplore").value) };
  if (Object.values(mix).some(value => !Number.isFinite(value) || value < 0) || Object.values(mix).reduce((sum, value) => sum + value, 0) !== 100) { $p("profileStatus").textContent = "推荐比例必须是非负数且合计 100%"; return; }
  payload.city_preference_mode = $p("profileCityMode").value; payload.recommendation_mix = mix;
  const result = await fetch("/api/profile", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }).then(r => r.json());
  $p("profileStatus").textContent = result.saved ? "已保存结构化画像" : "本次仅在当前会话使用";
}
$p("saveProfile").addEventListener("click", saveProfile);
$p("clearProfile").addEventListener("click", async () => { await fetch("/api/profile", { method: "DELETE" }); fillProfile({}); $p("profileStatus").textContent = "已删除保存的结构化画像"; });
$p("previewResume").addEventListener("click", async () => {
  const encoded = await encodeFile(); if (!encoded) return;
  const result = await fetch("/api/resume/preview", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ filename: encoded.file.name, content_base64: encoded.content_base64 }) }).then(r => r.json());
  $p("resumePreview").hidden = false; $p("resumePreview").textContent = result.profile ? `候选画像预览（需要你确认）\n${JSON.stringify(result.profile, null, 2)}\n\n文本片段：\n${result.text_preview || ""}` : (result.detail || "解析失败");
});
$p("analyzeResume").addEventListener("click", async () => {
  const encoded = await encodeFile(); if (!encoded) return;
  const result = await fetch("/api/resume/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ filename: encoded.file.name, content_base64: encoded.content_base64, external_ai_consent: $p("externalAiConsent").checked }) }).then(r => r.json());
  pendingResumeProfile = result.profile || null; $p("applyResumeProfile").hidden = !pendingResumeProfile; $p("resumePreview").hidden = false; $p("resumePreview").textContent = result.profile ? `结构化分析结果（需要你确认）\n${JSON.stringify(result.profile, null, 2)}` : (result.detail || "分析失败");
});
$p("applyResumeProfile").addEventListener("click", () => { if (!pendingResumeProfile) return; if (pendingResumeProfile.education) $p("profileEducation").value = pendingResumeProfile.education; const years = pendingResumeProfile.graduation_year_candidates || []; if (years.length) $p("profileYear").value = years[0]; if (Array.isArray(pendingResumeProfile.skills)) $p("profileSkills").value = pendingResumeProfile.skills.join(", "); $p("profileStatus").textContent = "已应用到能力画像，请检查后保存"; });
loadProfile();
