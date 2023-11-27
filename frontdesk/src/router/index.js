
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
import NotFound from "@/components/NotFound.vue";
import Activity from "@/views/activities/Activity.vue";
import DepositLedger from "@/views/deposit_ledger/DepositLedger.vue";
import AccountCodeSortOrder from "@/views/other/AccountCodeSortOrder.vue";
import AccountCategorySortOrder from "@/views/other/AccountCategorySortOrder.vue";
import CashierShift from "@/views/cashier_shift/CashierShift.vue";

import authRoutes from './auth';

 


let routes = [
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
  { path: "/frontdesk/housekeeping/room-block", name: "HousekeepingRoomBlock", component: RoomBlock, meta: { layout: 'main_layout', title: 'Room Block' } },
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
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound },
  { path: "/frontdesk/test2", name: "Test2", component: TestPage2, meta: { layout: 'main_layout' } },
  { path: "/frontdesk/test-page", name: "TestPage", component: TestPage, meta: { layout: 'main_layout' } },
  { path: "/frontdesk/activity", name: "Activity", component: Activity, meta: { layout: 'main_layout' } },
  { path: "/frontdesk/deposit-ledger", name: "DepositLedger", component: DepositLedger, meta: { layout: 'main_layout',title:"Deposit Ledger" } },
  { path: "/frontdesk/account-code-sort-order", name: "AccountCodeSortOrder", component:AccountCodeSortOrder, meta: { layout: 'blank_layout',title:"Sort Order Account Code" } },
  { path: "/frontdesk/account-category-sort-order", name: "AccountCategorySortOrder", component:AccountCategorySortOrder, meta: { layout: 'blank_layout',title:"Sort Order Account Category" } },
  { path: "/frontdesk/cashier-shift", name: "CashierShift", component:CashierShift, meta: { layout: 'main_layout',title:"Cashier Shift" } },
 
  ...authRoutes,

]  
export  const  getRoutes = function  (whitelist_route,edoor_menu) {
  let default_menu = edoor_menu.filter(r=>r.parent_edoor_menu=="All Menus")[0]
  if(default_menu){
    const default_route =JSON.parse(JSON.stringify( routes.filter(r=>r.name ==default_menu.menu_name)))
    routes.push({
        path:"/",
        redirect: default_route[0].path 
      })
     
      routes.push({
        path:"/frontdesk",
        redirect: default_route[0].path 
      })
     
   
  }
  

  routes = routes.filter(r=>whitelist_route?.includes(r.name) || r.path=="/" || r.path=='/frontdesk')
  
   const   router = createRouter({
		base: "/edoor/frontdesk/",
		history: createWebHistory(),
		routes
	  });
    return router
}

export const allRoutes = function (){
  return routes
}

export default {
  getRoutes,
  allRoutes
}