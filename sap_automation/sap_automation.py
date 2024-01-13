# --------------------------Importações de Bibliotecas-------------------------
#Importando as bibliotecas
import win32com.client 
import win32gui
import win32con

import subprocess
import time
import threading
import os
import psutil


# --------------------------Configurações de Variaveis-------------------------
login = "login"
senha = "senha"


# --------------------------Automações-----------------------------------------
# Função VBS Para procurar Janela do Windowns Utilizar
def importar(adress_file):
    
    # define o conteúdo do arquivo VBS
    script = r'''Set WshShell = CreateObject("WScript.Shell")
    
    startTime = Timer
    maxTime = 600
    counter = 0
        
    Do While True
        bWindowFound = WshShell.AppActivate("Importar File")
        WScript.Sleep 1000
        
        counter = Timer - startTime
        If counter >= maxTime Then
            Exit Do
        End If        
        
        If bWindowFound Then
            WshShell.SendKeys "{TAB}{TAB}"
            WScript.Sleep 1000
            WshShell.SendKeys"'''+adress_file+'''"
            WScript.Sleep 1000
            WshShell.SendKeys "{ENTER}"
            WScript.Sleep 1000
            Exit Do
        End If
        
    Loop
    '''

    # WshShell.SendKeys "{TAB}"
    #         WshShell.SendKeys "^%{a}"


    # cria o arquivo VBS e grava o conteúdo
    with open('importar.vbs', 'w') as f:
        f.write(script)

    # executa o arquivo VBS
    subprocess.Popen(['cscript','importar.vbs'])

# Fechar todos os VBS
def wscript_exe_finish():
    for processo in psutil.process_iter(): 
        nome_processo = processo.name() 
        if nome_processo == "wscript.exe": 
            processo.kill() 

# Função para fechar sap retornando relatorio da automação
def fechar_SAP(): 
    Timeout_janela_SAP.cancel() # Cancelar timer do timeout SAP# Cancelar timer do timeout VBS    
    
    global session
    global SapGuiAuto
    global application 
    global connection 
    
    try:        
        session.ActiveWindow.Close()
        session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()
    except:
        print('SAP não fechou corretamente')
        
    os.system("TASKKILL /F /IM saplogon.exe")
    
    SapGuiAuto = None
    application = None
    connection = None
    session = None
        
    return 

#Função Principal 
def Importar_SAP(CtrAut, coleta) -> str:
    '''
    Objetivo:
        Importar Relatorio em uma Ordem do SAP

    Parametros:
        coleta: df da coleta a ser preenchida
        name_coleta: nome da coleta para encontrar modelo do relatorio
        adress_file: Endereço do arquivo a ser anexado

    Retorno:[
        Nome do Processo
        Status Do Processo
        Erroelatorio
        Outros ...
    ]
    '''
    # ---------------------- Variaveis ----------------------
    # Variaveis para o relatorio da automação 
    name_coleta = CtrAut['name_coleta']
    adress_file = CtrAut['Aut']['GerarRelatorio']['adress_relatorio']
    path = r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"
    
    # Variaveis da sessão
    global session
    global SapGuiAuto
    global application 
    global connection
    
    global Timeout_janela_SAP
    global Timeout_janela_VBS 
    
    # ---------------------- Iniciar Automação ----------------------
    try:  
        # Verificar se Alguma Aplicação esta utilizando o SAP
        Verific_SAP_Open = 0
        while Verific_SAP_Open <= 16:
            # Verificar se esta aberto
            SAP_running = False
            for p in psutil.process_iter(['pid','name']):
                if 'sap' in p.info['name']:
                    SAP_running = True
                    Verific_SAP_Open += 1 
                    
            if SAP_running:
                print("SAP - Aberto, Waiting for 1m N°:{}/15".format(Verific_SAP_Open))
                time.sleep(60*1)
                if Verific_SAP_Open >= 10:
                    erro_SAP_Aberto = erro_SAP_Aberto+5+'Erro'
            else:
                break        
        
        
        # Encerrar VBS abertos
        wscript_exe_finish()
        
        
        # Executar codigo VBS para procular janela do windowns
        thread = threading.Thread(target=importar(adress_file))
        thread.start()
        
        # Configurar timeout para toda a execução do SAP  
        Timeout_janela_SAP = threading.Timer(60*6, fechar_SAP)
        Timeout_janela_SAP.start()
        
        # Abrir SAP
        subprocess.Popen(path)
        time.sleep(2)


        # Etapa conecção SAP 1
        SapGuiAuto = win32com.client.GetObject('SAPGUI')
        if not type(SapGuiAuto) == win32com.client.CDispatch:
            fechar_SAP()
            CtrAut['Aut']['AnexarRelatSAP']['Lista_Erros'].append("Erro na Etapa conecção SAP 1")
            CtrAut['Aut']['AnexarRelatSAP']['status'] = 'Repetir'
            return CtrAut


        # Etapa conecção SAP 2
        application = SapGuiAuto.GetScriptingEngine
        if not type(application) == win32com.client.CDispatch:
            fechar_SAP()
            CtrAut['Aut']['AnexarRelatSAP']['Lista_Erros'].append("Erro na Etapa conecção SAP 2")
            CtrAut['Aut']['AnexarRelatSAP']['status'] = 'Repetir'
            return CtrAut
        
        
        # Etapa conecção SAP 3
        connection = application.OpenConnection("PRD - SAP ERP", True) #nome da conexão
        if not type(connection) == win32com.client.CDispatch:
            fechar_SAP()
            CtrAut['Aut']['AnexarRelatSAP']['Lista_Erros'].append("Erro na Etapa conecção SAP 3")
            CtrAut['Aut']['AnexarRelatSAP']['status'] = 'Repetir'
            return CtrAut


        # Etapa conecção SAP 4
        session = connection.Children(0)
        if not type(session) == win32com.client.CDispatch:
            fechar_SAP()
            CtrAut['Aut']['AnexarRelatSAP']['Lista_Erros'].append("Erro na Etapa conecção SAP 4")
            CtrAut['Aut']['AnexarRelatSAP']['status'] = 'Repetir'
            return CtrAut

        
        #Login no SAP
        time.sleep(1)
        session.findById("wnd[0]/usr/txtRSYST-BNAME").text = login
        session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = senha
        session.findById("wnd[0]").sendVKey(0)
        if "O nome ou a senha não está correto" in (session.findById("wnd[0]/sbar").Text):
            fechar_SAP()
            CtrAut['Aut']['AnexarRelatSAP']['Lista_Erros'].append("Erro na Etapa Login: Login ou Senha Incorreto")
            CtrAut['Aut']['AnexarRelatSAP']['status'] = 'Erro'
            return CtrAut        
        if not "Menu usuário" in session.ActiveWindow.Text:
            fechar_SAP()
            CtrAut['Aut']['AnexarRelatSAP']['Lista_Erros'].append("Erro na Etapa De conecção: Não chegou na tela do menu")
            CtrAut['Aut']['AnexarRelatSAP']['status'] = 'Repetir'
            return CtrAut
          

        # Acessar Trasação do SAP 
        session.findById("wnd[0]").maximize()
        session.findById("wnd[0]/tbar[0]/okcd").text = "iw32" #-> Acessa transação IW32
        session.findById("wnd[0]").sendVKey (0)
        if not "Modificar Ordem: 1ª tela" in session.ActiveWindow.Text:
            fechar_SAP()
            CtrAut['Aut']['AnexarRelatSAP']['Lista_Erros'].append("Erro na Etapa De entrar na Transação: Não chegou na tela Correta")
            CtrAut['Aut']['AnexarRelatSAP']['status'] = 'Repetir'
            return CtrAut
        
        
        # Entrar na ordem
        session.findById("wnd[0]/usr/ctxtCAUFVD-AUFNR").text = str(int(coleta['OrdServ'])) #-> Número da ordem de teste
        session.findById("wnd[0]/usr/ctxtCAUFVD-AUFNR").caretPosition = (8)
        session.findById("wnd[0]").sendVKey (0)
        if "modificar ordem" in str(session.ActiveWindow.Text).lower():
            texto_erro_ordem = session.findById("wnd[0]/sbar").Text
            
            # Erro de Ordem Nao existente:
            if "Não existe ordem" in texto_erro_ordem:
                fechar_SAP()
                CtrAut['Aut']['AnexarRelatSAP']['Lista_Erros'].append(
                    "Erro na Etapa De Entrar na Ordem: N° de Ordem nao existe '{}'".format(str(int(coleta['OrdServ']))))
                CtrAut['Aut']['AnexarRelatSAP']['status'] = 'Erro'
                return CtrAut
            
            if "Falta autoriz" in texto_erro_ordem:
                fechar_SAP()
                CtrAut['Aut']['AnexarRelatSAP']['Lista_Erros'].append(
                    "Erro na Etapa De Entrar na Ordem: '{}'".format(texto_erro_ordem))
                CtrAut['Aut']['AnexarRelatSAP']['status'] = 'Erro'
                return CtrAut
            
            # Ler pop-diagnose (janela)
            else:
                try:
                    # Erro Caso a "Ordem está em processamento"
                    if "Ordem está em processamento" in session.findById("wnd[1]/usr/txtSPOP-DIAGNOSE1").Text:
                        session.findById("wnd[1]/usr/btnSPOP-OPTION1").press()
                        session.findById("wnd[0]/usr/btnALL_DETAIL").press()
                        Text_erro = session.findById("wnd[0]/usr/cntlGRID1/shellcont/shell/shellcont[1]/shell").GetCellValue(0,"CMF_TEXT")
                        
                        fechar_SAP()
                        print(f'{Text_erro}, deley 1m')
                        time.sleep(60)
                        CtrAut['Aut']['AnexarRelatSAP']['Lista_Erros'].append(
                            f"{Text_erro}, Tentativa: {CtrAut['Aut']['AnexarRelatSAP']['repeticao']}")
                        CtrAut['Aut']['AnexarRelatSAP']['status'] = 'Repetir'
                        return CtrAut
                    
                    # Verificar se esta escrito outra coisa no pop-diagnose (janela)
                    else:
                        fechar_SAP()
                        CtrAut['Aut']['AnexarRelatSAP']['Lista_Erros'].append(
                            "Erro na Etapa De Entrar na Ordem: {}, , Tentativa: {} ".format(
                                session.findById("wnd[1]/usr/txtSPOP-DIAGNOSE1").Text,
                                CtrAut['Aut']['AnexarRelatSAP']['repeticao']))
                        CtrAut['Aut']['AnexarRelatSAP']['status'] = 'Repetir'
                        return CtrAut
                        
                except Exception as e:
                    fechar_SAP()
                    CtrAut['Aut']['AnexarRelatSAP']['Lista_Erros'].append(
                        f"Erro na Etapa De Entrar na Ordem: Erro Desconhecido, {str(e)}, Tentativa: {CtrAut['Aut']['AnexarRelatSAP']['repeticao']}")
                    CtrAut['Aut']['AnexarRelatSAP']['status'] = 'Repetir'
                    return CtrAut
        
        
        # Verificar se é edição caso sim, iniciar etapa de remover relatorio antigo 
        if True:
        # if "Edit" in str(coleta['ID']):
            try:
                # Abrir Lista de Anexo Para Deletar Old File
                session.findById("wnd[0]/titl/shellcont/shell").pressContextButton ("%GOS_TOOLBOX") #-> Inicia "anexar"
                session.findById("wnd[1]/usr/tblSAPLSWUGOBJECT_CONTROL/txtSWLOBJTDYN-DESCRIPT[0,1]").setFocus()
                session.findById("wnd[1]/usr/tblSAPLSWUGOBJECT_CONTROL/txtSWLOBJTDYN-DESCRIPT[0,1]").caretPosition = (7)
                session.findById("wnd[1]").sendVKey (2)
                session.findById("wnd[0]/titl/shellcont/shell").selectContextMenuItem ("%GOS_VIEW_ATTA")
                grid = session.findById("wnd[1]/usr/cntlCONTAINER_0100/shellcont/shell")
                
                # Percorrer cada Linha da tabela de Anexos e Deletar Old File
                for i in range(grid.RowCount):
                    # Se tiver os numeros do ID Arquivo
                    if str(coleta['ID'])[:12] in grid.GetCellValue(i, "BITM_FILENAME"): 
                        # Deletar
                        grid.selectedRows = str(i) 
                        grid.pressToolbarButton("%ATTA_DELETE")
                        print("Deletei Old File SAP")
                        break 
                
                # Fechar Lista de Anexo Para Deletar Old File
                session.findById("wnd[1]/tbar[0]/btn[0]").press()
                
            except Exception as e:
                fechar_SAP()
                CtrAut['Aut']['AnexarRelatSAP']['Lista_Erros'].append(
                    "Erro na Etapa, Deletar Arquivo Antigo do SAP:'{}'".format(str(e)))
                CtrAut['Aut']['AnexarRelatSAP']['status'] = 'Erro'
                return CtrAut
            
            time.sleep(1)
        
        
        # Abrir Lista de Anexos para Anexar 
        session.findById("wnd[0]/titl/shellcont/shell").pressContextButton ("%GOS_TOOLBOX") #-> Inicia "anexar"
        session.findById("wnd[1]/usr/tblSAPLSWUGOBJECT_CONTROL/txtSWLOBJTDYN-DESCRIPT[0,1]").setFocus()
        session.findById("wnd[1]/usr/tblSAPLSWUGOBJECT_CONTROL/txtSWLOBJTDYN-DESCRIPT[0,1]").caretPosition = (7)
        session.findById("wnd[1]").sendVKey (2)
        
        # Garantir que  session Ative esteja na frente para executar o VBS
        sap_hwnd = win32gui.FindWindow(None, session.ActiveWindow.Text)
        win32gui.ShowWindow(sap_hwnd, win32con.SW_MINIMIZE); time.sleep(0.5)
        win32gui.ShowWindow(sap_hwnd, win32con.SW_MAXIMIZE)
        
        # Configurar timeout Para Janela para inserir o file  
        Timeout_janela_VBS = threading.Timer(20, fechar_SAP)
        
        # Executar Abertura da janela
        try:
            Timeout_janela_VBS.start() # Iniciar Timer 
            session.findById("wnd[0]/titl/shellcont/shell").selectContextMenuItem ("%GOS_PCATTA_CREA") #-> Abre janela Windonws
        except:
            Timeout_janela_VBS.cancel() # Cancelar timer do timeout VBS 
            fechar_SAP()
            CtrAut['Aut']['AnexarRelatSAP']['Lista_Erros'].append(
                f"Erro na Etapa de inserir Relatorio na Ordem: VBS não foi executado corretamente, Tentativa: {CtrAut['Aut']['AnexarRelatSAP']['repeticao']}")
            CtrAut['Aut']['AnexarRelatSAP']['status'] = 'Repetir'
            return CtrAut
        finally:
            Timeout_janela_VBS.cancel() # Cancelar timer do timeout VBS
        
        time.sleep(3)
        
        # Verificar se foi anexado
        if not "O anexo foi criado com êxito" in session.findById("wnd[0]/sbar").Text:
            fechar_SAP()
            CtrAut['Aut']['AnexarRelatSAP']['Lista_Erros'].append(
                "Erro na Etapa De Anexar arquivo: {}, Tentativa: {}".format(session.findById("wnd[0]/sbar").Text,CtrAut['Aut']['AnexarRelatSAP']['repeticao']))
            CtrAut['Aut']['AnexarRelatSAP']['status'] = 'Repetir'
            return CtrAut
        
        Timeout_janela_SAP.cancel() # Cancelar timer do timeout SAP
        fechar_SAP()
        
        # Verificar se houve erro e atualizar status
        CtrAut['Aut']['AnexarRelatSAP']['status'] = 'OK'
        CtrAut['Aut']['AnexarRelatSAP']['Lista_Erros'] = ['']
        return CtrAut
        
       
    except Exception as e:
        wscript_exe_finish()
        print(f'Erro Geral SAP: {e}')
        fechar_SAP()
        CtrAut['Aut']['AnexarRelatSAP']['Lista_Erros'].append(f"Erro Geral: {str(e)}, Tentativa: {CtrAut['Aut']['AnexarRelatSAP']['repeticao']}")
        CtrAut['Aut']['AnexarRelatSAP']['status'] = 'Repetir'
        return CtrAut
 