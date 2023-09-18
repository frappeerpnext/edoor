import './index.css';
//theme
import "./assets/css/theme.css";
//core
import "./assets/css/primevue.css";
//icon 
import 'primeicons/primeicons.css';
// flex css
import '/node_modules/primeflex/primeflex.css'

import './assets/css/style.css'



import { createApp, reactive } from "vue";
import App from "./App.vue";

import Error from "./components/Error.vue";

import router from './router';

import Auth from "./utils/auth";

import { FrappeApp } from 'frappe-js-sdk';
import { resourcesPlugin } from "./resources"
import { setConfig, frappeRequest } from './resource'
setConfig('resourceFetcher', frappeRequest)
import PrimeVue from 'primevue/config';
import ConfirmationService from 'primevue/confirmationservice';
import NumberFormat from 'number-format.js'
import { vue3Debounce } from 'vue-debounce'

const app = createApp(App);


const auth = reactive(new Auth());
const frappe = new FrappeApp()



// inject
import moment from "./utils/moment";
import Gv from './providers/gv';
import Housekeeping from './providers/housekeeping';
import Reservation from './providers/reservation';
import ReservationStay from './providers/reservation_stay';

// directive
import BadgeDirective from 'primevue/badgedirective';

// prime components //
import Button from "primevue/button"
import Menu from 'primevue/menu';
import Skeleton from 'primevue/skeleton';
import Avatar from 'primevue/avatar';
import Toast from 'primevue/toast';
import ToastService from 'primevue/toastservice';
import Checkbox from 'primevue/checkbox';
import Dropdown from 'primevue/dropdown';
import InputNumber from 'primevue/inputnumber';
import InputSwitch from 'primevue/inputswitch';
import InputText from 'primevue/inputtext';
import Listbox from 'primevue/listbox';
import MultiSelect from 'primevue/multiselect';
import RadioButton from 'primevue/radiobutton';
import SelectButton from 'primevue/selectbutton';
import Textarea from 'primevue/textarea';
import SplitButton from 'primevue/splitbutton';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import ColumnGroup from 'primevue/columngroup';   // optional
import Row from 'primevue/row';                   // optional
import Timeline from 'primevue/timeline';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import Card from 'primevue/card';
import Divider from 'primevue/divider';
import Fieldset from 'primevue/fieldset';
import Panel from 'primevue/panel';
import ScrollPanel from 'primevue/scrollpanel';
import TabView from 'primevue/tabview';
import TabPanel from 'primevue/tabpanel';
import Toolbar from 'primevue/toolbar';
import ConfirmDialog from 'primevue/confirmdialog';
import ConfirmPopup from 'primevue/confirmpopup';
import Dialog from 'primevue/dialog';
import DynamicDialog from 'primevue/dynamicdialog';
import OverlayPanel from 'primevue/overlaypanel';
import Sidebar from 'primevue/sidebar';
import Tooltip from 'primevue/tooltip';
import Badge from 'primevue/badge';
import Chip from 'primevue/chip';
import DialogService from 'primevue/dialogservice';
import AutoComplete from 'primevue/autocomplete';
import Calendar from 'primevue/calendar';
import Chart from 'primevue/chart';
import Message from 'primevue/message';
// custom components //
import ComAvatar from './components/form/ComAvatar.vue'
import ComAutoComplete from './components/form/ComAutoComplete.vue'
import ComSelect from './components/form/ComSelect.vue'
import ComAttachFile from './components/form/ComAttachFile.vue'
import ComPanel from './components/layout/components/ComPanel.vue'
import ComHeader from './components/layout/components/ComHeader.vue'
import ComFieldset from './components/layout/components/ComFieldset.vue'
import ComDocument from './components/layout/ComDocument.vue'
import ComDialogContent from './components/form/ComDialogContent.vue'
import ComInputTime from './components/form/ComInputTime.vue'
import ComOverlayPanelFooter from './components/form/ComOverlayPanelFooter.vue'
import ComOverlayPanelContent from './components/form/ComOverlayPanelContent.vue'
import CurrencyFormat from './components/CurrencyFormat.vue'
import ComChartDoughnut from './components/chart/ComChartDoughnut.vue'
import ComIcon from './components/ComIcon.vue'
import ComPlaceholder from './components/layout/components/ComPlaceholder.vue'
import ComReservationStatus from './components/label/ComReservationStatus.vue'
import ComUploadProfile from './components/form/ComUploadProfile.vue'
import ComColorPicker from './components/form/ComColorPicker.vue'
import ComInputCurrency from './components/form/ComInputCurrency.vue'
import ComSelectRoomTypeAvailability from '@/views/reservation/components/form/ComSelectRoomTypeAvailability.vue'
import ComSelectRoomAvailability from '@/views/reservation/components/form/ComSelectRoomAvailability.vue'
import ComNote from './components/form/ComNote.vue'
import ComDialogNote from './components/form/ComDialogNote.vue'
import socket from './utils/socketio';
import ComStayInfoNoBox from '@/views/reservation/components/ComStayInfoNoBox.vue'
import ComLastModifiedInfo from './components/layout/components/ComLastModifiedInfo.vue'
import VueTippy from 'vue-tippy'
import 'tippy.js/dist/tippy.css' // optional for styling

// use components //
app.component('Button', Button);
app.component('Menu', Menu);
app.component('Avatar', Avatar);
app.component('Toast', Toast);
app.component('Checkbox', Checkbox);
app.component('Dropdown', Dropdown);
app.component('InputNumber', InputNumber);
app.component('InputSwitch', InputSwitch);
app.component('InputText', InputText);
app.component('Listbox', Listbox);
app.component('MultiSelect', MultiSelect);
app.component('RadioButton', RadioButton);
app.component('SelectButton', SelectButton);
app.component('Textarea', Textarea);
app.component('SplitButton', SplitButton);
app.component('DataTable', DataTable);
app.component('Column', Column);
app.component('ColumnGroup', ColumnGroup);
app.component('Row', Row);
app.component('Timeline', Timeline);
app.component('Accordion', Accordion);
app.component('AccordionTab', AccordionTab);
app.component('Card', Card);
app.component('Divider', Divider);
app.component('Fieldset', Fieldset);
app.component('Panel', Panel);
app.component('ScrollPanel', ScrollPanel);
app.component('TabView', TabView);
app.component('TabPanel', TabPanel);
app.component('Toolbar', Toolbar);
app.component('ConfirmDialog', ConfirmDialog);
app.component('ConfirmPopup', ConfirmPopup);
app.component('Dialog', Dialog);
app.component('DynamicDialog', DynamicDialog);
app.component('OverlayPanel', OverlayPanel);
app.component('Sidebar', Sidebar);
app.component('Badge', Badge);
app.component('Chip', Chip);
app.component('Tooltip', Tooltip);
app.component('AutoComplete', AutoComplete)
app.component('Calendar', Calendar)
app.component('Chart', Chart)
app.component('Skeleton', Skeleton)
app.component('Message', Message)
// use custom components //
app.component('ComAvatar', ComAvatar)
app.component('ComPanel', ComPanel)
app.component('ComAutoComplete', ComAutoComplete)
app.component('ComSelect', ComSelect)
app.component('ComHeader', ComHeader)
app.component('ComFieldset', ComFieldset)
app.component('ComDialogContent', ComDialogContent)
app.component('CurrencyFormat', CurrencyFormat)
app.component('ComChartDoughnut', ComChartDoughnut)
app.component('ComOverlayPanelFooter', ComOverlayPanelFooter)
app.component('ComOverlayPanelContent', ComOverlayPanelContent)
app.component('ComIcon', ComIcon)
app.component('ComAttachFile', ComAttachFile)
app.component('ComDocument', ComDocument)
app.component('ComInputTime', ComInputTime)
app.component('ComPlaceholder', ComPlaceholder)
app.component('ComReservationStatus', ComReservationStatus)
app.component('ComUploadProfile', ComUploadProfile)
app.component('ComSelectRoomTypeAvailability', ComSelectRoomTypeAvailability)
app.component('ComSelectRoomAvailability', ComSelectRoomAvailability)
app.component('ComNote', ComNote)
app.component('ComDialogNote', ComDialogNote)
app.component('ComColorPicker', ComColorPicker)
app.component('ComInputCurrency', ComInputCurrency)
app.component('ComStayInfoNoBox', ComStayInfoNoBox)
app.component('ComLastModifiedInfo', ComLastModifiedInfo)

// Plugins
app.use(frappe)
app.use(router);
app.use(resourcesPlugin);
app.use(PrimeVue, {
	ripple: true,
	inputStyle: "filled",
	pt: {
		button: {
			class: 'submit'
		}
	}
})
app.use(ToastService);
app.use(DialogService);
// app.use(resourceManager);
app.use(ConfirmationService);



app.use(
	VueTippy,
	// optional
	{
		directive: 'tippy', // => v-tippy
		component: 'tippy', // => <tippy/>
		componentSingleton: 'tippy-singleton', // => <tippy-singleton/>,
		defaultProps: {
			placement: "bottom",
			allowHTML: true,
			followCursor: true,
			//interactive: true,
		},
	}
)

// Global Properties,

app.provide("$auth", auth);

app.provide("$socket", socket)
app.provide("$frappe", frappe);
app.provide("$numberFormat", NumberFormat)



app.directive('badge', BadgeDirective);
app.directive('tooltip', Tooltip);
app.directive('debounce', vue3Debounce({ lock: true }))

const gv = reactive(new Gv());
const housekeeping = reactive(new Housekeeping());
const reservation = reactive(new Reservation());
const reservation_stay = reactive(new ReservationStay());
 
app.provide("$moment", moment)
app.provide("$gv", gv)
app.provide("$housekeeping", housekeeping)
app.provide("$reservation", reservation)
app.provide("$reservation_stay", reservation_stay)
// get global data
const apiCall = frappe.call()
 


const config = await getConfigData()
if (!auth.isLoggedIn) {
	const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + config.backend_port;
	window.location.replace(serverUrl)
}
 
router.beforeEach(async (to, from, next) => {
	 
	document.title = (to.meta.title || '') + ' | eDoor Front Desk'
	if (to.matched.some((record) => !record.meta.isLoginPage)) {
		// this route requires auth, check if logged in
		// if not, redirect to login page.
		if (!getCookie("user_id") || getCookie("user_id") == "Guest") {
			const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + config.backend_port;
			window.location.replace(serverUrl)
		} else {
			if (to?.name) {
			 
				const setting = JSON.parse(localStorage.getItem('edoor_setting'))
				if (setting.edoor_menu.filter((r) => r.menu_name == to.name).length > 0 || ["NoPermission", "ReservationStayDetail", "ReservationDetail"].includes(to.name)) {
				
					next();

				} else {
					 
					next({ name: 'NoPermission' });
				}
			}
		}


	} else {
		if (getCookie("user_id") != "Guest") {

			//find first record of edoor menu 
			const setting = JSON.parse(localStorage.getItem('edoor_setting'))
			if (setting) {
				let edoorMenu = setting?.edoor_menu?.filter(r => r.menu_name != 'All Menus' && r.parent_edoor_menu == 'All Menus')
				edoorMenu = edoorMenu.sort((a, b) => {
					return a.sort_order - b.sort_order;
				});
				if (edoorMenu) {
					  
					next({ name: edoorMenu[0].menu_name });
				} else {
				 
					next({ name: 'Dashboard' });
				}
			}


		} else {


			const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + config.backend_port;
			window.location.replace(serverUrl)


		}

	}
});



apiCall.get('edoor.api.frontdesk.get_edoor_setting', {
	property: localStorage.getItem("edoor_property") ? JSON.parse(localStorage.getItem("edoor_property"))?.name : null
}).then((r) => {

	const data = r.message
	if (data.user.name == "Guest") {
		const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + config.backend_port;

		window.location.replace(serverUrl)
	} else {
	
		localStorage.setItem('edoor_user', JSON.stringify(data.user))
		localStorage.setItem("edoor_setting", JSON.stringify(data.edoor_setting))
		gv.setting = data.edoor_setting
		if (r.message.property == "Invalid Property") {
			localStorage.removeItem("edoor_property")
		}
		else {
			localStorage.setItem('edoor_working_day', JSON.stringify(r.message.working_day))
			console.log(r.message.property)
			if (r.message.property) {
			
				if (r.message.property.length == 1) {
					
					localStorage.setItem('edoor_property', JSON.stringify(r.message.property[0]))
					 
					window.property = r.message.property[0].name
				}
			}
		}

		app.mount("#app");
	}

})





function getConfigData() {
	return new Promise((resolve, reject) => {

		apiCall.get('edoor.api.frontdesk.get_config_data').then((r) => {

			resolve(r.message)
		}).catch((err) => {
			reject(err)
		})

	});

}
function getCookie(name) {
	let cookie = document.cookie;
	let decodedCookie = decodeURIComponent(cookie);
	let ca = decodedCookie.split(';');

	for (let i = 0; i < ca.length; i++) {
		let parts = ca[i].split('=');
		if (parts[0].trim() === name) {
			return parts[1];
		}
	}

	return null;
}