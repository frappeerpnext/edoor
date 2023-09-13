import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import Dashboard from "../views/dashboard/Dashboard.vue";
import Frontdesk from "../views/frontdesk/Frontdesk.vue"
import ReservationList from "../views/frontdesk/ReservationList.vue";
import ReservationStayList from "@/views/frontdesk/ReservationStayList.vue";
import Housekeeping from "../views/housekeeping/Housekeeping.vue";
import ReservationStayDetail from "../views/reservation/ReservationStayDetail.vue";
import ReservationDetail from "../views/reservation/ReservationDetail.vue";
import GuestList from "../views/guest/GuestList.vue";
import GuestType from "../views/guest/GuestType.vue";
import TestPage from "../views/TestPage.vue";
import TestPage2 from "../views/TestPage2.vue";
import RoomInventory from "@/views/frontdesk/RoomInventory.vue";
import FolioTransaction from "@/views/frontdesk/FolioTransactionList.vue";
import DeskFolio from "@/views/desk_folio/DeskFolio.vue";
import Note from "@/views/note/Note.vue";
import NoPermission from "@/views/other/driver/NoPermission.vue";
import GuestLedger from "@/views/guest_ledger/GuestLedger.vue";
import GuestLedgerTransaction from "@/views/guest_ledger/GuestLedgerTransaction.vue";
import RoomBlock from "@/views/room_block/RoomBlockList.vue";
import CityLedger from "@/views/city_ledger/CityLedger.vue";
import CityLedgerAccount from "@/views/city_ledger/CityLedgerAccount.vue";
import CityLedgerType from "@/views/city_ledger/CityLedgerType.vue";
import Reports from "@/views/report/Reports.vue";
import BusinessSource from "@/views/business_source/BusinessSource.vue";
import BusinessSourceType from "@/views/business_source/BusinessSourceType.vue";
import authRoutes from './auth';

const routes = [
  { path: "/", redirect: '/frontdesk/dashboard' }, 
  { path: "/frontdesk", name: "Dashboard", component: Dashboard, meta: { layout: 'main_layout', title: 'Dashboard' } },
  { path: "/frontdesk/dashboard", name: "Dashboard", component: Dashboard, meta: { layout: 'main_layout', title: 'Dashboard' } },
  { path: "/frontdesk/frontdesk", name: "Frontdesk", component: Frontdesk, meta: { layout: 'main_layout', title: 'Front Desk' } },
  { path: "/frontdesk/reservations", name: "ReservationList", component: ReservationList, meta: { layout: 'main_layout', title: 'Reservations' } },
  { path: "/frontdesk/inventory", name: "RoomInventory", component: RoomInventory, meta: { layout: 'main_layout', title: 'Room Inventory' } },

  { path: "/frontdesk/folio-transaction", name: "FolioTransaction", component: FolioTransaction, meta: { layout: 'main_layout', title: 'Folio Transaction List' } },

  { path: "/frontdesk/reservation-stay", name: "ReservationStayList", component: ReservationStayList, meta: { layout: 'main_layout', title: 'Reservation Stay List' } },
  { path: "/frontdesk/desk-folio", name: "DeskFolio", component: DeskFolio, meta: { layout: 'main_layout', title: 'Desk Folio' } },
  { path: "/frontdesk/no-permission", name: "NoPermission", component:NoPermission, meta: { layout: 'main_layout', title: 'Access Denied' } },
  { path: "/frontdesk/note", name: "Note", component: Note, meta: { layout: 'main_layout', title: 'Note' } },
  { path: "/frontdesk/room-block", name: "RoomBlock", component: RoomBlock, meta: { layout: 'main_layout', title: 'Room Block' } },
  { path: "/frontdesk/housekeeping", name: "Housekeeping", component: Housekeeping, meta: { layout: 'main_layout', title: 'Housekeeping' } },
  { path: "/frontdesk/stay-detail/:name?", name: "ReservationStayDetail", component:ReservationStayDetail, meta: { layout: 'main_layout', title: 'Reservation Stay Detail' } },
  { path: "/frontdesk/reservation-detail/:name?", name: "ReservationDetail", component:ReservationDetail, meta: { layout: 'main_layout', title: 'Reservation Detail' } },
  { path: "/frontdesk/guest-database", name: "GuestDatabase", component:GuestList, meta: { layout: 'main_layout', title:"Guest Database" } },
  { path: "/frontdesk/guest-type", name: "GuestType", component:GuestType, meta: { layout: 'main_layout', title:"Guest Type" } },
  { path: "/frontdesk/guest-ledger", name: "GuestLedger", component:GuestLedger, meta: { layout: 'main_layout', title:"Guest Ledger" } },
  { path: "/frontdesk/city-ledger", name: "CityLedger", component:CityLedger, meta: { layout: 'main_layout', title:"City Ledger" } },
  { path: "/frontdesk/city-ledger-type", name: "CityLedgerType", component:CityLedgerType, meta: { layout: 'main_layout', title:"City Ledger Account Type" } },
  { path: "/frontdesk/city-ledger-account", name: "CityLedgerAccount", component:CityLedgerAccount, meta: { layout: 'main_layout', title:"City Ledger Account" } },
  { path: "/frontdesk/reports", name: "Reports", component:Reports, meta: { layout: 'main_layout', title:"Reports" } },
  { path: "/frontdesk/reports", name: "Reports", component:Reports, meta: { layout: 'main_layout', title:"Reports" } },
  { path: "/frontdesk/guest-ledger-transaction", name: "GuestLedgerTransaction", component:GuestLedgerTransaction, meta: { layout: 'main_layout', title:"Guest Ledger Transaction" } },
  { path: "/frontdesk/business-source", name: "BusinessSource", component:BusinessSource, meta: { layout: 'main_layout', title:"Business Source" } },
  { path: "/frontdesk/business-source-type", name: "BusinessSourceType", component:BusinessSourceType, meta: { layout: 'main_layout', title:"Business Source Type" } },
 
  { path: "/frontdesk/test2", name: "Test2", component: TestPage2, meta: { layout: 'main_layout' } },
  ...authRoutes,
];

const router = createRouter({
  base: "/edoor/frontdesk/",
  history: createWebHistory(),
  routes,
});

export default router;
