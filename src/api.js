const BASE = "/api";

async function request(path, options = {}) {
  const token = localStorage.getItem("token");
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(BASE + path, { ...options, headers });
  if (res.status === 401) {
    localStorage.removeItem("token");
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }
  return res.json();
}

export const api = {
  auth: {
    login: (username, password) => request("/auth/login", { method: "POST", body: JSON.stringify({ username, password }) }),
    me: () => request("/auth/me"),
  },
  questions: {
    list: (params = {}) => request("/questions?" + new URLSearchParams(params)),
    stats: () => request("/questions/stats"),
    create: (data) => request("/questions", { method: "POST", body: JSON.stringify(data) }),
    update: (id, data) => request(`/questions/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    delete: (id) => request(`/questions/${id}`, { method: "DELETE" }),
  },
  exams: {
    list: (params = {}) => request("/exams?" + new URLSearchParams(params)),
    create: (data) => request("/exams", { method: "POST", body: JSON.stringify(data) }),
    get: (id) => request(`/exams/${id}`),
    start: (id) => request(`/exams/${id}/start`, { method: "POST" }),
  },
  answers: {
    submit: (paperId, data) => request(`/answers/submit/${paperId}`, { method: "POST", body: JSON.stringify(data) }),
  },
  results: {
    list: () => request("/results"),
    get: (id) => request(`/results/${id}`),
    stats: () => request("/results/stats"),
  },
};
