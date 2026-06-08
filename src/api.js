const BASE = "/api"
const API_ORIGIN = import.meta.env.DEV ? "http://192.168.0.230:8000" : window.location.origin
export const IMAGE_BASE = API_ORIGIN;

async function request(path, options = {}) {
  const token = localStorage.getItem("token");
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(BASE + path, { ...options, headers });
  if (res.status === 401 && !path.startsWith("/auth/")) {
    localStorage.removeItem("token");
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "请求失败");
  }
  return data;
}

export const api = {
  auth: {
    login: (username, password) => request("/auth/login", { method: "POST", body: JSON.stringify({ username, password }) }),
    me: () => request("/auth/me"),
    profile: (data) => request("/auth/profile", { method: "PUT", body: JSON.stringify(data) }),
    profile: (data) => request("/auth/profile", { method: "PUT", body: JSON.stringify(data) }),
  },
  questions: {
    list: (params = {}) => request("/questions?" + new URLSearchParams(params)),
    stats: () => request("/questions/stats"),
    categories: () => request("/questions/categories"),
    create: (data) => request("/questions", { method: "POST", body: JSON.stringify(data) }),
    update: (id, data) => request(`/questions/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    delete: (id) => request(`/questions/${id}`, { method: "DELETE" }),
    batchDelete: (ids) => request("/questions/batch-delete", { method: "POST", body: JSON.stringify({ ids }) }),
    batchExport: async (ids) => { const token = localStorage.getItem("token"); const headers = {"Content-Type": "application/json"}; if (token) headers["Authorization"] = "Bearer " + token; const resp = await fetch("/api/questions/batch-export", { method: "POST", headers, body: JSON.stringify({ ids }) }); return resp; },
    batchCategory: (ids, category) => request("/questions/batch-category", { method: "PUT", body: JSON.stringify({ ids, category }) }),
  },
  categories: {
    list: () => request("/categories"),
    create: (name, sort) => request("/categories", { method: "POST", body: JSON.stringify({ name, sort }) }),
    update: (id, data) => request(`/categories/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    delete: (id) => request(`/categories/${id}`, { method: "DELETE" }),
  },
  dashboard: {
    get: () => request("/dashboard"),
  },
  exams: {
    list: (params = {}) => request("/exams?" + new URLSearchParams(params)),
    create: (data) => request("/exams", { method: "POST", body: JSON.stringify(data) }),
    get: (id) => request(`/exams/${id}`),
    detail: (id) => request(`/exams/${id}/detail`),
    papers: (id) => request(`/exams/${id}/papers`),
    start: (id, mode) => request(`/exams/${id}/start` + (mode ? `?mode=${mode}` : ""), { method: "POST" }),
    updateStatus: (id, status) => request(`/exams/${id}/status?status=${status}`, { method: "PUT" }),
    update: (id, data) => request(`/exams/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    delete: (id) => request(`/exams/${id}`, { method: "DELETE" }),
    generate: (id) => request(`/exams/${id}/generate`, { method: "POST" }),
    questions: (id) => request(`/exams/${id}/questions`),
    retake: (eid, uid) => request(`/exams/${eid}/retake/${uid}`, { method: "POST" }),
    paper: (pid) => request(`/exams/paper/${pid}`),
  },
  answers: {
    submit: (paperId, data) => request(`/answers/submit/${paperId}`, { method: "POST", body: JSON.stringify(data) }),
    grade: (paperId, data) => request(`/answers/grade/${paperId}`, { method: "PUT", body: JSON.stringify(data) }),
  },
    settings: {
    get: () => request("/settings"),
    update: (data) => request("/settings", { method: "PUT", body: JSON.stringify(data) }),
  },
  logs: {
    list: (params = {}) => request("/logs?" + new URLSearchParams(params)),
    actions: () => request("/logs/actions"),
  },
  notifications: {
    list: () => request("/notifications"),
    unread: () => request("/notifications/unread"),
    markRead: (id) => request("/notifications/" + id + "/read", { method: "PUT" }),
  },
  settings: {
    get: () => request("/settings"),
    update: (data) => request("/settings", { method: "PUT", body: JSON.stringify(data) }),
  },
  logs: {
    list: (params = {}) => request("/logs?" + new URLSearchParams(params)),
    actions: () => request("/logs/actions"),
  },
  notifications: {
    list: () => request("/notifications"),
    unread: () => request("/notifications/unread"),
    markRead: (id) => request("/notifications/" + id + "/read", { method: "PUT" }),
  },
  results: {
    list: () => request("/results"),
    byExam: () => request("/results/by-exam"),
    get: (id) => request(`/results/${id}`),
    stats: () => request("/results/stats"),
    my: () => request("/results/my"),
  },
};
