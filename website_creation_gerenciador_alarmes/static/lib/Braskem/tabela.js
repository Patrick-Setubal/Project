// Variaveis
// colunas do SAP
Var_Col_SAP = ['TAG SAP', 'Data Nota', 'Nota', 'Ordem', 'Descricao Curta',
'Descricao Longa', 'Criador', 'TP', 'Prioridade', 'A',
'Centro de Trabalho', 'Fim avaria', 'Conclusao Desejada', 'Falha',
'Status Usuario', 'Status Sistema', 'Notificador', 'Campo ordenação',
'GPM']

$(document).ready(function(){

    login('sim')

    //Iniciar Virtual Select
    VirtualSelect.init({
        ele: '.VirtualSelect',
        multiple:"true", search: "true",
        selectAllOnlyVisible: "true",
        hideValueTooltipOnSelectAll: 'true',
    });

    //Crinando Lista e selecionando o Select Especialidades
    var SelecOptions= ['Rotativos','Elétricos','Instrumentos','Estáticos','Automação']
    document.querySelector('#Filtro_Especialidade').setOptions(SelecOptions)
    document.querySelector('#Filtro_Especialidade').toggleSelectAll()


    //Crinando Lista e selecionando o Select Niveis
    var SelecOptions= ['Silenciado','Normal','Nivel 1','Nivel 2','Nivel 3']
    document.querySelector('#Filtro_Nivel_do_Alarme').setOptions(SelecOptions)
    document.querySelector('#Filtro_Nivel_do_Alarme').toggleSelectAll()

    
    //Crinando Lista e selecionando o Select Sistemas
    var SelecOptions= ["Todos"]
    document.querySelector('#Filtro_Sistema').setOptions(SelecOptions)
    document.querySelector('#Filtro_Sistema').toggleSelectAll()
   
    
    $(".arrastar").draggable({ handle:'.modal-header'})

    $('#tabela_tags').hide()
    $('.Login-Hide').hide()
    $('#filtro-DataInicial').val(dataAtualFormatada(364)),
    $('#filtro-DataFinal').val(dataAtualFormatada(-364)),


    Filtro_Post(false,"Sim")

});


// Cria um objeto URLSearchParams a partir da string de consulta da URL
URLparams = new URLSearchParams(window.location.search);
// URL
function AtualizandoUrlFiltros(){
    opcoes = ['Filtro_Especialidade','Filtro_Sistema','Filtro_Nivel_do_Alarme','Filtro_Modo_de_falha','Filtro_TAG']
    opcoes.forEach(filtro => {
        URLparams.set(filtro, $('#'+filtro).val())
    })
    window.history.replaceState({}, '', `${window.location.pathname}?${URLparams.toString()}`)
}


//////////////////////// Resetar Pagina a cada x Minutos //////////////////////////////////
var idleTime = 0;
$(document).ready(function () {
    //Increment the idle time counter every minute.
    var idleInterval = setInterval(timerIncrement, 60000); // 1 minute = 60 000

    //Zero the idle timer on mouse movement.
    $(this).mousemove(function (e) {
        idleTime = 0;
    });
    $(this).keypress(function (e) {
        idleTime = 0;
    });
});

function timerIncrement() {
    idleTime = idleTime + 1;
    if (idleTime > 3) { // x minutes
            $.notify("Pag. Atualizando Automaticamente", "success");
            Filtro_Post(false);
            idleTime = 0
    }
};

///////////////////////////    INTERAÇÃO COM O SERVIDOR     ///////////////////////////////

// Atualizar todos os alarmes e exportar excel se for solicitado
function Filtro_Post(Exportar_Excel,Direto_URL = 'Nao'){

    if(Direto_URL=="Nao"){
        // Caso vazio Selecionar com "Todos"
        if($('#Filtro_Especialidade').val()[0] == undefined){
            document.querySelector('#Filtro_Especialidade').toggleSelectAll();}

        if($('#Filtro_Sistema').val()[0] == undefined){
            document.querySelector('#Filtro_Sistema').toggleSelectAll();}

        if($('#Filtro_Nivel_do_Alarme').val()[0] == undefined){
            document.querySelector('#Filtro_Nivel_do_Alarme').toggleSelectAll();}
        
        AtualizandoUrlFiltros()
    }


    $('#Loading_Modal').modal('show')
    resetdragg()
    
    if( URLparams.get('Filtro_Especialidade')==null){
        Filtro_Especialidade = '';
        document.querySelector('#Filtro_Especialidade').toggleSelectAll()
        document.querySelector('#Filtro_Especialidade').toggleSelectAll()
    } 
    else{Filtro_Especialidade = URLparams.get('Filtro_Especialidade').split(',')}
    
    if( URLparams.get('Filtro_Sistema')==null){
        Filtro_Sistema = ''
        document.querySelector('#Filtro_Sistema').toggleSelectAll()
        document.querySelector('#Filtro_Sistema').toggleSelectAll()
    }
    else{Filtro_Sistema = URLparams.get('Filtro_Sistema').split(',')}

    if( URLparams.get('Filtro_Nivel_do_Alarme')==null){
        Filtro_Nivel_do_Alarme = ''
        document.querySelector('#Filtro_Nivel_do_Alarme').toggleSelectAll()
        document.querySelector('#Filtro_Nivel_do_Alarme').toggleSelectAll()
    }
    else{Filtro_Nivel_do_Alarme = URLparams.get('Filtro_Nivel_do_Alarme').split(',')}

    if( URLparams.get('Filtro_Modo_de_falha')==null)  {Filtro_Modo_de_falha = ''}
    else{Filtro_Modo_de_falha = URLparams.get('Filtro_Modo_de_falha')}

    if( URLparams.get('Filtro_TAG')==null)  {Filtro_TAG = ''}
    else{Filtro_TAG = URLparams.get('Filtro_TAG')}

    var params = {
    "NumeroLog": $('#filtro-NumeroLogs').val(),
    "PaginaLog": $('#PaginacaoTabela_Input').text(),
    "DataInicial": $('#filtro-DataInicial').val(),
    "DataFinal": $('#filtro-DataFinal').val(),
    "Especialidade": [Filtro_Especialidade],
    "Sistemas": [Filtro_Sistema],
    "Filtro_modfalha": Filtro_Modo_de_falha,
    "Tag": Filtro_TAG,
    "NivelAlarme": [Filtro_Nivel_do_Alarme],
    "Exportar_Excel":Exportar_Excel,
    };


    $.ajax({
        type: "POST",
        url: "/POST",
        data: params,
        dataType: 'json',
        error: function(request, status, error) { 
            $('#Loading_Modal').modal('hide')
            $.notify("Erro ao executar esta ação", "error") 
            console.log(request)
            console.log(status)
            console.log(error)
        },
        success: function (results) {
            dados = results.results[0]  
        
            var tbody = document.getElementById("table_tbody");
            tbody.innerHTML =""
            
            for(var i=0; i< dados.DataHora.length; i++){
                tbody.innerHTML +=`
<tr class="border-b-detalhe-t">
    <td>`+(dados.DataHora[i])+`</td>
    <td>`+dados.Especialidade[i]+`</td>
    <td>`+dados.Sistema[i]+`</td>
    <td>
        <div class="row">
            <div val="`+dados.NivelAlarme[i]+`" class="col xcentro" id="Marcador"></div>
        </div>
    </td>
    <td>`+dados.ModoDeFalha[i]+`</td>
    <td>`+dados.TAG[i]+`</td>
    <td>
        <div class="btn-group" role="group" aria-label="...">

            <button title="Detalhes do Alarme" onclick="LerMultAlarmes(['`+dados.Adress[i]+`'])" type="button" class="btn btn-default border-detalhe">
            <i class="fa-regular fa-window-maximize color-detalhe"></i>
            </button>

            <div class="border-detalhe">
            <input title="Selecionar Alarme" style="height: 20px;width: 20px;" class="form-check-input m-2" type="checkbox" id="linha_`+[i]+`" value="`+dados.Adress[i]+`" >
            </div>

            <button onclick="ExibirGrafico('`+dados.Adress[i]+`','definir','definir',$('#Multipla_Escala')[0].checked,[''])" type="button" class="btn btn-default border-detalhe">
            <i class="fa-solid fa-chart-line color-detalhe"></i>
            </button>

        </div>
    </td>
</tr>`}
            // Preencher opções do Select Sistema e selecionar ultimjo preenchido     
            document.querySelector('#Filtro_Sistema').setOptions(dados.List_Sistema);
            
            if (URLparams.get('Filtro_Sistema')==null){
                document.querySelector('#Filtro_Sistema').toggleSelectAll()
                document.querySelector('#Filtro_Sistema').toggleSelectAll()
            } 
            else if (URLparams.get('Filtro_Sistema')=="Todos"){
                document.querySelector('#Filtro_Sistema').toggleSelectAll()
                document.querySelector('#Filtro_Sistema').toggleSelectAll()                
            } 
            else {document.querySelector('#Filtro_Sistema').setValue(URLparams.get('Filtro_Sistema').split(','))}
            
            

            //Formatar Criticidade            
            formatacaoCondicional()

            //Atualizar Paginação e Indicadores
            $('#PaginacaoTabela_Input').text(params.PaginaLog)
            $("#PaginacaoTabela_NTotal").text(dados.ContagemLogs[3])
            $("#text-indicador-1").text(dados.ContagemLogs[2])
            $("#text-indicador-2").text("-")
            $("#text-indicador-3").text("-")
            $("#text-indicador-4").text("-")
            
            if(Exportar_Excel){
                
                Json_Excel = dados.Json_Excel
                const EXCEL_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8';
                const EXCEL_EXTENSION = '.xlsx'
                const worksheet = XLSX.utils.json_to_sheet(Json_Excel);
                const workbook = {Sheets:{'data':worksheet},SheetNames:['data']};
                const excelBuffer = XLSX.write(workbook,{bookType:'xlsx',type:'array'});
                const conteudo = new Blob([excelBuffer],{type:EXCEL_TYPE})
                saveAs(conteudo,"Gerenciador de Alarmes"+EXCEL_EXTENSION)
            }

            // Direto_URL=="Sim" Preencher selectes e inpus com calores da URL
            if(Direto_URL=="Sim"){

                if(URLparams.get('Filtro_Especialidade')==null){
                    document.querySelector('#Filtro_Especialidade').toggleSelectAll()
                    document.querySelector('#Filtro_Especialidade').toggleSelectAll()}
                else{document.querySelector('#Filtro_Especialidade').setValue(URLparams.get('Filtro_Especialidade').split(','))}

                if(URLparams.get('Filtro_Sistema')==null){
                    document.querySelector('#Filtro_Sistema').toggleSelectAll()}
                else{
                    if(URLparams.get('Filtro_Sistema')=="Todos"){
                        document.querySelector('#Filtro_Sistema').toggleSelectAll()}
                    else{document.querySelector('#Filtro_Sistema').setValue(URLparams.get('Filtro_Sistema').split(','))}}

                if(URLparams.get('Filtro_Nivel_do_Alarme')==null){
                    document.querySelector('#Filtro_Nivel_do_Alarme').toggleSelectAll()
                    document.querySelector('#Filtro_Nivel_do_Alarme').toggleSelectAll()}
                else{document.querySelector('#Filtro_Nivel_do_Alarme').setValue(URLparams.get('Filtro_Nivel_do_Alarme').split(','))}

                if( URLparams.get('Filtro_Modo_de_falha')==null)  {$('#Filtro_Modo_de_falha').val('')}
                else{$('#Filtro_Modo_de_falha').val(String(URLparams.get('Filtro_Modo_de_falha')))}
            
                if( URLparams.get('Filtro_TAG')==null)  {$('#Filtro_TAG').val('')}
                else{$('#Filtro_TAG').val(URLparams.get('Filtro_TAG'))}
            }



            $('#Loading_Modal').modal('hide')

            // Criar Indicadores
            indicadores = results.results[1]
            Grafico_Indicadores (indicadores)

            //Criar grafico por modo de falha 
            Graf_por_ModoDeFalha = results.results[2]
            Grafico_por_ModoDeFalha(Graf_por_ModoDeFalha)


            //watchdog
            $("#WatchDogstext").text("Inicio do Ciclo de Varredura: "+results.results[0].watchdog[1])
            
            if (results.results[0].watchdog[0] === 'Falha'){
                document.querySelector("#WatchDogs").innerHTML=`
                    <i class="fa-solid fa-circle-xmark fa-3x Alam-color-Nivel3"></i>`
            }else{
                document.querySelector("#WatchDogs").innerHTML=`
                    <i class="fa-solid fa-circle-check fa-3x Alam-color-Normal"></i>`
            }


            $.notify("Pagina Atualizada", "success")          
        }
        });
};


// abrir .log de varios alarmes
function LerMultAlarmes(adress){
    var params =""
    var params = {"Adress_Log": adress};
    $.ajax({
    type: "POST",
    url: "/POSTDentroMultLog",
    data: params,
    dataType: 'json',
    error: function(request, status, error) { 
        $('#Loading_Modal').modal('hide')
        $.notify("Erro ao executar esta ação", "error") 
        console.log(request)
        console.log(status)
        console.log(error)
    },
    success: function (results) {
        dados = results.results;

        if(dados!="ERRO"){
        carroseis.innerHTML=""
        
        for(var i = 0; i < dados.DataHora.length; i++){
            if(dados.fonte_dados[i]=="Preditiva IDMI.xlsx"){
                IDMI = `
        <div class="col xcentro">
            <button style="width:170px;height:40px" title="IDMI" type="button" class="row btn btn-default border-detalhe" 
            onclick="window.open('/IDMI?Filtro_TAG=`+dados.TAG[i]+`','_blank')">
                <div class="row text-center align-middle"> 
                    <text class="col xcentro ycentro">IDMI</text>   
                    <i class="col-3 m-auto fa-solid fa-file-contract color-detalhe"></i>
                </div>
            </button> 
        </div>`
            }else{IDMI = ""}

            if(dados.fonte_dados[i]=="Preditiva Baterias.xlsx"){
                Baterias = `
        <div class="col xcentro">
            <button style="width:170px;height:40px" title="Baterias" type="button" class="row btn btn-default border-detalhe" 
            onclick="window.open('/Baterias?Filtro_TAG=`+dados.TAG[i]+`','_blank')">
                <div class="row text-center align-middle"> 
                    <text class="col xcentro ycentro">Baterias</text>   
                    <i class="col-3 m-auto fa-solid fa-file-contract color-detalhe"></i>
                </div>
            </button> 
        </div>`
            }else{Baterias = ""}

            
        
            carroseis.innerHTML +=`
<div id="carousel-item-`+i+`" class="carousel-item">

    <div class="row pt-2">
        <div class="row border-b-detalhe-t m-0">
            <div class="col-3 xcentro ycentro"><h6 class="m-1 negrito">Data: </h6></div>
            <div class="col-3 xcentro ycentro"><h6 class="m-1" id='Modal_Text_DataHora_`+i+`'></h6></div>

            <div class="col-3 xcentro ycentro border-l-detalhe-t"><h6 class="m-1 negrito">Tag: </h6></div>
            <div class="col-3 xcentro ycentro"><h6 class="m-1" id='Modal_Text_Tag_`+i+`'></h6></div>            
        </div>

        <div class="row border-b-detalhe-t m-0">
            <div class="col-3 xcentro ycentro"><h6 class="m-1 negrito">Especialidade: </h6></div>
            <div class="col-3 xcentro ycentro"><h6 class="m-1" id='Modal_Text_Especialidade_`+i+`'></h6></div>

            <div class="col-3 xcentro ycentro border-l-detalhe-t"><h6 class="m-1 negrito">Sistema: </h6></div>
            <div class="col-3 xcentro ycentro"><h6 class="m-1" id='Modal_Text_Sistema_`+i+`'></h6></div>
        </div>

        <div class="row border-b-detalhe-t m-0">
            <div class="col-3 xcentro ycentro"><h6 class="m-1 negrito">Modo de Falha: </h6></div>
            <div class="col-3 xcentro ycentro"><h6 class="m-1" id='Modal_Text_Modo_de_Falha_`+i+`'></h6></div>

            <div class="col-3 xcentro ycentro border-l-detalhe-t"><h6 class="m-1 negrito">Nível do Alarme: </h6></div>
            <div class="col-3 xcentro ycentro"><h6 class="m-1" id='Modal_Text_Nivel_Alarme_`+i+`'></h6></div>
        </div>

        <div class="row border-b-detalhe-t m-0">
            <div class="col-3 xcentro ycentro"><h6 class="m-1 negrito">Planta: </h6></div>
            <div class="col-3 xcentro ycentro"><h6 class="m-1" id='Modal_Text_Planta_`+i+`'></h6></div>

            <div class="col-3 xcentro ycentro border-l-detalhe-t"><h6 class="m-1 negrito">Unidade: </h6></div>
            <div class="col-3 xcentro ycentro"><h6 class="m-1" id='Modal_Text_Unidade_`+i+`'></h6></div>
        </div>
        
        <div class="row border-b-detalhe-t m-0">
            <div class="col-3 xcentro ycentro"><h6 class="m-1 negrito">Area: </h6></div>
            <div class="col-3 xcentro ycentro"><h6 class="m-1" id='Modal_Text_Area_`+i+`'></h6></div>

            <div class="col-3 xcentro ycentro border-l-detalhe-t"><h6 class="m-1 negrito">Criticidade: </h6></div>
            <div class="col-3 xcentro ycentro"><h6 class="m-1" id='Modal_Text_Criticidade_`+i+`'></h6></div>
        </div>

        <div class="row border-b-detalhe-t m-0">
            <div class="col-3 xcentro ycentro"><h6 class="m-1 negrito">TAG e Valor: </h6></div>
            <div class="col-9 ycentro"><h6 class="m-1" id='Modal_Text_TAG_e_Valor_`+i+`'></h6></div>
        </div>

        <div class="row border-b-detalhe-t m-0 mt-1">
            <div class="col-3 xcentro ycentro"><h6 class="m-1 negrito">Lógica do Alarme: </h6></div>
            <div class="col-9 ycentro"><h6 class="m-1" id='Modal_Text_Logica_Alarme_`+i+`'></h6></div>
        </div>

        <div class="row border-b-detalhe-t m-0 mt-1">
            <div class="col-3 xcentro ycentro"><h6 class="m-1 negrito">Tempo de Aquisição: </h6></div>
            <div class="col-9 ycentro"><h6 class="m-1" id='Modal_Text_Tempacq_`+i+`'></h6></div>
        </div>

        <div class="row border-b-detalhe-t m-0">
            <div class="col-3 xcentro ycentro"><h6 class="m-1 negrito">Comentário: </h6></div>
            <div class="col-9 ycentro"><h6 class="m-1" id='Modal_Text_Comentario_`+i+`'></h6></div>
        </div>
    </div>

    <div class="row mt-2 border-b-detalhe-t">
        <div class="row m-3 xcentro">
            <div class="col xcentro">

                <button style="width:170px;height:40px" title="Abrir Grafico" type="button" class="row btn btn-default border-detalhe" 
                onclick="ExibirGrafico('`+adress[i]+`','definir','definir',$('#Multipla_Escala')[0].checked,[''])">
                    <div class="row text-center align-middle"> 
                        <text class="col xcentro ycentro">Abrir Grafico</text>   
                        <i class="col-3 m-auto fa-solid fa-chart-line color-detalhe"></i>
                    </div>
                </button> 
            </div>

            <div class="col xcentro">

                <button style="width:170px;height:40px" title="Verificar se Existe Nota SAP para este TAG" type="button" class="row btn btn-default border-detalhe" 
                onclick="Verif_Alarme_SAP('`+dados.TAG[i]+`')">
                    <div class="row text-center align-middle"> 
                        <text class="col xcentro ycentro">SAP</text>   
                        
                    </div>
                </button> 
            </div>
            
            `+IDMI+``+Baterias+`

        </div>
    </div>
</div>
`
        // Atualizar textos
        
        $('#Modal_Text_DataHora_'+i+'').text(dados.DataHora[i]);
        $('#Modal_Text_Tag_'+i+'').text(dados.TAG[i]);
        $('#Modal_Text_Especialidade_'+i+'').text(dados.Especialidade[i]);
        $('#Modal_Text_Sistema_'+i+'').text(dados.Sistema[i]);
        $('#Modal_Text_Modo_de_Falha_'+i+'').text(dados.ModoDeFalha[i]);
        $('#Modal_Text_Nivel_Alarme_'+i+'').text(dados.NivelAlarme[i]);
        $('#Modal_Text_TAG_e_Valor_'+i+'').text(dados.TAG_Valor[i]);
        $('#Modal_Text_Logica_Alarme_'+i+'').text(dados.Logica_Alarme[i]);
        $('#Modal_Text_Tempacq_'+i+'').text(dados.tempo_acq[i]);
        $('#Modal_Text_Comentario_'+i+'').text(dados.Comentario[i]);
        $('#Modal_Text_Planta_'+i+'').text(dados.planta[i]);
        $('#Modal_Text_Unidade_'+i+'').text(dados.unidade[i]);
        $('#Modal_Text_Area_'+i+'').text(dados.area[i]);
        $('#Modal_Text_Criticidade_'+i+'').text(dados.criticidade[i]);
        
        }

        num = (adress.length-1)
        $('#Carroseu_N').text(0)
        $('#Carroseu_NTotal').text(num)

        document.querySelector("#carousel-item-0").classList.add('active')

        // Resetar Inputs
        $('#AlterarComent_Log').val('');
        $("#AlterarNivel_Log").val('Selecione');
        $('#Comentario_Rapido').val('Selecione');

        // Modal Visivel
        $('#Alterar-DadosLogModal').modal('show');
        resetdragg()
        $('#GraficoModal').modal('hide');
        
        //Resetar e configurar botão
        recreateNode(document.getElementById("AlterarLogModalButton"))
        
        document.querySelector("#AlterarLogModalButton").addEventListener('click',function click(){
            var paramsMult =""
            var paramsMult = {
                "file_path":adress,
                "alarmed_expr":dados.Logica_Alarme,
                "alarmed_values":dados.TAG_Valor,
                "input_comentario":$('#AlterarComent_Log').val(),
                "input_nivel":$("#AlterarNivel_Log").val(),
                "OldComentario":dados.Comentario,
                'user': usuario.df.login,
            }  
            AlterarMult(paramsMult, dados.Especialidade, dados.Sistema)
        })


        }
        else{                
        Filtro_Post(false)
        $.notify("Alarme(s) Não encontrado(s) Tente novamente", "warn")
        }
    }
    })

}

// alterar .log dos alarmes 
function AlterarMult(paramsMult, espec, sistema){
    
    //Verificar se campos estao preenchidos
    if ($('#AlterarComent_Log').val() == "" || $("#AlterarNivel_Log").val() =="Selecione"){
        return alert('Preencha o campo "Comentario" e selecione um Nivel')}
   
   
    // Verificar se existe conta logada
    if (usuario.df.login == 'Desconectado'){
        return alert('Necessario efetuar o login para esta ação')}

    
    //Verificar se tem permissao na Especialidade
    end = 'nao'  
    if(!(usuario.df.Especialidade == "Todos")){
        usuario.df.Especialidade.split(';')
        espec = [...new Set(espec)]
        espec.forEach(element => {
            if(!(usuario.df.Especialidade.includes(element))){
                end = 'sim'   
                text_end = ('Usuario: '+ usuario.df.login +', Não possui Permissão Para alterar Alarmes da Especialidade: '+ element)
            }
        })
    } 
    if(end == 'sim'){return alert(text_end)}


    //Verificar se tem permissao na sistema
    end = 'nao'  
    if(!(usuario.df.Sistemas == "Todos")){
        usuario.df.Sistemas.split(';')
        sistema = [...new Set(sistema)]
        sistema.forEach(element => {
            if(!(usuario.df.Sistemas.includes(element))){
                end = 'sim'   
                text_end = ('Usuario: '+ usuario.df.login +', Não possui Permissão Para alterar Alarmes do Sistema: '+ element)
            }
        })
    } 
    if(end == 'sim'){return alert(text_end)}
    
    // Realizar a alteração
    $.ajax({
        type: "POST",
        url: "/POSTAlterarMultLog",
        data: paramsMult,
        dataType: 'json',
        error: function(request, status, error) { 
            $('#Loading_Modal').modal('hide')
            $.notify("Erro ao executar esta ação", "error") 
            console.log(request)
            console.log(status)
            console.log(error)
        },
        success: function (results) {
        dados = results;
        
        $('#Alterar-DadosLogModal').modal('hide')
        Filtro_Post(false);                   
        $.notify("Alarme(s) Alterado(s) com sucesso", "success")
        }
        });
    
}

// efetuar login
usuario = {'df':{'login':'Desconectado'}}
function login(attOptions){
    // Logar em alguma conta 
    // attOptions = 'sim' = Atualizar seleções
    // attOptions = 'nao' = tentar efetuar login

    //caso tente efetuar login ver se campos estao preenchidos     
    if(attOptions=='nao' & ($('#Login-User').val()=='' || $('#Login-Senha').val() =='' )){
        return alert('Preencher Login e Senha')}
    
    
    var params ={   "login": $('#Login-User').val(),
                    "senha": $('#Login-Senha').val(),
                    "attOptions": attOptions }
    $.ajax({
        type: "POST",
        url: "/POSTLogin",
        data: params,
        dataType: 'json',
        error: function(request, status, error) { 
            $('#Loading_Modal').modal('hide')
            $.notify("Erro ao executar esta ação", "error") 
            console.log(request)
            console.log(status)
            console.log(error)
        },
        success: function (results) {
            dados = results.results;

            //Atualizar opções do select 
            if (attOptions=='sim'){

                dados.forEach(function(item){
                    $('#Login-User').append('<option>'+item+'</option>');
                });
                
                //Caso tenha cookies de login conectar atumaticamente
                if (getCookie('LoginUser') != ''){
                    console.log('logar automatico')
                    $('#Login-User').val(getCookie('LoginUser'))
                    $('#Login-Senha').val(getCookie('LoginSenha')) 
                    login('nao')
                    $('.Login-Hide').hide(1000)
                }
                return false
            }

            if(attOptions=='nao' & (dados.status != 'Conectado')){
                $('#Login-User').focus()
                return alert(dados.status)
            }

            //Login efetuado 
            setCookie('LoginUser', $('#Login-User').val() , 1)
            setCookie('LoginSenha', $('#Login-Senha').val() , 1)
            document.getElementById('imagemUser').style.color = 'green';

            $('#Login-User').val('');
            $('#Login-Senha').val('');
            
            
            usuario = eval(dados)
            usuario.df = eval(usuario.df)[0]
            $('.Login-Hide').hide(1000)

            //Texto com primeira letra maiuscula
            nome_doUser=usuario.df.login
            $('#NomeUsuarioText').text(nome_doUser[0].toUpperCase() + nome_doUser.substring(1))

        }
    })
}



function Verif_Alarme_SAP(tag){
    tag = tag.toUpperCase()

    Conf_SAP_col = getCookie('Conf_SAP_col') // não esta sendo usado no python
    if (Conf_SAP_col==''){Conf_SAP_col = "TAG SAP,Nota,Data Nota,Descricao Curta,Descricao Longa"} // não esta sendo usado no python
    
    params = {
        // Coletar configuração em outra pagina
        Conf_SAP_cols: Conf_SAP_col, // não esta sendo usado no python
        TAG: tag
    }    
    

    $.ajax({
        type: "POST",
        url: "/POST_Verif_Alarme_SAP",
        data: params,
        dataType: 'json',
        error: function(a,b,c) { 
            console.log(a)
            console.log(b)
            console.log(c)
            $('#Loading_Modal').modal('hide')
            $.notify("Erro ao executar esta ação", "error") 
        },
        success: function (results) { 
            dados_SAP =  results.results.dados_SAP
            data_sap = results.results.dados_datas.Data_Get_SAP

 
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

            
            table = new Tabulator("#TableSAP", {
                
                data: dados_SAP,
                movableColumns: true,
                columns:[
                    {field: 'TAG SAP', title: 'TAG', headerFilter:"input", visible:true, headerMenu: headerMenu, tooltip: true,},
                    {field: 'Nota', title: 'Nota', headerFilter:"input", visible:true, headerMenu: headerMenu, tooltip: true,},
                    {field: 'Ordem', title: 'Ordem', headerFilter:"input", visible:true, headerMenu: headerMenu, tooltip: true,},
                    {field: 'Criador', title: 'Criador', headerFilter:"input", visible:true, headerMenu: headerMenu, tooltip: true,},
                    {field:"Data Nota", title:"Data Nota", headerFilter:"input", visible:true, headerMenu: headerMenu, tooltip: true,},
                    {field: 'Descricao Curta', title: 'Descricao Curta', headerFilter:"input", visible:true, headerMenu: headerMenu, tooltip: true,},
                    {field: 'Descricao Longa', title: 'Descricao Longa', headerFilter:"input", visible:true, headerMenu: headerMenu, tooltip: true,},
                    
                    
                    // {field: 'Data Nota', title: 'Data Nota', headerFilter:"input", visible:true, headerMenu: headerMenu, tooltip: true, sorter:"date", sorterParams:{format:"dd.MM.yyyy"}},  headerFilterFunc:minMaxFilterFunction,   headerFilterLiveFilter:false

                    // {title:"Data Nota", field:"Data Nota", width:150, headerFilter:minMaxFilterEditor  },
                    
                    

                    {field: 'Conclusao Desejada', title: 'Conclusao Desejada', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true, sorter:"date", sorterParams:{format:"dd.MM.yyyy"}},
                    
                    {field: 'Centro de Trabalho', title: 'Centro de Trabalho', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
                    
                    {field: 'Falha', title: 'Falha', headerFilter:"select", headerFilterParams: {value:" X",multiSelect: true }, visible:false, headerMenu: headerMenu, tooltip: true,},
                    
                    
                    {field: 'Campo ordenação', title: 'Campo ordenação', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
                   
                    {field: 'Fim avaria', title: 'Fim avaria', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true, sorter:"date", sorterParams:{format:"dd.MM.yyyy"}},
                   
                    {field: 'Status Sistema', title: 'Status Sistema', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
                    {field: 'Status Usuario', title: 'Status Usuario', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
                    {field: 'A', title: 'A', headerFilter:"input", visible:false,},
                    {field: 'Notificador', title: 'Notificador', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
                    {field: 'Prioridade', title: 'Prioridade', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
                    {field: 'TP', title: 'TP', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
                    {field: 'GPM', title: 'GPM', headerFilter:"input", visible:false, headerMenu: headerMenu, tooltip: true,},
                ], 

                
                pagination:"local",
                paginationSize:5,
                paginationSizeSelector:[5, 10, 25, 50, 100],
                paginationCounter:"rows",

                resizableColumnFit:true,
                layout: "fitColumns",//"fitDataTable",//
            
            })

            $("#input_tag_SAP").val(tag)

            $("#UltAttSAP").text(data_sap)

            $('#Notas_SAP').modal('show')

        }
    })
}


//////////////////////////   CRIAR GRAFICOS ///////////////////////////////

function Grafico_Indicadores (indicadores){
 
    
    Total = 0
    Object.values(indicadores).forEach(value => {Total = Total+value})
    $('#total_indicador').text('De '+Total+' Alarmes')
    
    document.getElementById("Titulo_Indicador").innerHTML = "Analise Grafica Por Nível de Alarme"

    var Grafico = document.getElementById("div_Grafico");
    Grafico.innerHTML =""         
    Grafico.innerHTML = '<canvas id="Grafico_Indicador" style="height: 80px; max-height: 80px;"></canvas>'


    const data = {
        labels: ['Alarmes'],
        datasets: [
        {
            label: 'Normal',
            data: [indicadores.Normal],
            backgroundColor: ['rgba(0 , 128, 0 , 0.3)'],
            borderColor: ['rgba(0 , 128, 0 , 1)'],

        },
        {
            label: 'Nivel 1',
            data: [indicadores['Nivel 1']],
            backgroundColor: ['rgba(255, 255 , 0 , 0.3)'],
            borderColor: ['rgba(255, 255 , 0 , 1)'],
        },
        {
            label: 'Nivel 2',
            data: [indicadores['Nivel 2']],
            backgroundColor: ['rgba(255, 127, 0, 0.3)'],
            borderColor: ['rgba(255, 127, 0, 1)'],
        },
        {
            label: 'Nivel 3',
            data: [indicadores['Nivel 3']],
            backgroundColor: ['rgba(255, 0 , 0 , 0.3)'],
            borderColor: ['rgba(255, 0 , 0 , 1)'],
        },
        {
            label: 'Silenciado',
            data: [indicadores.Silenciado],
            backgroundColor: ['rgba(0 , 0 , 255 , 0.3)'],
            borderColor: ['rgba(0 , 0 , 255 , 1)'],
        },

        ]
    };
    
    // config 
    const config = {
    type: 'bar',
    data,
    plugins: [ChartDataLabels],
    options: {
        indexAxis:'y',
        borderSkipped: false,
        borderWidth: 1,
        barPercentage: 0.5,
        categoryPercentage: 1,
        scales: {
            x: {
                max:Total,
                stacked: true,
                grid: {
                    display: false,
                    drawBorder: false,
                    drawTicks: false,
                },
                ticks: {display: false,},
            },
            y: {
                stacked: true,
                grid: {
                    display: false,
                    drawBorder: false,
                    drawTicks: false,
                },
                ticks: {display: false,},
            }
        },
        plugins : {
            legend: {
                display: false,
            },
            datalabels: {
                display: false
            },
        },  
    },
    };


    ctx = document.getElementById('Grafico_Indicador')
    const Grafico_Indicador = new Chart(ctx,config);

    // Escrever na Legenda Manual
    if(isNaN(indicadores.Normal)){Por_Res = "0%"}else{Por_Res = (indicadores.Normal * 100 / Total).toFixed(0)+'%'}
    if(isNaN(indicadores['Nivel 1'])){Por_Aten = "0%"}else{Por_Aten = (indicadores['Nivel 1'] * 100 / Total).toFixed(0)+'%'}
    if(isNaN(indicadores['Nivel 2'])){Por_Impo = "0%"}else{Por_Impo = (indicadores['Nivel 2'] * 100 / Total).toFixed(0)+'%'}
    if(isNaN(indicadores['Nivel 3'])){Por_Crit = "0%"}else{Por_Crit = (indicadores['Nivel 3'] * 100 / Total).toFixed(0)+'%'}
    if(isNaN(indicadores.Silenciado)){Por_Sil = "0%"}else{Por_Sil = (indicadores.Silenciado * 100 / Total).toFixed(0)+'%'}

    $('.legenda_Normal').text("Normal - "+Por_Res) 
    $('.legenda_Nivel1').text("Nivel 1 - "+Por_Aten)
    $('.legenda_Nivel2').text("Nivel 2 - "+Por_Impo)
    $('.legenda_Nivel3').text("Nivel 3 - "+Por_Crit)
    $('.legenda_Silenciado').text("Silenciado - "+Por_Sil)

    
    
};

function Grafico_por_ModoDeFalha(Graf_por_ModoDeFalha){
    resultado = Graf_por_ModoDeFalha
    console.log(resultado)

    document.getElementById("Titulo_Graf_por_ModoDeFalha").innerHTML = "Analise Grafica Por Modo de Falha"

    var Grafico = document.getElementById("div_Graf_por_ModoDeFalha");
    Grafico.innerHTML =""         
    Grafico.innerHTML = '<canvas id="Canvas_Graf_por_ModoDeFalha" style="height: 80px; max-height: 80px;"></canvas>'
    
    var modosFalha = resultado['Modo de Falha'];
    var porcentagens = resultado['Porcentagem'];
    var porcentagens_outros = 100 - eval(porcentagens.join('+')) ;
    var repeticao = resultado['Repeticao'];


    $("#mododefalha_1").text( modosFalha[0] +' ('+ String(Math.round(porcentagens[0]*100)/100)+"%)")
    $("#mododefalha_2").text( modosFalha[1] +' ('+ String(Math.round(porcentagens[1]*100)/100)+"%)")
    $("#mododefalha_3").text( modosFalha[2] +' ('+ String(Math.round(porcentagens[2]*100)/100)+"%)")
    $("#mododefalha_4").text( modosFalha[3] +' ('+ String(Math.round(porcentagens[3]*100)/100)+"%)")
    $("#mododefalha_5").text( modosFalha[4] +' ('+ String(Math.round(porcentagens[4]*100)/100)+"%)")
    $("#mododefalha_outros").text( "Outros" +' ('+ String(Math.round(porcentagens_outros*100)/100)+"%)")


    document.getElementById("mododefalha_1").setAttribute("onClick","choice_filtro(['"+modosFalha[0]+"'],'Filtro_Modo_de_falha'),'input'")
    document.getElementById("mododefalha_2").setAttribute("onClick","choice_filtro(['"+modosFalha[1]+"'],'Filtro_Modo_de_falha'),'input'")
    document.getElementById("mododefalha_3").setAttribute("onClick","choice_filtro(['"+modosFalha[2]+"'],'Filtro_Modo_de_falha'),'input'")
    document.getElementById("mododefalha_4").setAttribute("onClick","choice_filtro(['"+modosFalha[3]+"'],'Filtro_Modo_de_falha'),'input'")
    document.getElementById("mododefalha_5").setAttribute("onClick","choice_filtro(['"+modosFalha[4]+"'],'Filtro_Modo_de_falha'),'input'")
    document.getElementById("mododefalha_outros").setAttribute("onClick","choice_filtro([],'Filtro_Modo_de_falha'),'input'")


    if(typeof modosFalha[0]=="undefined"){$("#mododefalha_1").text('')}
    if(typeof modosFalha[1]=="undefined"){$("#mododefalha_2").text('')}
    if(typeof modosFalha[2]=="undefined"){$("#mododefalha_3").text('')}
    if(typeof modosFalha[3]=="undefined"){$("#mododefalha_4").text('')}
    if(typeof modosFalha[4]=="undefined"){$("#mododefalha_5").text('')}

    data = {
        labels: ['Modo de Falha'],
        datasets: [
            {
                label: "Outros",
                data: [resultado['Outros']],
                backgroundColor: ['rgba(76, 76, 76, 0.3)'],
                borderColor: ['rgba(76, 76, 76, 1)'],

            }, 
            {
                label: modosFalha[0],
                data: [repeticao[0]],
                backgroundColor: ['rgba(9, 36, 245, 0.3)'],
                borderColor: ['rgba(9, 36, 245, 1)'],
            },
            {
                label: modosFalha[1],
                data: [repeticao[1]],
                backgroundColor: ['rgba(0, 170, 255, 0.3)'],
                borderColor: ['rgba(0, 170, 255, 1)'],
            },
            {
                label: modosFalha[2],
                data: [repeticao[2]],
                backgroundColor: ['rgba(0, 255, 140, 0.3)'],
                borderColor: ['rgba(0, 255, 140, 1)'],
            },            
            {
                label: modosFalha[3],
                data: [repeticao[3]], 
                backgroundColor: ['rgba(47, 255, 0, 0.3)'],
                borderColor: ['rgba(47, 255, 0, 1)'],
            },
            {
                label: modosFalha[4],
                data: [repeticao[4]],
                backgroundColor: ['rgba(251, 255, 0, 0.3)'],
                borderColor: ['rgba(251, 255, 0, 1)'],
            },
        ]
    }
      
    var confi = {
        type: 'bar',
        data,
        plugins: [ChartDataLabels],
        options: {
            indexAxis:'y',
            borderSkipped: false,
            borderWidth: 1,
            barPercentage: 0.5,
            categoryPercentage: 1,
            scales: {
                x: {
                    max:Total,
                    stacked: true,
                    grid: {
                        display: false,
                        drawBorder: false,
                        drawTicks: false,
                    },
                    ticks: {display: false,},
                },
                y: {
                    stacked: true,
                    grid: {
                        display: false,
                        drawBorder: false,
                        drawTicks: false,
                    },
                    ticks: {display: false,},
                }
            },
            plugins : {
                legend: {
                    display: false,
                },
                datalabels: {
                    display: false
                },
            },  
        },
    };
    
    
    var ctx = document.getElementById('Canvas_Graf_por_ModoDeFalha').getContext('2d');
    var Canvas_Graf_por_ModoDeFalha = new Chart(ctx, confi);
    
    




}


var myChart = ""
function ExibirGrafico(Adress,datastart,dataend,conf,Extra_tags){

    var Grafico = document.getElementById("LocalGraficoLinha");
    Grafico.innerHTML =""         
    Grafico.innerHTML = '<canvas id="GraficoLinha"></canvas>'
    var params = {"Adress": Adress,
                "datastart": datastart,
                "dataend": dataend,
                "conf":conf,
                "Extra_tags": Extra_tags}
    $.ajax({
    type: "POST",
    url: "/POSTBuscarPi",
    data: params,
    dataType: 'json',
    success: function (results) {
        dados = results.results;

        if (dados == 'ERRO'){

            $.notify("Não foi possivel realizar esta consulta no PI", "error");
            }

        else{
            

            $("#SolicitarGrafico").val(Adress)
            $("#intervalinicial").val(dados['InicioFim'][0])
            $("#intervalfinal").val(dados['InicioFim'][1])
            
            document.getElementById("LerAlarmButGrafc").setAttribute(`onclick`,`LerMultAlarmes(['`+dados.Adress+`']);`)
            
            const data = {
                datasets: dados['Pontos'][0]
            };
            
            if(dados['InicioFim'][0] == dados['InicioFim'][1]){
                valor_pointRadius = 5}
            else {valor_pointRadius = 0}

            const config = {
                data,
                options: {    
                    interaction: {
                        mode: 'index',
                    },
                    pointRadius: valor_pointRadius,
                    pointHoverRadius: 7,
                    pointHitRadius: 10,
                    hoverBackgroundColor: 'white',
                    pointHoverBorderWidth: 3,             
                    plugins:{
                        zoom:{
                            zoom:{
                                overScaleMode:'xy',
                                wheel:{enabled:true,},
                                drag:{
                                    enabled:true,
                                    backgroundColor:'rgba(211, 190, 4, 0.3)',
                                    modifierKey: 'ctrl',
                                },
                            },
                            pan:{
                                enabled:true,  
                            },
                            
                        },
                        legend:{
                            display: true,
                            position: 'bottom',
                            labels: {
                                color: 'rgba(255,255,255,0.5)'
                            },
                        },     
                        annotation: {
                          annotations: dados['annotations'],
                        },
                    },
                    scales: dados['scales']
                },
            };

            
            
            var ctx = document.getElementById('GraficoLinha').getContext('2d');
            myChart = new Chart(ctx,config);

            $('#Alterar-DadosLogModal').modal('hide');
            $('#GraficoModal').modal('show');
            resetdragg()

            myChart.options.scales.x.ticks.color = 'rgba(255,255,255,0.8)';
            if(conf){}else{myChart.options.scales.y.ticks.color = 'rgba(255,255,255,0.8)'};
            
            myChart.options.plugins.annotation.annotations.Alarm.display = false
            myChart.update();

            // Criar tabela descrição das tags
            var tbody = document.getElementById("tabela_detalhes_tag");
            tbody.innerHTML =""

            InpTag_1 = 'nao'
            InpTag_2 = 'nao'
            InpTag_3 = 'nao'
            for(var i=0; i< dados.infPoints.Tag.length; i++){

                // Cor para Identificar tags encontradas
                if (dados.infPoints.Tag[i].toUpperCase()==$('#AdicionarTagGrafico_1').val().toUpperCase()){InpTag_1='sim'}
                if (dados.infPoints.Tag[i].toUpperCase()==$('#AdicionarTagGrafico_2').val().toUpperCase()){InpTag_2='sim'}
                if (dados.infPoints.Tag[i].toUpperCase()==$('#AdicionarTagGrafico_3').val().toUpperCase()){InpTag_3='sim'}           
                
                //Tabela
                tbody.innerHTML +=`
<tr>
    <th scope="row">`+dados.infPoints.Tag[i]+`</th>
    <td>`+dados.infPoints.Descricao[i]+`</td>
    <td>`+dados.infPoints.Unidade[i]+`</td>
    <td>`+dados.infPoints.ValorAtual[i]+`</td>
    <td>`+dados.infPoints.Max[i]+`</td>
    <td>`+dados.infPoints.Min[i]+`</td>
    <td>`+dados.infPoints.Std[i]+`</td>
</tr>`}
            
            if(InpTag_1=='sim')
                {$('#AdicionarTagGrafico_1')[0].style.backgroundColor = 'rgb(144, 238, 144)'}
            else{$('#AdicionarTagGrafico_1')[0].style.backgroundColor = 'white'}
            if(InpTag_2=='sim')
                {$('#AdicionarTagGrafico_2')[0].style.backgroundColor = 'rgb(144, 238, 144)'}
            else{$('#AdicionarTagGrafico_2')[0].style.backgroundColor = 'white'}
            if(InpTag_3=='sim')
                {$('#AdicionarTagGrafico_3')[0].style.backgroundColor = 'rgb(144, 238, 144)'}
            else{$('#AdicionarTagGrafico_3')[0].style.backgroundColor = 'white'}
             

            
            
        }
        
    }})
   
};

///////////////////////////////// FUNÇÕES SIMPLES /////////////////////////////////////

$("#Filtro_Modo_de_falha").keypress(function(k) {if(k.key=='Enter'){Atualizar()}});
$("#Filtro_TAG").keypress(function(k) {if(k.key=='Enter'){Atualizar()}});
$("#Login-Senha").keypress(function(k) {if(k.key=='Enter'){login('nao')}});
$('#input_tag_SAP').keypress(function(k) {if(k.key=='Enter'){Verif_Alarme_SAP($('#input_tag_SAP').val())}});


function Config(){
    //Iniciar Virtual Select
    VirtualSelect.init({
        ele: '#Conf_SAP_col',
        multiple:"true", search: "true",
        selectAllOnlyVisible: "true",
        hideValueTooltipOnSelectAll: 'true',
        options: Var_Col_SAP
    });
    document.querySelector("#Conf_SAP_col").setValue(getCookie('Conf_SAP_col'))

    $("#Modal_Confi").modal("show")
}

function Config_Save(){
    setCookie('Conf_SAP_col',$("#Conf_SAP_col").val(),30)
    $("#Modal_Confi").modal("hide")
}

function Config_Reset(){
    setCookie('Conf_SAP_col','',1)
    $("#Modal_Confi").modal("hide")
}







// Atalhos para trocar o filtro do nivel de alarme 
function choice_filtro(valor,filtro,modo){
    if(valor!='undefined'){
        if(modo=='selected'){
            document.querySelector('#'+ filtro).setValue(valor)
        }else{
            $('#'+ filtro).val(valor)
        }
        Atualizar()
    }
    
}

function intervalo_grafico(interval){  
    // interval = [inicial, final, OsDois]

    // Separar input    
    const intervalinput = $('#intervalinput').val().replace(' ','')
    const regex = /^([\+\-\*\/]?)(\d+)([a-zA-Z]+)$/;
    const match = intervalinput.match(regex);


    try {const caracter_especial = match[1]} 
    catch (erro) {return alert(`Formato de texto fora do padrão.

    O padrão correto é:   "Numero" + "Unidade de Tempo"
    Exemplos: 1h  5m   10s

    Podendo colocar ou nao o simbolo de Adição ou subtração
    Exemplos: +1h  -5m   -10s

    Caso nao coloque é definido por padrão a soma`)}

    const caracter_especial = match[1]
    const numero = parseInt(match[2]);
    const letra = match[3].toLowerCase();


    // Separar todos os dados do intervalo inicial  
    var intervalinicial =  new Date($('#intervalinicial').val());
    var intervalfinal =  new Date($('#intervalfinal').val());

    if(letra=="h"){Dt="Hours"}
    else if(letra=="d"){Dt="Date"}
    else if(letra=="m"){Dt="Minutes"}
    else if(letra=="s"){Dt="Seconds"}
    else if(letra==""){alert(`Insira uma letra para indicar a escala de tempo:
    [h = Hora, m = Minuto, s = Segundo]`)}
    else {return alert("I")}  

    // Logica
    // Se For escolhido um lado
    if(interval == "final"){
        // Se For para Subtrair
        if (caracter_especial == "-"){
            eval("intervalfinal = intervalfinal.set"+Dt+"(new Date(intervalfinal).get"+Dt+"() - Math.abs("+numero+"))")
        }
        // Se For para Somar
        else if (caracter_especial == "+") {
            eval("intervalfinal = intervalfinal.set"+Dt+"(new Date(intervalfinal).get"+Dt+"() + "+numero+")")
        }

        else if (caracter_especial == "") {
            eval("intervalfinal = intervalfinal.set"+Dt+"(new Date(intervalfinal).get"+Dt+"() + "+numero+")")
            eval("intervalinicial = intervalinicial.set"+Dt+"(new Date(intervalinicial).get"+Dt+"() + "+numero+")")
        }
    }

    else if(interval == "inicial"){
        // Se For para Subtrair
        if (caracter_especial == "-"){
            eval("intervalinicial = intervalinicial.set"+Dt+"(new Date(intervalinicial).get"+Dt+"() + ("+numero+"))")
        }
        // Se For para Somar
        else if (caracter_especial == "+") {
            eval("intervalinicial = intervalinicial.set"+Dt+"(new Date(intervalinicial).get"+Dt+"() - Math.abs("+numero+"))")
        }

        else if (caracter_especial == "") {
            eval("intervalfinal = intervalfinal.set"+Dt+"(new Date(intervalfinal).get"+Dt+"() - Math.abs("+numero+"))")
            eval("intervalinicial = intervalinicial.set"+Dt+"(new Date(intervalinicial).get"+Dt+"() - Math.abs("+numero+"))")
        }
    }

    else {
        if (caracter_especial == "-"){
            eval("intervalinicial = intervalinicial.set"+Dt+"(new Date(intervalinicial).get"+Dt+"() + ("+numero+"))")
            eval("intervalfinal = intervalfinal.set"+Dt+"(new Date(intervalfinal).get"+Dt+"() - Math.abs("+numero+"))")
        }
        else{
            eval("intervalinicial = intervalinicial.set"+Dt+"(new Date(intervalinicial).get"+Dt+"() - Math.abs( "+numero+"))")
            eval("intervalfinal = intervalfinal.set"+Dt+"(new Date(intervalfinal).get"+Dt+"() + "+numero+")")
        }
    }

    if (intervalinicial>intervalfinal){return alert("A data Inicial esta maior que a data final")}

    // Se inicial for maior que a final
    $('#intervalinicial').val(formatarDataParaString(new Date(intervalinicial)))
    $('#intervalfinal').val(formatarDataParaString(new Date(intervalfinal)))
    

    SolicitarGrafico()   

}

// Formato ano-mes-diaThora:minutos:segundos
function formatarDataParaString(data) {
    function adicionarZero(numero) {
      if (numero < 10) {
        return '0' + numero.toString();
      }
      return numero.toString();
    }
  
    let ano = data.getFullYear();
    let mes = adicionarZero(data.getMonth() + 1);
    let dia = adicionarZero(data.getDate());
    let hora = adicionarZero(data.getHours());
    let minutos = adicionarZero(data.getMinutes());
    let segundos = adicionarZero(data.getSeconds());
  
    let dataFormatada = `${ano}-${mes}-${dia}T${hora}:${minutos}:${segundos}`;
    return dataFormatada;
  }




$('#SelectAll').click(function () {
    var linhas = $('#table_tbody tr')
  
    if ($('#SelectAll').val() == 'Sim') {
      for (var i = 0; i < linhas.length; i++) {
        $('#linha_' + i)[0].checked = true
      }
      $('#SelectAll').val('Não')
    } else {
      for (var i = 0; i < linhas.length; i++) {
        $('#linha_' + i)[0].checked = false
      }
      $('#SelectAll').val('Sim')
    }
});


function resetZoomChart(){
    myChart.resetZoom()
}


$('#RecoMult').click(function(){
    //Encontrar Linhas selecionadas
    var linhas = document.getElementById("table_tbody").getElementsByTagName("tr");      
    var selecionados = []
    $('#SelectAll').val("Sim")

    for(var i = 0; i < linhas.length; i++){
    linha = "#linha_"+i+""    
    if ($(linha)[0].checked == true){
        LinhaSelecionada = $(linha).val()
        selecionados.push(LinhaSelecionada)
        $(linha)[0].checked = false
    }; 
    };
    
    if(selecionados.length == 0){alert("Selecione Algum Alarme")}
    else{LerMultAlarmes(selecionados)}
})


function SendEmail() {
    id = $('.carousel-item.active').attr('id').slice(-1)

    var email = 'Digitar Email';
    var subject = 'Alarme do Gerenciador de Alarmes: '+$('#Modal_Text_Especialidade_'+id).text();
    var emailBody = `
Prezados, %0D%0A %0D%0A

Segue Abaixo alarme disparado na data de `+$('#Modal_Text_DataHora_'+id).text()+`  %0D%0A
Tag: `+$('#Modal_Text_Tag_'+id).text()+`  %0D%0A
Especialidade: `+$('#Modal_Text_Especialidade_'+id).text()+`  %0D%0A
Sistema: `+$('#Modal_Text_Sistema_'+id).text()+`  %0D%0A
Modo de Falha: `+$('#Modal_Text_Modo_de_Falha_'+id).text()+`  %0D%0A
Nivel do Alarme: `+$('#Modal_Text_Nivel_Alarme_'+id).text()+`  %0D%0A
TAG e Valor: `+$('#Modal_Text_TAG_e_Valor_'+id).text()+`  %0D%0A
Logica do Alarme: `+$('#Modal_Text_Logica_Alarme_'+id).text()+`  %0D%0A
Comentario: `+$('#Modal_Text_Comentario_'+id).text()+` %0D%0A
%0D%0A
Atenciosamente,
`
;
    document.location = "mailto:"+email+"?subject="+subject+"&body="+emailBody;
};


function SolicitarGrafico(){
    Adress = $("#SolicitarGrafico").val()
    datastart = $("#intervalinicial").val()
    dataend = $("#intervalfinal").val()
    conf = $('#Multipla_Escala')[0].checked
    Extra_tags = [$('#AdicionarTagGrafico_1').val(),$('#AdicionarTagGrafico_2').val(),$('#AdicionarTagGrafico_3').val()]
    ExibirGrafico(Adress,datastart,dataend,conf,Extra_tags)
};


$('#Exportar_Excel').click(function(){
    Filtro_Post(true)
})


$('#Comentario_Rapido').change(function(){
    if($('#Comentario_Rapido').val() == "Selecione"){
    $('#AlterarComent_Log').val('')
    }
    else{
    $('#AlterarComent_Log').val($('#Comentario_Rapido').val()+" ");
    $('#AlterarComent_Log').focus()
    }
})

function resetdragg(){
    $('.arrastar').animate({
        top: "0px",
        left: "0px"
    });
}


function LinhaAlarm(){
    if (myChart.options.plugins.annotation.annotations.Alarm.display == true){
        myChart.options.plugins.annotation.annotations.Alarm.display = false;
    }
    else{myChart.options.plugins.annotation.annotations.Alarm.display = true}
   
    myChart.update();
};


function formatacaoCondicional(){
    trs = document.querySelectorAll('#table_tbody tr')
    trs.forEach(function(item){
    trMarcador = item.querySelector('#Marcador')    
    trsNivel = trMarcador.attributes.val.value

    switch (trsNivel) {
        case "Nivel 3":
        trMarcador.innerHTML=`<i class="fa-solid fa-triangle-exclamation fa-2x Alam-color-Nivel3"></i>`
        break;
        case "Nivel 2":
        trMarcador.innerHTML=`<i class="fa-solid fa-circle-exclamation fa-2x Alam-color-Nivel2"></i>`
        break;
        case "Nivel 1":
        trMarcador.innerHTML=`<i class="fa-solid fa-bell fa-2x Alam-color-Nivel1"></i>`
        break;
        case "Normal":
        trMarcador.innerHTML=`<i class="fa-solid fa-circle-check fa-2x Alam-color-Normal"></i>`
        break; 
        case "Silenciado":
        trMarcador.innerHTML=`<i class="fa-solid fa-snowflake fa-2x Alam-color-silenciado"></i>`
        break;
    }
    })
};


function AcrescentarPaginacao(){
    max = $("#PaginacaoTabela_NTotal").text()
    atual = $("#PaginacaoTabela_Input").text()
    if (atual==max){}
    else{
        $("#PaginacaoTabela_Input").text(parseInt(atual)+1);
        Filtro_Post(false);
    }
};


function DiminuirPaginacao(){
    min = 1
    atual = $("#PaginacaoTabela_Input").text()
    if (atual==min){}
    else{
        $("#PaginacaoTabela_Input").text(parseInt(atual)-1);
        Filtro_Post(false);
    }
};


function AcrescentarCarroseu(){
    max = $("#Carroseu_NTotal").text()
    atual = $("#Carroseu_N").text()
    if (atual==max){}
    else{
        $("#Carroseu_N").text(parseInt(atual)+1);
    }
    Carroseu_chang()
};


function DiminuirCarroseu(){
    min = 0
    atual = $("#Carroseu_N").text()
    if (atual==min){}
    else{
        $("#Carroseu_N").text(parseInt(atual)-1);
    }
    Carroseu_chang()
};


function Carroseu_chang(){
    document.querySelector('.carousel-item.active').classList.remove('active')
    document.querySelector("#carousel-item-"+$('#Carroseu_N').text()).classList.add('active')
}


function LimparFiltro(){
    $('#PaginacaoTabela_Input').val(1);
    $('#filtro-NumeroLogs').val(5);
    $('#filtro-DataInicial').val(dataAtualFormatada(365));
    $('#filtro-DataFinal').val(dataAtualFormatada(-10));
    $('#Filtro_Modo_de_falha').val('');
    $('#Filtro_TAG').val('');

    document.querySelector('#Filtro_Especialidade').reset();
    document.querySelector('#Filtro_Sistema').reset();
    document.querySelector('#Filtro_Nivel_do_Alarme').reset();
    document.querySelector('#Filtro_Especialidade').toggleSelectAll();
    document.querySelector('#Filtro_Sistema').toggleSelectAll(); 
    document.querySelector('#Filtro_Nivel_do_Alarme').toggleSelectAll();

    Filtro_Post(false)        
}



function Atualizar(){
    $("#PaginacaoTabela_Input").text(1)
    Filtro_Post(false);
}




