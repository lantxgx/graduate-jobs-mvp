const $ = id => document.getElementById(id);
const PAGE_SIZE = 100;
const familyLabels = {algorithm_ai:"算法 / AI",data:"数据",design:"设计",functional:"职能",hardware:"硬件研发",manufacturing:"制造 / 工艺",marketing:"市场 / 销售",operations:"运营",product:"产品",sales:"销售",software_rnd:"软件研发",supply_chain:"供应链 / 采购",testing_quality:"测试 / 质量"};
let allJobs = [], filteredJobs = [], shown = PAGE_SIZE;
const fields = {company:$("company"),city:$("city"),category:$("category"),job_family:$("jobFamily"),job_nature:$("jobNature"),degree:$("degree")};
const clean = value => String(value || "").replace(/\s+/g," ").trim();
const unique = key => [...new Set(allJobs.map(job => clean(job[key])).filter(Boolean))].sort((a,b) => a.localeCompare(b,"zh-CN"));

function fillSelect(select, values, labels={}) { for (const value of values) { const option=document.createElement("option"); option.value=value; option.textContent=labels[value]||value; select.appendChild(option); } }
function render() {
  const jobs=filteredJobs.slice(0,shown), container=$("jobs"), template=$("jobTemplate"); container.replaceChildren();
  for (const job of jobs) {
    const node=template.content.cloneNode(true); node.querySelector(".company").textContent=job.company||"未知公司"; node.querySelector(".title").textContent=job.title||"未命名岗位";
    const category=node.querySelector(".category"); if(job.category) category.textContent=job.category; else category.remove();
    const chips=node.querySelector(".chips"); for(const value of [job.city,job.job_nature,job.degree,job.graduate_year].filter(Boolean)){const chip=document.createElement("span");chip.className="chip";chip.textContent=value;chips.appendChild(chip);}
    const description=clean(job.description), requirements=clean(job.requirements); if(description) node.querySelector(".description").textContent=description; else node.querySelector(".description-section").remove(); if(requirements) node.querySelector(".requirements").textContent=requirements; else node.querySelector(".requirements-section").remove(); if(!description&&!requirements) node.querySelector(".job-details").remove();
    node.querySelector(".updated").textContent=`最近发现：${clean(job.last_seen_at).slice(0,10)||"—"}`; const apply=node.querySelector(".apply"); apply.href=job.apply_url||job.source_url; container.appendChild(node);
  }
  $("resultCount").textContent=`${filteredJobs.length} 个结果`; $("empty").hidden=filteredJobs.length>0; $("loadMore").hidden=jobs.length>=filteredJobs.length; $("loadMoreStatus").textContent=`已显示 ${jobs.length} / ${filteredJobs.length}`;
}
function filterJobs() {
  const keyword=clean($("keyword").value).toLowerCase(); shown=PAGE_SIZE;
  filteredJobs=allJobs.filter(job => Object.entries(fields).every(([key,field]) => !field.value || clean(job[key])===field.value) && (!keyword || [job.company,job.title,job.city,job.category,job.degree,job.description,job.requirements].some(value => clean(value).toLowerCase().includes(keyword)))); render();
}
async function init() {
  const response=await fetch("./jobs.json"); if(!response.ok) throw new Error(`HTTP ${response.status}`); const data=await response.json(); allJobs=data.items||[]; filteredJobs=[...allJobs];
  fillSelect(fields.company,unique("company")); fillSelect(fields.city,unique("city")); fillSelect(fields.category,unique("category")); fillSelect(fields.job_family,unique("job_family"),familyLabels); fillSelect(fields.job_nature,unique("job_nature")); fillSelect(fields.degree,unique("degree"));
  $("total").textContent=allJobs.length; $("companyCount").textContent=unique("company").length; $("cityCount").textContent=unique("city").length; $("snapshotTime").textContent=data.exported_at?`快照时间：${String(data.exported_at).slice(0,16)}`:""; render();
}
$("searchBtn").addEventListener("click",filterJobs); $("keyword").addEventListener("keydown",event=>{if(event.key==="Enter")filterJobs();}); Object.values(fields).forEach(field=>field.addEventListener("change",filterJobs)); $("resetBtn").addEventListener("click",()=>{$("keyword").value="";Object.values(fields).forEach(field=>field.value="");filterJobs();}); $("loadMore").addEventListener("click",()=>{shown+=PAGE_SIZE;render();});
init().catch(error=>{$("resultCount").textContent="岗位快照加载失败";$("loadMoreStatus").textContent=error.message;});
