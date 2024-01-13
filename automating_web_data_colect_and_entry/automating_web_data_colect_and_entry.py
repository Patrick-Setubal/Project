
# --------------------------Importações de Bibliotecas-------------------------
#Importando as bibliotecas
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import os
import glob
import time
import datetime
import pandas as pd
import warnings
warnings.simplefilter("ignore")

nav=''

# --------------------------Configurações de Variaveis-------------------------
#Informações do Usuário
cnpj = '....'
user = 'login'
senha = 'senha'
adress_dowload = 'C:/Users/.../Downloads/*'
filename = 'Relatório de .....xls'
file_controle = './file/....xlsx'
file_ColetaAnaliseOleo = 'Z:/Central Preditiva - Coletas Offline/ColetaAnaliseOleo.xlsx'

# --------------------------Functions-----------------------------------------
### Para WebScraptinng
def click(XPATH, mode='located'):
    if mode == 'located':
        WebDriverWait(nav, 120).until(EC.presence_of_element_located((By.XPATH, XPATH))).click()
    if mode == 'clickable':
        WebDriverWait(nav, 120).until(EC.element_to_be_clickable((By.XPATH, XPATH))).click()

def clear(XPATH):
  WebDriverWait(nav, 120).until(EC.presence_of_element_located((By.XPATH, XPATH))).clear()

def send_keys(XPATH,texto):
    WebDriverWait(nav, 120).until(EC.presence_of_element_located((By.XPATH, XPATH))).clear()
    WebDriverWait(nav, 120).until(EC.presence_of_element_located((By.XPATH, XPATH))).send_keys(str(texto))

def selected(XPATH, option):
    Select(WebDriverWait(nav, 120).until(EC.presence_of_element_located((By.XPATH, XPATH)))).select_by_visible_text(option)
              
def get_Attribute(XPATH,Attribute):
    return WebDriverWait(nav, 120).until(EC.presence_of_element_located((By.XPATH, XPATH))).get_attribute(Attribute)
        
def Verificar_campo(XPATH,input):
    
    # Verificar se esta escrito oque deveria
    if get_Attribute(XPATH,'value') != input:
        # 1° Tentativa, Caso Nao esteja, escreva:
        send_keys(XPATH,input)
        time.sleep(1)
        
        # Verificar se esta escrito oque deveria
        if get_Attribute(XPATH,'value') != input:
            # 2° Tentativa, Caso Nao esteja, escreva:
            send_keys(XPATH,input)
            time.sleep(1)
            
            # Verificar se esta escrito oque deveria
            if get_Attribute(XPATH,'value') != input:
                return False
                
    return True


# --------------------------Automações-----------------------------------------      
def BaixarRelatorioZip():
    global nav
    
    # Deletar Relatorios Antigos
    lista_relatorios = glob.glob('C:/Users/usr_pnbordo/Downloads/*'+filename)
    for relatorio in lista_relatorios:
        os.remove(relatorio) 
    
    # Interação com Site
    try:
        # # Abrir Site
        nav = webdriver.Edge()
        nav.get('https://...../RelatorioAnaliseCompleto.seam')
        
        # # Logar
        click('//*[@id="anuncioMobile"]/div/div/span') # Fechar Anuncio
        send_keys('//*[@id="loginForm:cnpjField:cnpj"]',cnpj) # Digitar cnpj
        send_keys('//*[@id="loginForm:usernameField:username"]',user) # Digitar Usuario
        send_keys('//*[@id="loginForm:passwordField:password"]',senha) # Digitar senha
        click('//*[@id="loginForm:submit"]') # Entrar no Site        
        
        # Preencher data inicio
        data_inicio = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%d-%m-%Y')
        send_keys('//*[@id="relCompletoSearch:j_id206:inicioInputDate"]',data_inicio)
        
        # Preencher data final
        data_final = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%d-%m-%Y')
        send_keys('//*[@id="relCompletoSearch:j_id220:fimInputDate"]',data_final)
        
        # # Preencher e Baixar
        selected('//*[@id="relCompletoSearch:j_id268:arquivoSelect"]', '.xls') # Selecionar 'XLS'
        click('//*[@id="relCompletoSearch:generate"]') # Baixar  
        
        # Aguardar conclusão do dowload
        loop = 0 
        while loop <60:
            lista_relatorios = glob.glob(adress_dowload+filename)
            if len(lista_relatorios)>0:
                relatorio = lista_relatorios[0] 
                nav.quit() # Fechar Sessão
                break
            time.sleep(10); loop += 1
            
        return(relatorio)        
              
    except Exception as e:
        print('Erro no Webscrapting', e)    


def Tratar_dados(df):
    # Trocar nome das colunas
    dict_name_col = {
        'Unidade': 'Un',    'Obra':	'Unidade',  'Equipamento':'TAG',    'Data Coleta': 'Data'
    }
    df.rename(columns=dict_name_col,inplace=True)

    # Remover Colunas caso tenha menos que 2 colunas preenchidas Nan
    list_col_na = [] # Criar Lista vazia
    cols = df.isna().sum().to_dict() # Criar 'dict' = 'col': num na

    for col in cols: # Percorrer Dict
        if cols[col] >= len(df)-2:
            list_col_na.append(col) # Listar Colunas Na
            continue

        if len(df[col].unique())<=2:
            lista = list(map(str,df[col].unique()))
            if 'nan' and '0,0' in lista:
                list_col_na.append(col)
                continue

    df.drop(columns=list_col_na,inplace=True)

    
    # União do Tag com o Compartimento
    df['TAG'] = df['TAG'] + " - " + df['Compartimento'].str.split(" - ").str[0]
    
    # Adicionar RJ0x nos tags
    df.loc[(df.Unidade == 'PE9') | (df.Unidade == 'Q4') , 'TAG'] = 'RJ08-' + df['TAG']
    df.loc[(df.Unidade == 'PP5') , 'TAG'] = 'RJ09-' + df['TAG'] 
    
    # Remover Duplicidade ('TAG') mantendo os 5 mais recente
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y') # Coluna data no formato data
    df.sort_values(by='Data', ascending=False, inplace=True) # ordenar df com base na data
    df = df.groupby("TAG").head(5)
    df.sort_values(by='Data', ascending=True, inplace=True) # ordenar df com base na data
    
    # Padronizando Condição
    df.loc[df.Condicao.str.contains('Trocar|Intervir|Att.Limite|Altissimo|Muito Alto'), 'Condicao'] = 'Intervir'
    df.loc[df.Condicao.str.contains('Atenção|Acompanhar|Alto'), 'Condicao'] = 'Acompanhar'
    df.loc[df.Condicao.str.contains('Ok|Normal'), 'Condicao'] = 'Normal'
    
    return df
    
# Main    
def AnaliseOleo():
    try:
        relatorio = BaixarRelatorioZip() # Baixar Dados
        # relatorio = 'C:/Users/usr_pnbordo/Downloads\\0973B - Relatório de análise completo.xls'       
        
        df = pd.read_excel(relatorio) # Ler Planilha
        
        df = Tratar_dados(df) # Tratar Dados
                
        # Pegar planilha controle 
        df_controle = pd.read_excel(file_controle)  
        df_novas_coletas = df[~df['Nr.Laudo'].isin(df_controle['Nr.Laudo'])]  # Filtrar apenas oque é novo 
        
        # Se tiver Coletas Novas
        if len(df_novas_coletas)>0:
            
            # Concatenar Controle com as novas coletas
            df_controle = pd.concat([df_controle, df_novas_coletas[['Nr.Laudo','TAG','Compartimento','Data']] ] )
            
            # Coletar ColetaAnaliseOleo e concatenar oq tinha com o novo 
            df_ColetaAnaliseOleo = pd.read_excel(file_ColetaAnaliseOleo)
            df_ColetaAnaliseOleo = pd.concat([df_ColetaAnaliseOleo, df_novas_coletas])
            
            # Salvar arquivos
            df_ColetaAnaliseOleo.to_excel(file_ColetaAnaliseOleo, index=False) #
            df_controle.to_excel(file_controle, index=False)
            
            print(f"Foi encontrado {len(df_novas_coletas)} coletas novas e foram atualizadas")
            
        else:
            print(f"Não tme nada de novo")
        
    except Exception as e:
        print("Erro no tratamento das planilhas: ", e)
        
    print('Analise de Óleo - Atualizado')



while True:
    AnaliseOleo()
    time.sleep(60*30)










