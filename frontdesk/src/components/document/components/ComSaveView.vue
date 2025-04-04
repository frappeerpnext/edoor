<template>
    <ComDialogContent @onOK="onOk" hideButtonClose titleButtonOK="Save" :hideIcon="false" :loading="loading">
        <Stack>
            <div>
                <label for="view_namne">{{ $t('View Name') }}</label>
                <InputText id="view_namne" class="w-full" type="text" v-model="viewName"
                    placeholder="Please enter view name" />
            </div>
            <div>

                <Checkbox v-tippy="$t('If you tick this check box, this view will be show for all user')"
                    v-model="isPublic" :binary="true" :trueValue="1" inputId="for_user" :falseValue="0" />

                <label for="for_user" class="ml-2">{{ $t('Everyone can see this view') }}</label>
            </div>
            <div v-if="data?.current_view">

                <Checkbox
                    v-tippy="$t('If you tick this check box, view name and filter option will be update to current selected view.')"
                    v-model="overrideView" :binary="true" :trueValue="1" inputId="override_view" :falseValue="0" />

                <label for="override_view" class="ml-2">{{ $t('Override this view') }}</label>
            </div>

        </Stack>
    </ComDialogContent>


</template>
<script setup>
import { ref, inject, useDialog, createDocument, updateData } from "@/plugin"
import { i18n } from '@/i18n';
import { onMounted } from "vue";
const { t: $t } = i18n.global;
const dialog = useDialog();
const dialogRef = inject("dialogRef");
const viewName = ref();
const loading = ref(false)
const isPublic = ref(1)
const gv = inject("$gv")
const data = ref()
const overrideView = ref(1)

async function onOk() {
    loading.value = true;

    if (!viewName.value) {
        gv.toast('warn', $t('Please enter view name'))
        loading.value = false;
        return
    }

    let res = null
    if (data.value.current_view && overrideView.value==1) {
        res = await updateData(
            {
                doctype: "List Filter",
                name: data.value.current_view.name,
                data: {
                    filter_name: viewName.value,
                    filters: JSON.stringify(data.value.filters),
                    custom_view_filters: JSON.stringify(data.value.view_filters),
                    for_user: isPublic.value ? "" : window.user.name
                }
            }

        )

    } else {
        res = await createDocument("List Filter", {
            filter_name: viewName.value,
            reference_doctype: data.value.doctype,
            filters: JSON.stringify(data.value.filters),
            custom_view_filters: JSON.stringify(data.value.view_filters),
            for_user: isPublic.value ? "" : window.user.name
        })

    }

    loading.value = false;

    if (res.data) {
        dialogRef.value.close(res.data)
    }
}

onMounted(() => {
    data.value = dialogRef?.value?.data;
    if (data.value.current_view) {
        viewName.value = data.value.current_view.filter_name
        isPublic.value = (data.value.current_view.for_user == "" ? 1 : 0);
    }
})







</script>