<template>
  <div class="min-h-folio-cus mt-3">

    <Button class="conten-btn mr-1 mb-3" serverity="waring" @click="onEditRoomRate()">
      <i class="pi pi-file-edit me-2" style="font-size: 1rem"></i>
      {{$t('Edit Rate') }}
     
      <template v-if="rs.selectedRoomRates.length>0">
        ({{ rs.selectedRoomRates.length  }})
      </template>
    </Button>
    <DataTable v-model:selection="rs.selectedRoomRates" :value="rs?.room_rates" tableStyle="min-width: 80rem" paginator :rows="20"
      :rowsPerPageOptions="[20, 50, 100]">
      <div class="absolute bottom-6 left-10">
        <strong> {{$t('Total Records') }}: <span class="ttl-column_re">{{ rs?.room_rates?.length }}</span></strong>
      </div>
      <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
      <Column  field="is_package" :header="$t('Package')" bodyClass="text-center" headerClass="text-center">
        <template #body="slotProps">
          <span><i v-if="slotProps.data?.is_package"  class="pi pi-folder-open package_room_rate"></i></span>
        </template>
      </Column>
      
      <Column field="date" :header="$t('Date')" bodyClass="text-center" headerClass="text-center">
        <template #body="slotProps">
          <span>{{ gv.dateFormat(slotProps.data?.date) }}</span>
        </template>
      </Column>

      <Column field="room_number" :header="$t('Room')">
        <template #body="slotProps">
          <div> 
            <span  v-tippy="slotProps.data.room_type">
              {{ slotProps.data.room_type_alias }}</span>/
              <span v-if="slotProps.data.room_number">{{ slotProps.data.room_number }}</span>     
              <span v-else>
                {{ $t('Room No (Unassign)') }}
                
              </span>                          
          </div>
        </template>
      </Column>
      <Column field="rate_type" :header="$t('Rate Type')">
        <template #body="{ data }">
          <span @click="onEditRoomRate(data)" class="p-0 link_line_action1">{{ data.rate_type }}</span>
        </template>
      </Column>
      <Column field="rate" :header="$t('Rate')" bodyStyle="text-align:right" headerStyle="text-align:right">
          <template #body="{ data }">
            <button @click="onEditRoomRate(data)" class="link_line_action1 w-12rem">
              <div class="flex justify-between w-full items-center">
              <span class="text-sm" v-if="data.is_manual_rate"> ({{ $t('Manual') }}) </span>
                                  <span class="text-sm" v-else>({{$t('Plan')}})</span>
              <CurrencyFormat  :value="data.rate" class="p-0 "/>
            </div>
            </button>
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
          <Column :footer="$t('Total') + ':'" :colspan="4" footerStyle="text-align:right" />
          <Column >
            <template #footer>
              {{ rs?.room_rates?.length }} 
              {{ $t('Room Night(s)') }}
              
            </template>
          </Column>
          <Column footerStyle="text-align:right">
            <template #footer>
              <CurrencyFormat :value="getTotal('rate')" />
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
    </DataTable>
  </div>
</template>
<script setup>
import { inject, ref, useDialog,onMounted,useToast } from '@/plugin';
import ComEditReservationRoomRate from './ComEditReservationRoomRate.vue';
import ComReservationStayAssignRoom from '@/views/reservation/components/ComReservationStayAssignRoom.vue';
import Message from 'primevue/message';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const isMobile = ref(window.isMobile)

const rs = inject('$reservation_stay')
const data = ref([])
const setting = JSON.parse(localStorage.getItem('edoor_setting'))
 
const moment = inject("$moment")
const gv = inject('$gv')
const dialog = useDialog();
const toast = useToast()

const getTotal = ref((column_name) => {
  if (rs.room_rates.length == 0) {
    return 0
  } else {
    return rs.room_rates.reduce((n, d) => n + d[column_name], 0)
  }
});


function onEditRoomRate(room_rate = null) {
  if(!gv.cashier_shift?.name){
        gv.toast('error', 'Please Open Cashier Shift.')
        return
    }

  if( rs.reservationStay?.reservation_status != 'Cancelled' && rs.reservationStay?.reservation_status != 'Void'){
    if(room_rate){
    const dialogRef = dialog.open(ComEditReservationRoomRate, {
      data: {
        selected_room_rate:room_rate,
        reservation_stay:rs.reservationStay,
        },
      props: {
        header: $t('Edit Room Rate '),
        style: {
          width: '50vw',
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
            rs.room_rates = result
            rs.getReservationDetail(rs.reservationStay.name);
           
        }
    }

    })
  }else if(rs.selectedRoomRates.length > 0 ){

    const dialogRef = dialog.open(ComEditReservationRoomRate, {
      data: {
        selected_room_rates:rs.selectedRoomRates,
        reservation_stay:rs.reservationStay,
        
        },
      props: {
        header: $t('Edit Room Rate '),
        style: {
          width: '50vw',
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
          rs.room_rates = result
          rs.selectedRoomRates = []
          rs.getReservationDetail(rs.reservationStay.name);
           
        }
    }

    })
  } else if (rs.selectedRoomRates.length == 0){
    toast.add({ severity: 'warn', summary: 'Edit Room Rate', detail: "Please select room to edit.", life: 3000 })
    return 
  }
  }else {
          toast.add({ severity: 'warn', summary: 'Edit Room Rate', detail: "This Reservation Stay has been Cancelled or Void.", life: 3000 })
          return 
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
  rs.getRoomRate(rs.reservationStay.name);
 
});

</script>
<style>
.p-datatable .p-column-header-content {
  display: contents !important;
}
</style>