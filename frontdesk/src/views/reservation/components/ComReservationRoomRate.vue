<template>
  <div class="min-h-folio-cus mt-3">
    <div class="flex justify-between">               
      <div class="">
        <span class="p-input-icon-left">
          <i class="pi pi-search" />
          <InputText v-model="filters['global'].value" :placeholder="$t('Search')" />
        </span>
      </div>
      <div class="flex gap-2">
        <div>
          <Button   class="conten-btn mr-1 mb-3" serverity="waring" @click="onEditRoomRate()">
            <i class="pi pi-file-edit me-2" style="font-size: 1rem"></i>
            {{ $t('Edit Rate') }}
            
            <template v-if="rs.selectedRoomRates.length>0">
              ({{ rs.selectedRoomRates.length  }})
            </template>
          </Button>
        </div>
        <!-- hide funtion -->
        <div>
          <Button class="conten-btn mr-1 mb-3" serverity="waring" @click="onChangePax">
            <i class="pi pi-user me-2" style="font-size: 1rem"></i>
            {{ $t('Change Pax') }}
            
            <template v-if="rs.selectedRoomRates.length>0">
              ({{ rs.selectedRoomRates.length  }})
            </template>
          </Button>
        </div>
        <!-- hide funtion -->
        <div>
          <Button class="conten-btn mr-1 mb-3" serverity="waring" @click="onDiscount">
            <i class="pi pi-percentage me-2" style="font-size: 1rem"></i>
            {{ $t('Discount') }}
            
            <template v-if="rs.selectedRoomRates.length>0">
              ({{ rs.selectedRoomRates.length  }})
            </template>
          </Button>
        </div>
      </div>
    </div>
      <DataTable v-model:selection="rs.selectedRoomRates" :value="rs?.room_rates" tableStyle="min-width: 80rem" paginator :rows="20"
      v-model:filters="filters"
      :globalFilterFields="['room_number','date_search','room_type','room_type_alias','rate_type','reservation_stay','guest_name']"
      :rowsPerPageOptions="[20, 50, 100]">

      <div class="absolute bottom-6 left-4">
        <strong>{{ $t('Total Records') }}: <span class="ttl-column_re">{{rs?.room_rates.length }}</span></strong>
       </div>
      <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
      <Column  field="is_package"  bodyClass="text-center p-0" headerClass="text-center p-0">
        <template #body="slotProps">
          <span v-if="slotProps.data?.is_package" class="package_room_rate" >
          <ComIcon icon="iconPackage" height="20px" /> 
          </span>
        </template>
      </Column>
      <Column field="date" :header="$t('Date')" bodyClass="text-center" headerClass="text-center">
        <template #body="slotProps">
          <span>{{ gv.dateFormat(slotProps.data?.date) }}</span>
        </template>
      </Column>
      <Column field="reservation_stay" :header="$t('Stay') + '#' " bodyClass="text-center" headerClass="text-center">
        <template #body="slotProps">
          <button @click="showReservationStayDetail(slotProps.data?.reservation_stay)" class="link_line_action w-auto">
            {{slotProps.data?.reservation_stay}}
        </button>
        </template>
      </Column>

      <Column field="room_number" :header="$t('Room')">
        <template #body="slotProps">
          <div> 
            <span v-tippy ="slotProps.data.room_type">{{ slotProps.data.room_type_alias }}</span>/<span>{{ slotProps.data.room_number }}</span>                               
          </div>
        </template>
      </Column>
      <Column field="guest_name" :header="$t('Guest Name')">
        <template #body="slotProps">
          <Button  class="p-0 link_line_action1 overflow-hidden text-overflow-ellipsis whitespace-nowrap max-w-12rem"  @click="onViewCustomerDetail(slotProps.data.guest)" link>
            {{slotProps.data.guest_name}}
         </Button>
        </template>
      </Column>
      <Column  :header="$t('Pax(A/C)')" bodyClass="text-center" headerClass="text-center">
        <template #body="{ data }">
          <span @click="onEditRoomRate(data)" class="p-0 link_line_action1" >{{ data?.adult }} / {{ data?.child }}</span>
        </template>
      </Column>
      <Column field="rate_type" :header="$t('Rate Type')" bodyClass="text-center" headerClass="text-center">
        <template #body="{ data }">
          <span @click="onEditRoomRate(data)" class="p-0 link_line_action1">{{ data.rate_type }}</span>
        </template>
      </Column>
      <Column field="rate" :header="$t('Rate Before Tax')" bodyClass="text-right" headerClass="text-right">
          <template #body="{ data }">
            <CurrencyFormat @click="onEditRoomRate(data)" :value="data.total_rate + data.discount_amount - data.total_tax" class="p-0 link_line_action1"/>
          </template>
      </Column>

      <Column field="discount_amount" :header="$t('Discount Amount')" bodyStyle="text-align:right" headerStyle="text-align:right">
        <template #body="{ data }">
          <CurrencyFormat @click="onEditRoomRate(data)" :value="data.discount_amount" class="p-0 link_line_action1"/>
        </template>
      </Column>

      <Column field="total_tax" :header="$t('Total Tax')" bodyStyle="text-align:right" headerStyle="text-align:right">
        <template #body="{ data }">
          <CurrencyFormat @click="onEditRoomRate(data)" :value="data.total_tax" class="p-0 link_line_action1"/>
        </template>
      </Column>

      <Column field="total_amount" :header="$t('Total Amount')" bodyStyle="text-align:right" headerStyle="text-align:right">
        <template #body="{ data }">
            <CurrencyFormat :value="data.total_rate" />
        </template>
      </Column>
      <ColumnGroup type="footer">
        <Row>
          <Column :footer="$t('Total') + ':'" :colspan="7" footerStyle="text-align:right" />
          <Column footerStyle="text-align:center">
            <template #footer>
              {{ rs?.room_rates?.length }} {{$t('Room Night(s)')}}
            </template>
          </Column>
          <Column footerStyle="text-align:right">
            <template #footer>
              <CurrencyFormat :value="getTotal('input_rate')" />
            </template>
          </Column>
          <Column footerStyle="text-align:right">
            <template #footer>
              <CurrencyFormat :value="getTotal('discount_amount')" />
            </template>
          </Column>
          <Column footerStyle="text-align:right">
            <template #footer>
              <CurrencyFormat :value="getTotal('total_tax')" />
            </template>
          </Column>
          <Column footerStyle="text-align:right">
            <template #footer>
              <CurrencyFormat :value="getTotal('total_rate')" />
            </template>
          </Column>
        </Row>
      </ColumnGroup>
      <template #empty>
        <div class="p-4 text-center text-gray-400">
            <div><img :src="iconNoData" style="width: 80px; margin: 0 auto;"></div>
            <div class="mt-2 text-sm italic">{{$t('Empty Data')}}</div>
        </div>
      </template>
    </DataTable>
  
      </div>

    <!-- show change pax -->
    <OverlayPanel ref="showChangePax" style="max-width:70rem">
      <ComOverlayPanelContent  :loading="isLoading" @onSave="onSaveChangePax" @onCancel="onCloseOplaypanel">  
        <div class="flex gap-2">
          <div>
            <label>{{$t('Adults')}}</label>
                <InputNumber inputId="stacked-buttons" v-model="pax.adult" showButtons :min="1" :max="100"
                    class="child-adults-txt w-full" inputClass="border-noround-right"/>
          </div>
          <div>
            <label>{{$t('Children')}}</label>
            <InputNumber inputId="stacked-buttons" v-model="pax.child" showButtons :min="0" :max="100"
                class="child-adults-txt w-full" inputClass="border-noround-right"/>
          </div>
        </div>
      </ComOverlayPanelContent>
    </OverlayPanel>


    <!-- show discount -->
    <OverlayPanel ref="showDiscount" style="max-width:70rem">
      <div class="flex gap-2"> 
        <div>
          <label>{{ $t('Discount Type') }}</label>
          <ComSelect class="w-full min-w-full" optionLabel="label" optionValue="value"
              :clear="false" />
        </div>
        <div>
          <label>{{ $t('Discount') }}</label>
            <InputNumber class="w-full" :input-class="'w-full'" :minFractionDigits="2"
                :maxFractionDigits="10" />
        </div>
        <div>
          <label>{{ $t('Discount Amount') }}</label>
          <div class="w-full rounded-lg max-h-3rem h-edoor-35 leading-8 bg-gray-edoor-10 justify-end flex items-center px-3" style="height: 36.5px;">
              <CurrencyFormat />
          </div>
        </div>
      </div>
    </OverlayPanel>
</template>
<script setup>
import {inject, ref, onMounted,useDialog,postApi, useToast} from "@/plugin"
import { FilterMatchMode } from 'primevue/api';
import InputNumber from 'primevue/inputnumber';
import ComEditReservationRoomRate from '@/views/reservation/components/ComEditReservationRoomRate.vue';
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue";
import iconNoData from '@/assets/svg/icon-no-notic-r-comment.svg'
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const rs = inject('$reservation')
const dialog = useDialog();
const pax = ref({ adult: 0, child: 0 });
const toast = useToast()
const isLoading = ref()
const gv = inject('$gv')
const filters = ref(
    {
        global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    
    }
);

const showChangePax = ref()
const showDiscount = ref()

const getTotal = ref((column_name) => {
  if (rs.room_rates.length == 0) {
    return 0
  } else {
    return rs.room_rates.reduce((n, d) => n + d[column_name], 0)
  }
});
function onEditRoomRate(room_rate = null){
  if(!gv.cashier_shift?.name){
      gv.toast('error', 'Please Open Cashier Shift.')
      return
  }
  if(room_rate){
    const dialogRef = dialog.open(ComEditReservationRoomRate, {
      data: {
        selected_room_rate:room_rate,
        reservation:rs.reservation,
        },
      props: {
        header: 'Edit Room Rate',
        style: {
          width: '55vw',
        },
        position: "top",
        modal: true,
        closeOnEscape: false,
        breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
      },
      onClose: (options) => {
        const result = options.data;
        if(result){
            // rs.getRoomRate(rs.reservation.name)
            rs.getReservationDetail(rs.reservation.name);
           
        }
    }

    })
  }else if(rs.selectedRoomRates.length>0){

    const dialogRef = dialog.open(ComEditReservationRoomRate, {
      data: {
        selected_room_rates:rs.selectedRoomRates,
        reservation:rs.reservation,
        
        },
      props: {
        header: $t('Edit Room Rate '),
        style: {
          width: '55vw',
        },
        position: "top",
        modal: true,
        closeOnEscape: false,
        breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
      },
      onClose: (options) => {
        const result = options.data;
        
        if(result){
          // rs.getRoomRate(rs.reservation.name)
          rs.selectedRoomRates = []
          rs.getReservationDetail(rs.reservation.name);
           
        }
    }

    })
  } else if (rs.selectedRoomRates.length == 0){
    toast.add({ severity: 'warn', summary: 'Edit Room Rate', detail: "Please select room to edit.", life: 3000 })
    return 
  }
}
function showReservationStayDetail(selected) {
    let stayName = selected
    if(selected.data && selected.data?.reservation_stay){
        stayName = selected.data?.reservation_stay
    }
    const dialogRef = dialog.open(ReservationStayDetail, {
        data: {
            name: stayName
        },
        props: {
            header: $t('Reservation Stay Detail'),
            contentClass: 'ex-pedd',
            style: {
                width: '80vw',
            },
            maximizable: true,
            modal: true,
            closeOnEscape: false,
            position:"top", 
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        }, 
    });
}
function onViewCustomerDetail(name) {
    window.postMessage('view_guest_detail|' + name, '*')
}
 
onMounted(() => {
  if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
  rs.getRoomRate(rs.reservation.name, false);
 
});


function onChangePax (event) { 
  if( rs.reservation?.reservation_status != 'Cancelled' && rs.reservation?.reservation_status != 'Void'){
  if(!gv.cashier_shift?.name){
      gv.toast('error', 'Please Open Cashier Shift.')
      return
  }
  if (rs.selectedRoomRates.length>0) {
    const selectedRate = rs.selectedRoomRates[0];
    pax.value.adult = selectedRate.adult ;
    pax.value.child = selectedRate.child;
    showChangePax.value.toggle(event);
  } else if (rs.selectedRoomRates.length == 0){
    toast.add({ severity: 'warn', summary: 'Change Pax', detail: "Please select room to edit.", life: 3000 })
    return 
  }
}else {
    toast.add({ severity: 'warn', summary: 'Change Pax', detail: "This Reservation Stay has been Cancelled or Void.", life: 3000 })
    return 
  }
}

const onSaveChangePax = () => {
  let reservation_stay_names = []
  reservation_stay_names = Array.from(new Set(rs.selectedRoomRates.map(d => d["reservation_stay"])))
  isLoading.value = true
    postApi('reservation.change_pax', {
      data:{
        stay_name:reservation_stay_names,
        adult:pax.value.adult,
        child:pax.value.child
      },
      room_rates:rs.selectedRoomRates
    }, "Edit room rate successfully")
        .then((doc) => {
          isLoading.value = false
          rs.getRoomRate(rs.reservation.name);
          rs.selectedRoomRates = []
          onCloseOplaypanel()
            
        })
        .catch((error) => {
          isLoading.value = false;

        });   
}

function onCloseOplaypanel(){
  showChangePax.value.hide();
}

function onDiscount (event) { 
  if(!gv.cashier_shift?.name){
      gv.toast('error', 'Please Open Cashier Shift.')
      return
  }
  if (rs.selectedRoomRates.length>0) {
    showDiscount.value.toggle(event); 
  } else if (rs.selectedRoomRates.length == 0){
    toast.add({ severity: 'warn', summary: 'Edit Room Rate', detail: "Please select room to edit.", life: 3000 })
    return 
  }
}

</script>