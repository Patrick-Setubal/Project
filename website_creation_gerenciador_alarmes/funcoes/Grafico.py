import pandas as pd
import datetime as dt
import PIconnect as PI
import codecs
import re
import random
from numpy import (mean, min, max, abs, median, std, NaN, )
from System import TimeSpan
import pytz

DadosEntrada = r'//.../...$/.../'

nan='nan'
NaN='nan'


PI_SERVER_CONF = {
    'Q4':('serv', 'login', 'senha'),
    'PE9':('serv', 'login', 'senha'),
    'PP5':('serv', 'login', 'senha')}

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
    '00001': 'Resolvido',
    '00010': 'Atencao',
    '00100': 'Importante',
    '01000': 'Critico',
    '00000': 'Indefinido'
}
traducao_filtro = {
    'Rotativos': '_E1_',
    'Elétricos': '_E2_',
    'Instrumentos': '_E3_',
    'Estáticos': '_E4_',
    'Automação': '_E5_',

    'Silenciado': '_10000.REC',
    'Resolvido': '_00001.REC',
    'Atencao': '_00010.REC',
    'Importante': '_00100.REC',
    'Critico': '_01000.REC', 
    'Indefinido': '_00000.REC',

    'Todos': '_'
}

def Limpar_Tag(tag):
    if type(tag) != 'str':
        tag = str(tag) 
    tag = re.sub(r"[^A-Z0-9]","",tag.upper())
    tag = tag.replace('RJ08', '')
    tag = tag.replace('RJ09', '')
    return tag


def ColetarCurvas(Adress,datastart,dataend,conf, Extra_tags):  

    AdressAlarm = Adress
    try:
        Return = {'Pontos': [], 'annotations':{}}  
        infPoints = {'Tag': [], 'Descricao': [], 'Unidade': [], 'ValorAtual': [],
            'Max':[], 'Min': [], 'Std': [], 'Limites':[]}
        
        linhas = []
        for tags in Extra_tags:
            if tags != '':
                linhas.append(tags)
        
        log = Adress.split("_")
        Data_Log = pd.to_datetime(log[1],format='%Y%m%d-%H%M%S')

        limites = {}
        # Ler .REC
        try:
            with codecs.open(Adress, 'r', "utf-8") as Adress:
                try:
                    txt = eval(Adress.read())           
                    linhas = linhas + (list(txt['alarmed_values'].keys()))
                    Area = txt['planta']
                    fonte_dados = txt['fonte_dados']
                    
                    if fonte_dados == 'PI':
                        tempo_acq = float(txt['tempo_acq'][2:-1])
                        unid_tempo_acq = txt['tempo_acq'][-1:].lower()
                        
                        try:
                            val_pi_dt = float(txt['pi_dt'][:-1])
                            unid_pi_dt = txt['pi_dt'][-1:].lower()
                            pi_dt = txt['pi_dt']
                        except:
                            val_pi_dt = 1
                            unid_pi_dt = 's'
                            pi_dt = '1s'

                except Exception(e):
                    print(f'rec antigo - {e}')

        except FileNotFoundError:
                Return['status'] = "nao encontrado"
                print('--->LOG NAO ENCONTRADO<---') 


        if fonte_dados == 'PI':
            traducao_time_tempo_acq = { #converter para minutos
                    'd': tempo_acq/1440,
                    's': tempo_acq/60,
                    'm': tempo_acq,
                    'h': tempo_acq*60}

            traducao_time_pi_dt = { #converter para segundos
                's': val_pi_dt,
                'm': val_pi_dt/60,
                'h': val_pi_dt/3600}

            intervalo_minute = traducao_time_tempo_acq[unid_tempo_acq]
            intervalo_pontos_segundos = traducao_time_pi_dt[unid_pi_dt]

            #Caso os pontos plotados configurados sejam muitos 
            if ((intervalo_minute*60)/intervalo_pontos_segundos) > 2000:
                datastart = Data_Log - dt.timedelta(minutes=(traducao_time_tempo_acq[unid_tempo_acq]/2))
                dataend = Data_Log + dt.timedelta(minutes=(traducao_time_tempo_acq[unid_tempo_acq]/2))

            #Definir data Inicio Fim com base no txt
            if datastart == "definir":
                                
                #Definindo Pontos
                Start_Time = Data_Log - dt.timedelta(minutes=(traducao_time_tempo_acq[unid_tempo_acq]/2))
                End_Time = Data_Log + dt.timedelta(minutes=(traducao_time_tempo_acq[unid_tempo_acq]/2))
                interval = pi_dt
            
            #Pegar data ja definida e definir intervalo entre pontos para N_Pontos fixo
            else:
                Start_Time = pd.to_datetime(datastart, format='%Y-%m-%d %H:%M:%S')
                End_Time = pd.to_datetime(dataend, format='%Y-%m-%d %H:%M:%S')
                tempo_segundos = ((End_Time - Start_Time).value)/1000000000
                N_pontos = 2000
                interval =  str(tempo_segundos/N_pontos) + "s"

            #Limpar linhas = 
            lista_linhas = []
            for linha in linhas:                 
                if 'df' in linha: 
                    try:
                        i = re.search('df\[\"[\w\- \.]*', linha).group(0)[4:]
                        lista_linhas.append(i)
                    except:
                        lista_linhas.append(linha)
                else:
                    lista_linhas.append(linha)
            linhas = lista_linhas

            # Coletar no PI    
            server = PI_SERVER_CONF[Area][0]
            username = PI_SERVER_CONF[Area][1]
            password = PI_SERVER_CONF[Area][2]


            PI.PIConfig.DEFAULT_TIMEZONE = 'Etc/GMT+3'
            linhas = list(set(linhas))

            #Resolver Erro de TimeoutException do PI
            timeout = [0,0,30] #hours, minutes, seconds
            server_manager = PI.PIServer(server=server, username=username, password=password)
            server_manager.connection.ConnectionInfo.OperationTimeOut = TimeSpan(*timeout)


            with server_manager as server:
                points = server.search(linhas)
                df = [point.interpolated_values( Start_Time, End_Time, interval) for point in points]
                df = pd.concat(df, axis=1) 
         
                for point in points:
                    infPoints['Descricao'].append(point.description)
                    infPoints['Unidade'].append(point.units_of_measurement)
                    infPoints['ValorAtual'].append(float(str(point.current_value)))          
 
            Data_Log = Data_Log._repr_base
            
            # resolver erro de "<class 'OSIsoft.AF.Asset.AFEnumerationValue'>"
            for col in df.columns:
                if str(type(df[col][0]))=="<class 'OSIsoft.AF.Asset.AFEnumerationValue'>":
                    df[col] = df[col].astype(str)
                    
            

        # Se nao for PI
        else:
            tag_log = Limpar_Tag(log[6])
            #Ler Arquivo fonte de dados 
            fonte_f = fonte_dados.split('.')
            if 'xlsx' in fonte_dados.lower():
                arq_fonte = pd.read_excel(DadosEntrada+fonte_dados)
            if 'csv' in fonte_dados.lower():
                arq_fonte = pd.read_csv(DadosEntrada+fonte_dados)
    
            #Todos os textos em minusculo
            col_low = [col.lower() for col in arq_fonte.columns]
            arq_fonte.columns = col_low
            for x in arq_fonte.columns:
                if arq_fonte[x].dtypes == object:
                    arq_fonte[x] = arq_fonte[x].str.lower()

       
            # Limpar TAG de todos os linhas e filtrando arq_fonte
            arq_fonte['tag'] = [Limpar_Tag(fonte_linhas) for fonte_linhas in arq_fonte['tag']]
            arq_fonte = arq_fonte[(arq_fonte['tag']==tag_log)]

            # coluna data virar data
            arq_fonte['data'] = pd.to_datetime(arq_fonte['data'], format='%d/%m/%Y')

            # Ordenar por data
            arq_fonte = arq_fonte.sort_values(by=['data'])

            #filtrar data
            if datastart != "definir":
                arq_fonte = arq_fonte[(arq_fonte['data'] >= datastart) & (arq_fonte['data'] <= dataend)]  
         

            # Data como index
            arq_fonte.rename(columns = {'data':'index'}, inplace = True)
            df = (arq_fonte.set_index('index'))


            # remover colunas inuteis 
            colunas = list(df.columns)
            for col in linhas:
                colunas.remove(col)

            df = df.drop(columns=colunas)
            df.sort_index()
            
            
            Start_Time = df.index[0]
            End_Time = df.index[-1] 
            Data_Log = End_Time.strftime("%Y-%m-%d")

            for col in df.columns: 
                infPoints['Descricao'].append('Coleta Offline')
                infPoints['Unidade'].append('-')
                infPoints['ValorAtual'].append(('Coleta Offline'))  



        # Simplificar
        df.index = [ data.strftime('%Y-%m-%d %H:%M:%S') for data in df.index]

        #Limpar Dados Null, tudo float
        for col in df.columns: 
            df = df[pd.to_numeric(df[col], errors='coerce').notnull()].astype(float)
            infPoints['Tag'].append(col)
            infPoints['Max'].append(float(max(df[col])))
            infPoints['Min'].append(float(min(df[col])))
            infPoints['Std'].append(float(std(df[col])))
            # infPoints['Limites'].append(limites[col.upper()])

        linhas = [col for col in df.columns]

        datasets=[]
        scales = {}
        escalas_Y = []
        annotations = {}
        
        for i in range(len(linhas)):

            cor ='rgb('+str(random.randint(150,255))+','+str(random.randint(150,255))+','+str(random.randint(150,255))+')'
            minimo = min(list(df[linhas[i]]))
            maximo = max(list(df[linhas[i]]))
            a = (df.to_json(orient='table'))
            a = eval((a.replace('index',"x")).replace(linhas[i],"y"))
            
            grid = True if i == 0 else False

            multscala = 'Y_'+linhas[i] if conf == 'true' else 'y'
            # Criar curvas
            datasets.append({
                'type':'line',
                'borderColor':cor,
                'backgroundColor':cor,
                'borderWidth': 1,
                'label':linhas[i], 
                'data': a['data'],
                'yAxisID': multscala,
                'stepped': True,
                })


            # Multiplas Escalas
            if conf == 'true':
                escalas_Y.append({
                    multscala :{
                        'type': 'linear',
                        'display': True,
                        'title': {
                            'color': cor,
                            'display': True,
                            'text': linhas[i],
                        },
                        'grid':{
                            'display':grid,
                        },
                        'ticks':{
                            'color': 'rgba(255,255,255,0.8)',
                            'precision':4
                        },
                    }
                })


        #Organizar Json Scala
        for escala_Y in escalas_Y:     
            key = str(list(escala_Y.keys())[0])
            scales[key] = escala_Y[key]

        # Escala Eixo x
        x = {
            'type':'time',
            'time': {
                # 'parser': 'timeFormat',
                # #round: 'day',
                # 'tooltipFormat': 'YYYY-MM-DD HH:mm',
                'displayFormats': {
                    'millisecond': 'HH:mm:ss.SSS',
                    'second': 'HH:mm:ss',
                    'minute': 'HH:mm:ss',
                    'hour': 'HH:mm:ss',
                    'day': 'd MMM h:mm:ss'
                }
            #         # 'ticks': {'source':'auto',},
            },
        }

        scales['x'] = x

        annotations ={
            'Alarm': {
                'type': 'line',
                'xMin': Data_Log,
                'xMax': Data_Log,
                'borderColor': 'rgb(255,0,0,0.25)',
                'borderWidth': 3, 
            } 
        }
    


        Return['Pontos'].append(datasets)
        Return['InicioFim'] = [Start_Time.strftime("%Y-%m-%d %H:%M:%S"),End_Time.strftime("%Y-%m-%d %H:%M:%S")]
        Return['scales'] = scales
        Return['infPoints'] = infPoints 
        Return['annotations'] = annotations
        Return['Adress'] = AdressAlarm
        return(Return)

    except:
        return 'ERRO'

    
