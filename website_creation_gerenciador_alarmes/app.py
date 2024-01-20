from flask import Flask, render_template, request, jsonify, send_file
import datetime
from waitress import serve
import logging
logging.basicConfig(level=logging.INFO,
  filename="erros.log", \
  format="%(asctime)s ; %(levelname)s ; %(message)s; "
)
import sys

sys.path.insert(0, "./funcoes")
import Alarms as Py_Alarms
import Grafico as Py_Grafico
import login as Py_Login
import idmi as Py_idmi
import baterias as Py_baterias
import cockpit as Py_cockpit
import CAC as Py_CAC
import rele as Py_rele

link_host = "...ip"

print('''
Gerenciador de Alarme esta funcionando
Link: {}'''.format(link_host))

app = Flask(__name__,template_folder="Telas",static_folder="static")

if True: # TELAS

    @app.route("/IDMI")
    def IDMI():
        print("{}  Pagina IDMI Aberta ".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
        return render_template('IDMI.html')

    @app.route("/COCKPIT")
    def COCKPIT():
        print("{}  Pagina COCKPIT Aberta ".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
        return render_template('COCKPIT.html')

if True: # POST PARA A TELA TABELA         
    @app.route('/POST', methods = ['POST'])
    def Post():
        inp1 = dict((key, request.form.getlist(key)) for key in request.form.keys())


        inp={}
        for old_key in inp1.keys():
            new_key = old_key.replace("[0]", "").replace("[]", "")
            inp[new_key] = inp1[old_key]


        Filtrado = Py_Alarms.Filtro_E_Coleta_Dos_Logs(int(inp['NumeroLog'][0]),int(inp['PaginaLog'][0]), inp['DataInicial'][0] , inp['DataFinal'][0] , inp['Especialidade'] , inp['Sistemas'] , inp['Filtro_modfalha'][0] , inp['Tag'][0] , inp['NivelAlarme'],inp['Exportar_Excel'][0])
        
        print("{}  Pagina Principal Atualizada ".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
        return jsonify(results=Filtrado)

    @app.route('/POSTDentroMultLog', methods = ['POST'])
    def PostDentroMultLog():
        Adress = list(request.form.listvalues())[0]
        InLog = (Py_Alarms.LerMultLog(Adress))

        print("{}  Leitura dos Logs Feita ".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
        return jsonify(results=InLog)

    @app.route('/POSTAlterarMultLog', methods = ['POST'])
    def POSTAlterarMultLog():
        
        lista = (list(request.form.listvalues()))
        Alterar = (Py_Alarms.AlterarMultLog(lista[0], lista[1], lista[2], lista[3], lista[4],lista[5],lista[6]))

        print("{}  Alteracao de Logs Feita ".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
        return jsonify(results=Alterar)

    @app.route('/POSTBuscarPi', methods = ['POST'])
    def POSTBuscarPi():
        inp = dict((key, request.form.getlist(key)) for key in request.form.keys())
        Adress = inp['Adress'][0]
        datastart = inp['datastart'][0].replace("T"," ")
        dataend = inp['dataend'][0].replace("T"," ")
        conf = inp['conf'][0]
        Extra_tags = inp['Extra_tags[]']

        dados = Py_Grafico.ColetarCurvas(Adress,datastart,dataend,conf,Extra_tags)

        print("{}  Abertura de Grafico ".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))

        return jsonify(results=dados)   

    @app.route('/POSTLogin', methods = ['POST'])
    def POSTLogin():
        form = request.form
        attOptions = form['attOptions']
        form = Py_Login.attOption() if form['attOptions'] == 'sim' \
                else  Py_Login.Login(form['login'],form['senha'])

        if attOptions != 'sim':
            print("{}  Login Realizado ".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
        return jsonify(results=form)


    @app.route('/POST_Verif_Alarme_SAP', methods = ['POST'])
    def POST_Verif_Alarme_SAP():
        inp = dict((key, request.form.getlist(key)) for key in request.form.keys())
        inp['Conf_SAP_cols'] = inp['Conf_SAP_cols'][0].split(",")

        df = Py_Alarms.Verif_Alarme_SAP(inp)     

        return jsonify(results=df)

if True: # POST PARA A TELA COCKPIT
    @app.route('/ColetarDados', methods = ['POST'])
    def ColetarDados():
        # Coletar os dados do post 
        inp1 = dict((key, request.form.getlist(key)) for key in request.form.keys())

        # Executar função
        retorno = Py_cockpit.ColetarDados(inp1['especialidade'][0])

        print("{}  Coleta de Dados do COCKPIT".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
        return jsonify(results= retorno)

    @app.route('/SolicitarAlteracao', methods = ['POST'])
    def SolicitarAlteracao():
        # Coletar os dados do post
        inp = dict((key, request.form.getlist(key)) for key in request.form.keys())
        print(inp)
        # Executar função
        retorno = Py_cockpit.SolicitarAlteracao(inp)

        print("{}  Alteracao de Dados do COCKPIT".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
        return jsonify(results= retorno)

    @app.route('/CreateReport', methods = ['POST'])
    def CreateReport():
        # Solicitar P/ python criar PDF
        inp1 = dict((key, request.form.getlist(key)) for key in request.form.keys())

        inp={}
        for old_key in inp1.keys():
            new_key = old_key.replace("[0]", "").replace("[]", "")
            inp[new_key] = inp1[old_key]

        p = Py_cockpit.CreateReport(inp)

        return send_file(p, download_name='Relatorio CGA.pdf')


    # Pasta onde os arquivos serão salvos
    UPLOAD_FOLDER = './static/img/RelatorioCGA'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    @app.route('/uploadImg', methods=['POST'])
    def uploadImg():

        retorno = Py_cockpit.uploadImg(request)
        
        return jsonify(results= retorno)



if __name__ == "__main__":   
    # context = ('cert.pem', 'key.pem')
    if link_host == "....":
        serve(app, port='..', host=link_host)
    else:
        serve(app, host=link_host, port='.....', url_scheme='https')
    # app.run(debug=True)

