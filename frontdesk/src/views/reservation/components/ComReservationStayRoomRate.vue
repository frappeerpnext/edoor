<template>
  <div class="min-h-folio-cus mt-3">

    <Button   class="conten-btn mr-1 mb-3" serverity="waring" @click="onEditRoomRate()">
      <i class="pi pi-file-edit me-2" style="font-size: 1rem"></i>
      Edit Rate 
      <template v-if="selectedRoomRates.length>0">
        ({{selectedRoomRates.length  }})
      </template>
      <template v-if="selectedRoomRates.length0">
        ({{selectedRoomRates.length  }})
      </template>
    </Button>
 
    <DataTable v-model:selection="selectedRoomRates" :value="data" tableStyle="min-width: 80rem" paginator :rows="20"
      :rowsPerPageOptions="[20, 50, 100]">
      <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
      
      <Column field="date" header="Date">
        <template #body="slotProps">
          <span>{{ gv.dateFormat(slotProps.data?.date) }}</span>
        </template>
      </Column>

      <Column field="room_number" header="Room">
        <template #body="slotProps">
          {{ slotProps.data.room_number }} - {{ slotProps.data.room_type }}
        </template>
      </Column>
      <Column field="rate_type" header="Rate Type">
        <template #body="{ data }">
          <span @click="onEditRoomRate(data)" class="p-0 link_line_action1">{{ data.rate_type }}</span>
        </template>
      </Column>
      <Column field="rate" header="Rate" bodyStyle="text-align:right" headerStyle="text-align:right">
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
              {{ data.length }} Room Night(s)
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
import { inject, ref, getDocList, useDialog } from '@/plugin';
import ComEditReservationRoomRate from './ComEditReservationRoomRate.vue';

const rs = inject('$reservation_stay')
const data = ref([])
const selectedRoomRates = ref([])
const moment = inject("$moment")
const gv = inject('$gv')
const dialog = useDialog();
const visible = ref(false)


const getTotal = ref((column_name) => {
  if (data.value.length == 0) {
    return 0
  } else {
    return data.value.reduce((n, d) => n + d[column_name], 0)
  }
});

const doc = ref({})

getDocList('Reservation Room Rate', {
  filters: [['reservation_stay', '=', rs.reservationStay.name]],
  fields: ["*"],
  orderBy: {
    field: 'date',
    order: 'asc',
  },
  limit:1000
})
  .then((doc) => {
    data.value = doc
  })
  .catch((error) => console.error(error));

 

function onEditRoomRate(room_rate = null) {
  if(room_rate){
    const dialogRef = dialog.open(ComEditReservationRoomRate, {
      data: {
        selected_room_rate:room_rate,
        reservation_stay:rs.reservationStay,
        },
      props: {
        header: 'Edit Room Rate ',
        style: {
          width: '50vw',
        },
        position: "top",
        modal: true
      },
      onClose: (options) => {
        const result = options.data;
        
        if(result){
            data.value = result
        }
    }

    })
  }else if(selectedRoomRates.value.length>0){
    const dialogRef = dialog.open(ComEditReservationRoomRate, {
      data: {
        selected_room_rates:selectedRoomRates.value,
        reservation_stay:rs.reservationStay
        },
      props: {
        header: 'Edit Room Rate ',
        style: {
          width: '50vw',
        },
        position: "top",
        modal: true
      },
      onClose: (options) => {
        const result = options.data;
        
        if(result){
            data.value = result
        }
    }

    })
  } else if (selectedRoomRates.value.length == 0){
    alert('Please Select Field to Edit First')
  }

}

</script>
<style>
.p-datatable .p-column-header-content {
  display: contents !important;
}
</style>