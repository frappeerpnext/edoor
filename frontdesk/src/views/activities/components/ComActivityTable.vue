<template>

<ComPlaceholder text="No Data" height="70vh" :loading="gv.loading" :is-not-empty="data.length > 0">
				<DataTable 
					class=" max-w-screen" 
					:resizableColumns="true" 
					columnResizeMode="fit" 
					showGridlines
					stateStorage="local" 
					:reorderableColumns="true" 
					:value="data"
					scrollable
					tableStyle="max-width:100vw;" 
					scrollHeight="70vh"
					@row-dblclick="onViewReservationStayDetail">
						<Column field="custom_posting_date" header="Audit date">
							<template #body="slotProps">
								{{ moment(slotProps.data.custom_posting_date).format("DD-MM-YYYY") }}
							</template>
						</Column>
						<Column field="reference_doctype" header="Reference Type"></Column>
						<Column field="reference_name" header="Reference Name">
							<template #body="slotProps">
								<Button class="p-0 link_line_action1" @click="onOpenLink(slotProps.data)" link>
									{{ slotProps.data.reference_name }}

								</Button>
							</template>

						</Column>
						<Column field="subject" header="Subject"></Column>
						<Column field="content" header="Description">
							<template #body="slotProps">
								<div class="white-space-nowrap overflow-hidden text-overflow-ellipsis content-note-comment" style="width:500px" v-html="slotProps.data.content" v-tippy="slotProps.data.content"></div>
							</template>
						</Column>
						<Column field="comment_by" header="By"></Column>
						<Column field="modified" header=" Date & Time"><template #body="slotProps">
								<ComTimeago :date="slotProps.data.modified" />

							</template>
						</Column>
				</DataTable>
			</ComPlaceholder>
</template>

<script setup>
import { inject } from '@/plugin';
const props = defineProps({
    data:{
        type:  Object ,
        default: []
    }
})
const gv = inject("$gv")
const moment = inject("$moment")

function onOpenLink(data) {
	const action = ("view_" + data.reference_doctype.toLowerCase().replaceAll(" ", "_") + "_detail")
	window.postMessage(action + '|' + data.reference_name, '*')
}


</script>