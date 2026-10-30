const queryInput = document.getElementById("query");
const resultsEl = document.getElementById("results");
const errorEl = document.getElementById("error");

async function loadDocumentCount() {
  const docs = await fetch("/api/documents").then(r => r.json());
  document.getElementById("docCount").textContent = docs.length;
}
function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
async function runSearch() {
  const query = queryInput.value.trim();
  errorEl.textContent = "";
  if (!query) { errorEl.textContent = "Please enter a query."; return; }
  const button = document.getElementById("searchBtn");
  button.disabled = true; button.textContent = "Searching…";
  try {
    const response = await fetch("/api/search", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query})});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Search failed.");
    document.getElementById("resultCount").textContent = data.count;
    document.getElementById("vocabCount").textContent = data.vocabulary_size;
    document.getElementById("queryLabel").textContent = `Query: ${data.query}`;
    resultsEl.innerHTML = data.results.length ? data.results.map(doc => `
      <article class="doc">
        <div class="doc-top"><h3>${escapeHtml(doc.title)}</h3><span class="doc-id">DOC-${String(doc.id).padStart(3,"0")}</span></div>
        <p>${escapeHtml(doc.content)}</p><div class="meta">Category: ${escapeHtml(doc.category)}</div>
      </article>`).join("") : '<div class="empty">No documents matched this query. Try OR to broaden your search.</div>';
  } catch (err) { errorEl.textContent = err.message; }
  finally { button.disabled = false; button.textContent = "Search documents"; }
}
document.getElementById("searchBtn").addEventListener("click", runSearch);
queryInput.addEventListener("keydown", e => { if(e.key === "Enter") runSearch(); });
document.querySelectorAll(".chip").forEach(chip => chip.addEventListener("click", () => {queryInput.value=chip.dataset.query;runSearch();}));
loadDocumentCount();
runSearch();
