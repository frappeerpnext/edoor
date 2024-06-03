<template>
    <div class="min-h-folio-cus mt-3">

        <!-- hide funtion -->
        <!-- <Button  class="conten-btn mr-1 mb-3" serverity="waring" @click="addnew()">
      <i class="pi pi-plus me-2" style="font-size: 1rem"></i>
      {{$t('Add New Package') }}
    </Button> -->
    <ComPlaceholder text="No Data" :loading="loading" :isNotEmpty="data.length > 0">
        <DataTable  :value="data" tableStyle="min-width: 80rem" paginator :rows="20"
      :rowsPerPageOptions="[20, 50, 100]">
                <Column field="account_code" :header="$t('Account Code')" bodyClass="text-center" headerClass="text-center">
                    <template #body="slotProps">
                     <!-- @click="onEdit(slotProps.data)"   link_line_action1 -->
                        <span  class="p-0 " >{{ slotProps.data.account_code }}-{{ slotProps.data.account_name }}</span>
                    </template>
                </Column>
                <Column field="posting_rule" :header="$t('Posting Rule')" bodyClass="text-center" headerClass="text-center">
                    <template #body="slotProps">
                        <span>{{ slotProps.data.posting_rule }}</span>
                    </template>
                </Column>
                <Column field="charge_rule" :header="$t('Charge Rule')" bodyClass="text-center" headerClass="text-center">
                    <template #body="slotProps">
                        <span>{{ slotProps.data.charge_rule }}</span>
                    </template>
                </Column>
                <Column field="rate" :header="$t('Rate')" bodyClass="text-right" headerClass="text-right">
                    <template #body="slotProps">
                        <CurrencyFormat :value="slotProps.data.rate" />
                    </template>
                </Column>
                <Column field="adult_rate" :header="$t('Adult Rate')" bodyClass="text-right" headerClass="text-right">
                    <template #body="slotProps">
                        <CurrencyFormat :value="slotProps.data.adult_rate" />
                    </template>
                </Column>
                <Column field="child_rate" :header="$t('Child Rate')" bodyClass="text-right" headerClass="text-right">
                    <template #body="slotProps">
                        <CurrencyFormat :value="slotProps.data.child_rate" />
                    </template>
                </Column>
                <!-- hide funtion -->
                <!-- <Column header="">
                    <template #body="slotProps">
                        <div v-if="slotProps.data.name">
                            <div class="res_btn_st">
                            <Button class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded icon="pi pi-ellipsis-v"
                                @click="toggle"></Button>
                        </div>
                        <Menu :model="menus" :popup="true" ref="show" style="min-width: 180px;">
                            <template #end>
                                <template v-if="isEdit">
                                    <button @click="onEdit(slotProps.data)"
                                        class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                                        {{$t('Edit')}}
                                    </button>
                                </template>
                                <template v-if="isDelete">
                                    <button 
                                        class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                                        {{$t('Delete')}} 
                                    </button>
                                </template>
                            </template>
                        </Menu>
                        </div>
                    </template>
                </Column> -->
                </DataTable>
            </ComPlaceholder>            
    </div>
</template>
<script setup>
import {ref,inject,useDialog} from "@/plugin"
import {i18n} from '@/i18n';
import ComEditReservationStayPackageItems from '@/views/reservation/components/ComEditReservationStayPackageItems.vue';
import ComAddNewPackageItems from '@/views/reservation/components/ComAddNewPackageItems.vue';
const dialog = useDialog();
const { t: $t } = i18n.global;
const gv = inject("$gv")
const rs =inject("$reservation_stay")
const data = rs.reservationStay?.inclusion_items
const props = defineProps({
    data: Object,
    isEdit: {
        type: Boolean,
        default: true
    },
    isDelete: {
        type: Boolean,
        default: true
    }
})
const show = ref()
const loading = ref()
const opDelete = ref(false)
const toggle = (event) => {
    show.value.toggle(event)
}
function onEdit(item = null){
     dialog.open(ComEditReservationStayPackageItems, {
      data: {
        data:item,        
        },
      props: {
        header: $t('Edit Package & Inclusion'),
        style: {
          width: '40vw',
        },
        position: "top",
        modal: true,
        closeOnEscape: false,
        breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
      },

    })
}
function addnew(){
     dialog.open(ComAddNewPackageItems, {
      data:{
        rs:rs.reservationStay.name,
      },
      props: {
        header: $t('Add New Package & Inclusion'),
        style: {
          width: '40vw',
        },
        position: "top",
        modal: true,
        closeOnEscape: false,
        breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
      },

    })
}
function onOpenDelete() {
   
   
}

</script>