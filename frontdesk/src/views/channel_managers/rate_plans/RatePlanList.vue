<template>
    <div>
        <ComHeader :isRefresh="true" @onRefresh="onRefresh">
            <template #start>
                <div class="flex">
                    <div class="flex align-items-center justify-content-between w-full">
                        <div class="text-xl md:text-2xl white-space-nowrap">{{ $t('Rate Plan') }}</div>

                    </div>
                </div>
            </template>
            <template #end>
                <div class="flex gap-2 w-full justify-content-end">
                    <Button class="border-0">Bulk Edit</Button>
                </div>
            </template>
        </ComHeader>
        <div class="bg-white border-1 p-2 rounded-xl">
            <!-- {{ data }}              -->
            <DataTable :value="data.rate_type_list" tableStyle="min-width: 50rem">
                <Column header="Rate Plan">
                    <template #body="slotProps">
                        <RouterLink class="p-button p-component p-button-link link_line_action1"
                            :to="`/frontdesk/channel-manager/rate-plan/${encodeURIComponent(slotProps.data.rate_type_name)}`">
                            {{ slotProps.data.rate_type_name }}
                        </RouterLink>
                    </template>
                </Column>

                <Column header="Prices Set Date" class="text-center">
                    <template #body="slotProps"> 
                        <Chip v-if="slotProps.data.room_rates_max_min_date.length > 0">
                            {{ slotProps.data.room_rates_max_min_date.map(r=>moment(r.start_date).format("DD-MM-yyyy")).join('') }} &#8594;
                            {{ slotProps.data.room_rates_max_min_date.map(r=>moment(r.end_date).format("DD-MM-yyyy")).join('') }}
                             
                        </Chip>
                        <template v-else>
                            -
                        </template>
                    </template>
                </Column>

                <Column header="Restriction" class="text-center">
                    <template #body="slotProps">
                        <Chip v-if="slotProps.data?.room_restriction?.group_restriction_type"
                            :label="slotProps.data.room_restriction.group_restriction_type" />
                        <template v-else>-</template>
                    </template>
                </Column>
                <Column header="Rate and Restriction Period" class="text-center">
                    <template #body="slotProps">  
                        <Chip v-if="slotProps.data.room_restriction.start_date || slotProps.data.room_restriction.start_date">
                            {{ moment(slotProps.data.room_restriction.start_date).format("DD-MM-yyyy") }} &#8594;
                            {{ moment(slotProps.data.room_restriction.end_date).format("DD-MM-yyyy") }}
                        </Chip>
                        <template v-else>
                            -
                        </template>
                    </template>
                </Column>
                <Column header="Connted with Channel Manager">
                    <template #body="slotProps">
                        <template v-if="slotProps.data.status == 'Connected'">
                            <div class="flex gap-2 align-items-center">
                                <span>{{$t('Connected with')}}</span>
                                <Image :src="data.cm_logo" width="50" />
                            </div>
                        </template>
                    </template>
                </Column> 
            </DataTable>
        </div>


    </div>
</template>
<script setup>
import { inject, onMounted, ref } from "vue";
import Image from 'primevue/image';
import { i18n } from '@/i18n';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
const moment = inject("$moment")
const { t: $t } = i18n.global;
const property = JSON.parse(localStorage.getItem("edoor_property"))
const data = ref([])
const checked = ref(1)
async function getRatePlanList() {
    const l = await window.showLoading()
    const res = await app.getApi("rate_plan.get_rate_type_list", {
        property: property.name
    })
    if (res.data) {
        data.value = res.data 
    }

    l.close()
}
onMounted(async () => {
    await getRatePlanList()
})
</script>