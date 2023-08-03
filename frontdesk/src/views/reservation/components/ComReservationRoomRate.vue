<template>
  <div class="min-h-folio-cus mt-3">
    <div class="grid">               
      <div class="col-2">
        <span class="p-input-icon-left">
          <i class="pi pi-search" />
          <InputText v-model="filters['global'].value" placeholder="Search" />
        </span>
      </div>
      <div class="col-2">
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
     
      <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
      
      <Column field="date" header="Date">
        <template #body="slotProps">
          <span>{{ gv.dateFormat(slotProps.data?.date) }}</span>
        </template>
      </Column>
      <Column field="reservation_stay" header="Res Stay#">
        <template #body="slotProps">
          <span>{{ slotProps.data?.reservation_stay }}</span>
        </template>
      </Column>

      <Column field="room_number" header="Room">
        <template #body="slotProps">
          <div class="rounded-xl px-2 me-1 bg-gray-edoor inline"> 
            <span v-tooltip.top="slotProps.data.room_type">{{ slotProps.data.room_type_alias }}</span>/<span>{{ slotProps.data.room_number }}</span>                               
          </div>
          <!-- {{ slotProps.data.room_number }} - {{ slotProps.data.room_type }} -->
        </template>
      </Column>
      <Column field="guest_name" header="Guest Name">
        <template #body="slotProps">
          <span>{{ slotProps.data?.guest_name }}</span>
        </template>
      </Column>
      <Column field="rate_type" header="Rate Type">
        <template #body="{ data }">
          <span @click="onEditRoomRate(data)" class="p-0 link_line_action1">{{ data.rate_type }}</span>
        </template>
      </Column>
      <Column field="rate" header="Rate" bodyStyle="text-align:center" headerStyle="text-align:center">
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
          <Column footer="Total:" :colspan="3" footerStyle="text-align:right" />
          <Column >
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
    </DataTable>
  
      </div>
</template>
<script setup>
import {inject, ref, onMounted,useDialog} from "@/plugin"
import { FilterMatchMode, FilterOperator } from 'primevue/api';
import ComEditReservationRoomRate from '@/views/reservation/components/ComEditReservationRoomRate.vue';
const rs = inject('$reservation')
const dialog = useDialog();
 
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
            rs.room_rates = result
            rs.getReservationDetail(rs.reservationStay.name);
           
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
          rs.room_rates = result
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
 
onMounted(() => {
  
  rs.getRoomRate(rs.reservation.name);
 
});

</script>