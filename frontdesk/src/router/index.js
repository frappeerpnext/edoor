import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import Dashboard from "../views/dashboard/Dashboard.vue";
import Frontdesk from "../views/frontdesk/Frontdesk.vue"
import ReservationList from "../views/frontdesk/ReservationList.vue";
import Housekeeping from "../views/housekeeping/Housekeeping.vue";
import ReservationStayDetail from "../views/reservation/ReservationStayDetail.vue";
import GuestList from "../views/guest/GuestList.vue";
import TestPage from "../views/TestPage.vue";
import TestPage2 from "../views/TestPage2.vue";
import authRoutes from './auth';

const routes = [
  { path: "/", redirect: '/edoor/frontdesk' }, 
  { path: "/edoor/frontdesk", name: "Home", component: Home, meta: { layout: 'main_layout' } },
  { path: "/edoor/frontdesk/dashboard", name: "Dashboard", component: Dashboard, meta: { layout: 'main_layout' } },
  { path: "/edoor/frontdesk/frontdesk", name: "Frontdesk", component: Frontdesk, meta: { layout: 'main_layout' } },
  { path: "/edoor/frontdesk/reservations", name: "ReservationList", component: ReservationList, meta: { layout: 'main_layout' } },
  { path: "/edoor/frontdesk/housekeeping", name: "Housekeeping", component: Housekeeping, meta: { layout: 'main_layout' } },
  { path: "/edoor/frontdesk/stay-detail/:name?", name: "ReservationStayDetail", component:ReservationStayDetail, meta: { layout: 'main_layout' } },
  { path: "/edoor/frontdesk/guest-database", name: "GuestDatabase", component:GuestList, meta: { layout: 'main_layout' } },




  { path: "/edoor/frontdesk/test", name: "Test", component: TestPage, meta: { layout: 'main_layout' } },
  { path: "/edoor/frontdesk/test2", name: "Test2", component: TestPage2, meta: { layout: 'main_layout' } },
  ...authRoutes,
];

const router = createRouter({
  base: "/edoor/frontdesk/",
  history: createWebHistory(),
  routes,
});

export default router;
