(() => {
  const TOKEN_KEY = "py_files_access_token";

  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const authStatus = document.getElementById("auth-status");
  const uploadForm = document.getElementById("upload-form");
  const fileInput = document.getElementById("file-input");
  const uploadBtn = document.getElementById("upload-btn");
  const progressWrap = document.getElementById("progress-wrap");
  const progressBar = document.getElementById("progress-bar");
  const progressLabel = document.getElementById("progress-label");
  const uploadLog = document.getElementById("upload-log");
  const filesTbody = document.getElementById("files-tbody");
  const filesRefreshBtn = document.getElementById("files-refresh");

  function log(line) {
    const ts = new Date().toISOString();
    uploadLog.textContent += `[${ts}] ${line}\n`;
    uploadLog.scrollTop = uploadLog.scrollHeight;
  }

  function setAuthStatus(text, ok) {
    authStatus.textContent = text;
    authStatus.classList.remove("ok", "err");
    if (ok === true) authStatus.classList.add("ok");
    if (ok === false) authStatus.classList.add("err");
  }

  function getToken() {
    return sessionStorage.getItem(TOKEN_KEY);
  }

  function setToken(token) {
    if (token) sessionStorage.setItem(TOKEN_KEY, token);
    else sessionStorage.removeItem(TOKEN_KEY);
  }

  function baseName(fn) {
    const s = String(fn || "");
    const i = Math.max(s.lastIndexOf("/"), s.lastIndexOf("\\"));
    const out = i >= 0 ? s.slice(i + 1) : s;
    return out.trim() ? out : "download.bin";
  }

  function renderPlaceholderRow(message, isMuted) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 4;
    td.textContent = message;
    if (isMuted) td.classList.add("file-muted");
    tr.appendChild(td);
    filesTbody.appendChild(tr);
  }

  async function refreshFileList() {
    const token = getToken();
    if (!token) {
      filesTbody.textContent = "";
      renderPlaceholderRow("Sign in to see your uploaded files.", true);
      return;
    }
    try {
      const r = await fetch("/api/v1/objects", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const body = await r.json().catch(() => []);
      filesTbody.textContent = "";
      if (!r.ok) {
        const msg =
          typeof body.detail === "string"
            ? body.detail
            : `List failed (${r.status})`;
        renderPlaceholderRow(msg, false);
        return;
      }
      if (!Array.isArray(body) || body.length === 0) {
        renderPlaceholderRow("No stored files yet.", true);
        return;
      }
      for (let i = 0; i < body.length; i += 1) {
        const o = body[i];
        const tr = document.createElement("tr");
        const nameCell = document.createElement("td");
        nameCell.className = "file-name-cell";
        nameCell.title = o.original_filename;
        nameCell.textContent = baseName(o.original_filename);
        tr.appendChild(nameCell);

        const sizeCell = document.createElement("td");
        sizeCell.textContent = String(o.byte_size);
        tr.appendChild(sizeCell);

        const expCell = document.createElement("td");
        expCell.textContent = String(o.expires_at || "");
        expCell.title = expCell.textContent;
        tr.appendChild(expCell);

        const act = document.createElement("td");
        act.className = "file-actions";
        const bn = document.createElement("button");
        bn.type = "button";
        bn.textContent = "Download";
        bn.dataset.action = "download";
        bn.dataset.id = String(o.id);
        bn.dataset.name = String(o.original_filename);
        act.appendChild(bn);
        tr.appendChild(act);

        filesTbody.appendChild(tr);
      }
    } catch (err) {
      filesTbody.textContent = "";
      renderPlaceholderRow(
        err instanceof Error ? err.message : String(err),
        false,
      );
    }
  }

  async function downloadObject(id, displayName, token) {
    const safeId = encodeURIComponent(id);
    const r = await fetch(`/api/v1/objects/${safeId}/content`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!r.ok) {
      let detail = "";
      try {
        const j = await r.json();
        detail = typeof j.detail === "string" ? j.detail : "";
      } catch {
        detail = "";
      }
      throw new Error(detail || `Download failed (${r.status})`);
    }
    const blob = await r.blob();
    const url = URL.createObjectURL(blob);
    try {
      const a = document.createElement("a");
      a.href = url;
      a.download = baseName(displayName);
      a.rel = "noopener";
      document.body.appendChild(a);
      a.click();
      a.remove();
    } finally {
      URL.revokeObjectURL(url);
    }
  }

  filesRefreshBtn.addEventListener("click", () => {
    void refreshFileList();
  });

  filesTbody.addEventListener("click", (ev) => {
    const btn = ev.target.closest("button[data-action='download']");
    if (!btn) return;
    const token = getToken();
    if (!token) {
      log("Download blocked: sign in first.");
      return;
    }
    const oid = btn.getAttribute("data-id");
    const oname = btn.getAttribute("data-name") || "download.bin";
    log(`Downloading… ${oname} (id=${oid})`);
    void downloadObject(oid, oname, token)
      .then(() => {
        log(`Download started: ${oname}`);
      })
      .catch((err) => {
        log(
          `Download failed (${oname}): ${
            err instanceof Error ? err.message : String(err)
          }`,
        );
      });
  });

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(loginForm);
    const login = String(fd.get("login") || "").trim();
    const password = String(fd.get("password") || "");
    setAuthStatus("Signing in…", undefined);
    try {
      const r = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ login, password }),
      });
      const body = await r.json().catch(() => ({}));
      if (!r.ok) {
        setAuthStatus(body.detail || `Login failed (${r.status})`, false);
        setToken(null);
        return;
      }
      setToken(body.access_token);
      setAuthStatus("Signed in.", true);
      log(`Signed in as ${login}`);
      void refreshFileList();
    } catch (err) {
      setAuthStatus(err instanceof Error ? err.message : String(err), false);
      setToken(null);
    }
  });

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(registerForm);
    const login = String(fd.get("login") || "").trim();
    const password = String(fd.get("password") || "");
    setAuthStatus("Registering…", undefined);
    try {
      const r = await fetch("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ login, password }),
      });
      const body = await r.json().catch(() => ({}));
      if (!r.ok) {
        setAuthStatus(body.detail || `Registration failed (${r.status})`, false);
        return;
      }
      setAuthStatus("Registered. You can sign in now.", true);
      log(`Registered user ${login}`);
    } catch (err) {
      setAuthStatus(err instanceof Error ? err.message : String(err), false);
    }
  });

  function uploadOne(file, token) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const fd = new FormData();
      fd.append("file", file, file.name);

      xhr.open("POST", "/api/v1/objects");
      xhr.setRequestHeader("Authorization", `Bearer ${token}`);

      xhr.upload.onloadstart = () => {
        progressWrap.hidden = false;
        progressBar.value = 0;
        progressBar.removeAttribute("value");
        progressLabel.textContent = "0%";
      };

      xhr.upload.onprogress = (ev) => {
        if (!ev.lengthComputable) return;
        const pct = Math.round((ev.loaded / ev.total) * 100);
        progressBar.value = pct;
        progressLabel.textContent = `${pct}% (${ev.loaded} / ${ev.total} bytes)`;
      };

      xhr.onload = () => {
        progressWrap.hidden = true;
        let parsed = {};
        try {
          parsed = JSON.parse(xhr.responseText || "{}");
        } catch {
          /* ignore */
        }
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(parsed);
        } else {
          const raw = parsed.detail ?? parsed.message ?? `HTTP ${xhr.status}`;
          let msg;
          if (typeof raw === "string") {
            msg = raw;
          } else if (Array.isArray(raw)) {
            msg = raw.map((x) => x.msg || JSON.stringify(x)).join("; ");
          } else {
            msg = JSON.stringify(raw);
          }
          reject(new Error(msg));
        }
      };

      xhr.onerror = () => reject(new Error("Network error during upload"));

      xhr.send(fd);
    });
  }

  uploadForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const token = getToken();
    if (!token) {
      log("Upload blocked: sign in first.");
      setAuthStatus("Sign in before uploading.", false);
      return;
    }
    const files = fileInput.files;
    if (!files || files.length === 0) {
      log("No file selected.");
      return;
    }
    uploadBtn.disabled = true;
    for (let i = 0; i < files.length; i += 1) {
      const file = files[i];
      log(`Starting upload: ${file.name} (${file.size} bytes)`);
      try {
        const meta = await uploadOne(file, token);
        log(`OK ${file.name} → id=${meta.id} size=${meta.byte_size}`);
        void refreshFileList();
      } catch (err) {
        log(`FAIL ${file.name}: ${err instanceof Error ? err.message : String(err)}`);
      }
    }
    uploadBtn.disabled = false;
    fileInput.value = "";
  });

  if (getToken()) {
    setAuthStatus("Session restored (token in memory).", true);
  }
  void refreshFileList();
})();
