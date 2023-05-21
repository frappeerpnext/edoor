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
import resourceManager from "../../../doppio/libs/resourceManager";
import call from "../../../doppio/libs/controllers/call";

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
import Gv from './providers/gv';

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
import AutoComplete from 'primevue/autocomplete';
// custom components //
import ComAvatar from './components/form/ComAvatar.vue'
import ComAutoComplete from './components/form/ComAutoComplete.vue'
import ComPanel from './components/layout/components/ComPanel.vue'

import socket from './utils/socketio';




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

// use custom components //
app.component('ComAvatar', ComAvatar)
app.component('ComPanel',ComPanel)
app.component('ComAutoComplete',ComAutoComplete)
 


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
app.provide("$socket",socket)
app.provide("$frappe", frappe);

app.directive('badge', BadgeDirective);
app.directive('tooltip', Tooltip);


const gv = reactive(new Gv());
app.provide("$moment", moment)
app.provide("$gv", gv)
// get global data
const apiCall = frappe.call()


// Configure route gaurds
router.beforeEach(async (to, from, next) => {
	if (to.matched.some((record) => !record.meta.isLoginPage)) {
		// this route requires auth, check if logged in
		// if not, redirect to login page.
		if (!auth.isLoggedIn) {
			const setting = JSON.parse(localStorage.getItem('edoor_setting'))
			const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
			window.location.replace(serverUrl)
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
apiCall.get('edoor.api.frontdesk.get_logged_user').then((r)=>{
	
	localStorage.setItem('edoor_user', JSON.stringify(r.message))
	if(r.message.property){
		if (r.message.property.length==1){
			localStorage.setItem('edoor_property', JSON.stringify(r.message.property[0]))
		}
	}
	app.mount("#app");

}).catch((error)=>{
	 
	const errorApp = createApp(Error);
	errorApp.mount("#app");
})


 