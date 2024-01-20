


////////////////////////////    Utilizaveis  ///////////////////////////////////


function dataAtualFormatada(days){
    var data = new Date(Date.now() - days*24*60*60*1000) 
        dia  = (data.getDate()).toString().padStart(2, '0'),
        mes  = (data.getMonth()+1).toString().padStart(2, '0'),
        ano  = data.getFullYear();
    return ano+"-"+mes+"-"+dia;
}

function dataBRFormat(DataSelect){
    const dateObj = new Date(DataSelect);
    let year = dateObj.getFullYear();

    let month = dateObj.getMonth();
    month = ('0' + (month + 1)).slice(-2);

    let date = dateObj.getDate();
    date = ('0' + date).slice(-2);

    let hour = dateObj.getHours();
    hour = ('0' + hour).slice(-2);

    let minute = dateObj.getMinutes();
    minute = ('0' + minute).slice(-2);

    let second = dateObj.getSeconds();
    second = ('0' + second).slice(-2);

    return `${date}/${month}/${year} ${hour}:${minute}:${second}`;
}

//Resetar ações definidas como listening
function recreateNode(el, withChildren) {
    if (withChildren) {
    el.parentNode.replaceChild(el.cloneNode(true), el);
    }
    else {
    var newEl = el.cloneNode(false);
    while (el.hasChildNodes()) newEl.appendChild(el.firstChild);
    el.parentNode.replaceChild(newEl, el);
    }
}

function generateColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';

    for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function hide_show(element,button, time=1000){
    
    if($(button)[0].visivel != 'sim'){
        $(element).show(time)
        $(button)[0].visivel = 'sim'
    }
    else{
        $(element).hide(time)
        $(button)[0].visivel = 'nao'
    }
}

hide_show_choice_Change = 1
function hide_show_choice(hide,show,change=false){    
    if (change){
        if (hide_show_choice_Change==1){
            $(hide).hide(1000)
            $(show).show(1000)
            hide_show_choice_Change=2
        }else{
            $(show).hide(1000)
            $(hide).show(1000)
            hide_show_choice_Change=1
        }
        

    }else{
        $(hide).hide(1000)
        $(show).show(1000)
    }


}

function maximizar(modal,original,grafico){

    classList = $(modal)[0].classList
    if (classList.value.includes(original)){
        classList.remove(original);
        classList.add('modal-fullscreen');
        resetdragg();
    }
    else {
        classList.add(original);
        classList.remove('modal-fullscreen')
        if(grafico=="sim"){
            SolicitarGrafico()
        }
        resetdragg();
    }  
}


function getAllIndex(arr, val) {
    var indexes = [], i;
    for(i = 0; i < arr.length; i++)
        if (arr[i] === val)
            indexes.push(i);
    return indexes;
}


////////////////////////////// funções de cookie //////////////////////////////////////

function setCookie(cname, cvalue, exdays) {
    const d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    let expires = "expires="+d.toUTCString();
    document.cookie = `${cname}=${cvalue};${expires};path=/` 
}
  
function getCookie(cname) {
let name = cname + "=";
let ca = document.cookie.split(';');
for(let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
    c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
    return c.substring(name.length, c.length);
    }
}
return "";
}
  
function checkCookie() {
    let user = getCookie("username");
    if (user != "") {
        alert("Welcome again " + user);
    } else {
        user = prompt("Please enter your name:", "");
        if (user != "" && user != null) {
        setCookie("username", user, 365);
        }
    }
}


