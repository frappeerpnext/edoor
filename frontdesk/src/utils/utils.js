export function getDialogScrollHeight(adjustHeight = 0){
    let el = document.querySelectorAll(".p-dialog-content")
    if(el){
        el = el[el.length-1]
      return (el.offsetHeight + adjustHeight) + "px"
    }


}