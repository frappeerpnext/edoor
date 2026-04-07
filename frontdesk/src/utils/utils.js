 

export function getDialogScrollHeight(adjustHeight = 0){
    let el = document.querySelectorAll(".p-dialog-content")
    if(el){
        el = el[el.length-1]
      return (el.offsetHeight + adjustHeight) + "px"
    }


}

export function getYearOption(){
  const currentYear = new Date().getFullYear();
  const years = [];

  for (let i = currentYear - 10; i <= currentYear + 10; i++) {
    years.push({ label: `${i}`, value: i });
  }

  return years;


}
export function getMothOptions(){
  return [
    { value: 1, label: "Jan" },
    { value: 2, label: "Feb" },
    { value: 3, label: "Mar" },
    { value: 4, label: "Apr" },
    { value: 5, label: "May" },
    { value: 6, label: "Jun" },
    { value: 7, label: "Jul" },
    { value: 8, label: "Aug" },
    { value: 9, label: "Sep" },
    { value: 10, label: "Oct" },
    { value: 11, label: "Nov" },
    { value: 12, label: "Dec" }
];

}


export function getDaysInMonth(month, year) {
  const days = [];
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const date = new Date(year, month - 1, 1); // JS months are 0-based

  while (date.getMonth() === month - 1) {
      const dayOfWeek = date.getDay(); // 0 = Sunday, 6 = Saturday
      days.push({
          value: date.getDate(),
          label: dayNames[dayOfWeek],
          isWeekend: dayOfWeek === 0 || dayOfWeek === 6
      });
      date.setDate(date.getDate() + 1);
  }

  return days;
}

export function showWarning(title,message=""){

  window.toast.add({ severity: 'warn', summary: title, detail: message, life: 3000 })
}

export function groupDatesToPeriods(dateInput) {
    // handle Set or Array
    let dates = Array.isArray(dateInput)
        ? dateInput
        : Array.from(dateInput);

    // sort dates
    dates.sort();

    const periods = [];

    if (dates.length === 0) return periods;

    let start = dates[0];
    let prev = dates[0];

    for (let i = 1; i < dates.length; i++) {
        const current = dates[i];

        const prevDate = new Date(prev);
        prevDate.setDate(prevDate.getDate() + 1);

        const nextDay = prevDate.toISOString().slice(0, 10);

        // break period if not consecutive
        if (current !== nextDay) {
            periods.push({
                start_date: start,
                end_date: prev
            });

            start = current;
        }

        prev = current;
    }

    // push last period
    periods.push({
        start_date: start,
        end_date: prev
    });

    return periods;
}


 