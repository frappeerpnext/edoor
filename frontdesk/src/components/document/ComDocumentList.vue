<template>
    <div class="mt-4">

        <ComFilter @onSearch="onSearch" />
        <div id="table-container">
            <!-- rowGroupMode="subheader" groupRowsBy="reservation"  -->
            <DataTable v-if="scrollHeight" :value="items"
             scrollable :scrollHeight="scrollHeight" 
             :loading="loading"
                
                
                tableStyle="min-width: 50rem"
                :virtualScrollerOptions="{ itemSize: 46 }">
                <!-- <template #groupheader="slotProps">
                    <div class="flex align-items-center gap-2">
                               <span>{{ slotProps.data.reservation }}</span>
                    </div>
                </template> -->


                <Column v-for="(col, index) of columns" :field="col.field" :header="col.header"
                    :key="col.field + '_' + index">
                    <template #body="slotProps">
                        <slot :name="col.field" :item="slotProps.data" :index="col.field + '_' + index">
                            <span>{{ slotProps.data[col.field] }}</span>
                        </slot>
                    </template>
                </Column>

            </DataTable>
        </div>
    </div>
</template>
<script setup>

import { useDocumentList } from "@/components/document/hooks/useDocumentList"
import ComFilter from "@/components/document/components/ComFilter.vue"

const props = defineProps({
    doctype: String,
    options: {
        type: Object,
        default: {
            limit: 100
        }
    }
})


const { items, scrollHeight, onSearch, loading, columns } = useDocumentList(props)

</script>