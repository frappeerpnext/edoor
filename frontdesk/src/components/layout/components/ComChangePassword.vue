<template>
    <ComDialogContent @onOK="onSave" hideButtonClose :titleButtonOK="Save" :hideIcon="false" :loading="loading">
        <div class="grid">
            <div class="col-12">
                <label for="username">{{ $t('Username')}}</label>
                <InputText v-model="user.full_name" id="username" type="text"
                    class="p-inputtext-sm w-full" :placeholder="$t('Username')" :maxlength="50" />
            </div>
            <div class="col-12">
                <label for="password">{{ $t('Password')}}</label>
                <InputText v-model="data.password" id="password" type="text"
                    class="p-inputtext-sm w-full" :placeholder="$t('Password')" :maxlength="50" />
            </div> 
            <div class="col-12">
                <label for="confirm_password">{{ $t('Confirm Password')}}</label>
                <InputText v-model="data.confirm_password" id="confirm_password" type="text"
                    class="p-inputtext-sm w-full" :placeholder="$t('Confirm Password')" :maxlength="50" />
            </div> 
        </div> 
    </ComDialogContent>
</template>
<script setup> 
    import {ref,postApi, useToast} from '@/plugin'
    import {i18n} from '@/i18n';
    const { t: $t } = i18n.global;

    const toast = useToast();
    const loading = ref(false)
 
    const data = ref({})

    const user = ref(JSON.parse(localStorage.getItem('edoor_user')))

    const onSave = () => {  
        if (!data.value.password) {
            toast.add({ severity: 'warn', summary: "Please Enter Password", life: 3000})
            return 
        }
        
        if (!data.value.confirm_password) {
            toast.add({ severity: 'warn', summary: "Please Enter Confirm Password", life: 3000})
            return 
        }

        if (data.value.confirm_password != data.value.password) {
            toast.add({ severity: 'warn', summary: "Password Not Match", life: 3000})
            return 
        }

        if (data.value.password.length < 4) {
            toast.add({ severity: 'warn', summary: "Please enter a password of 4 characters", life: 3000})
            return 
        }


        loading.value = true 
        postApi("epos_restaurant_2023.employee_management.doctype.employee.employee.change_password",{
            user:user.value.name,
            password:data.value.password
        },"",true,"").then(r=>{
            loading.value = false
        }).catch(err=>{
            loading.value = false
        })
      
    }
</script>