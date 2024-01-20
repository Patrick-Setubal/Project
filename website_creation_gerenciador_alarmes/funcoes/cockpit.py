# ------------------------------------------------ Importações
import pandas as pd 
import json
from datetime import datetime
import base64
import os

from fpdf import FPDF
import codecs
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ------------------------------------------------ Variaveis
adress_csv_cockpit = r'//.../...$/Gerenciador de Alarme/cockpit.xlsx'
adress_csv_sap = r'//.../...$/Gerenciador de Alarme/Resumo Nota-Alarme.csv'
adress_txt_conf_sap = r'//.../...$/Gerenciador de Alarme/conf.txt'
UPLOAD_FOLDER = './static/img/RelatorioCGA'

# ------------------------------------------------ Funções
# Coletar dados da planilha SAP e transformar em um Dicionario
def Get_dic_sap_cockipt(especialidade):
    
    #################################### Coletar dados do SAP
    # Coletar Data do txt
    try:
        with open(adress_txt_conf_sap,"r") as txt:
            datas = json.loads(txt.read()) # datas da ultima coleta dos dados
        datas = datas['Data_Get_SAP']
    except:
        datas = 'erro'

        
    # Coletar Dados da planilha SAP
    try:
        df_SAP = pd.read_csv(adress_csv_sap, sep=";", encoding='latin1')

        # Filtrar apenas RCP Tratando dados do SAP
        df_SAP = df_SAP[df_SAP['Descricao Curta'].str.startswith("RCP")]
        
        # Ordenar Por data Vencida, criar coluna boleana de datas vencidas
        df_SAP['Conclusao Desejada'] = pd.to_datetime(df_SAP['Conclusao Desejada'], format='%d.%m.%Y')
        df_SAP['Vencida'] = ['Sim' if x < datetime.now() else 'Nao' for x in df_SAP['Conclusao Desejada']]
        df_SAP.sort_values(by=['Conclusao Desejada'], inplace=True)

        # Criar Coluna com Especialidade
        df_SAP.loc[df_SAP['Centro de Trabalho'].str.contains('SUME|SULU|SUCA'),'Especialidade'] = 'Mecânica'
        df_SAP.loc[df_SAP['Centro de Trabalho'].str.contains('SUIN'),'Especialidade'] = 'Instrumentação'
        df_SAP.loc[df_SAP['Centro de Trabalho'].str.contains('SUEL|SLAB'),'Especialidade'] = 'Elétrica'
        df_SAP['Especialidade'].fillna('Eletrica', inplace=True) 

        # Filtrar por especialidade
        df_SAP = df_SAP[df_SAP['Especialidade'] == especialidade]

        # Tratando erro no caso de df vazio
        # Se tiver linhas no DF SAP
        if len(df_SAP)>0:
            # Criar Coluna com Unidade
            df_SAP.loc[df_SAP['Centro de Trabalho'].str.startswith('RJ09'),'Unidade'] = 'PP5'
            df_SAP.loc[df_SAP['Centro de Trabalho'].str.endswith('P'),'Unidade'] = 'PE9'
            df_SAP['Unidade'].fillna('Q4', inplace=True) 
        # Caso não tenha linhas
        else:
            # Criar coluna com Unidade vazio para nao sair do padrão
            df_SAP.insert(0,'Unidade', None)

        # Ordenar Colunas
        df_SAP = df_SAP[['Nota', 'TAG SAP', 'Descricao Curta', 'Conclusao Desejada', 'Vencida',
            'Status Sistema',  'Notificador', 'Ordem', 'Data Nota', 
            'Descricao Longa', 'Criador', 'TP', 'Prioridade', 'A',
            'Centro de Trabalho', 'Fim avaria',  'Falha',
            'Status Usuario', 'GPM', 'Unidade']]
    except:
        df_SAP = pd.DataFrame(columns=['Nota', 'TAG SAP', 'Descricao Curta', 'Conclusao Desejada', 'Vencida',
            'Status Sistema',  'Notificador', 'Ordem', 'Data Nota', 
            'Descricao Longa', 'Criador', 'TP', 'Prioridade', 'A',
            'Centro de Trabalho', 'Fim avaria',  'Falha',
            'Status Usuario', 'GPM', 'Unidade'])

        datas = 'erro'
    

    #################################### Coletar dados Cockpit 
    # Coletar dados do cockpit
    df_cockpit = pd.read_excel(adress_csv_cockpit, dtype=str )
            
    # Filtrar os dados por especialidade e os nao encerrados
    df_cockpit = df_cockpit[df_cockpit['especialidade'] == especialidade]
    df_cockpit = df_cockpit[df_cockpit['data_encerrada'] == '-']


    #################################### Melhorar DF SAP com dados do Cockpit
    # Uniformizar dataframes
    df_cockpit = df_cockpit.astype(str)
    df_SAP = df_SAP.astype(str)

    # Colocar coluna Status do cockpit no dataframe do sap
    df_SAP['status_cockpit'] = pd.merge(df_SAP, df_cockpit, how='left', left_on='Nota', right_on='nota_sap')['status'].to_list()
    df_SAP['status_cockpit'] = df_SAP['status_cockpit'].fillna('-')

    #################################### Melhorar DF cockpit com dados do SAP
    df_cockpit['conclucao_nota_SAP'] = pd.merge(df_SAP,
                        df_cockpit,
                        how='right',
                        left_on='Nota',
                        right_on='nota_sap')['Conclusao Desejada'].to_list()

    df_cockpit['conclucao_nota_SAP'] = df_cockpit['conclucao_nota_SAP'].fillna('-')

    #################################### Transformar df cockpit em JSON/DIC cockpit
    dic_cockpit = {} # Iniciar variavel do dicionario do cockpit
    dic_sort_tag = {}

    # Separar em Df_cockpit's por unidade
    group_unidade = df_cockpit.groupby(by=['unidade'])
    for unidade, df_unidade in group_unidade:
        # Ordenando por tag 
        df_unidade.sort_values(by=['tag'], inplace=True)

        #Criando Key unidade
        dic_cockpit[unidade] = {}

        #Criando tag_cod_list
        tag_cod_list = []

        # Colotar o tag e todas as informações pertinentes 
        for i, line in df_unidade.iterrows():
            dic_cockpit[unidade][line['id']] = {
                'nivel_criticidade': line.nivel_criticidade,
                'status': line.status,
                'data_atualizada': line.data_atualizada,
                'detalhamentos_data': line.detalhamentos_data.split("&"),
                'detalhamentos_user': line.detalhamentos_user.split("&"),
                'detalhamentos': line.detalhamentos.split("&"),
                'data_abertura': line.data_abertura,
                'data_encerrada': line.data_encerrada,
                'tag': line.tag,
                'especialidade': line.especialidade,
                'img': line.img.split("&"),
                'nota_sap': line.nota_sap,
                'conclucao_nota_SAP': line.conclucao_nota_SAP 
            }
            # Preenchendo uma lista de lista com o tag e o codigo
            tag_cod_list.append([line['tag'], line['id']])
        # Ordenando por tag para obter a lista de codigos na ordem correta 
        dic_sort_tag[unidade] = sorted(tag_cod_list)   



    #################################### Transformar df SAP em JSON/DIC SAP
    dic_indicador= {} 
    for Unidade in df_SAP['Unidade'].unique():
        df_sap_filtred = df_SAP[df_SAP['Unidade'] == Unidade]

        dic_indicador[Unidade] = {
            'total': len(df_sap_filtred),
            'vencidas': len(df_sap_filtred[df_sap_filtred['Vencida'] == 'Sim']),
            'abertas': len(df_sap_filtred[df_sap_filtred['Vencida'] == 'Nao'])
        }
        

    # Tratar formato
    df_SAP = df_SAP.astype(str) 
    dic_SAP = df_SAP.to_dict(orient="records")


    return dic_SAP, datas, dic_indicador , dic_cockpit, dic_sort_tag


# Editar String que na verdade é lista separado em &
def EditarStringList(oldtexto, index, newPart, tipo='str'):
    # Se for data tratar formato
    if tipo == 'data':
        data = datetime.strptime(newPart, '%Y-%m-%dT%H:%M')
        newPart = data.strftime('%d/%m/%Y %H:%M')

    # Separo o texto antigo
    lista = oldtexto.split('&')

    # Altero valor usando o index
    if isinstance(index, int):
        lista[index] = newPart
    else:
        if lista == ['']:
            lista = [newPart]
        else:
            lista.append(newPart)

    # Transformo em texto novamente 
    newText = '&'.join(lista)

    return newText

# ------------------------------------------------ Função Principal
# Coletar dados da planilha com dados do RelatorioCGA
def ColetarDados(especialidade):

    # Pegar dados SAP e Cockpit
    dic_SAP, Data_Get_SAP, dic_indicador, dic_cockpit, dic_sort_tag = Get_dic_sap_cockipt(especialidade)
    
    retorno = {
        'SAP':{
            'dic_SAP': dic_SAP,
            'Data_Get_SAP': Data_Get_SAP,
            'dic_indicador': dic_indicador
            },
        'dic_cockpit': dic_cockpit,
        'dic_sort_tag': dic_sort_tag
    }
    
    return retorno

# Alterar PLanilha com dados do RelatorioCGA
def SolicitarAlteracao(inp):
    # Definir Variaveis
    mode = inp['mode'][0]

    # Pegar dados
    df_cockpit = pd.read_excel(adress_csv_cockpit)

    # Definir index da planilha a ser alterado ou criado 
    if inp['id'][0] != '':
        # Se tiver Encontrar o index e definilo 
        id_line = df_cockpit[df_cockpit['id']==inp['id'][0]].index[0]
        
    else:
        # Se n tiver Acrescentar um no final
        id_line = len(df_cockpit)

    # Impedir Duplicidade de nota_sap
    if len(df_cockpit[(df_cockpit.index != id_line) & (df_cockpit['nota_sap'] == inp['nota_sap'][0])])>0:
        return ['Error','Esta Nota já esta sendo associado']
    # print(df_dupli_nota[df_dupli_nota['nota_sap'] == inp['nota_sap'][0] ]

    # Se for mesmo tag usar linha existente caso contratio criar outra 
    df_filter = df_cockpit.loc[id_line] if mode == 'Edit' or mode == 'New_detalhamento' else {}

    # Editar Valores editaveis simples
    df_filter['especialidade'] = inp['especialidade'][0]
    df_filter['unidade'] = inp['unidade'][0]
    df_filter['tag'] = inp['TAG'][0]
    df_filter['nivel_criticidade'] = inp['Criticidade'][0]
    df_filter['status'] = inp['Status'][0]
    df_filter['nota_sap'] = inp['nota_sap'][0] 

    # Definir index da lista dos detalhamentos se e o ultimo ou um do meio
    index_list = int(inp['index_list'][0]) if mode == 'Edit' else 'append'

    if mode == 'New_TAG':
        # Editar Valores formatos de lista
        df_filter['id'] = datetime.today().strftime('%y%m%d-%H%M%S-%f')
        df_filter['detalhamentos'] = inp['Detalhamento'][0] 
        df_filter['detalhamentos_data'] = datetime.strptime(inp['Data'][0], '%Y-%m-%dT%H:%M').strftime('%d/%m/%Y %H:%M') 
        df_filter['detalhamentos_user'] = inp['Usuario'][0] 
        df_filter['data_encerrada'] = '-'
        df_filter['data_abertura'] = datetime.strptime(inp['Data'][0], '%Y-%m-%dT%H:%M').strftime('%d/%m/%Y %H:%M')
        df_filter['img'] = 'vazio.png'
        
     
    else:
        # Editar Valores formatos de lista
        df_filter['detalhamentos'] = EditarStringList(df_filter['detalhamentos'], index_list, inp['Detalhamento'][0]) 
        df_filter['detalhamentos_data'] = EditarStringList(df_filter['detalhamentos_data'], index_list, inp['Data'][0], tipo='data')
        df_filter['detalhamentos_user'] = EditarStringList(df_filter['detalhamentos_user'], index_list, inp['Usuario'][0])
        
    if inp['Concluir'][0] == 'true':
        df_filter['data_encerrada'] = datetime.strptime(inp['Data'][0], '%Y-%m-%dT%H:%M').strftime('%d/%m/%Y %H:%M')


    # Converter no formato correto para datas 
    Data = datetime.strptime(inp['Data'][0], '%Y-%m-%dT%H:%M')
    df_filter['data_atualizada'] = Data.strftime('%d/%m/%Y %H:%M')

    df_cockpit.loc[id_line] = df_filter
    
    df_cockpit = df_cockpit.astype(str)
    df_cockpit.to_excel(adress_csv_cockpit, index=False)

    return ['ok','Sucesso']

# Gerar Relatorio em PDF
def CreateReport(inp):
    
    width_page = 190

    # Coletar DF
    df = pd.read_excel(adress_csv_cockpit, dtype=str)


    # Coletar DF SAP e Somar com df
    try:
        df_SAP = pd.read_csv(adress_csv_sap, sep=";", encoding='latin1', dtype=str)

        # Filtrar apenas RCP Tratando dados do SAP
        df_SAP = df_SAP[df_SAP['Descricao Curta'].str.startswith("RCP")]
        
        # Criar Coluna Vencida
        df_SAP['Vencida'] = ['Sim' if x < datetime.now() else 'Nao' for x in 
                pd.to_datetime(df_SAP['Conclusao Desejada'], format='%d.%m.%Y')]
        
        # Criar Coluna com Especialidade
        df_SAP.loc[df_SAP['Centro de Trabalho'].str.contains('SUME|SULU|SUCA'),'Especialidade'] = 'Mecânica'
        df_SAP.loc[df_SAP['Centro de Trabalho'].str.contains('SUIN'),'Especialidade'] = 'Instrumentação'
        df_SAP.loc[df_SAP['Centro de Trabalho'].str.contains('SUEL|SLAB'),'Especialidade'] = 'Elétrica'
        df_SAP['Especialidade'].fillna('Eletrica', inplace=True) 

        # Criar Coluna com Unidade
        df_SAP.loc[df_SAP['Centro de Trabalho'].str.startswith('RJ09'),'Unidade'] = 'PP5'
        df_SAP.loc[df_SAP['Centro de Trabalho'].str.endswith('P'),'Unidade'] = 'PE9'
        df_SAP['Unidade'].fillna('Q4', inplace=True) 
        
        # Procv entre pranilhas DF receber Conclusao Desejada
        df['Conclusao Desejada'] = pd.merge(
            df,                     # Df left
            df_SAP,                 # Df Right
            how='left',             # keep o Df left 
            left_on='nota_sap',     # key do df Left
            right_on='Nota'         # key do df right 
            )['Conclusao Desejada'].to_list()  #Get Coll, #form List to eliminate index
                         
        # Limpar dados        
        df['Conclusao Desejada'] = df['Conclusao Desejada'].fillna('-')
        df['Conclusao Desejada'] = df['Conclusao Desejada'].str.replace('.', '/', regex=True)

        # Procv entre pranilhas DF_SAP receber Status CGA
        df_SAP['Status CGA'] = pd.merge(
            df_SAP,                 # Df left
            df,                     # Df Right
            how='left',             # keep o Df left 
            left_on='Nota',     # key do df Left
            right_on='nota_sap'         # key do df right 
            )['status'].to_list()  #Get Coll, #form List to eliminate index

        df_SAP['Status CGA'] = df_SAP['Status CGA'].fillna('-')
        

    except:
        df['Conclusao Desejada'] = '-'

    # Renomear colunas 
    df.columns = ['ID','Especialidade','Unidade','TAG','Criticidade','Nota SAP' ,'Status','Data Atualização','Datas Detalhamentos','User Detalhamentos','Comentario','Data Abertura','Data Encerramento','img', 'Conclusão Desej.']
   

    # Remover Encerradas
    df = df[df['Data Encerramento'] == '-']

    # Filtrar Selected
    df = df[df['Especialidade'].isin(inp['Export_pdf_especialidade'])]
    df = df[df['Unidade'].isin(inp['Export_pdf_unidade'])]
    df = df[df['Criticidade'].isin(inp['Export_pdf_criticidade'])]

    # Transformar todos em formato data
    data_inicial = pd.to_datetime(inp['Export_pdf_data_abertura_init'],  format='%Y-%m-%dT%H:%M')
    data_final = pd.to_datetime(inp['Export_pdf_data_abertura_fim'],  format='%Y-%m-%dT%H:%M')
    df['Data Abertura'] = pd.to_datetime(df['Data Abertura'],format='%d/%m/%Y %H:%M')

    # Filtrar Data e transformar em str no formato desejado novamente
    df = df[(df['Data Abertura'] >= data_inicial[0]) & (df['Data Abertura'] <= data_final[0])]
    df['Data Abertura'] = df['Data Abertura'].dt.strftime("%d/%m/%Y %H:%M")

    # Ordenar
    df.sort_values(by=['Unidade', 'Especialidade', 'TAG'], inplace=True)

    # Criar PDF
    dic_link = {}
    class PDF(FPDF):
        def header(self):
            # Logo
            logo = r'./funcoes/files/logo.png'
            self.image(logo, 10, 8, 40,link=pdf.add_link(page=1))
            
            # Title
            self.set_font('Arial', 'b', 16)
            self.cell(0, 10, 'Relatorio CGA', ln=1, align='C')
            
            # SubTitle
            self.set_font('Arial', '', 8)
            self.set_text_color(153, 153, 102)
            self.cell(0, 4, '03/07/2023 16:16:03', ln=1, align='C')
            pdf.ln(3)
            
        def footer(self):
            # Set possition of the footer
            self.set_y(-15)
            self.set_font('Arial', 'I', 10)
            self.cell(0, 5, f'Page {self.page_no()}/{{nb}}', align='C')
            self.image(r'./funcoes/files/icon/Arrow Up.png', w=5, h=5, link=pdf.add_link(page=1))
            
        def sumario(self):
            ######################################## Criar Sumario
                #Title Sumario
            self.set_text_color(0, 0, 0)
            self.set_font('arial', 'b', 12)
            self.cell(0, 10, 'Sumario', align='C', ln=True) 
            self.ln(3)

            #Criar Sumario
            for unidade, df_unidade in df.groupby('Unidade'):
                # Title Unidade
                self.set_font('Arial', 'b', 12)
                self.set_text_color(0, 0, 0)
                x, y= self.get_x(), self.get_y()
                self.cell(0, 8, unidade, ln=1, border='L') 
                self.set_xy(x=x,y=y)
                self.cell(0, 8, '', ln=1, border='T') 
                
                for especialidade, df_especialidade in df_unidade.groupby('Especialidade'):
                    # Title Especialidade
                    self.set_font('Arial', 'b', 10)
                    self.set_text_color(0, 0, 0)
                    x, y= self.get_x(), self.get_y()
                    self.cell(0, 8, " "*7+especialidade, ln=1, border='L')


                    # Valores Tags
                    for i, line in df_especialidade.iterrows():
                        # configuraçãoes  icone Status
                        self.set_font('couriernew', '', 8) # Formatação do Texto
                        dic_link[line['TAG']] = self.add_link() # Definir Link
                        adress_icon = f"./funcoes/files/icon/{line['Status']}_{line['Criticidade'][-1]}.png" # Definir Icone

                        # configuraçãoes  icone Status_SAP
                        if line['Conclusão Desej.'] == '-':
                            adress_icone_SAP = "./funcoes/files/icon/NaoAssociado.png"
                            texto_SAP = 'Sem Nota SAP'
                        else:
                            if datetime.now() > pd.to_datetime(line['Conclusão Desej.'], format='%d/%m/%Y'):
                                adress_icone_SAP = "./funcoes/files/icon/EmAtraso.png"
                                texto_SAP = 'Nota em Atraso'
                            else:
                                adress_icone_SAP = "./funcoes/files/icon/EmDia.png"
                                texto_SAP = 'Nota em Dia'



                        # Escrever dados
                        self.cell(width_page/4, 5, " "*7+line['TAG'], link= dic_link[line['TAG']], border='L')
                        self.cell(width_page/4, 5, " "*7+line['Data Atualização'], link= dic_link[line['TAG']], align='L')

                        self.set_x(x=self.get_x()+5) 
                        x, y= self.get_x()+6, self.get_y()
                        self.image(adress_icone_SAP, w=4 ,h=4, link=dic_link[line['TAG']])
                        self.set_xy(x=x,y=y)
                        self.cell(30, 5, texto_SAP, link=dic_link[line['TAG']])
                        

                        x, y= self.get_x()+6, self.get_y()
                        self.image(adress_icon, w=4 ,h=4, link=dic_link[line['TAG']])
                        self.set_xy(x=x,y=y)
                        self.cell(30, 5, line['Status'],ln=1, link=dic_link[line['TAG']])


                    # Criar Sumario da Tabela SAP
                    ID_Name = 'SAP-'+unidade+'-'+especialidade 
                    dic_link[ID_Name] = self.add_link() # Definir Link

                    # Filtrar df por Unidade e especialidade e definir quantas vencidas e quantas em dia.
                    df_filtered = df_SAP[(df_SAP['Unidade']==unidade) & (df_SAP['Especialidade']==especialidade)] 
                    Dic_Vencidas = df_filtered.groupby(['Vencida'])['Vencida'].count().to_dict()
                    
                    # Tratar erro caso nao tenha Alguma das Keys e ja escrever textos 
                    Dic_Vencidas['Sim'] = 0 if not 'Sim' in Dic_Vencidas else Dic_Vencidas['Sim']
                    Dic_Vencidas['Nao'] = 0 if not 'Nao' in Dic_Vencidas else Dic_Vencidas['Nao']

                    text_2 = 'Notas Abertas:'+str(Dic_Vencidas['Nao']+Dic_Vencidas['Sim'])
                    text_3 = 'Notas Em Dia:'+str(Dic_Vencidas['Nao'])
                    text_4 = 'Notas Vencidas:'+str(Dic_Vencidas['Sim'])
                    
                    # Escrever No pdf
                    self.cell(width_page/4, 5, " "*7+'Notas SAP', link= dic_link[ID_Name], border='L')
                    self.cell(width_page/4, 5, " "*7+text_2 , link= dic_link[ID_Name], align='L')

                    self.set_xy(x=self.get_x()+5+6, y=self.get_y())
                    self.cell(30, 5, text_3 , link= dic_link[ID_Name])
                    
                    self.set_xy(x=self.get_x()+6, y=self.get_y())
                    self.cell(30, 5, text_4,ln=1, link=dic_link[ID_Name])
                    

                self.ln(3)
                
                    
            self.add_page()

        def conteudo(self):
            ######################################## Criar Body
            # Definir parametros table
            cols = ['TAG','Especialidade','Criticidade','Status','Nota SAP','Conclusão Desej.','Data Atualização']
            w = width_page/len(cols)
            h = 7
            dic_dimension = {
                'TAG': 30,
                'Especialidade': 24,
                'Criticidade': 20,
                'Status': 35,
                'Nota SAP': 27,
                'Conclusão Desej.': 27,
                'Data Atualização': 27
            }



            for i, line in df.iterrows():
                # Setar Link
                self.set_link(dic_link[line['TAG']],y=self.get_y(), x=self.get_x())    
                
                # Formatação head Table
                self.set_font('Arial', 'b', 8)
                self.set_fill_color(217, 217, 217)
                
                
                for col in cols:
                    # Criando head Table
                    self.cell(dic_dimension[col], h, col, fill=True, border=1, align='C')
                self.ln(h)

                # Formatação body Table
                self.set_font('Arial', '', 8)
                self.set_fill_color(255, 255, 255)
                for col in cols:
                    # Criando body Table
                    self.cell(dic_dimension[col], h, line[col], fill=True, border=1, align='C')
                self.ln(h)
                
                # Formatação head Table comentario
                self.set_font('Arial', 'b', 8)
                self.set_fill_color(217, 217, 217)
                self.cell(0, h, 'Comentario', fill=True, border=1, align='C')
                self.ln(h)
                
                # Formatação body Table comentario
                self.set_font('Arial', '', 8)
                self.set_fill_color(255, 255, 255)
                self.multi_cell(0, h, line['Comentario'].encode('latin-1', 'replace').decode('latin-1').replace('&',';  '), fill=True, border=1, align='C')
                self.ln(h*2) 


        def table(self):
            self.add_page()

            # Definir parametros table
            list_Col_SAP = ['Nota','TAG SAP','Descricao Curta','Conclusao Desejada','Vencida','Status CGA']
            w = width_page/len(list_Col_SAP)
            h = 5
            dic_dimension_SAP = {
                'Nota': 20,
                'TAG SAP': 37.5,
                'Descricao Curta': 62.5,
                'Conclusao Desejada': 20,
                'Vencida': 15,
                'Status CGA': 35,
            }
            dic_col_SAP = {
                'Nota': 'Nota',
                'TAG SAP': 'TAG',
                'Descricao Curta': 'Descricao Curta',
                'Conclusao Desejada': 'Concl. Desej.',
                'Vencida': 'Vencida',
                'Status CGA': 'Status CGA'
            }
            
            # Titulo da Tabela
            self.set_font('Arial', 'b', 12)
            self.set_text_color(0, 0, 0)
            self.cell(width_page, h, 'Tabela SAP - RCP', align='C') 
            self.ln(h)
                        
            #Divisões das Tabelas
            for unidade, df_unidade in df_SAP.groupby('Unidade'):                
                # Escrever Unidade - Especialidade
                for especialidade, df_especialidade in df_unidade.groupby('Especialidade'):
                    # Setar Link
                    ID_Name = 'SAP-'+unidade+'-'+especialidade 
                    self.set_link(dic_link[ID_Name],y=self.get_y(), x=self.get_x()) 

                    # Formatar e Escrever Unidade e especialidade
                    self.set_font('Arial', 'b', 10)
                    self.set_text_color(0, 0, 0)
                    self.cell(0, h, unidade+' - '+especialidade)
                    self.ln(h*2)

                    # Formatar e Escrever Head da Tabela
                    self.set_font('Arial', 'b', 8)
                    self.set_fill_color(217, 217, 217)
                    for col in list_Col_SAP:   
                        self.cell(dic_dimension_SAP[col], h, dic_col_SAP[col], fill=True, border=1, align='C')
                    self.ln(h)
                    
                    # Formatar e Escrever Body da Tabela
                    self.set_font('Arial', '', 8)
                    self.set_fill_color(255, 255, 255)
                    for i, line in df_especialidade.iterrows():
                        for col in list_Col_SAP:
                            self.cell(dic_dimension_SAP[col], h, line[col], fill=True, border=1, align='C')
                        self.ln(h)

                    self.ln(h)
                    
            self.ln(h*3)

                    
                   
    pdf = PDF('P', 'mm', 'A4') # Iniciar PDF
    pdf.add_page() # Iniciar Pagina
    pdf.alias_nb_pages() # Iniciar Contagem de pag P/ rodape

    # Criar Suamario
    pdf.sumario()

    # Criar conteudo
    pdf.conteudo() 

    pdf.table()

    # Salvar Arquivo
    pdf.output(name='Relatorio CGA.pdf', dest = 'F')
     
    
    return  'Relatorio CGA.pdf'

# Fazer upload das imagens
def uploadImg(request):
    
    try:
        # Se nao existir o arquivo retornar erro
        if 'files' not in request.files: 
            return [['ERRO'],['Nenhum arquivo encontrado']]

        # Pegar arquivos e percorrer cada um deles 
        files = request.files.getlist('files')  
        for file in files:

            # Caso arquivo nao tenha nome, enviar erro
            if file.filename == '':
                return [['ERRO'],['Nenhum arquivo selecionado']]

            # Caso o arquivo exista 
            if file:

                # Cria um nome com ID + DATA + .png
                ID = request.form['id']
                data_file = '-file-'+ datetime.now().strftime('%Y%m%d-%H%M%S-%f')
                nome_file = ID + data_file + '.png'
                
                # Salvar File  
                file.save(os.path.join(UPLOAD_FOLDER, nome_file))

                # Atualizar Planilhha
                df_cockpit = pd.read_excel(adress_csv_cockpit) # Pegar df

                # Se for mesmo tag usar linha existente caso contratio criar outra 
                df_filter_id = df_cockpit.loc[df_cockpit['id'] == ID].index[0] # Coleto index da linha que quero editar
                df_filter = df_cockpit.loc[df_filter_id] # Pego a linha que quero editar 
                textold = '' if df_filter['img'] == 'vazio.png' else df_filter['img'] # Definir texto old
                df_filter['img'] = EditarStringList(textold, 'final', nome_file) # Edito a linha 
                df_cockpit.loc[df_filter_id] = df_filter # Insiro Alteração no Df

                # Salvar planilha Atualizada
                df_cockpit = df_cockpit.astype(str)
                df_cockpit.to_excel(adress_csv_cockpit, index=False)

        return [['SUCESSO'],[f'Imagem: ({nome_file}) Criada']]
    except Exception as e:
        return [['ERRO'],[f'Erro interno no servidor: {str(e)}']]