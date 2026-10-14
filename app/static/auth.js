const secLog=document.getElementById("lg")
const secRg=document.getElementById("rg")

function mudar(sec){
    if(sec=="rg"){
        secLog.classList.add("ativo")
        secRg.classList.remove("ativo")
    }else if(sec=="lg"){
        secLog.classList.remove("ativo")
        secRg.classList.add("ativo")
    }
}