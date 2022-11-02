var date= document.getElementsByClassName("time")
var className=this.date
for (var i = 0; i < className.length; i++){
    console.log(date[i])
    x=moment(date[i].innerHTML).fromNow()
    console.log(x)
    document.getElementById(date[i].id).innerHTML=x


}
