$(document).ready(function () {
    // Permitir que as classes arrastar possam ser arrastadas 
    $(".arrastar").draggable({ handle:'.modal-header'})

    //Iniciar Virtual Select
    VirtualSelect.init({
        ele: '.VirtualSelect',
        multiple:"true", search: "true",
        selectAllOnlyVisible: "true",
        hideValueTooltipOnSelectAll: 'true',
    });
    
})

// ------------------------------------------------ Funções Exibir Detalhamentos
// Solicitar Dados com Base na Especialidade

function ColetarDados(especialidade) {
    //Abrir Tela de Loading
    $('#Loading_Modal').modal('show');

    // Resetar visual de todo os botões
    classes = "btn_Espec btn btn-outline-dark border-detalhe text-light"
    document.getElementById("btn_Sistemas").className = classes
    document.getElementById("btn_Mecânica").className = classes
    document.getElementById("btn_Instrumentação").className = classes
    document.getElementById("btn_Elétrica").className = classes

    // Marcar visual do botao clicaco
    document.getElementById("btn_"+especialidade).className = "btn_Espec btn btn-outline-dark text-light"

    // Definir Parametros
    var params = {
        especialidade: especialidade
    }
    
    // Realizar Ajax solicitando os dados
    $.ajax({
        type: 'POST',
        url: '/ColetarDados',
        data: params,
        dataType: 'json',
        error: function (request, status, error) {
            $('#Loading_Modal').modal('hide')
            $.notify('Erro ao executar esta ação', 'error')
            console.log(request)
            console.log(status)
            console.log(error)
        },
        success: function (results) {
            // Simplificar Resultado 
            console.log(results)
            dic_cockpit = results.results.dic_cockpit
            dic_sap = results.results.SAP
            dic_sort_tag = results.results.dic_sort_tag
            

            // Criar HTML com os Dados Preenchidos 
            CreateBoxUnidade(dic_cockpit, dic_sap, especialidade, dic_sort_tag)
            ActiveSelectStatus()
            
            

            // Finalizando Abrir Aba das Unidade, Fechar loading e Notificar Sucesso!
            $("#Aba_Unidades").show(1000)
            setTimeout(function(){
                // Minimizar loading
                $('#Loading_Modal').modal('hide')
                
                // Rodar todos os carroseis 
                var elms = document.getElementsByClassName( 'splide' );
                for (var i = 0; i < elms.length; i++){
                    // Configurar carroseis
                    new Splide( elms[ i ], {
                        perPage  : 3,
                        focus    : 'center',
                        // type   : 'loop',
                        pagination: true,
                        paginationDirection: 'ltr',
                    }).mount();
                }

                // Tela cheia das imagens 
                Fancybox.bind("[data-fancybox]", {  
                    Toolbar: {
                        display: {
                          left: ["infobar"],
                          middle: [
                            "zoomIn",
                            "zoomOut",
                            "toggle1to1",
                            "rotateCCW",
                            "rotateCW",
                            "flipX",
                            "flipY",
                            "slideshow", 
                            "thumbs",
                          ],
                        },
                      },
                    Images: {
                        zoom: true,
                    },
                });


            }, 1500)
            $.notify('Pagina Atualizada', 'success')
        }
    })
}


// Cria HTML das Unidades
dados_AlterarDetalhamento = {}
function CreateBoxUnidade(dic_cockpit, dic_sap, especialidade, dic_sort_tag){
    // Definindo variaveis
    document.getElementById("Aba_Unidades").innerHTML=''

    // Criar Vazio se for preciso
    if (especialidade == 'Sistemas'){}else{
        if ('Q4' in dic_cockpit){}else{CreateBoxUnidadeEmpty('Q4', dic_sap, especialidade)}
        if ('PE9' in dic_cockpit){}else{CreateBoxUnidadeEmpty('PE9', dic_sap, especialidade)}
        if ('PP5' in dic_cockpit){}else{CreateBoxUnidadeEmpty('PP5', dic_sap, especialidade)}
    }

    i = 0
    for(Unidade in dic_cockpit){
        // Utilizar para ordenar os tags  
        listas_tag_cod = dic_sort_tag[Unidade]

        // Code para localizar os dados_AlterarDetalhamento
        code_AlterarDetalhamento = 'Uni-'+Unidade+String(i)

        // Criando Var com todos od dados para o ModalAlterarDetalhamento
        dados_AlterarDetalhamento[code_AlterarDetalhamento] = {
            'data': Data_Now(), 
            'user':'', 
            'detalhamento':'', 
            'Ultima': true, 
            'mode':'New_TAG', 
            'id':'', 
            'criticidade':'Nivel 1', 
            'Status':'', 
            'index_list':'', 
            'unidade': Unidade, 
            'TAG':'', 
            'especialidade':especialidade,
            'conclucao_nota_SAP': '-',
            'nota_sap': '-',
        }
        
        document.getElementById("Aba_Unidades").innerHTML+= `
            <!-- `+Unidade+` -->
            <div class="row-12">
                <div class="col bloco mb-0">

                    <!-- Cabeçalho - `+Unidade+` -->
                    <div class="row border-b-detalhe-t">
                        
                        <!-- Titulo -->
                        <div class="col-3 px-3 titulo">`+Unidade+`</div>

                        <!-- Icones -->
                        `+CreateBoxIconTAGs(dic_cockpit, Unidade)+`
            
                        <!-- icon Adicionar TAG -->
                        <div class="col-1 xd ycentro px-3" style="width:50px" id="Exib_`+Unidade+`"
                            onclick="AbrirAlterarDetalhamento('`+code_AlterarDetalhamento+`')">
                            <i class="fa-solid fa-2x fa-square-plus color-detalhe"></i>
                        </div>

                        <!-- icon Exibir TAG's -->
                        <div class="col-1 xd ycentro px-3" style="width:50px" id="Exib_`+Unidade+`"
                            onclick="hide_show('.`+Unidade+`','#Exib_`+Unidade+`')">
                            <i class="fa-solid fa-2x fa-square-caret-down color-detalhe"></i>
                        </div>
            
                    </div>
            
                    <!-- Conteudo - TAGS -->
                    <div class="row `+Unidade+` mt-2" style="display: none;">
                        <div id="Conteudo_Tags_`+Unidade+`">
                            
                            `+CreateBoxTAG(dic_cockpit, Unidade, listas_tag_cod)+`

                            `+CreateBoxSAP(Unidade, dic_sap)+`

                        </div>
                    </div>
            
                </div>
            
            </div>`


        
        CreateTableSAP(Unidade, dic_sap)
        i += 1
        

    }

    

}

function CreateBoxUnidadeEmpty(Unidade, dic_sap, especialidade){

    // Code para localizar os dados_AlterarDetalhamento
    code_AlterarDetalhamento = 'Uni-'+Unidade+'Empty'

    // Criando Var com todos od dados para o ModalAlterarDetalhamento
    dados_AlterarDetalhamento[code_AlterarDetalhamento] = {
        'data': Data_Now(), 
        'user':'', 
        'detalhamento':'', 
        'Ultima': true, 
        'mode':'New_TAG', 
        'id':'', 
        'criticidade':'Nivel 1', 
        'Status':'', 
        'index_list':'', 
        'unidade': Unidade, 
        'TAG':'', 
        'especialidade':especialidade,
        'conclucao_nota_SAP': '-',
        'nota_sap': '-',
    }

    document.getElementById("Aba_Unidades").innerHTML+= `
        <!-- `+Unidade+` -->
        <div class="row-12">
            <div class="col bloco mb-0">

                <!-- Cabeçalho - `+Unidade+` -->
                <div class="row border-b-detalhe-t">
                    
                    <!-- Titulo -->
                    <div class="col-3 px-3 titulo">`+Unidade+`</div>

                    <!-- Icones -->
                    <div class="col ycentro"> 
                        <i title="Em Acompanhamento" class="fa-solid fa-eye"></i> <div class="px-2"> 0 </div> 
                        <i title="Realizando Estudos" class="fa-solid fa-book"></i> <div class="px-2"> 0 </div>
                        <i title="RCP Aberta" class="fa-solid fa-file-prescription"></i> <div class="px-2"> 0 </div>
                        <i title="Aguardando Detalhamento" class="fa-solid fa-clipboard-list"></i> <div class="px-2"> 0 </div>
                        <i title="Aguardando Execução" class="fa-solid fa-clipboard-check"></i> <div class="px-2"> 0 </div>
                        <i title="Manutenção Externa" class="fa-solid fa-truck"></i> <div class="px-2"> 0 </div>
                        <i title="Manutenção Interna" class="fa-solid fa-industry"></i> <div class="px-2"> 0 </div>
                        <i title="Testes Pós Execução" class="fa-solid fa-check-to-slot"></i> <div class="px-2"> 0 </div>
                    </div>
        
                    <!-- addUnidade -->
                    <div class="col-1 xd ycentro px-3" style="width:50px" id="Exib_`+Unidade+`"
                        onclick="AbrirAlterarDetalhamento('`+code_AlterarDetalhamento+`')">
                        <i class="fa-solid fa-2x fa-square-plus color-detalhe"></i>
                    </div>

                    <!-- icon Exibir TAG's -->
                    <div class="col-1 xd ycentro px-3" style="width:50px" id="Exib_`+Unidade+`"
                        onclick="hide_show('.`+Unidade+`','#Exib_`+Unidade+`')">
                        <i class="fa-solid fa-2x fa-square-caret-down color-detalhe"></i>
                    </div>
        
                </div>
        
                <!-- Conteudo - TAGS -->
                <div class="row `+Unidade+` mt-2" style="display: none;">
                    <div id="Conteudo_Tags_`+Unidade+`">

                        `+CreateBoxSAP(Unidade, dic_sap)+`

                    </div>
                </div>
        
            </div>
        
        </div>`


}

// Criar icones ao lado do title tags
function CreateBoxIconTAGs(dic_cockpit, Unidade){
    // Resetar Variaveis
    Em_Acompanhamento = 0
    Realizando_Estudos = 0
    RCP_Aberta = 0
    Aguardando_Detalhamento = 0
    Aguardando_Execução = 0
    Manutenção_Externa = 0
    Manutenção_Interna = 0
    Testes_Pós_Execução = 0
    
    for (id in dic_cockpit[Unidade]){
        // Contagem de Repetições
        switch (dic_cockpit[Unidade][id]['status']){
            case 'Em Acompanhamento': Em_Acompanhamento += 1 ; break
            case 'Realizando Estudos': Realizando_Estudos += 1 ; break
            case 'RCP Aberta': RCP_Aberta += 1 ; break
            case 'Aguardando Detalhamento': Aguardando_Detalhamento += 1 ; break
            case 'Aguardando Execução': Aguardando_Execução += 1 ; break
            case 'Manutenção Externa': Manutenção_Externa += 1 ; break
            case 'Manutenção Interna': Manutenção_Interna += 1 ; break
            case 'Testes Pós Execução': Testes_Pós_Execução += 1 ; break
        }
    }
    // Definição do texto html
    icones = `
    <div class="col ycentro"> 
        <i title="Em Acompanhamento" class="fa-solid fa-eye"></i> <div class="px-2">`+Em_Acompanhamento+`</div> 
        <i title="Realizando Estudos" class="fa-solid fa-book"></i> <div class="px-2">`+Realizando_Estudos+`</div>
        <i title="RCP Aberta" class="fa-solid fa-file-prescription"></i> <div class="px-2">`+RCP_Aberta+`</div>
        <i title="Aguardando Detalhamento" class="fa-solid fa-clipboard-list"></i> <div class="px-2">`+Aguardando_Detalhamento+`</div>
        <i title="Aguardando Execução" class="fa-solid fa-clipboard-check"></i> <div class="px-2">`+Aguardando_Execução+`</div>
        <i title="Manutenção Externa" class="fa-solid fa-truck"></i> <div class="px-2">`+Manutenção_Externa+`</div>
        <i title="Manutenção Interna" class="fa-solid fa-industry"></i> <div class="px-2">`+Manutenção_Interna+`</div>
        <i title="Testes Pós Execução" class="fa-solid fa-check-to-slot"></i> <div class="px-2">`+Testes_Pós_Execução+`</div>
    </div>`

    return icones
}

// Cria HTML dos Tags
function CreateBoxTAG(dic_cockpit, Unidade, listas_tag_cod){
    // Definir variaveis
    html_TAG = ''
    
    listas_tag_cod.forEach(lista_tag_cod =>{
        id = lista_tag_cod[1]
    
        // Resetar variavel p/ cada id
        Icone_status = ''
        color_status = ''

        // Verificar Criticidade
        switch (dic_cockpit[Unidade][id]['nivel_criticidade']) {
            case 'Nivel 3':  color_status = 'style="color: red; width: 20px"'  ;  break
            case 'Nivel 2':  color_status = 'style="color: orange; width: 20px"'  ;  break
            default:  color_status = 'style=" width: 20px"'  ;  break            
        }
        
        // Verificar Status
        switch (dic_cockpit[Unidade][id]['status']) {
            case 'Em Acompanhamento':  Icone_status = '<i class="fa-solid fa-eye" ' + color_status + '"></i>'; break
            case 'Realizando Estudos':  Icone_status = '<i class="fa-solid fa-book" ' + color_status + '"></i>'; break
            case 'RCP Aberta':  Icone_status = '<i class="fa-solid fa-file-prescription" ' + color_status + '"></i>'; break
            case 'Aguardando Detalhamento':  Icone_status = '<i class="fa-solid fa-clipboard-list" ' + color_status + '"></i>'; break
            case 'Aguardando Execução':  Icone_status = '<i class="fa-solid fa-clipboard-check" ' + color_status + '"></i>'; break
            case 'Manutenção Externa':  Icone_status = '<i class="fa-solid fa-truck" ' + color_status + '"></i>'; break
            case 'Manutenção Interna':  Icone_status = '<i class="fa-solid fa-industry" ' + color_status + '"></i>'; break
            case 'Testes Pós Execução':  Icone_status = '<i class="fa-solid fa-check-to-slot" ' + color_status + '"></i>'; break
            default:  Icone_status = '<i class="fa-regular fa-circle-question" ' + color_status + '"></i>'; break
        }

        // Verificar Status Nota SAP
        // Coletar Variavel 
        var conclucao_nota_SAP = dic_cockpit[Unidade][id]['conclucao_nota_SAP']

        // Existe nota ?
        if(conclucao_nota_SAP != '-'){
            // Se Sim, Ela esta em Dia?
            if(new Date() < new Date(conclucao_nota_SAP)){
                Icone_status_nota = '<i title="Nota SAP em Dia! ('+dic_cockpit[Unidade][id]['nota_sap']+')" class="fa-solid fa-calendar-check" style="width: 20px"></i>'
            }
            // Caso Exista Porem esteja Atrasada
            else{
                Icone_status_nota = '<i title="Nota SAP Atrasada! ('+dic_cockpit[Unidade][id]['nota_sap']+')" class="fa-solid fa-calendar-xmark" style="color: red; width: 20px"></i>'
            }
        }
        // Caso Não exista nota associada
        else{
            Icone_status_nota = '<i title="Nenhuma Nota SAP Associada! ('+dic_cockpit[Unidade][id]['nota_sap']+')" class="fa-solid fa-question" style="color: orange; width: 20px"></i>'
        }
        

        tag = dic_cockpit[Unidade][id]['tag']

        html_TAG += `

        <!-- `+tag+` -->                    
        <div class="row ps-3">
            
            <!-- Botão Exibir Detalhes -->
            <div class="col-1 xcentro" style="width:50px" id="Exib_`+id+`"
            onclick="hide_show('#`+id+`','#Exib_`+id+`')">
                <i class="fa-solid fa-2x fa-square-caret-down color-detalhe"></i>
            </div>
    
            <!-- Title -->
            <div class="col-3 mx-1 mb-2"><b class="px-1">`+tag+`</b></div>
    
            <!-- Data -->
            <div class="col-2 mx-1 mb-2"><b class="px-1">`+dic_cockpit[Unidade][id]['data_atualizada']+`</b></div>

            <!-- Icones Nota SAP -->
            <div class="col-1"> 
                <div class="row">
                    <div class="col-2 xcentro ycentro">`+Icone_status_nota+`</div>
                </div>
            </div>
    
            <!-- Icones -->
            <div class="col"> 
                <div class="row">
                    <div class="col-1 xcentro ycentro">`+Icone_status+`</div>
                    <div class="col ycentro"><text> `+dic_cockpit[Unidade][id]['status']+` </text></div>
                </div>
            </div>
    
            <!-- Conteudo -->
            <div class="row px-2 ps-3">
    
                <!-- Body -->
                <div id="`+id+`" class="row mb-3" style="display: none;">
    
                    <!-- Texto -->
                    <div class="row my-2">
                        <div class="p-1 subtexto2 px-3" style="background-color:rgb(20, 20, 20);border-radius: 20px;"> 
    
                            `+CreateBoxDetalhamento(dic_cockpit, Unidade, id)+`
                            
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        `
    })
    return html_TAG

}

// Cria HTML dos Detalhamentos
function CreateBoxDetalhamento(dic_cockpit, Unidade, id) {
    
    // Definido Variaveis
    detalhamentos =  dic_cockpit[Unidade][id]
    nivel_criticidade = detalhamentos['nivel_criticidade']
    Status = detalhamentos['status']
    detalhamentos_data =  detalhamentos['detalhamentos_data']
    detalhamentos_user =  detalhamentos['detalhamentos_user']
    detalhamento =  detalhamentos['detalhamentos']
    especialidade = detalhamentos['especialidade']
    

    // Crinaod html vazio
    html_Detalhamento = ''

    // Iniciando for 
    detalhamentos_data.forEach(function (value, i) {
        

        // Definindo Se é o Ultimo 
        Ultima = detalhamentos_data.length == i+1 | detalhamentos_data.length == 0 

        // Code para localizar os dados_AlterarDetalhamento
        code_AlterarDetalhamento = 'Uni-'+Unidade+'id'+id+'Detal'+String(i)+'Edit'

        // Criando Var com todos od dados para o ModalAlterarDetalhamento
        dados_AlterarDetalhamento[code_AlterarDetalhamento] = {
            'data': detalhamentos_data[i], 
            'user': detalhamentos_user[i], 
            'detalhamento': detalhamento[i].replace(/\\n/g, '\\n'), 
            'Ultima': Ultima, 
            'mode':'Edit', 
            'id': id, 
            'criticidade': nivel_criticidade, 
            'Status': Status, 
            'index_list': i, 
            'unidade': Unidade, 
            'TAG': detalhamentos['tag'], 
            'especialidade':especialidade,
            'conclucao_nota_SAP': detalhamentos['conclucao_nota_SAP'],
            'nota_sap': detalhamentos['nota_sap'],
        }

        // Escrevendo html
        html_Detalhamento +=`

        <div class="row hoverDestaque border-b-detalhe-t py-2">
        <div class="col-2">
            <div class="row xcentro">`+detalhamentos_data[i]+`</div>
            <div class="row xcentro">`+detalhamentos_user[i]+`</div>
        </div>
        <div class="col ycentro">`+detalhamento[i].replace(/\\n/g, '<br>')+`</div>
    
        <div class="col-1 xcentro ycentro" style="width:50px" onclick="AbrirAlterarDetalhamento('`+code_AlterarDetalhamento+`')">
            <i class="fa-regular fa-2x fa-pen-to-square color-detalhe"></i>
        </div>
    
    </div>
        `
    })

    // Botão para criar nova linha 
    // Definindo variavel
    // Code para localizar os dados_AlterarDetalhamento
    code_AlterarDetalhamento = 'Uni-'+Unidade+'id'+id+'Detal'+String(i)+'New'

    // Criando Var com todos od dados para o ModalAlterarDetalhamento
    dados_AlterarDetalhamento[code_AlterarDetalhamento] = {
        'data': Data_Now(), 
        'user': '', 
        'detalhamento': '', 
        'Ultima': true, 
        'mode':'New_detalhamento', 
        'id': id, 
        'criticidade': 'Nivel 1', 
        'Status': '', 
        'index_list': '', 
        'unidade': Unidade, 
        'TAG': detalhamentos['tag'], 
        'especialidade':especialidade ,
        'conclucao_nota_SAP': detalhamentos['conclucao_nota_SAP'],
        'nota_sap': detalhamentos['nota_sap'],
    }
    
    // Criando HTML
    html_Detalhamento +=`<!-- Botões e input -->
    <div class="row p-2">
        
        <!-- Box imagens -->
        `+CreateBoxImagens(dic_cockpit, Unidade, id)+`
         

        <!-- Botões -->
        <div class="row m-1 pt-2">

            <!-- Adicionar Linha --> 
            <div class="col ">
                <div class="row">
                    <button onclick="AbrirAlterarDetalhamento('`+code_AlterarDetalhamento+`')" type="button" title="Atualizar"
                    class="btn btn-outline-dark border-detalhe text-light">
                        Adicionar nova Linha
                    </button>
                </div>
            </div>

            <!-- Adicionar Imagem --> 
            <div class="col ">
                <div class="row">
                    <button onclick="uploadIMG('`+code_AlterarDetalhamento+`')" type="button" title="Atualizar"
                    class="btn btn-outline-dark border-detalhe text-light">
                        Adicionar Imagem
                    </button>
                </div>
            </div>
            
        </div>
    </div>`

    return html_Detalhamento
    
}

function CreateBoxImagens(dic_cockpit, Unidade, id){
    // Coletar Lista de imagens 
    lista_img = dic_cockpit[Unidade][id]['img']

    // Caso tenha Itens na lista
    if(lista_img[0] == 'vazio.png'){return ''}
        
    // Criar slides das Imagens 
    html_imagens = ''
    
    //data-caption="Texto Aleatorio"
    lista_img.forEach(img => {html_imagens += `
        <li class="splide__slide">
            <a 
                data-fancybox
                data-src="../static/img/RelatorioCGA/`+img+`"
                
                data-width="6096" 
                data-height="2730"
                >

                <img src="../static/img/RelatorioCGA/`+img+`" alt="" height="140" width="200" style="display: block; margin-left: auto; margin-right: auto;">

            </a>
        </li>`}
    )

    
    // criar carrosel e inserir as imagens 
    html_Carrosel = `
    <div class="row m-1 pt-2" style="height:180px">            
        <section class="splide" aria - label="My Awesome Gallery" >
            <div class="splide__track">
                <ul class="splide__list">
                    `+html_imagens+`
                </ul>
            </div>
        </section >
    </div>`


    return html_Carrosel

}

// Cria HTML e javascript da Tabela SAP
function CreateBoxSAP(Unidade, dic_sap){
    // Definir Variaveis
    sap_html = ''
    data_sap = dic_sap.Data_Get_SAP
    dados_SAP =  dic_sap.dic_SAP
    dic_indicador = dic_sap.dic_indicador[Unidade]
    
    if(dic_indicador == undefined){
        dic_indicador = {
            'total': 0,
            'abertas': 0,
            'vencidas': 0
        }        
    }

    
    sap_html = `
    <!-- SAP -->                    
    <div class="row ps-3">
        
        <!-- Botão Exibir Detalhes -->
        <div class="col-1 xcentro" style="width:50px" id="Exib_SAP_`+Unidade+`"
        onclick="hide_show('#SAP_`+Unidade+`','#Exib_SAP_`+Unidade+`')">
            <i class="fa-solid fa-2x fa-square-caret-down color-detalhe"></i>
        </div>

        <!-- Title -->
        <div class="col-3 mx-1 mb-2"><b class="px-1">SAP</b></div>

        <!-- Data -->
        <div class="col-2 mx-1 mb-2"><b class="px-1">`+data_sap.slice(0, -3)+`</b></div>

        <!-- Icones -->
        <div class="col"> 
            <i title="Total Notas Abertas" class="px-2 fa-solid fa-door-open"> `+dic_indicador['total']+`</i>
            <i title="Notas não Vencidas" class="px-2 fa-solid fa-calendar-check"> `+dic_indicador['abertas']+`</i>
            <i title="Notas Vencidas" class="px-2 fa-solid fa-calendar-xmark"> `+dic_indicador['vencidas']+`</i>
        </div>

        <!-- Conteudo -->
        <div class="row px-2 ps-3">

            <!-- Body -->
            <div id="SAP_`+Unidade+`" class="row mb-3" style="display: none;">

                <!-- Texto -->
                <div class="row my-2">

                    <div id="TableSAP_`+Unidade+`">
                        <!-- Javascript Escreve aqui -->
                    </div>

                </div>
                

            </div>

        </div>

    </div>`
   
    return sap_html
}

// Criar tabela do SAP
function CreateTableSAP(Unidade, dic_sap){
    // Esperar um tempo p/ criar as tabelas 
    setTimeout(() => {

    data_sap = dic_sap.Data_Get_SAP
    dados_SAP =  dic_sap.dic_SAP
        
    // Criar menu 
    var headerMenu = function(){
        var menu = [];
        var columns = this.getColumns();
    
        for(let column of columns){
    
            //create checkbox element using font awesome icons
            let icon = document.createElement("i");
            icon.classList.add("fas");
            icon.classList.add(column.isVisible() ? "fa-check-square" : "fa-square");
    
            //build label
            let label = document.createElement("span");
            let title = document.createElement("span");
    
            title.textContent = " " + column.getDefinition().title;
    
            label.appendChild(icon);
            label.appendChild(title);
    
            //create menu item
            menu.push({
                label:label,
                action:function(e){
                    //prevent menu closing
                    e.stopPropagation();
    
                    //toggle current column visibility
                    column.toggle();
    
                    //change menu item icon
                    if(column.isVisible()){
                        icon.classList.remove("fa-square");
                        icon.classList.add("fa-check-square");
                    }else{
                        icon.classList.remove("fa-check-square");
                        icon.classList.add("fa-square");
                    }
                }
            });
        }
    
        return menu;
    };

    // Configurar Tabela
    window["table_" + Unidade] = new Tabulator("#TableSAP_"+Unidade, {
        
        data: dados_SAP,
        movableColumns: true,

        columns:[

            {field: 'Nota', title: 'Nota', headerFilter:"input", visible:true, headerMenu: headerMenu, tooltip: true,},
            {field: 'TAG SAP', title: 'TAG', headerFilter:"input", visible:true, headerMenu: headerMenu, tooltip: true,},
            {field: 'Descricao Curta', title: 'Descricao Curta', headerFilter:"input", visible:true, headerMenu: headerMenu, tooltip: true,},
            {field: 'Conclusao Desejada', title: 'Conclusao Desejada', headerFilter:"input", visible:true, headerMenu: headerMenu, tooltip: true, sorter:"date", sorterParams:{format:"dd.MM.yyyy"}},
            {field: 'Vencida', title: 'Vencida', headerFilter:"input", visible:true, headerMenu: headerMenu, tooltip: true,},
            {field: 'Status Sistema', title: 'Status Sistema', headerFilter:"input", visible:true, headerMenu: headerMenu, tooltip: true,},
            {field: 'Criador', title: 'Criador', headerFilter:"input", visible:true, headerMenu: headerMenu, tooltip: true,},
            {field: 'status_cockpit', title: 'status_cockpit', headerFilter:"input", visible:true, headerMenu: headerMenu, tooltip: true,},
            
            
            {field: 'Ordem', title: 'Ordem', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
            {field:"Data Nota", title:"Data Nota", headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
            {field: 'Descricao Longa', title: 'Descricao Longa', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
            {field: 'TP', title: 'TP', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
            {field: 'Prioridade', title: 'Prioridade', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
            {field: 'Notificador', title: 'Notificador', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
            {field: 'A', title: 'A', headerFilter:"input", visible:false,},
            {field: 'Centro de Trabalho', title: 'Centro de Trabalho', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
            {field: 'Fim avaria', title: 'Fim avaria', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true, sorter:"date", sorterParams:{format:"dd.MM.yyyy"}},
            {field: 'Falha', title: 'Falha', headerFilter:"select", headerFilterParams: {value:" X",multiSelect: true }, visible:false, headerMenu: headerMenu, tooltip: true,},
            {field: 'Status Usuario', title: 'Status Usuario', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
            {field: 'GPM', title: 'GPM', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
            {field: 'Campo ordenação', title: 'Campo ordenação', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
            {field: 'Unidade', title: 'Unidade', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
        ], 

        pagination:"local",
        paginationSize:5,
        paginationSizeSelector:[5, 10, 25, 50, 100],
        paginationCounter:"rows",
        resizableColumnFit:true,
        layout: "fitDataTable",//"fitColumns",//

        // Formatar Linhas
        rowFormatter:function(row){
            if(row.getData().status_cockpit == "-"){ // ficar laranja se n tiver associado
                row.getElement().style.backgroundColor = "rgb(89,61,7)";
            } // caso esteja associado remover cursor clicavel
            else{row.getElement().style.cursor = "default";}
        },       

    })

    window["table_" + Unidade].setFilter('Unidade', "=", Unidade);

    window["table_" + Unidade].on("rowClick", function(e, row){      
        if(row.getData().status_cockpit != "-"){}
        else{
            user = ''
            switch(row.getData().Criador){
                case 'GABRIH02': user = '' ;break
                case 'ALEXRO17': user = ''  ;break
                case 'MARCEB58': user = ''  ;break
                case 'WELLSA10': user = ''  ;break
                case 'PAULRU01': user = 'Paulo Rumao'  ;break
                case 'MARCED32': user = 'Kelvis'  ;break
                case 'MARCOB31': user = ''  ;break
                case 'ANAILA01': user = 'Anailton'  ;break
                case 'MARCID13': user = 'Marcio'  ;break
                case 'FLAVIB11': user = 'Flavio'  ;break
                case 'LEONAP20': user = 'Paganine'  ;break
                case 'RONILB01': user = ''  ;break
                case 'FELIPS24': user = ''  ;break
                case 'KELVIF01': user = 'Kelvis'  ;break
                default: user = ''  ;break
                // Marcio | Kelvis | Paganine | Flavio | João | Anailton | Natalia | David | Paulo Rumao | Outros

            }
            console.log(row.getData().Criador)
            console.log(user)


            dados_AlterarDetalhamento['Criar_Base_SAP'] = {
                'data': Data_Now(), 
                'user': user, 
                'detalhamento': row.getData()['Descricao Longa'], 
                'Ultima': true, 
                'mode':'New_TAG', 
                'id':'', 
                'criticidade':'Nivel 1', 
                'Status':'RCP Aberta', 
                'index_list':'', 
                'unidade': Unidade, 
                'TAG': row.getData()['TAG SAP'], 
                'especialidade': especialidade,
                'conclucao_nota_SAP': '-',
                'nota_sap': row.getData()['Nota'],
            }
            console.log(especialidade)
            AbrirAlterarDetalhamento('Criar_Base_SAP')
        }
    })

    }, 3000);


}


// ------------------------------------------------------ Função Alterar Detalhamentos
// Ativa Os Selected 
function ActiveSelectStatus(){
    //Iniciar Virtual Select
    VirtualSelect.init({
        ele: '.VirtualSelect',
        multiple: 'true',
        search: 'true',
        selectAllOnlyVisible: 'true',
        hideValueTooltipOnSelectAll: 'true'
    })
}

// Abrir Modal de alteração dos detalhemntso
function AbrirAlterarDetalhamento(code_AlterarDetalhamento){
    // Criar os dados do Detalhamento
    console.log(dados_AlterarDetalhamento[code_AlterarDetalhamento])
    dic_AlterarDetalhamento = dados_AlterarDetalhamento[code_AlterarDetalhamento]
    // Configurar Modal

    // Se for modo de edição
    if(dic_AlterarDetalhamento.mode=='Edit'){
        // Definir textos
        Title_Mod = "Editando um Detalhamento"
        SaveButton_Text = "Salvando Alteração"

        // Desabilitar elementos 
        document.getElementById("AlterarInputTAG").disabled = true
    } 
    
    // Se for modo de criar um novo detalhamento
    if(dic_AlterarDetalhamento.mode=='New_detalhamento'){
        // Definir textos
        Title_Mod = "Criando um novo Detalhamento"
        SaveButton_Text = "Criar Novo Detalhamento"

        // Desabilitar Inputs
        document.getElementById("AlterarInputTAG").disabled = true
        document.getElementById("AlterarButaoConcluido").disabled = false
    }

    // Se for Novo TAG
    if(dic_AlterarDetalhamento.mode=='New_TAG'){
        // Definir textos
        Title_Mod = "Criando um novo TAG"
        SaveButton_Text = "Novo TAG"

        // Desabilitar Inputs
        document.getElementById("AlterarInputTAG").disabled = false
        document.getElementById("AlterarButaoConcluido").disabled = true

    }
    
    // Se for o Ultimo detalhamento da TAG
    if(dic_AlterarDetalhamento.Ultima == true){
        // Habilitar Inputs
        document.getElementById("AlterarInputStatus").disabled = false
        document.getElementById("AlterarInputCriticidade").disabled = false
        document.getElementById("AlterarButaoConcluido").disabled = false;
        document.getElementById("AlterarInputTAG").disabled = false
        if(dic_AlterarDetalhamento.mode == 'New_TAG'){
            document.getElementById("AlterarButaoConcluido").disabled = true;
        }

    }
    
    // Se nao for o ultimo detalhamento
    else{
        // Desabilitar elementos 
        document.getElementById("AlterarInputStatus").disabled = true
        document.getElementById("AlterarInputCriticidade").disabled = true
        document.getElementById("AlterarButaoConcluido").disabled = true;
    }

    
    // Head Modal
    $("#Alterar_Detalhamento_title_Mod").text(Title_Mod)
    
    // Body Modal
    $("#AlterarInputTAG").val(dic_AlterarDetalhamento.TAG)
    $("#AlterarInputData").val(Data_To_DataSelect(dic_AlterarDetalhamento.data))
    $("#AlterarInputUser").val(dic_AlterarDetalhamento.user)
    $("#AlterarInputCriticidade").val(dic_AlterarDetalhamento.criticidade)
    $("#AlterarInputStatus").val(dic_AlterarDetalhamento.Status)
    $("#AlterarInputDetalhamento").val(dic_AlterarDetalhamento.detalhamento)
    $("#AlterarInputNotaSAP").val(dic_AlterarDetalhamento.nota_sap)

    // Footer Modal
    $("#AlterarButaoAlterar").text(SaveButton_Text)

    // Passar informações para o Botão de Alterar 
    document.getElementById("AlterarButaoAlterar").setAttribute(`onclick`,`SolicitarAlteracao('`+code_AlterarDetalhamento+`')`)

    document.getElementById("AlterarButaoConcluido").setAttribute(`onclick`,`SolicitarAlteracao('`+code_AlterarDetalhamento+`',true)`)


    // Exibir Modal
    $("#Alterar_Detalhamento").modal('show')
}

// Solicitar alteracao na planilha
function SolicitarAlteracao(code_AlterarDetalhamento, concluir=false){
    dic_AlterarDetalhamento = dados_AlterarDetalhamento[code_AlterarDetalhamento]


    // Verificar se todos os inputs estão preenchidos 
    if($("#AlterarInputTAG").val() == null){return alert("Preencher Todos os Campos")}
    if($("#AlterarInputData").val() == null){return alert("Preencher Todos os Campos")}
    if($("#AlterarInputUser").val() == null){return alert("Preencher Todos os Campos")}
    if($("#AlterarInputCriticidade").val() == null){return alert("Preencher Todos os Campos")}
    if($("#AlterarInputStatus").val() == null){return alert("Preencher Todos os Campos")}
    if($("#AlterarInputDetalhamento").val() == null || $("#AlterarInputDetalhamento").val() == ''){return alert("Preencher Todos os Campos")}

    // Tratar Campo Nota
    // Remove espaço, Se tiver Vazio Preencher com '-'
    valor_AlterarInputNotaSAP = $("#AlterarInputNotaSAP").val().replace(' ','')

    if( valor_AlterarInputNotaSAP == null || 
        valor_AlterarInputNotaSAP == undefined ||
        valor_AlterarInputNotaSAP == '' ||
        valor_AlterarInputNotaSAP == '-'){ valor_AlterarInputNotaSAP = '-'}
    
    // Se nao tiver vazio e oq tiver preenchido nao for '-', verificar se é um valor valido?
    else{ 
        if(!/^[0-9]{11}/.test(valor_AlterarInputNotaSAP)){
            return alert("O numero da Nota SAP deve conter 11 caracteres Numericos")
        }
    }
    // Preencher campo com o valor tratado 
    $("#AlterarInputNotaSAP").val(valor_AlterarInputNotaSAP)

    // Exibir Loading, ocultar Detalhamento
    $('#Loading_Modal').modal('show')
    $("#Alterar_Detalhamento").modal('hide')

    
    id_index_SolAlt = dic_AlterarDetalhamento.id
    // Parametros
    params = {
        'Data': $("#AlterarInputData").val(),
        'Usuario': $("#AlterarInputUser").val(),
        'Detalhamento': $("#AlterarInputDetalhamento").val().replace(/\r?\n/g, '\\n').replace(/&/g, 'e'),
        'Criticidade': $("#AlterarInputCriticidade").val(),
        'Status': $("#AlterarInputStatus").val(),
        'Concluir': concluir,
        'id': dic_AlterarDetalhamento.id,
        'index_list': dic_AlterarDetalhamento.index_list,
        'mode': dic_AlterarDetalhamento.mode,
        'unidade': dic_AlterarDetalhamento.unidade,
        'TAG': $("#AlterarInputTAG").val(),
        'especialidade': dic_AlterarDetalhamento.especialidade,
        'nota_sap': valor_AlterarInputNotaSAP,
    }
    
    // Solicitar Alteracao
    $.ajax({
        type: 'POST',
        url: '/SolicitarAlteracao',
        data: params,
        dataType: 'json',
        error: function (request, status, error) {
            $.notify('Erro ao executar esta ação', 'error')
            console.log(request)
            console.log(status)
            console.log(error)
        },
        success: function (results) {
            retorno = results.results
            console.log(retorno)
            if(retorno[0] == 'Error'){alert(retorno[1])}
            // Simplificar Resultado 
            ColetarDados(dic_AlterarDetalhamento.especialidade)
            setTimeout(() => {
                
                hide_show("."+dic_AlterarDetalhamento.unidade,"#Exib_"+dic_AlterarDetalhamento.unidade,0)
                hide_show("#"+id_index_SolAlt,"#Exib_"+id_index_SolAlt,0)
                document.getElementById("Exib_"+id_index_SolAlt).scrollIntoView()
                $('#Loading_Modal').modal('hide')
            }, 1500);
              
        }
    })





    
}

// ------------------------------------------------------ Função PDF
function OpenExportPDF(){
    if(!document.querySelector("#Export_pdf_unidade").isAllSelected()){
        document.querySelector("#Export_pdf_unidade").toggleSelectAll()
    }
    if(!document.querySelector("#Export_pdf_especialidade").isAllSelected()){
        document.querySelector("#Export_pdf_especialidade").toggleSelectAll()
    }
    if(!document.querySelector("#Export_pdf_criticidade").isAllSelected()){
        document.querySelector("#Export_pdf_criticidade").toggleSelectAll()
    }

    $("#Export_pdf_data_abertura_init").val('2020-01-01T01:00')
    $("#Export_pdf_data_abertura_fim").val('2030-01-01T00:00')
    $("#Modal_Export_pdf").modal('show')
}


function CreateReport(){
    // Parametros com base nos inputs
    params = {
        'Export_pdf_unidade': $("#Export_pdf_unidade").val(), 
        'Export_pdf_especialidade': $("#Export_pdf_especialidade").val(), 
        'Export_pdf_criticidade': $("#Export_pdf_criticidade").val(), 
        'Export_pdf_data_abertura_init': $("#Export_pdf_data_abertura_init").val(), 
        'Export_pdf_data_abertura_fim': $("#Export_pdf_data_abertura_fim").val(), 
    }
    // Solicitar Alteracao
    $.ajax({    
        type: 'POST',
        url: '/CreateReport',
        data: params,
        dataType: 'native',
        xhrFields: {
            responseType: 'blob'
        },
        error: function (request, status, error) {
            $.notify('Erro ao executar esta ação', 'error')
            console.log(request)
            console.log(status)
            console.log(error)
        },
        success: function(blob){
            var link=document.createElement('a');
            link.href=window.URL.createObjectURL(blob);
            link.download="Relatorio CGA.pdf";
            link.click();
            $("#Modal_Export_pdf").modal('hide')
            $.notify('Relatorio Exportado', "success")
        }
    })
}

function uploadIMG(code_AlterarDetalhamento){
    document.getElementById("enviarArquivos").setAttribute(`onclick`,`Send_uploadIMG('`+code_AlterarDetalhamento+`')`)
    $("#Modal_uploadIMG").modal('show')
}

  
// Drop Zone
Dropzone.options.dropzoneArea = {
    url: "/upload", // Substitua pela rota de upload no servidor
    acceptedFiles: ".jpg, .jpeg, .png",
    addRemoveLinks: true,
    autoProcessQueue: false, // Desativa o envio automático dos arquivos
};

// Evento para colar a imagem na área de texto e adicionar como arquivo no Dropzone
document.getElementById('imagemUrl').addEventListener('paste', function(event) {
    const clipboardData = event.clipboardData || window.clipboardData;
    const items = clipboardData.items;
  
    for (const item of items) {
      if (item.kind === "file" && item.type.includes("image")) {
        const blob = item.getAsFile();
        const imageName = moment().format('YYYYMMDD-hhmmssSSS')+".png";
        const file = new File([blob], imageName, { type: "image/png" });
  
        const dropzoneInstance = Dropzone.forElement("#dropzoneArea");
        dropzoneInstance.addFile(file);
  
        break;
      }
    }
});
  
// Evento do botão para enviar os arquivos do Dropzone via Ajax
function Send_uploadIMG(code_AlterarDetalhamento){
    // Definir Variavel que contem os files
    const dropzoneInstance = Dropzone.forElement("#dropzoneArea");

    // Verificar Se possui arquivo
    if (dropzoneInstance.files.length == 0){return alert("Insire uma Imagem")}

    // Criar Variavel FormData
    const formData = new FormData();
    // Informar id
    id_Index_CGA = dados_AlterarDetalhamento[code_AlterarDetalhamento]['id']
    console.log(id_Index_CGA)
    formData.append('id', id_Index_CGA)
    // Passar file
    dropzoneInstance.files.forEach(function(file) {
      formData.append('files', file);
    });
  
    $.ajax({
      type: 'POST',
      url: '/uploadImg',
      data: formData,
      processData: false, // Evita que o jQuery processe o FormData
      contentType: false, // Evita que o jQuery defina o Content-Type
      error: function(request, status, error) {
        $.notify('Erro ao executar esta ação', 'error');
        console.log(request);
        console.log(status);
        console.log(error);
      },
      success: function(result) {
        result = result.results
    
        if (result[0]=='ERRO'){
            console.log(result[1])
            $.notify('Erro ao executar esta ação', 'error');
        }else{
            console.log(result[1])
            $("#Modal_uploadIMG").modal('hide');
            $.notify('Imagem Inserida com Sucesso', "success");

            // Coletar para abrir aba novamente
            especialidade = dados_AlterarDetalhamento[code_AlterarDetalhamento]['especialidade']
            unidade = dados_AlterarDetalhamento[code_AlterarDetalhamento]['unidade']

            // Recarregar pagina abrindo local correto
            ColetarDados(especialidade)
                setTimeout(() => {
                    hide_show("."+unidade,"#Exib_"+unidade,0)
                    hide_show("#"+id_Index_CGA,"#Exib_"+id_Index_CGA,0)
                    document.getElementById("Exib_"+id_Index_CGA).scrollIntoView()
                    $('#Loading_Modal').modal('hide')
                }, 2000);
        }

        






        
      }
    });
  
    // Limpar os arquivos do Dropzone após o envio
    dropzoneInstance.removeAllFiles();
}

// ------------------------------------------------------ Função simples
function Data_To_DataSelect(date){
    // Transformar string dd/mm/aa hh:mm em MM/DD/YYYY HH:MM
    var dateParts = date.split(/[\/ :]/)
    dateFormat = dateParts[2] + '-' + dateParts[1] + '-' + dateParts[0] + 'T' + dateParts[3] + ':' + dateParts[4]
    
    return dateFormat
}

function Data_Now(){return moment().format('DD/MM/YYYY hh:mm')}
