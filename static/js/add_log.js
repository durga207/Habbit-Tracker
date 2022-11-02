$(document).ready( function() {
    var now = new Date();
    var month = (now.getMonth() + 1);               
    var day = now.getDate();
    if (month < 10) 
        month = "0" + month;
    if (day < 10) 
        day = "0" + day;
    var hours = now.getHours()
    if (hours<10)
        hours = "0" + hours

    var min = now.getMinutes()
    if (min<10)
        min = "0" + min
    var sec = now.getSeconds()
    if (sec<10)
        sec = "0" + sec
    var today = now.getFullYear() + '-' + month + '-' + day + 'T' + hours + ":" + min + ":" + sec;
    $('#timestamp').val(today);
});
