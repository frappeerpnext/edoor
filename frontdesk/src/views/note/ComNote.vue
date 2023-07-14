<template>
	
{{ Note}}
<ComAddNote></ComAddNote>

</template>

<script setup>
import { ref, inject,} from '@/plugin'
import ComAddNote from './ComAddNote.vue';
const frappe = inject('$frappe')
const db = frappe.db();
const Note = ref();

db.getDocList('Frontdesk Note', {
		fields: ['note_date','reference_doctype','reference_name', "reservation", "reservation_stay", "content"],	
		
	})
		.then((docs) => {
      Note.value = docs;			
		}
	)
</script>
