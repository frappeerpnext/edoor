import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import Dashboard from "../views/dashboard/Dashboard.vue";
import Frontdesk from "../views/frontdesk/Frontdesk.vue"
import ReservationList from "../views/frontdesk/ReservationList.vue"
import authRoutes from './auth';

const routes = [
  { path: "/", redirect: '/edoor/frontdesk' }, 
  { path: "/edoor/frontdesk", name: "Home", component: Home, meta: { layout: 'main_layout' } },
  { path: "/edoor/frontdesk/dashboard", name: "Dashboard", component: Dashboard, meta: { layout: 'main_layout' } },
  { path: "/edoor/frontdesk/frontdesk", name: "Frontdesk", component: Frontdesk, meta: { layout: 'main_layout' } },
  { path: "/edoor/frontdesk/reservations", name: "ReservationList", component: ReservationList, meta: { layout: 'main_layout' } },
  ...authRoutes,
];

const router = createRouter({
  base: "/edoor/frontdesk/",
  history: createWebHistory(),
  routes,
});

export default router;
