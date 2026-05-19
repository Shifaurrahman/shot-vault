import { useState, useEffect } from "react";

/* ─── API config ─── */
const API_BASE = "http://localhost:8000";

const api = {
  upload: async (formData) => {
    const res = await fetch(`${API_BASE}/api/upload`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Upload failed");
    }
    return res.json();
  },

  query: async (query, topK = 5, filterType = null) => {
    const res = await fetch(`${API_BASE}/api/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, top_k: topK, filter_type: filterType }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Query failed");
    }
    return res.json();
  },

  count: async () => {
    const res = await fetch(`${API_BASE}/api/entries/count`);
    if (!res.ok) return { count: 0 };
    return res.json();
  },

  suggestions: async () => {
    const res = await fetch(`${API_BASE}/api/query/suggestions`);
    if (!res.ok) return { suggestions: [] };
    return res.json();
  },
};

/* ─── Shared tokens ─── */
const colors = {
  blue50: "#E6F1FB", blue800: "#0C447C", blue600: "#185FA5",
  teal50: "#E1F5EE", teal800: "#0F6E56",
  purple50: "#EEEDFE", purple800: "#3C3489",
  red50: "#FCEBEB", red600: "#E24B4A",
  green50: "#E6F7F0", green700: "#0F6E56",
  border: "0.5px solid #e5e5e0",
};

const inputStyle = {
  width: "100%", padding: "8px 10px", border: colors.border,
  borderRadius: 8, background: "#fafafa", color: "#111",
  fontSize: 13, fontFamily: "inherit", outline: "none", boxSizing: "border-box",
};

const btnPrimary = {
  background: colors.blue600, color: "#fff", border: "none",
  padding: "9px 18px", borderRadius: 8, fontSize: 13, fontWeight: 500,
  cursor: "pointer", display: "flex", alignItems: "center", gap: 6,
};

const btnSecondary = {
  background: "#fff", color: "#555", border: colors.border,
  padding: "9px 14px", borderRadius: 8, fontSize: 13,
  cursor: "pointer", display: "flex", alignItems: "center", gap: 6,
};

function Sidebar({ page, setPage, entryCount }) {
  const navItems = [
    { id: "upload", label: "Upload details", icon: "☁️" },
    { id: "query",  label: "Query & retrieve", icon: "🔍" },
  ];
  return (
    <aside style={{ width: 220, background: "#fff", borderRight: colors.border, display: "flex", flexDirection: "column", flexShrink: 0 }}>
      <div style={{ padding: "20px 16px 16px", borderBottom: colors.border }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <div style={{ width: 28, height: 28, background: colors.blue50, borderRadius: 6, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 15 }}>🎬</div>
          <span style={{ fontSize: 15, fontWeight: 500, color: "#111" }}>ShotVault</span>
        </div>
        <div style={{ fontSize: 11, color: "#bbb", paddingLeft: 36 }}>Filmmaking Knowledge Base</div>
      </div>
      <nav style={{ padding: "12px 8px", flex: 1 }}>
        <div style={{ fontSize: 10, color: "#bbb", letterSpacing: "0.05em", textTransform: "uppercase", padding: "0 8px 8px", fontWeight: 500 }}>Pages</div>
        {navItems.map(({ id, label, icon }) => (
          <div key={id} onClick={() => setPage(id)} style={{
            display: "flex", alignItems: "center", gap: 9, padding: "8px 10px",
            borderRadius: "0 8px 8px 0", cursor: "pointer", fontSize: 13, marginBottom: 2,
            borderLeft: page === id ? `2px solid ${colors.blue600}` : "2px solid transparent",
            background: page === id ? colors.blue50 : "transparent",
            color: page === id ? colors.blue600 : "#666",
            fontWeight: page === id ? 500 : 400, transition: "all 0.15s",
          }}>{icon}&nbsp;{label}</div>
        ))}
      </nav>
      <div style={{ padding: "10px 16px", borderTop: colors.border, fontSize: 11, color: "#ccc" }}>
        🗄 {entryCount} {entryCount === 1 ? "entry" : "entries"} stored
      </div>
    </aside>
  );
}

function Card({ children, style }) {
  return <div style={{ background: "#fff", border: colors.border, borderRadius: 12, padding: "16px 18px", marginBottom: 14, ...style }}>{children}</div>;
}

function SectionLabel({ children }) {
  return <div style={{ fontSize: 10, fontWeight: 500, color: "#aaa", letterSpacing: "0.05em", textTransform: "uppercase", marginBottom: 12 }}>{children}</div>;
}

function Field({ label, optional, noMargin, hint, children }) {
  return (
    <div style={{ marginBottom: noMargin ? 0 : 13 }}>
      <div style={{ fontSize: 12, fontWeight: 500, color: "#555", marginBottom: 4 }}>
        {label}
        {optional && <span style={{ fontWeight: 400, color: "#bbb", marginLeft: 6, fontSize: 10 }}>optional</span>}
        {hint && <span style={{ fontWeight: 400, color: "#bbb", marginLeft: 6, fontSize: 10 }}>· {hint}</span>}
      </div>
      {children}
    </div>
  );
}

function Toast({ msg, error, onClose }) {
  if (!msg) return null;
  return (
    <div style={{ background: error ? colors.red50 : "#111", color: error ? colors.red600 : "#fff", padding: "10px 16px", borderRadius: 8, fontSize: 12, marginBottom: 14, display: "flex", alignItems: "center", gap: 8, justifyContent: "space-between" }}>
      <span>{error ? "❌" : "✅"} {msg}</span>
      <span onClick={onClose} style={{ cursor: "pointer", opacity: 0.6, fontSize: 11 }}>✕</span>
    </div>
  );
}

function Spinner() {
  return <span style={{ display: "inline-block", width: 12, height: 12, border: "2px solid rgba(255,255,255,0.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />;
}

function MediaTypeChip({ label, icon, active, onClick }) {
  return (
    <button onClick={onClick} style={{ flex: 1, padding: "7px 4px", textAlign: "center", fontSize: 12, cursor: "pointer", border: "none", background: active ? colors.blue600 : "#fafafa", color: active ? "#fff" : "#888", fontWeight: active ? 500 : 400, transition: "all 0.15s" }}>{icon} {label}</button>
  );
}

/* ─── Upload page ─── */
function UploadPage({ onSaved }) {
  const [tags, setTags] = useState([]);
  const [tagInput, setTagInput] = useState("");
  const [uploadTab, setUploadTab] = useState("image");
  const [preview, setPreview] = useState(null);
  const [file, setFile] = useState(null);
  const [toast, setToast] = useState({ msg: "", error: false });
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");
  const [notes, setNotes] = useState("");
  const [shotType, setShotType] = useState("");
  const [loading, setLoading] = useState(false);

  const accept = uploadTab === "video" ? "video/*" : uploadTab === "both" ? "image/*,video/*" : "image/*";
  const formats = uploadTab === "video" ? ["MP4", "MOV", "WEBM"] : uploadTab === "both" ? ["PNG", "JPG", "WEBP", "MP4", "MOV"] : ["PNG", "JPG", "WEBP"];
  const zoneIcon = uploadTab === "video" ? "🎥" : uploadTab === "both" ? "📁" : "🖼️";
  const zoneLabel = uploadTab === "video" ? "Drag & drop a video file" : uploadTab === "both" ? "Drag & drop an image or video" : "Drag & drop an image";

  const handleFile = (e) => {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    const isVideo = f.type.startsWith("video/");
    const reader = new FileReader();
    reader.onload = (ev) => setPreview({ url: ev.target.result, name: f.name, type: isVideo ? "video" : "image" });
    reader.readAsDataURL(f);
  };

  const addTag = () => {
    const t = tagInput.trim();
    if (t && !tags.includes(t)) setTags([...tags, t]);
    setTagInput("");
  };

  const handleSave = async () => {
    if (!title.trim()) { alert("Please enter a title."); return; }
    if (!desc.trim()) { alert("Please enter a description."); return; }
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("title", title.trim());
      formData.append("description", desc.trim());
      if (shotType) formData.append("shot_type", shotType);
      if (notes) formData.append("notes", notes.trim());
      if (tags.length) formData.append("tags", tags.join(","));
      if (file) formData.append("file", file);
      const result = await api.upload(formData);
      setToast({ msg: `"${result.title}" saved and embedded!`, error: false });
      setTimeout(() => setToast({ msg: "", error: false }), 4000);
      onSaved();
      clearForm();
    } catch (err) {
      setToast({ msg: err.message, error: true });
    } finally {
      setLoading(false);
    }
  };

  const clearForm = () => {
    setTitle(""); setDesc(""); setNotes(""); setShotType("");
    setTags([]); setPreview(null); setFile(null);
    const fi = document.getElementById("fileInput");
    if (fi) fi.value = "";
  };

  return (
    <div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <Toast msg={toast.msg} error={toast.error} onClose={() => setToast({ msg: "", error: false })} />
      <div style={{ marginBottom: 20 }}>
        <div style={{ fontSize: 16, fontWeight: 500, color: "#111" }}>☁️ Add shot / scene details</div>
        <div style={{ fontSize: 12, color: "#888", marginTop: 3 }}>Store shot info, description, tags and media. Description gets embedded for AI retrieval.</div>
      </div>

      <Card>
        <SectionLabel>Basic info</SectionLabel>
        <Field label="Title / shot name">
          <input type="text" value={title} onChange={e => setTitle(e.target.value)} placeholder="e.g. Extreme wide shot — beach at golden hour" style={inputStyle} />
        </Field>
        <Field label="Description" hint="gets embedded for AI search">
          <textarea rows={3} value={desc} onChange={e => setDesc(e.target.value)} placeholder="Describe the shot, framing, lighting, mood, technique, camera movement…" style={{ ...inputStyle, resize: "none", lineHeight: 1.6 }} />
        </Field>
        <Field label="Shot type" optional>
          <input type="text" value={shotType} onChange={e => setShotType(e.target.value)} placeholder="e.g. extreme wide shot, handheld, aerial, POV…" style={inputStyle} />
        </Field>
        <Field label="Additional notes" optional noMargin>
          <input type="text" value={notes} onChange={e => setNotes(e.target.value)} placeholder="e.g. equipment used, ISO / aperture, director's intent…" style={inputStyle} />
        </Field>
      </Card>

      <Card>
        <SectionLabel>Tags <span style={{ fontSize: 10, textTransform: "none", letterSpacing: 0 }}>· helps with retrieval</span></SectionLabel>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 10 }}>
          {tags.map((t, i) => (
            <span key={i} style={{ background: colors.blue50, color: colors.blue800, padding: "4px 10px", borderRadius: 20, fontSize: 11, fontWeight: 500, display: "flex", alignItems: "center", gap: 5 }}>
              {t}<span onClick={() => setTags(tags.filter((_, idx) => idx !== i))} style={{ cursor: "pointer", fontSize: 10, opacity: 0.6 }}>✕</span>
            </span>
          ))}
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <input type="text" value={tagInput} onChange={e => setTagInput(e.target.value)} onKeyDown={e => e.key === "Enter" && addTag()} placeholder="Type a tag and press Enter…" style={{ ...inputStyle, flex: 1 }} />
          <button onClick={addTag} style={{ ...btnSecondary, fontSize: 12 }}>+ Add</button>
        </div>
      </Card>

      <Card>
        <SectionLabel>Upload media <span style={{ fontSize: 10, textTransform: "none", letterSpacing: 0 }}>· optional</span></SectionLabel>
        <div style={{ display: "flex", border: colors.border, borderRadius: 8, overflow: "hidden", marginBottom: 12 }}>
          <MediaTypeChip label="Image / Photo" icon="🖼️" active={uploadTab === "image"} onClick={() => { setUploadTab("image"); setPreview(null); setFile(null); }} />
          <MediaTypeChip label="Video" icon="🎥" active={uploadTab === "video"} onClick={() => { setUploadTab("video"); setPreview(null); setFile(null); }} />
          <MediaTypeChip label="Both" icon="📁" active={uploadTab === "both"} onClick={() => { setUploadTab("both"); setPreview(null); setFile(null); }} />
        </div>
        <label htmlFor="fileInput" style={{ border: "1.5px dashed #ddd", borderRadius: 10, padding: 28, textAlign: "center", background: "#fafafa", cursor: "pointer", display: "block" }}>
          <div style={{ fontSize: 34, marginBottom: 8 }}>{zoneIcon}</div>
          <p style={{ fontSize: 13, color: "#888", marginBottom: 3 }}>{zoneLabel}</p>
          <span style={{ fontSize: 11, color: "#bbb" }}>or click to browse</span>
          <div style={{ display: "flex", gap: 6, justifyContent: "center", marginTop: 10, flexWrap: "wrap" }}>
            {formats.map(f => <span key={f} style={{ background: "#f0f0ee", color: "#666", padding: "3px 8px", borderRadius: 6, fontSize: 10, fontWeight: 500 }}>{f}</span>)}
          </div>
        </label>
        <input id="fileInput" type="file" accept={accept} onChange={handleFile} style={{ display: "none" }} />
        {preview && (
          <div style={{ border: colors.border, borderRadius: 10, overflow: "hidden", marginTop: 12 }}>
            {preview.type === "video"
              ? <video src={preview.url} controls style={{ width: "100%", height: 180, objectFit: "cover", display: "block", background: "#000" }} />
              : <img src={preview.url} alt="preview" style={{ width: "100%", height: "auto", maxHeight: 420, objectFit: "contain", display: "block", background: "#f5f5f3" }} />}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "8px 12px", background: "#fafafa", borderTop: colors.border }}>
              <span style={{ fontSize: 12, color: "#555", fontWeight: 500 }}>{preview.type === "video" ? "🎬" : "🖼️"} {preview.name}</span>
              <span onClick={() => { setPreview(null); setFile(null); document.getElementById("fileInput").value = ""; }} style={{ fontSize: 11, color: colors.red600, cursor: "pointer", padding: "3px 8px", borderRadius: 6, background: colors.red50 }}>Remove</span>
            </div>
          </div>
        )}
      </Card>

      <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
        <button onClick={clearForm} style={btnSecondary}>🗑 Clear</button>
        <button onClick={handleSave} disabled={loading} style={{ ...btnPrimary, opacity: loading ? 0.75 : 1 }}>
          {loading ? <><Spinner /> Embedding…</> : <>💾 Save entry</>}
        </button>
      </div>
    </div>
  );
}

/* ─── Query page ─── */
function QueryPage() {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [results, setResults] = useState([]);
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.suggestions().then(d => setSuggestions(d.suggestions || []));
  }, []);

  const runQuery = async (q = query) => {
    if (!q.trim()) return;
    setLoading(true); setError(""); setAnswer(""); setResults([]); setSearched(true);
    try {
      const data = await api.query(q.trim());
      setAnswer(data.answer || "");
      setResults(data.results || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const setQ = (s) => { setQuery(s); runQuery(s); };

  return (
    <div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>

      {selectedEntry && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.45)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 }} onClick={() => setSelectedEntry(null)}>
          <div onClick={e => e.stopPropagation()} style={{ background: "#fff", borderRadius: 14, width: 440, maxWidth: "90vw", overflow: "hidden", border: colors.border }}>
            {selectedEntry.file_url
              ? (selectedEntry.media_type === "video"
                  ? <video src={`${API_BASE}${selectedEntry.file_url}`} controls style={{ width: "100%", height: 220, objectFit: "cover", display: "block", background: "#000" }} />
                  : <img src={`${API_BASE}${selectedEntry.file_url}`} alt="" style={{ width: "100%", height: 220, objectFit: "cover", display: "block" }} />)
              : <div style={{ width: "100%", height: 140, background: "#f5f5f3", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 48 }}>{selectedEntry.media_type === "video" ? "🎬" : "🖼️"}</div>
            }
            <div style={{ padding: "16px 20px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
                <div>
                  <div style={{ fontSize: 15, fontWeight: 500, color: "#111", marginBottom: 3 }}>{selectedEntry.title}</div>
                  {selectedEntry.shot_type && <span style={{ background: colors.blue50, color: colors.blue800, fontSize: 10, fontWeight: 500, padding: "2px 8px", borderRadius: 6 }}>{selectedEntry.shot_type}</span>}
                </div>
                <span onClick={() => setSelectedEntry(null)} style={{ cursor: "pointer", fontSize: 18, color: "#bbb" }}>✕</span>
              </div>
              <div style={{ fontSize: 13, color: "#555", lineHeight: 1.7, marginBottom: 10 }}>{selectedEntry.description}</div>
              {selectedEntry.notes && <div style={{ fontSize: 12, color: "#888", background: "#fafafa", padding: "8px 12px", borderRadius: 8, border: colors.border, marginBottom: 10 }}>📝 {selectedEntry.notes}</div>}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                  {selectedEntry.tags?.map(t => <span key={t} style={{ background: colors.teal50, color: colors.teal800, padding: "3px 9px", borderRadius: 10, fontSize: 10, fontWeight: 500 }}>{t}</span>)}
                  {selectedEntry.media_type && <span style={{ background: selectedEntry.media_type === "video" ? colors.purple50 : colors.blue50, color: selectedEntry.media_type === "video" ? colors.purple800 : colors.blue800, padding: "3px 9px", borderRadius: 10, fontSize: 10, fontWeight: 500 }}>{selectedEntry.media_type}</span>}
                </div>
                <span style={{ background: colors.green50, color: colors.green700, fontSize: 10, fontWeight: 500, padding: "2px 8px", borderRadius: 6 }}>{Math.round(selectedEntry.score * 100)}% match</span>
              </div>
              {selectedEntry.created_at && <div style={{ fontSize: 10, color: "#bbb", marginTop: 10 }}>Added {selectedEntry.created_at}</div>}
            </div>
          </div>
        </div>
      )}

      <div style={{ marginBottom: 20 }}>
        <div style={{ fontSize: 16, fontWeight: 500, color: "#111" }}>🔍 Query & retrieve</div>
        <div style={{ fontSize: 12, color: "#888", marginTop: 3 }}>Ask in natural language — Claude searches and answers from your stored shots.</div>
      </div>

      <Card>
        <SectionLabel>Search</SectionLabel>
        <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
          <input type="text" value={query} onChange={e => setQuery(e.target.value)} onKeyDown={e => e.key === "Enter" && runQuery()} placeholder="e.g. what is an extreme wide shot?" style={{ ...inputStyle, flex: 1, fontSize: 14, padding: "10px 12px" }} />
          <button onClick={() => runQuery()} disabled={loading} style={{ ...btnPrimary, opacity: loading ? 0.75 : 1 }}>
            {loading ? <><Spinner /> Searching…</> : <>🔍 Search</>}
          </button>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
          {suggestions.map(s => (
            <span key={s} onClick={() => setQ(s)} style={{ border: "0.5px dashed #ddd", borderRadius: 20, padding: "4px 12px", fontSize: 11, color: "#888", cursor: "pointer", background: query === s ? colors.blue50 : "transparent" }}>{s}</span>
          ))}
        </div>
      </Card>

      {error && <div style={{ background: colors.red50, color: colors.red600, padding: "10px 14px", borderRadius: 8, fontSize: 12, marginBottom: 14 }}>❌ {error}</div>}

      {answer && (
        <Card style={{ borderColor: "#C8DFFA", background: "#F7FBFF" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <div style={{ width: 22, height: 22, background: colors.blue600, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, color: "#fff" }}>✦</div>
            <span style={{ fontSize: 11, fontWeight: 600, color: colors.blue600, letterSpacing: "0.03em" }}>CLAUDE'S ANSWER</span>
          </div>
          <div style={{ fontSize: 13, color: "#333", lineHeight: 1.75 }}>{answer}</div>
        </Card>
      )}

      {searched && !loading && (
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
          <span style={{ fontSize: 12, fontWeight: 500, color: "#555" }}>Matched shots</span>
          <span style={{ background: colors.blue50, color: colors.blue600, padding: "2px 8px", borderRadius: 6, fontSize: 11, fontWeight: 500 }}>{results.length} found</span>
        </div>
      )}

      {loading && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 12 }}>
          {[1, 2, 3].map(i => (
            <div key={i} style={{ background: "#fff", border: colors.border, borderRadius: 12, overflow: "hidden" }}>
              <div style={{ height: 108, background: "#f0f0ee" }} />
              <div style={{ padding: "10px 12px" }}>
                <div style={{ height: 12, background: "#f0f0ee", borderRadius: 4, marginBottom: 6, width: "70%" }} />
                <div style={{ height: 10, background: "#f0f0ee", borderRadius: 4, width: "90%" }} />
              </div>
            </div>
          ))}
        </div>
      )}

      {searched && !loading && results.length === 0 && !error && (
        <div style={{ textAlign: "center", padding: "50px 20px", color: "#ccc" }}>
          <div style={{ fontSize: 36, marginBottom: 10 }}>🤷</div>
          <div>No matching shots found for "{query}"</div>
          <div style={{ fontSize: 11, marginTop: 6 }}>Try uploading some shots first, or rephrase your query.</div>
        </div>
      )}

      {!loading && results.length > 0 && (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 12 }}>
          {results.map(r => (
            <div key={r.id} onClick={() => setSelectedEntry(r)}
              style={{ background: "#fff", border: colors.border, borderRadius: 12, overflow: "hidden", cursor: "pointer", transition: "box-shadow 0.15s" }}
              onMouseEnter={e => e.currentTarget.style.boxShadow = "0 4px 16px rgba(0,0,0,0.08)"}
              onMouseLeave={e => e.currentTarget.style.boxShadow = "none"}
            >
              <div style={{ height: 108, background: "#f5f5f3", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 34, borderBottom: colors.border, position: "relative", overflow: "hidden" }}>
                {r.file_url
                  ? (r.media_type === "video"
                      ? <video src={`${API_BASE}${r.file_url}`} style={{ width: "100%", height: "100%", objectFit: "cover" }} muted />
                      : <img src={`${API_BASE}${r.file_url}`} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />)
                  : (r.media_type === "video" ? "🎬" : "🖼️")
                }
                <span style={{ position: "absolute", top: 7, right: 7, background: "rgba(0,0,0,0.55)", color: "#fff", fontSize: 10, padding: "2px 7px", borderRadius: 6, fontWeight: 500 }}>{r.media_type || "shot"}</span>
                <span style={{ position: "absolute", bottom: 7, left: 7, background: colors.green50, color: colors.green700, fontSize: 9, padding: "2px 6px", borderRadius: 5, fontWeight: 600 }}>{Math.round(r.score * 100)}% match</span>
              </div>
              <div style={{ padding: "10px 12px" }}>
                <div style={{ fontSize: 13, fontWeight: 500, color: "#111", marginBottom: 3 }}>{r.title}</div>
                {r.shot_type && <div style={{ fontSize: 10, color: colors.blue600, marginBottom: 5, fontWeight: 500 }}>{r.shot_type}</div>}
                <div style={{ fontSize: 11, color: "#888", lineHeight: 1.5, marginBottom: 7 }}>{r.description?.length > 80 ? r.description.slice(0, 80) + "…" : r.description}</div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                  {r.tags?.slice(0, 3).map(t => <span key={t} style={{ background: colors.teal50, color: colors.teal800, padding: "2px 8px", borderRadius: 10, fontSize: 10, fontWeight: 500 }}>{t}</span>)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ─── Root ─── */
export default function App() {
  const [page, setPage] = useState("upload");
  const [entryCount, setEntryCount] = useState(0);

  const refreshCount = async () => {
    const data = await api.count();
    setEntryCount(data.count ?? 0);
  };

  useEffect(() => { refreshCount(); }, []);

  return (
    <div style={{ display: "flex", height: "100vh", background: "#f5f5f3", fontFamily: "system-ui, -apple-system, sans-serif", fontSize: 13 }}>
      <Sidebar page={page} setPage={setPage} entryCount={entryCount} />
      <main style={{ flex: 1, overflowY: "auto", padding: "24px 28px" }}>
        {page === "upload" ? <UploadPage onSaved={refreshCount} /> : <QueryPage />}
      </main>
    </div>
  );
}