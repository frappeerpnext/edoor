<template>
  <div class="min-h-folio-cus mt-3">
    <div class="flex justify-between">               
      <div class="">
        <span class="p-input-icon-left">
          <i class="pi pi-search" />
          <InputText v-model="filters['global'].value" placeholder="Search" />
        </span>
      </div>
      <div class="">
        <Button   class="conten-btn mr-1 mb-3" serverity="waring" @click="onEditRoomRate()">
          <i class="pi pi-file-edit me-2" style="font-size: 1rem"></i>
          Edit Rate
          <template v-if="rs.selectedRoomRates.length>0">
            ({{ rs.selectedRoomRates.length  }})
          </template>
        </Button>
      </div>
    </div>
      <DataTable v-model:selection="rs.selectedRoomRates" :value="rs?.room_rates" tableStyle="min-width: 80rem" paginator :rows="20"
      v-model:filters="filters"
      :globalFilterFields="['room_number','date_search','room_type','room_type_alias','rate_type','reservation_stay','guest_name']"
      :rowsPerPageOptions="[20, 50, 100]">

      <div class="absolute bottom-6 left-4">
        <strong>Total Records: <span class="ttl-column_re">{{rs?.room_rates.length }}</span></strong>
       </div>
      <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
      
      <Column field="date" header="Date" bodyClass="text-center" headerClass="text-center">
        <template #body="slotProps">
          <span>{{ gv.dateFormat(slotProps.data?.date) }}</span>
        </template>
      </Column>
      <Column field="reservation_stay" header="Stay #" bodyClass="text-center" headerClass="text-center">
        <template #body="slotProps">
          <button @click="showReservationStayDetail(slotProps.data?.reservation_stay)" class="link_line_action w-auto">
            {{slotProps.data?.reservation_stay}}
        </button>
        </template>
      </Column>

      <Column field="room_number" header="Room">
        <template #body="slotProps">
          <div> 
            <span v-tippy ="slotProps.data.room_type">{{ slotProps.data.room_type_alias }}</span>/<span>{{ slotProps.data.room_number }}</span>                               
          </div>
          <!-- {{ slotProps.data.room_number }} - {{ slotProps.data.room_type }} -->
        </template>
      </Column>
      <Column field="guest_name" header="Guest Name">
        <template #body="slotProps">
          <Button  class="p-0 link_line_action1 overflow-hidden text-overflow-ellipsis whitespace-nowrap max-w-12rem"  @click="onViewCustomerDetail(slotProps.data.guest)" link>
            {{slotProps.data.guest_name}}
         </Button>
        </template>
      </Column>
      <Column field="rate_type" header="Rate Type" bodyClass="text-center" headerClass="text-center">
        <template #body="{ data }">
          <span @click="onEditRoomRate(data)" class="p-0 link_line_action1">{{ data.rate_type }}</span>
        </template>
      </Column>
      <Column field="rate" header="Rate" bodyClass="text-right" headerClass="text-right">
          <template #body="{ data }">
            <CurrencyFormat @click="onEditRoomRate(data)" :value="data.rate" class="p-0 link_line_action1"/>
          </template>
      </Column>

      <Column field="discount_amount" header="Disount Amount" bodyStyle="text-align:right" headerStyle="text-align:right">
        <template #body="{ data }">
          <CurrencyFormat @click="onEditRoomRate(data)" :value="data.discount_amount" class="p-0 link_line_action1"/>
        </template>
      </Column>

      <Column field="total_tax" header="Total Tax" bodyStyle="text-align:right" headerStyle="text-align:right">
        <template #body="{ data }">
          <CurrencyFormat @click="onEditRoomRate(data)" :value="data.total_tax" class="p-0 link_line_action1"/>
        </template>
      </Column>

      <Column field="total_amount" header="Total Amount" bodyStyle="text-align:right" headerStyle="text-align:right">
        <template #body="{ data }">
            <CurrencyFormat :value="data.total_rate" />
        </template>
      </Column>
      <ColumnGroup type="footer">
        <Row>
          <Column footer="Total:" :colspan="5" footerStyle="text-align:right" />
          <Column footerStyle="text-align:center">
            <template #footer>
              {{ rs?.room_rates?.length }} Room Night(s)
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
      <template #empty>
        <div class="p-4 text-center text-gray-400">
            <div><img :src="iconNoData" style="width: 80px; margin: 0 auto;"></div>
            <div class="mt-2 text-sm italic">Empty Data</div>
        </div>
      </template>
    </DataTable>
  
      </div>
</template>
<script setup>
import {inject, ref, onMounted,useDialog, useToast} from "@/plugin"
import { FilterMatchMode } from 'primevue/api';
import ComEditReservationRoomRate from '@/views/reservation/components/ComEditReservationRoomRate.vue';
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue";
import iconNoData from '@/assets/svg/icon-no-notic-r-comment.svg'
// import GuestDetail from "@/views/guest/GuestDetail.vue";
const rs = inject('$reservation')
const dialog = useDialog();
const toast = useToast()
const gv = inject('$gv')
const filters = ref(
    {
        global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    
    }
);


const getTotal = ref((column_name) => {
  if (rs.room_rates.length == 0) {
    return 0
  } else {
    return rs.room_rates.reduce((n, d) => n + d[column_name], 0)
  }
});
function onEditRoomRate(room_rate = null){
  if(room_rate){
    const dialogRef = dialog.open(ComEditReservationRoomRate, {
      data: {
        selected_room_rate:room_rate,
        reservation:rs.reservation,
        },
      props: {
        header: 'Edit Room Rate ',
        style: {
          width: '50vw',
        },
        position: "top",
        modal: true,
        closeOnEscape: false
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
        header: 'Edit Room Rate ',
        style: {
          width: '50vw',
        },
        position: "top",
        modal: true,
        closeOnEscape: false
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
            header: 'Reservation Stay Detail',
            contentClass: 'ex-pedd',
            style: {
                width: '80vw',
            },
            maximizable: true,
            modal: true,
            closeOnEscape: false,
            position:"top"
        }, 
    });
}
function onViewCustomerDetail(name) {
    window.postMessage('view_guest_detail|' + name, '*')
}
 
onMounted(() => {
  
  rs.getRoomRate(rs.reservation.name, false);
 
});

</script>