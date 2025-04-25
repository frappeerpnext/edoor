 <template>
    <ComDocumentList
      doctype="Business Source Type"
      list_view_setting="business_source_type_list"
      :options="options"
      @row-dblclick="onRowDoubleClick"
    > 
    <template #action-button>
        <Button class="border-none" :label="isMobile ? $t('Add New') : $t('Add New Business Source Type') " icon="pi pi-plus" @click="onAddNewBusinessSourceType" />
    </template>

        <template #name="{ item, index }">
             {{ item.name }}
        </template>
        <template #action="{ item }" >
            <div class="flex gap-2 justify-start">
                <Button
                    @click="onEdit(item)"
                    icon="pi pi-pencil text-sm"
                    class="h-2rem border-none"
                    :label="$t('Edit')"
                    rounded
                    />
                <Button
                    @click="onDelete(item.name)"
                    severity="danger"
                    icon="pi pi-trash text-sm"
                    class="h-2rem border-none"
                    :label="$t('Delete')"
                    rounded
                    />
                </div>
        </template>
    </ComDocumentList>
  </template> 
<script setup> 
import {useDialog, useConfirm, deleteDoc} from "@/plugin" 
import ComAddBusinessSourceType from "@/views/business_source/components/ComAddBusinessSourceType.vue"

const confirm = useConfirm()

const dialog = useDialog()


const options = {
    fields: [
        { fieldname: "name", label: "Business Source Type" },  
        { fieldname: "owner", label: "Owner" },  
        { fieldname: "note", label: "Note" }, 
        {fieldname: "name as action", label:"Action" },
    ],   
} 
function onEdit(edit) {
    dialog.open(ComAddBusinessSourceType, {
        props: {
            header: `Edit Business Source Type: ${edit.name}`,
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        data: edit,
        onClose: (options) => {
            const data = options.data;
            if (data) {
                loadData()
            }
        }
    });
}

function onDelete(name) {
    confirm.require({
        message: 'Are you sure you want to delete business source type?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            deleteDoc('Business Source Type', name)
                .then(() => {
                    loadData()
                    loading.value = false
                })
                .catch((err) => {
                    loading.value = false
                })
        },
    });
}

function onAddNewBusinessSourceType() {
    dialog.open(ComAddBusinessSourceType, {
        props: {
            header: `Add New Business Source Type`,
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                loadData()
            }
        }
    });
}

</script> 

<!-- <template>
    <div>
        <ComHeader colClass="col-6" isRefresh @onRefresh="Refresh()">
            <template #start>
                <div class="text-xl md:text-2xl"> {{ $t('Business Source Type') }} </div>
            </template>
            <template #end>
                <Button class="border-none" :label="isMobile ? $t('Add New') : $t('Add New Business Source Type') " icon="pi pi-plus" @click="onAddNewBusinessSourceType" />
            </template>
        </ComHeader>
        <div class="mb-3 w-full md:w-20rem">
            <div class="flex w-full flex-wrap gap-2 ">
                <div class="p-input-icon-left w-full">
                    <i class="pi pi-search" />
                    <InputText class="w-full" v-model="filter.keyword" :placeholder=" $t('Search') " @input="onSearch" />
                </div>
            </div>
        </div>
        <div class="">
            <ComPlaceholder text="No Data" :loading="gv.loading" :is-not-empty="gv.search(data, filter.keyword).length > 0">

                <DataTable showGridlines :value="gv.search(data, filter.keyword)" tableStyle="min-width: 50rem">
                    <Column headerClass="white-space-nowrap" field="business_source_type" :header=" $t('Business Source Type') "></Column>
                    <Column :header="$t('Owner')">
                        <template #body="slotProps">
                            <div v-if="slotProps?.data && slotProps?.data?.owner">
                                <template v-for="(item) in slotProps.data?.owner?.split('@')[0]" :key="index">
                                    <span>{{ item }}</span>
                                </template>
                            </div>  
                        </template>
                    </Column>
                    <Column field="note" class="w-6" :header=" $t('Note')"></Column>
                    <Column :header=" $t('Action') " class="text-center w-10rem">
                        <template #body="slotProps">
                            <div class="flex gap-2 justify-center">
                                <Button @click="onEdit(slotProps.data)" icon="pi pi-pencil text-sm" iconPos="right"
                                    class="h-2rem border-none" :label="$t('Edit')" rounded />
                                <Button @click="onDelete(slotProps.data.name)" severity="danger" icon="pi pi-trash text-sm"
                                    iconPos="right" class="h-2rem border-none" :label=" $t('Delete') " rounded />
                            </div>
                        </template>
                    </Column>
                </DataTable>
            </ComPlaceholder>
        </div>
    </div>
</template>
<script setup>
import { inject, ref, getDocList, onMounted, useDialog, useConfirm, deleteDoc,computed } from '@/plugin'
import ComAddBusinessSourceType from "@/views/business_source/components/ComAddBusinessSourceType.vue"
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const gv = inject("$gv")
const dialog = useDialog()
const data = ref([])
const filter = ref({})
const loading = ref(false)
const confirm = useConfirm()
const isMobile = ref(window.isMobile) 
function onDelete(name) {
    confirm.require({
        message: 'Are you sure you want to delete business source type?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            deleteDoc('Business Source Type', name)
                .then(() => {
                    loadData()
                    loading.value = false
                })
                .catch((err) => {
                    loading.value = false
                })
        },
    });
}
function onEdit(edit) {
    dialog.open(ComAddBusinessSourceType, {
        props: {
            header: `Edit Business Source Type: ${edit.name}`,
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        data: edit,
        onClose: (options) => {
            const data = options.data;
            if (data) {
                loadData()
            }
        }
    });
}

function loadData() {
    gv.loading = true
    getDocList('Business Source Type', {
        fields: ['business_source_type', 'note', 'owner', 'name'],
        limit: 10000,
    })
    .then((doc) => {
        data.value = doc
        gv.loading = false
    })
    .catch((error) => {
        gv.loading = false

    });
}
const Refresh = debouncer(() => {
    loadData()
}, 500);

function debouncer(fn, delay) {
    var timeoutID = null;
    return function () {
        clearTimeout(timeoutID);
        var args = arguments;
        var that = this;
        timeoutID = setTimeout(function () {
            fn.apply(that, args);
        }, delay);
    };
}

function onAddNewBusinessSourceType() {
    dialog.open(ComAddBusinessSourceType, {
        props: {
            header: `Add New Business Source Type`,
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                loadData()
            }
        }
    });
}
onMounted(() => {
    loadData()
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
})

</script> -->