<template>
    <ComPlaceholder text="There is no Folio transactions" :loading="loading" :isNotEmpty="folioTransactions.length > 0">
 
        <DataTable v-model:selection="selectedfolioTransactions"
            @row-dblclick="onViewFolioDetail"
            paginator  
            :stateKey="'folo_transaction_table_state_' + selectedFolio.name"
            :rows="10" 
            :rowsPerPageOptions="[5, 10, 20, 50]"
            
            :value="folioTransactions?.filter(r => (r.parent_reference || '') == '')" tableStyle="min-width: 120rem"
           
            :rowClass="onRowClass">
            <Column selectionMode="multiple" headerStyle="width: 3rem"  v-if="showCheckbox"/>
            <Column field="name" :header="$t('Folio Transaction')" headerClass="text-center" bodyClass="text-center">
                <template #body="slotProps">
                    <button @click="onViewFolioDetail(slotProps)" v-if="slotProps.data?.name" :class="'link_line_action1 ' + (slotProps.data?.is_auto_post==1?'auto_post':'')" >
                        {{slotProps.data?.name}}</button>
                </template>
            </Column>
            <Column  field="is_package"  bodyClass="text-center p-0" headerClass="text-center p-0">
        <template #body="slotProps">
          <span @click="onViewFolioDetail(slotProps)" v-if="slotProps.data?.is_package" class="package_room_rate" >
          <ComIcon icon="iconPackage" height="20px" /> 
          </span>
        </template>
      </Column>
            <Column field="posting_date" :header="$t('Date')" headerClass="text-center" bodyClass="text-center">
                <template #body="slotProps">
                    <span>{{ moment(slotProps.data?.posting_date).format("DD-MM-YYYY") }}</span>
                </template>
            </Column>
            <Column field="room_number" :header="$t('Room') + '#' " headerClass="text-center white-space-nowrap" bodyClass="text-center"></Column>
            <Column field="account_name" header="Account" style="min-width: 160px;">
                <template #body="slotProps">
                    <span v-if="setting?.show_account_code_in_folio_transaction == 1">{{ slotProps.data.account_code }} -
                    </span>
                    <span>{{ slotProps.data.report_description }} </span> <span v-if="slotProps.data.sale">({{slotProps.data.sale}}/{{slotProps.data.tbl_number}})</span>
                    
                    
                </template>
            </Column>
            <Column :header="$t('Qty')" class="text-center">
                <template #body="slotProps">
                    <span v-if="slotProps?.data.allow_enter_quantity==1">{{slotProps.data.quantity}}</span>

                </template>
            </Column>
            <Column frozen  field="price" :header="$t('Amount/Rate')" class="text-right" style="min-width: 70px;"  >
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.price" :class="slotProps.data.price<0?'white-space-nowrap text-green-700':'white-space-nowrap'" />
                </template>
            </Column>
            <Column field="discount_amount" :header="$t('Discount')" class="text-right">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.discount_amount" class="white-space-nowrap" />
                </template>
            </Column>
            <Column field="total_tax" :header="$t('Tax')" class="text-right" v-if="getTotal('total_tax')!=0">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.total_tax" class="white-space-nowrap" />
                </template>
            </Column>
            <Column field="bank_fee_amount" :header="$t('Bank Fee')" class="text-right" v-if="getTotal('bank_fee_amount')!=0">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.bank_fee_amount" class="white-space-nowrap" />
                </template>
            </Column>

            <Column field="total_amount" :header="$t('Total Amount')" class="text-right">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.total_amount" :class="slotProps.data.total_amount< 0?'white-space-nowrap text-green-700':'white-space-nowrap'" />
                </template>
            </Column>

            
            <Column :header="$t('Owner')">
                <template #body="slotProps">
                    <div v-if="slotProps?.data && slotProps?.data?.owner">
                        <template v-for="(item) in slotProps.data?.owner?.split('@')[0]" :key="index">
                            <span>{{ item }}</span>
                        </template>
                    </div>  
                </template>
                    </Column>
            <Column field="creation" :header="$t('Created')">
                <template #body="slotProps">
                    <span v-if="slotProps.data.creation">
                        <ComTimeago :date="slotProps.data.creation" />
                    </span>
                </template>
            </Column>
            <Column field="note" :header="$t('Note')" style="min-width: 160px;">
                <template #body="slotProps">
                    <div v-if="slotProps.data.note"  v-tippy="slotProps.data.note">
                        {{ slotProps.data.note.slice(0, 20) + (slotProps.data.note.length > 20 ? '...' : '') }}
                    </div>
                </template>
            </Column>
            <Column>
                <template #body="slotProps">
                    <div  v-if="slotProps.data.name">
                        <ComReservationStayFolioTransactionAction :data="slotProps.data"/> 
                    </div>
                </template>
            </Column>
            <ColumnGroup type="footer">
                <Row>
                    <Column :footer="$t('Total') + ':'" :colspan="showCheckbox?5:4" footerStyle="text-align:right" />
                    <Column footerStyle="text-align:center">
                        <template #footer>

                            {{ getTotal('quantity') }}
                        </template>
                    </Column>
                    <Column footerStyle="text-align:right">
                        <template #footer>
                            <CurrencyFormat :value="getTotal('amount')" />

                        </template>
                    </Column>

                    <Column footerStyle="text-align:right">
                        <template #footer>
                            <CurrencyFormat :value="getTotal('discount_amount')" />

                        </template>
                    </Column>

                    <Column footerStyle="text-align:right" v-if="getTotal('total_tax')!=0">
                        <template #footer>
                            <CurrencyFormat :value="getTotal('total_tax')" />

                        </template>
                    </Column>

                    <Column footerStyle="text-align:right" v-if="getTotal('bank_fee_amount')!=0">
                        <template #footer>
                            <CurrencyFormat :value="getTotal('bank_fee_amount')" />

                        </template>
                    </Column>
                    <Column footerStyle="text-align:right">
                        <template #footer>
                            <CurrencyFormat :value="(selectedFolio.total_debit - selectedFolio.total_credit)" />

                        </template>
                    </Column>

                    <Column />
                    <Column />
                    <Column />
                    <Column />
                </Row>
            </ColumnGroup>

        </DataTable>
       
    <div v-if="can_view_rate" class="w-full flex justify-content-end my-2" id="detl_foloi">
        <div class="w-30rem">
            <div v-for="(item, index) in folio_summary" :key="index" class="flex mt-2 gap-2">
                <ComBoxStayInformation :title="item?.account_category || 'Undefine'" :value="item?.amount || 0" isCurrency
                    valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="col font-semibold">
                </ComBoxStayInformation>
            </div>
            <div class="flex mt-2 gap-2">
                <ComBoxStayInformation isCurrency title="Total Debit" :value="totalDebit"
                    valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="col font-semibold">
                </ComBoxStayInformation>
            </div>
            <div class="flex mt-2 gap-2">
                <ComBoxStayInformation isCurrency title="Total Credit" :value="totalCredit"
                    valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="col font-semibold">
                </ComBoxStayInformation>

            </div>
            <div class="flex mt-2 gap-2">
                <ComBoxStayInformation isCurrency title="Balance" :value="(totalDebit - totalCredit)"
                    valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="col font-semibold">
                </ComBoxStayInformation>
            </div>
        </div>
    </div>
    </ComPlaceholder>

</template>
<script setup>

import { inject,ref,useDialog,computed,onUnmounted,onMounted,getApi,watch,getDocList} from '@/plugin';
 
import ComFolioTransactionDetail from '@/views/reservation/components/reservation_stay_folio/ComFolioTransactionDetail.vue';
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
import ComReservationStayFolioTransactionAction from '@/views/reservation/components/reservation_stay_folio/ComReservationStayFolioTransactionAction.vue';

import Enumerable from 'linq'
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const props = defineProps({
    folio:Object, 
    doctype:{
        type:String,
        default:"Reservation Folio"
    },
    showCheckbox:{
        type:Boolean,
        default:true
    }

})
 
const selectedFolio = ref(props.folio)

const can_view_rate=window.can_view_rate;
const folioTransactions = ref([])
const selectedfolioTransactions = ref([])
const folio_summary = ref()
const dialog = useDialog();
const show = ref()
 
const setting = window.setting

watch(() => props.folio, (newValue, oldValue) => {
    selectedFolio.value = newValue
    
    LoadFolioTransaction()
    selectedfolioTransactions.value = []
    clearState(oldValue.name)
})



//load data
function LoadFolioTransaction(){

				getDocList("Folio Transaction", {
					fields: [
						"name",
                        "transaction_number",
						'posting_date',
                        "reservation",
						"room_number",
						"parent_reference",
						"type",
						"account_code",
						"account_name",
						"quantity",
						"input_amount",
						"price",
						"amount",
						"discount_amount",
						"total_tax",
						"total_amount",
						"bank_fee_amount",
						"note",
						"creation",
						"owner",
						"modified",
						"modified_by",
						"show_print_preview",
						"print_format",
						"is_auto_post",
						"allow_enter_quantity",
                        "target_transaction_number",
                        "city_ledger_name",
                        "source_transaction_number",
                        "report_description",
                        "sale",
                        "tbl_number"
					],
					filters: [["transaction_number", "=", selectedFolio.value.name],["transaction_type", "=", props.doctype]],
					limit: 1000,
                    orderBy: {
                    field: 'modified',
                    order: 'desc',
                },
				}).then((result) => {
                   
					const folio_transaction = Enumerable.from(result).orderBy("$.posting_date").thenBy("name").toArray()
					folio_transaction.forEach(r => {
						r.quantity = r.allow_enter_quantity == 1? r.quantity:0;
						r.total_amount = r.type == "Credit" ? (r.total_amount - r.bank_fee_amount) * -1 : r.total_amount
						r.amount = r.type == "Credit" ? r.amount * -1 : r.amount
						r.price = r.type == "Credit" ? (r.price + r.bank_fee_amount) * -1 : r.price
					});
					folioTransactions.value  = folio_transaction
                  
                    
				})


			

        setTimeout(function(){
            getFolioSummary()
        },2000)   
}


 
const getTotal = ref((column_name) => {
    if (folioTransactions.value?.filter(r => (r.parent_reference || '') == '').length == 0) {
        return 0
    } else {
        return folioTransactions.value?.filter(r => (r.parent_reference || '') == '').reduce((n, d) => n + d[column_name], 0)
    }
});

function onRowClass(r){
    var classRow = ''
    if(r.is_auto_post){
        classRow = classRow + ("auto-post ")
    }
    return classRow
}


function getFolioSummary() {
		getApi("reservation.get_folio_summary_by_transaction_type", {
			transaction_type: "Reservation Folio",
			transaction_number: selectedFolio.value.name
		}).then((result) => {
			 folio_summary.value = result.message
		})
	}


const toggle = (event) => {
    show.value.toggle(event)
}
 


 

const moment = inject("$moment")
 
const rowStyleClass = (r) => {
    var classRow = ''
 
    if(!r.name){
        classRow = classRow + "ui-helper-hidden "
    }else{
        if(r.is_auto_post){
            classRow = classRow + ("auto-post ")
        }
        if (r.debit > 0){
            classRow = classRow + ("row-debit ")
        }
        else if(r.credit > 0){
            classRow = classRow + ("row-credit ")
        }
    }
    
    return classRow
};

 

const onViewFolioDetail = (doc) => { 
    if (doc.data.name){
        const dialogRef = dialog.open(ComFolioTransactionDetail, {
            data:{
                folio_transaction_number:doc.data.name
            },
            props: {
                header: 'Folio Transaction Detail - ' + doc.data.name ,
                style: {
                    width: '90vw',
                },
                modal: true,
                position:'top',
                closeOnEscape: false,
                breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
            },
            onClose: (options) => {
                
            }
        });
    }
     
}

const totalCredit = computed(() => {
		

		if (folioTransactions.value) {
	
				return folioTransactions.value.reduce((n, d) => n + (d.type == "Credit" ? Math.abs((d.amount || 0)) : 0), 0)
		
		}
		return 0

	})

const totalDebit = computed(() => {
		if (folioTransactions.value) {
	 
				return Math.abs(folioTransactions.value.reduce((n, d) => n + (d.type == "Debit" ? (d.amount || 0) : 0), 0))
			 


		}
		return 0

	})

 
const windowActionHandler = async function (e) {
    if (e.isTrusted) {
        if(e.data.action=="load_folio_transaction") {
            LoadFolioTransaction()
 
        }
       
    }
}
onMounted(() => {
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    window.addEventListener('message', windowActionHandler, false);

    LoadFolioTransaction()

})
function clearState(name){
     
        let state = sessionStorage.getItem("folo_transaction_table_state_" + name )
        if(state){
            state = JSON.parse(state)
            state.selection=[]
            sessionStorage.setItem("folo_transaction_table_state_" + name,JSON.stringify(state) )
        }
    }

onUnmounted(()=>{
    window.removeEventListener('message', windowActionHandler, false);
    clearState(selectedFolio.name)
})
</script>
<style>
    .ui-helper-hidden .p-selection-column .p-checkbox{
        display: none !important;
    }
    
    .link_line_action1.auto_post{
        border: 1px dashed #ff3720 !important;
        color: #ff3720 !important;
        }
</style>
 