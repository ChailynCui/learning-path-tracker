import { createRouter, createWebHistory } from "vue-router";

import ArchiveView from "../views/ArchiveView.vue";
import CreatePathView from "../views/CreatePathView.vue";
import DashboardView from "../views/DashboardView.vue";
import PathDetailView from "../views/PathDetailView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "dashboard", component: DashboardView },
    { path: "/paths/new", name: "create-path", component: CreatePathView },
    { path: "/paths/:id", name: "path-detail", component: PathDetailView },
    { path: "/archives", name: "archives", component: ArchiveView }
  ]
});

export default router;
