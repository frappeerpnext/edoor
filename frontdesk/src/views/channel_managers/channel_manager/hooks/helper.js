import moment from "@/utils/moment";

export   function getRecentReservation(){
    alert("hello")
}


export function timeAgo(date) {
    if (!date) return "";

    const now = moment();
    const target = moment(date);

    const seconds = now.diff(target, "seconds");
    const minutes = now.diff(target, "minutes");
    const hours = now.diff(target, "hours");
    const days = now.diff(target, "days");

    // Just now
    if (seconds < 60) {
        return "Just now";
    }

    // Minutes
    if (minutes < 60) {
        return `${minutes} minute${minutes !== 1 ? "s" : ""} ago`;
    }

    // Hours
    if (hours < 24) {
        return `${hours} hour${hours !== 1 ? "s" : ""} ago`;
    }

    // Days
    if (days < 7) {
        return `${days} day${days !== 1 ? "s" : ""} ago`;
    }

    // Old date
    return target.format("DD-MM-YYYY");
}