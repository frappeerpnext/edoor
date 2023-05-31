import { createToaster } from "@meforma/vue-toaster";
const userToaster = createToaster({
    position: "top-right"
});
export function toaster(type = 'success', message = ''){
    if(type == 'success'){
        userToaster.success(message)
    }
    else if(type == 'warn'){
        userToaster.warning(message)
    }
    else if(type == 'error'){
        userToaster.error(message)
    }
    else{
        userToaster.info(message)
    }
}