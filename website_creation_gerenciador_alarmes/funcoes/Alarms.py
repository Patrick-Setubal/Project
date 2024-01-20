import datetime
import pandas as pd
import os
import codecs
import re
import logging
import json

logging.basicConfig(level=logging.INFO,
  filename="erros.log", \
  format="%(asctime)s ; %(levelname)s ; %(message)s"
  )

nan = "nan"
NaN = "nan"
Pasta_Alarmes = (r'//.../..$/Alarmes/')
Pasta_Verif_Alarmes_SAP = r'//.../..$/Gerenciador de Alarme/'

# Listagem de-para
Type_Espec = {
    'E1': 'Rotativos',
    'E2': 'Elétricos',
    'E3': 'Instrumentos',
    'E4': 'Estáticos',
    'E5': 'Automação',
    'E0': 'Não Identificado'
}
Nivel = {
    '10000': 'Silenciado',
    '00001': 'Normal',
    '00010': 'Nivel 1',
    '00100': 'Nivel 2',
    '01000': 'Nivel 3',
    '00000': 'Indefinido'
}
traducao_filtro = {
    'Rotativos': '_E1_',
    'Elétricos': '_E2_',
    'Instrumentos': '_E3_',
    'Estáticos': '_E4_',
    'Automação': '_E5_',

    'Silenciado': '_10000.REC',
    'Normal': '_00001.REC',
    'Nivel 1': '_00010.REC',
    'Nivel 2': '_00100.REC',
    'Nivel 3': '_01000.REC', 
    'Indefinido': '_00000.REC',

    'Todos': '_'
}
traducao = {
    'Rotativos': 'E1',
    'Elétricos': 'E2',
    'Instrumentos': 'E3',
    'Estáticos': 'E4',
    'Automação': 'E5',

    'Silenciado': '10000.REC',
    'Normal': '00001.REC',
    'Nivel 1': '00010.REC',
    'Nivel 2': '00100.REC',
    'Nivel 3': '01000.REC', 
    'Indefinido': '00000.REC',

    'Todos': 'Todos',
    '': 'Todos'
}


def watchdog():
    timefile = r'//.../..$/Painel Web/Painel Py/exec.txt'
    with codecs.open(timefile, 'r', "utf-8") as timefile:   
        timefile = timefile.read()
        
        Now = datetime.datetime.now()
        Ultima = datetime.datetime.strptime(timefile, "%d/%m/%y %H:%M:%S")
        Intervalo = datetime.timedelta(minutes=15)

        if (Now - Ultima) > Intervalo:
            return  ['Falha',timefile]
        else:
            return  ['Funcionando',timefile]

def F_filtro_todos (Filtro):
    if Filtro == 'TODOS' or Filtro == '':
        Filtro = "Todos"
    else:
        Filtro = Filtro
    return Filtro

def Filtro_E_Coleta_Dos_Logs (
    n,
    pag,
    Filtro_data_inicial,
    Filtro_data_final,
    Filtro_especs,
    Filtro_sistemas,
    Filtro_modfalha,
    Filtro_tag,
    Filtro_nivels,
    Exportar_Excel):

    

    current_time1 = datetime.datetime.now()
    
    

    #Tratamento de erro e tradução dos dados 
    try:
        Filtro_data_inicial = pd.to_datetime(Filtro_data_inicial + " 00:00:00:000000", format='%Y-%m-%d %H:%M:%S:%f')
        Filtro_data_final = pd.to_datetime(Filtro_data_final + " 23:59:59:999999", format='%Y-%m-%d %H:%M:%S:%f')
    except:
        Filtro_data_inicial = current_time1
        Filtro_data_final = current_time1
    
    Filtro_espec = [traducao[Filtro_espec] for Filtro_espec in Filtro_especs]
    Filtro_nivel = [traducao[Filtro_nivel] for Filtro_nivel in Filtro_nivels]
   
    Filtro_sistema = [F_filtro_todos(Filtro_sistema.upper()) for Filtro_sistema in Filtro_sistemas] 
    Filtro_modfalha = F_filtro_todos(Filtro_modfalha.upper())
    Filtro_tag = F_filtro_todos(Filtro_tag.upper())


    Retrurn ={"DataHora":[],"Especialidade":[],
        "TAG":[],"NivelAlarme":[],
        "Sistema":[],"ModoDeFalha":[],
        "Adress": [],"Sistemas_List": [],}

    lista_Logs = []
    erros = []
    dirs_list=[]

    # Coletar Logs Pasta principal
    for root, dirs, files in os.walk(Pasta_Alarmes, topdown=False):
        if len(dirs)>5:
            dirs_list.extend(dirs)       
        for log in files: 
            log = (root+"/"+log)         
            #Limpar dados 
            if ("LOG" in log) and (log.count('_') == 7):
                lista_Logs.append(log)
            else:
                erros.append(log)

    
    #Criar ordenar e formatar DF
    df = [(lista_Logs[i].split("_")[1:]) + [lista_Logs[i]] for i in range(len(lista_Logs))]
    df = pd.DataFrame(df,columns=['DataHora','Ativo','Especialidade','Sistema','ModoDeFalha','TAG','NivelAlarme','Adress'])
    df = df.sort_values(by=['DataHora'],ascending=False) 
    df['DataHora'] = pd.to_datetime(df['DataHora'])
    
    # Criar Lista de Sistema
    List_Sistema = sorted(list(set(list(df['Sistema']))))

    #Filtrar
    df = df[(df['DataHora']>Filtro_data_inicial._repr_base) & (df['DataHora']<Filtro_data_final._repr_base)]
    
    if Filtro_espec[0] != 'Todos':
        df = df.loc[df['Especialidade'].isin(Filtro_espec)]

    if Filtro_sistema[0] != 'Todos':
        df = df.loc[df['Sistema'].isin(Filtro_sistema)]

    if Filtro_nivel[0] != 'Todos':
        df = df.loc[df['NivelAlarme'].isin(Filtro_nivel)]

    if Filtro_modfalha != 'Todos':
        df = df[(df['ModoDeFalha'].str.contains(Filtro_modfalha))]

    if Filtro_tag != 'Todos':
        df = df[(df['TAG'].str.contains(Filtro_tag))]    
    

    #Quantificar tipos de alarmes
    N_Alarme_Por_Niveis = df['NivelAlarme'].value_counts()


    #Definir Paginações
    n2 = pag*n
    n1 = n2-n
    nt = len(df)
    nl = round((nt/n)+0.5)



    #Caso Seja Para Exportar
    if Exportar_Excel == 'true':
        df_Export = df # Copiar Df para Export

        if len(df_Export)<15000:
            df_Export[['criticidade', 'planta', 'unidade', 'area', 'fonte_dados', # Criar Novas Colunas
            'tempo_acq', 'pi_tipo_acq', 'pi_dt', 'expr_alarme', 'alarmed_values', 'comentario']] = None 

            
            # Percorrer Todas as linhas do Df e Abri o arquivo log
            for i, log in df.iterrows():
                file = log['Adress']
                try:
                    with codecs.open(file, 'r', "utf-8") as file:   
                        txt = file.read()
                    txt = eval(txt)


                    if not 'comentario' in txt:
                        txt['comentario'] = 'nan'

                    # Prenecher colunas Criadas
                    df_Export.loc[[i],[
                        'criticidade', 'planta', 'unidade', 'area', 'fonte_dados', 
                        'tempo_acq', 'pi_tipo_acq', 'pi_dt', 'expr_alarme', 'alarmed_values',
                        'comentario']]      =      [str(txt['criticidade']), str(txt['planta']), 
                        str(txt['unidade']), str(txt['area']), str(txt['fonte_dados']), str(txt['tempo_acq']), 
                        str(txt['pi_tipo_acq']), str(txt['pi_dt']), str(txt['expr_alarme']), str(txt['alarmed_values']), 
                        str(txt['comentario'])]     
                except:
                    None
        else:
            df_Export[['OBS']] = "Demais colunas so serão exportadas se tiver menos de 15 mill alarmes" 

        df_Export = df_Export.drop(columns=['Adress'])
        df_Export['DataHora'] = [Val.strftime("%d/%m/%Y %H:%M:%S") for Val in df_Export['DataHora']]
        df_Export['Especialidade'] = [Type_Espec[esp] for esp in df_Export['Especialidade']]
        df_Export['NivelAlarme'] = [Nivel[nivel[:5]] for nivel in df_Export['NivelAlarme']]
        df_Export = df_Export.to_dict(orient='records')


    # Criar Grafico de Barra com os 5 maiores modo de falha 
    contagem = df['ModoDeFalha'].value_counts().head(5) # Separar os 5 maiores
    porcentagens = contagem / len(df) * 100 # Criar Calculo de porcentagem
    Graf_por_ModoDeFalha = {'Modo de Falha': list(contagem.index), 'Porcentagem': list(porcentagens), 'Repeticao': list(contagem), 'Outros':len(df)-sum(list(contagem))}

    #Limitar Visualização
    df = df[:][n1:n2]

    #Formatar dados
    df['DataHora'] = [Val.strftime("%d/%m/%Y %H:%M:%S") for Val in df['DataHora']]
    df['Especialidade'] = [Type_Espec[esp] for esp in df['Especialidade']]
    df['NivelAlarme'] = [Nivel[nivel[:5]] for nivel in df['NivelAlarme']]
    
    #Converter e Formatando Niveis
    N_Alarme_Por_Niveis = N_Alarme_Por_Niveis.to_dict()
    Alarm_Keys = [Nivel[key[:5]] for key in list(N_Alarme_Por_Niveis.keys())]
    N_Alarme_Por_Niveis = dict(zip(Alarm_Keys, list(N_Alarme_Por_Niveis.values()) )) 

    
    #Converter DF para Json
    df = df.to_dict(orient='list')
    df['ContagemLogs'] = [n1, n2, nt, nl]
    df['List_Sistema'] = List_Sistema  
    
    #Caso Seja Para Exportar
    if Exportar_Excel == 'true':
        df['Json_Excel'] = df_Export 

    df['watchdog'] = watchdog()


    return(df, N_Alarme_Por_Niveis, Graf_por_ModoDeFalha)

def LerMultLog(files):
    
    InLog ={
            "DataHora": [],
            "Especialidade": [],
            "Sistema": [],
            "ModoDeFalha": [],
            "TAG": [],
            "NivelAlarme": [],
            "tempo_acq": [],
            "Comentario":[],
            "Logica_Alarme":[],
            "TAG_Valor":[],
            "fonte_dados":[],

            "criticidade":[],
            "planta":[],
            'unidade':[], 
            'area': []
            }

    for file in files:
        fileNew = file

        log = file.split("_")
        Data_Log = pd.to_datetime(log[1])
        Espec_Log = Type_Espec[log[3]]
        Sistema_Log = log[4]
        ModoDeFalha_Log = log[5]
        Tag_Log = log[6]
        Nivel_Log = Nivel[log[7][:5]]

        try:
            # with open(fileNew,'r') as fileNew:
            with codecs.open(fileNew, 'r', "utf-8") as fileNew:   
                txt = fileNew.read()
            
            txt = eval(txt)
            
            InLog["DataHora"].append(((Data_Log).strftime("%d/%m/%Y %H:%M:%S"))),
            InLog["Especialidade"].append(Espec_Log),
            InLog["Sistema"].append(Sistema_Log),
            InLog["ModoDeFalha"].append(ModoDeFalha_Log),
            InLog["TAG"].append(Tag_Log),
            InLog["NivelAlarme"].append(Nivel_Log),
            try:
                InLog['TAG_Valor'].append(str(txt['alarmed_values'])[1:-1]) 
            except:
                InLog['TAG_Valor'].append("")
            try:
                InLog['Logica_Alarme'].append(txt['expr_alarme'])
            except:
                InLog['Logica_Alarme'].append("")
            
            try:
                InLog['fonte_dados'].append(txt['fonte_dados'])
            except:
                InLog['fonte_dados'].append('')
            
            try:
                if 'comentario' in txt.keys():
                    InLog['Comentario'].append(txt['comentario'])
                else:
                    InLog['Comentario'].append('')
            except:
                InLog['Comentario'].append('')

            try:
                InLog['criticidade'].append(txt['criticidade'])
            except:    
                InLog['criticidade'].append('')

            try:    
                InLog['planta'].append(txt['planta'])
            except:     
                InLog['planta'].append('')

            try:         
                InLog['unidade'].append(txt['unidade'])
            except:     
                InLog['unidade'].append('')

            try: 
                InLog['area'].append(txt['area'])
            except:     
                InLog['area'].append('')
            
            try:
                InLog['tempo_acq'].append(txt['tempo_acq'])
            except:
                InLog['tempo_acq'].append('')
            
        except: #Log antigo
            try:
                with open(file,'r') as file:
                    try:
                        txt = file.read()
                    except:
                        txt='Comentario: Nao Foi Possivel Ler o Arquivo Alarme\n \n \n'

                inicio = txt.find("Comentario:")+12
                txt = str(txt[inicio:]).splitlines()
                
                InLog["DataHora"].append(((Data_Log).strftime("%d/%m/%Y %H:%M:%S"))),
                InLog["Especialidade"].append(Espec_Log),
                InLog["Sistema"].append(Sistema_Log),
                InLog["ModoDeFalha"].append(ModoDeFalha_Log),
                InLog["TAG"].append(Tag_Log),
                InLog["NivelAlarme"].append(Nivel_Log),

                InLog['tempo_acq'].append('')
                
                try:
                    InLog['Comentario'].append(txt[0])
                except:
                    InLog['Comentario'].append([""])

                try:
                    InLog['Logica_Alarme'].append(txt[1])
                except:
                    InLog['Logica_Alarme'].append([""])
                
                try:
                    InLog['TAG_Valor'].append(txt[2][4:])
                except:
                    InLog['TAG_Valor'].append([""])
            except FileNotFoundError:
                InLog = "ERRO"
                print('--->LOG NAO ENCONTRADO<---') 

    

    
    return InLog

def AlterarMultLog(files, expr_alarme, alarmed_values,comentario,input_nivel,OldComentario,user):

    n=0
    for i in range (len(files)):
        
        try:
            file_path = files[i]
            oldfile_path = file_path
            newfile_path = file_path[:-10] + traducao_filtro[input_nivel[0]]
            # Rec Modelo Novo
            try:
                with codecs.open(oldfile_path, 'r', "utf-8") as file:
                    txt = file.read()
                txt = eval(txt)
            except:
                txt={}
                txt['expr_alarme'] = str(expr_alarme)
                txt['alarmed_values'] = str(alarmed_values)

            DataNow = datetime.datetime.now().strftime("%d/%m/%Y")
            txt['comentario'] = f'{str(OldComentario[i])[:]}     ({DataNow} {user[0]}) {str(comentario)[2:-2]} '
            
            # Salva arquivo .REC
            with codecs.open(newfile_path, 'w', "utf-8") as f:
                f.write(str(txt)) 

            if newfile_path != oldfile_path:
                os.remove(oldfile_path)
            n+=1

        except:
            print("ERRO--------->{}".format(files[i]))


    return(n)

def Verif_Alarme_SAP(inp):
    tag = inp['TAG'][0].replace("*",".*")

    # Pegar Df e Filtrar 
    df = pd.read_csv(Pasta_Verif_Alarmes_SAP+"Resumo Nota-Alarme.csv", sep=';', error_bad_lines=False)
    df = df[df['TAG SAP'].str.contains(tag)]
    
    # Tratar formato
    df = df.astype(str) 
    df = df.to_dict(orient="records")

    # Coletar Data da Atualização
    with open(Pasta_Verif_Alarmes_SAP+"conf.txt","r") as txt:
        datas = json.loads(txt.read())

    result = {
        'dados_SAP': df,
        'dados_datas': datas
        }

    return result
