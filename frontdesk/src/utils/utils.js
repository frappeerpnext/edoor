 
const isMobile = window.innerWidth <= 640
const isTablet = window.innerWidth <= 960
 
export function getDialogScrollHeight(adjustHeight = 0) {
  let el = document.querySelectorAll(".p-dialog-content")
  if (el) {
    el = el[el.length - 1]
    return (el.offsetHeight + adjustHeight) + "px"
  }


}

export function getYearOption() {
  const currentYear = new Date().getFullYear();
  const years = [];

  for (let i = currentYear - 10; i <= currentYear + 10; i++) {
    years.push({ label: `${i}`, value: i });
  }

  return years;


}
export function getMothOptions() {
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

export function showWarning(title, message = "", life = 5000, group = "tc", data = {}) {

  if (life == 0) {
    window.toast.add({ group: group, severity: 'warn', summary: title, detail: message, ...data, left: 1000 * 60 })
  } else {
 
    if (group=="tc"){
window.toast.add({   severity: 'warn', summary: title, detail: message, life: life, ...data })
    }else {
      window.toast.add({ group:group,  severity: 'warn', summary: title, detail: message, life: life, ...data })
    }
    
  }


}

export function showSuccess(title, message = "", life = 5000, group = "tc", data = {}) {

  if (life == 0) {
       if(group == "tc"){
        window.toast.add({  severity: 'success', summary: title, detail: message, ...data, left: 1000 * 60 })
       }else {
          window.toast.removeGroup(group);
          window.toast.add({ group: group, severity: 'success', summary: title, detail: message, ...data, left: 1000 * 60 })
       }
    
  } else {
    if(group == "tc"){
window.toast.add({ severity: 'success', summary: title, detail: message, life: life, ...data })
    }else {
      window.toast.add({ group: group, severity: 'success', summary: title, detail: message, life: life, ...data })
    }
    
  }


}




export function showInfo(title, message = "", life = 3000, group = "tc", data = {}) {
 
  if (life == 0) {
    if(group=="tc"){
      window.toast.add({   severity: 'info', summary: title, detail: message, ...data, left: 1000 * 60 })
    }else {
      window.toast.add({ group: group, severity: 'info', summary: title, detail: message, ...data, left: 1000 * 60 })
    }
    

  } else {
     if(group == "tc"){
      window.toast.add({  severity: 'info', summary: title, detail: message, "life": life, ...data })
     }else {
      window.toast.add({ group: group, severity: 'info', summary: title, detail: message, "life": life, ...data })
     }
  }




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


export function onConfirm(
  header = 'Confirmation',
  message = "Are you sure you want to proceed?",
  icon = "pi pi-exclamation-triangle"
) {
  return new Promise((resolve) => {

    window.confirm.require({
      // group: "headless",
      message,
      header,
      icon,

      rejectClass: 'p-button-secondary p-button-outlined',
      acceptLabel: 'Ok',
      accept: () => {
        resolve(true)
      },

      reject: () => {
        resolve(false)
      }
    })

  })
}

export function onConfirmHeadless(
  header = 'Confirmation',
  message = "Are you sure you want to proceed?",
  icon = "pi pi-exclamation-triangle"
) {
  return new Promise((resolve) => {

    window.confirm.require({
      group: "headless",
      message,
      header,
      icon,

      rejectClass: 'p-button-secondary p-button-outlined',
      acceptLabel: 'Ok',
      accept: () => {
        resolve(true)
      },

      reject: () => {
        resolve(false)
      }
    })

  })
}

export function openDialog(component, title = "Dialog", options = null) {
  return new Promise((resolve) => {
    let _options = {
      data: {
        ...options?.data
      },
      props: {

        header: title,
        style: { width: isMobile ? '100vw' : isTablet ? '90vw' : '65vw' },
        breakpoints: {
          '960px': '100vw',
          '640px': '100vw'
        },
        modal: true,
        closeOnEscape: true,
        position: "top"
      }
    }

    if (options?.props) {
      _options.props = { ..._options.props, ...options.props }
    }
    if (!options?.props?.position) {
      _options.props.position = "top"
    }


    // attach promise resolver
    _options.onClose = (data) => {
      if (data) {
        resolve(data.data)     // return data
      } else {
        resolve(false)    // return false if closed without data
      }
    }
    
    window.dialog.open(component, _options)

  })
}

export function getMonthlyRanges(startDate, endDate) {
  // Convert ISO strings to UTC-midnight Date objects (ignores time)
  const toUTCMidnight = (iso) => {
    const d = new Date(iso);
    return new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
  };

  const start = toUTCMidnight(startDate);
  const end = toUTCMidnight(endDate);
  
  const result = [];
  let current = new Date(start);
  
  while (current <= end) {
    const year = current.getUTCFullYear();
    const month = current.getUTCMonth();
    
    // First day of current month (UTC midnight)
    const monthStart = new Date(Date.UTC(year, month, 1));
    // Last day of current month (UTC midnight of that day)
    const monthEnd = new Date(Date.UTC(year, month + 1, 0));
    
    let segmentStart, segmentEnd;
    
    if (result.length === 0) {
      // First segment: from original start date to end of its month (or end date if earlier)
      segmentStart = new Date(start);
      segmentEnd = monthEnd < end ? monthEnd : new Date(end);
    } else if (monthEnd >= end) {
      // Last segment: from start of month to original end date
      segmentStart = monthStart;
      segmentEnd = new Date(end);
    } else {
      // Full month segment
      segmentStart = monthStart;
      segmentEnd = monthEnd;
    }
    
    // Format YYYY-MM-DD from UTC date
    const format = (date) => date.toISOString().split('T')[0];
    
    result.push({
      start_date: format(segmentStart),
      end_date: format(segmentEnd),
      max_days: monthEnd.getUTCDate() // days in this month
    });
    
    // Move to first day of next month
    current = new Date(Date.UTC(year, month + 1, 1));
  }
  
  return result;
}

export function compareJSON(obj1, obj2) {
    const diff = {};

    const keys = new Set([
        ...Object.keys(obj1 || {}),
        ...Object.keys(obj2 || {})
    ]);

    keys.forEach((key) => {
        const oldValue = obj1?.[key];
        const newValue = obj2?.[key];

        // skip if same
        if (JSON.stringify(oldValue) === JSON.stringify(newValue)) {
            return;
        }

        diff[key] = {
            key,
            old_value: oldValue,
            new_value: newValue,
            changed: true,
            type: !Object.hasOwn(obj1 || {}, key)
                ? 'added'
                : !Object.hasOwn(obj2 || {}, key)
                    ? 'removed'
                    : 'updated'
        };
    });

    return diff;
}