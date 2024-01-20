import pandas as pd
import datetime as dt

Adress_Banco_User = r'static/Usuarios/usuarios.xlsx'

def attOption():
    banco_usuarios = pd.DataFrame(pd.read_excel(Adress_Banco_User))
    Return = list(banco_usuarios['login'])
    
    return Return

def Login(login,senha):
    Return={'status':'','df':{}}
    
    # Coletar Banco, Login Minusculo, filtrar login
    banco_usuarios = pd.DataFrame(pd.read_excel(Adress_Banco_User))
    banco_usuarios['login'] = banco_usuarios['login'].str.lower() 
    banco_usuarios = banco_usuarios[banco_usuarios['login']==login.lower()]

    if len(banco_usuarios) == 0:
        Return['status'] = 'Login Incorreto'
    else:
        banco_usuarios.reset_index(inplace=True, drop=True)
        if banco_usuarios['senha'][0] != senha:
            Return['status']= 'Senha Incorreta'
        else:
            banco_usuarios = banco_usuarios.drop(columns='senha')
            Return['df'] = banco_usuarios.to_json(orient='records')
            Return['status']= 'Conectado'

    return(Return)

