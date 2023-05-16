import './index.css';
//theme
import "primevue/resources/themes/lara-light-indigo/theme.css";
//core
import "primevue/resources/primevue.min.css";
//icon 
import 'primeicons/primeicons.css';
// flex css
import '/node_modules/primeflex/primeflex.css'


import { createApp, reactive } from "vue";
import App from "./App.vue";

import router from './router';
import resourceManager from "../../../doppio/libs/resourceManager";
import call from "../../../doppio/libs/controllers/call";
import socket from "../../../doppio/libs/controllers/socket";
import Auth from "../../../doppio/libs/controllers/auth";
import { FrappeApp } from 'frappe-js-sdk';
import {resourcesPlugin} from "./resources"
import { setConfig, frappeRequest } from './resource'
setConfig('resourceFetcher', frappeRequest)
import PrimeVue from 'primevue/config';

const app = createApp(App);
const auth = reactive(new Auth());
const frappe = new FrappeApp()
// inject
import moment from "./utils/moment";

// directive
import BadgeDirective from 'primevue/badgedirective';

// prime components //
import Button from "primevue/button"
import Menu from 'primevue/menu';
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
// custom components //
import ComAvatar from './components/form/ComAvatar.vue'





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

// use custom components //
app.component('ComAvatar', ComAvatar)


// Plugins
app.use(router);
app.use(resourcesPlugin);
app.use(PrimeVue,{ 
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
app.use(resourceManager);

// Global Properties,
// components can inject this
app.provide("$auth", auth);
app.provide("$call", call);
app.provide("$socket", socket); 
app.provide("$frappe", frappe);

app.directive('badge', BadgeDirective);
app.directive('tooltip', Tooltip);

app.provide("$moment", moment)
// get global data
const apiCall = frappe.call()
apiCall.get('edoor.api.frontdesk.get_logged_user').then((r)=>{
	localStorage.setItem('current_user', JSON.stringify(r.message))
})

// Configure route gaurds
router.beforeEach(async (to, from, next) => {
	if (to.matched.some((record) => !record.meta.isLoginPage)) {
		// this route requires auth, check if logged in
		// if not, redirect to login page.
		if (!auth.isLoggedIn) {
			window.location.replace('http://192.168.10.114:1216/')
		} else {
			next();
		} 
	} else {
		if (auth.isLoggedIn) {
			next({ name: 'Dashboard' });
		} else {
			next();
		}
		next();
	}
});

app.mount("#app");
 