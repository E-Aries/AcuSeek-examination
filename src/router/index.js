import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/Login.vue"),
    meta: { layout: "blank" },
  },
  {
    path: "/",
    component: () => import("../components/AppLayout.vue"),
    redirect: "/dashboard",
    children: [
      {
        path: "dashboard",
        name: "Dashboard",
        component: () => import("../views/Dashboard.vue"),
      },
      {
        path: "questions",
        name: "Questions",
        component: () => import("../views/Questions.vue"),
        meta: { requiresAdmin: true },
      },
      {
        path: "exams",
        name: "Exams",
        component: () => import("../views/Exams.vue"),
      },
      {
        path: "exams/:id",
        name: "ExamDetail",
        component: () => import("../views/ExamDetail.vue"),
        meta: { requiresAdmin: true },
      },
      {
        path: "exams/:id/take",
        name: "TakeExam",
        component: () => import("../views/TakeExam.vue"),
      },
      {
        path: "results",
        name: "Results",
        component: () => import("../views/Results.vue"),
      },
      {
        path: "results/:id",
        name: "ResultDetail",
        component: () => import("../views/ResultDetail.vue"),
      },
      {
        path: "users",
        name: "Users",
        component: () => import("../views/Users.vue"),
        meta: { requiresAdmin: true },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const token = localStorage.getItem("token");
  if (to.name !== "Login" && !token) {
    return { name: "Login" };
  }
  if (to.name === "Login" && token) {
    return { name: "Dashboard" };
  }
  // Role guard: admin-only pages
  if (to.meta?.requiresAdmin) {
    try {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      if (user.role !== "admin") return { name: "Dashboard" };
    } catch(e) { return { name: "Login" }; }
  }
});

export default router;
