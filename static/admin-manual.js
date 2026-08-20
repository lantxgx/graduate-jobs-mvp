const form = document.getElementById('manualForm');
const result = document.getElementById('manualResult');
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(form).entries());
  data.city = [data.country, data.province, data.city].filter(Boolean).join(' / ');
  try {
    const response = await fetch('/api/manual/jobs', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({jobs:[data]})});
    const body = await response.json();
    if (!response.ok) throw new Error(body.detail ? JSON.stringify(body.detail) : '提交失败');
    result.textContent = `已入库 ${body.accepted} 条，拒绝 ${body.rejected} 条`;
    if (body.accepted) form.reset();
  } catch (error) { result.textContent = `录入失败：${error.message}`; }
});
