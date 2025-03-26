<template> 

    <template
        v-for="(d, index) in data" :key="index">
        <Button v-if="!d.sub_account" @click="onClick(d)" class="conten-btn mr-1">
            {{ $t(  d.label)  }}  
        </Button>
        <SplitButton v-else
        @click="onClick(d)"
        class="spl__btn_cs sp mr-1"
        :label="$t(d.label)"
        :model="d.sub_account"
        /> 
    </template> 
</template> 
                
<script setup>
 
    const emit = defineEmits(['onClick'])
    const props = defineProps({
        data: Object,
    }) 


    props.data.filter(x=>x.sub_account).forEach(r=>{
     
        r.sub_account.filter(y=>!y.separator).forEach(s=>{
            
            s.command =   () => {
                
                emit('onClick', s)
            }
        })
        
    })



    const onClick = (d) => {
        
        emit('onClick', d)
    }


</script>