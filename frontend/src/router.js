import { createRouter, createWebHistory } from 'vue-router'
import register from './components/register.vue'
import login from './components/login.vue'
import logout from './components/logout.vue'
import admin_dashboard from './components/admin_dashboard.vue'
import user_dashboard from './components/user_dashboard.vue'
import quiz from './components/quiz.vue'
import score from './components/score.vue'
import admin_summary from './components/admin_summary.vue'
import user_summary from './components/user_summary.vue'

const routes = [
  { path: "/", component: login },
  { path: "/login", component: login },
  { path: "/register", component: register },
  { path: "/logout", component: logout },
  { path: "/api/user/dashboard", component: user_dashboard },
  { path: "/api/admin/dashboard", component: admin_dashboard },
  { path: "/api/user/quiz/:quiz_id", component: quiz },
  { path: "/api/user/quiz/:quiz_id/score", component: score },
  { path: "/api/admin/summary", component: admin_summary },
  { path: "/api/user/summary", component: user_summary }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router