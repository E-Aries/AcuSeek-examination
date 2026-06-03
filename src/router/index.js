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
});

export default router;
