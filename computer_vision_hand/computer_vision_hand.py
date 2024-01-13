### Importações
import os
import cv2
import numpy as np
from time import sleep
import mediapipe as mp 
from pynput.keyboard import Controller


### Variaveis 
# Iniciar Variaveis de controle
bloco_notas = False
calculadora = False
navegador = False

# Cores em rgb
BRANCO = (255,255,255)
PRETO = (0,0,0)
AZUL = (255,0,0)
VERDE = (0,255,0)
VERMELHO = (0,0,255)
AZUL_CLARO = (255,255,0)

# Resoluções da tela
resolucao_x = 1280
resolucao_y = 720

## Variaveis para criação do teclado 
teclas = [['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A','S','D','F','G','H','J','K','L'],
            ['Z','X','C','V','B','N','M', ',','.',' ']]
offset = 50
contador = 0
texto = '>'

# Variaveis para Criação do Quadro e das funções de desenho
cor_pincel = (255,0,0)
espessura_pincel = 7
x_quadro, y_quadro = 0,0


### Obter Objetos para as soluções
# Definir controle do teclado
teclado = Controller()

# Criar quadro banco
img_quadro = np.ones((resolucao_y, resolucao_x, 3), np.uint8)*255

# Importando soluções do mp
mp_hand = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Iniciar Objeto maos do modelo que identifica a mao
maos = mp_hand.Hands()

# Definir e Parametrizar Camera
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolucao_x)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolucao_y)

### Funçãoes
# Encontrar as coordenadas da mao 
def find_coord_hands(img, lado_invertido = False):
    # Configurar imagem para padrão de cores do mediapipe
    img_rgb = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)

    # Processar Visao COmputacional das maos na imagem do midiapipe
    resultado = maos.process(img_rgb)
    
    todas_maos = []
    # Se tiver Resultado na imagem:
    if resultado.multi_hand_landmarks:
        # Percorrer cada ponto da mao 
        for lado_mao, marcacao_maos in zip(resultado.multi_handedness, resultado.multi_hand_landmarks):
            # Desenhar um ponto na imagem a cada ponto da mao encontrado e 
            # Criar conecções entre os pontos 
            mp_draw.draw_landmarks(img, marcacao_maos, mp_hand.HAND_CONNECTIONS)
            
            # Capturar os dados
            info_mao = {}
            coordenadas = [] # Iniciar lista para armazenar coordenadas da mao 
            for marcacao in marcacao_maos.landmark:
                # Calcular coordenadas convertendo para pixel cpm base no tamanho da imagem
                coord_x, coord_y, coord_z = int(marcacao.x*resolucao_x), int(marcacao.y*resolucao_y), int(marcacao.z*resolucao_x)
                coordenadas.append((coord_x, coord_y, coord_z)) # Armazenas cordenadas em uma lista
            
            # Armazenar as coordenadas de cada mao  dentro de todas as maos             
            info_mao['coordenadas'] = coordenadas

            # Adicionar o lado da mao aos dados armazenados porem antes verificar necessidade de inverter
            if lado_invertido: # Inverter Lados
                info_mao['lado'] = 'Right' if lado_mao.classification[0].label == 'Left' else 'Left'
            else: # COletar dado padrão
                info_mao['lado'] = lado_mao.classification[0].label

            todas_maos.append(info_mao)

    return img, todas_maos

# Informar quais dedos estao e nao estão levantados
def dedos_levantados(mao):
    dedos = []
    for ponta_dedo in [8,12,16,20]:
        if mao['coordenadas'][ponta_dedo][1] < mao['coordenadas'][ponta_dedo-2][1]:
            dedos.append(True)
        else:
            dedos.append(False)
    
    return dedos

# Desenhar botoes dos teclado na imagem
def imprime_botoes(img, posicao, letra, tamanho = 50, cor_retangulo = BRANCO):
    cv2.rectangle(img, posicao, (posicao[0]+tamanho, posicao[1]+tamanho), cor_retangulo, cv2.FILLED)
    cv2.rectangle(img, posicao, (posicao[0]+tamanho, posicao[1]+tamanho), AZUL, 1)
    cv2.putText(img, letra, (posicao[0]+15,posicao[1]+30), cv2.FONT_HERSHEY_COMPLEX, 1, PRETO, 2)
    return img


# Iniciar Loop
while True:

    # Abrir camera e retornar resultado e a imagem
    sucesso, img = camera.read()
    img = cv2.flip(img, 1) # Inverter imagem

    # Retornar imagem e coordenadas das maos 
    img, todas_maos = find_coord_hands(img)

    # Função que o utiliza 1 mao
    # Teclado virtual e abrir bloco de notas 
    if len(todas_maos) == 1:
        # Coletar quais dedos estão levantados
        info_dados_mao1 = dedos_levantados(todas_maos[0])

        # Se for a mao esquerda
        if todas_maos[0]['lado'] == 'Left':
            
            # Indicador levantado abrir bloco de notas 
            if info_dados_mao1 == [True, False, False, False] and bloco_notas == False:
                bloco_notas = True
                os.startfile(r'C:\WINDOWS\system32\notepad.exe')
            
            # 2 dedos levantados abrir calculadora 
            if info_dados_mao1 == [True, True, False, False] and calculadora == False:
                calculadora = True
                os.startfile(r'C:\WINDOWS\system32\calc.exe')
            
            # Mao fechada fechar bloco de notas
            if info_dados_mao1 == [False, False, False, False] and bloco_notas == True:
                bloco_notas = False
                os.system('TASKKILL /IM notepad.exe')

            # Dedo mindinho levantado resetar variavel para abrir outra calculadora
            if info_dados_mao1 == [False, False, False, True] and calculadora == True:
                calculadora = False

        # Se for a mao direita
        if todas_maos[0]['lado'] == 'Right':
            # Coletar posição do indicados
            indicador_x, indicador_y, indicador_z = todas_maos[0]['coordenadas'][8]

            # Escrever distancia do indicador (eixo Z) na tela 
            cv2.putText(img, f'Distancia Camera: {indicador_z}', (850,50), cv2.FONT_HERSHEY_COMPLEX, 1, BRANCO, 2)

            # Criar Teclado
            for indice_linha, linha_teclado in enumerate(teclas):
                 for indice, letra in enumerate(linha_teclado):
                    # Definir Letra Maiuscula ou minuscula
                    if sum(info_dados_mao1) <= 1:
                        letra = letra.lower() 
                    
                    # imprimir todos os botões na tela
                    img = imprime_botoes(img, (offset+indice*80, offset+indice_linha*80), letra)
                    
                    # Verificar se o indicador esta na area de alguma tecla
                    if offset+indice*80 < indicador_x < 100+indice*80 and offset+indice_linha*80 < indicador_y < 100+indice_linha*80:
                        # Se sim mudar de or 
                        img = imprime_botoes(img, (offset+indice*80, offset+indice_linha*80), letra, cor_retangulo=VERDE)
                        
                        # Verificar se indicador esta proximo da camera 
                        if indicador_z < -85: 
                            # Se sim contador 1 coleta a letra e muda para azul claro a tecla
                            contador = 1
                            escreve = letra
                            img = imprime_botoes(img, (offset+indice*80, offset+indice_linha*80), letra, cor_retangulo=AZUL_CLARO)


            # se contador for padrão 0 nao faz nada
            # Se contador for 1 
            if contador: 
                contador += 1 # Contador recebe +1 
                # Se nao colocar dedo em outro botao ira direto para ca novamente somando +1 novamente se tornando 3 
                if contador ==3:
                    # Adicionar letra ao texto e retornar contador para proxima letra
                    texto +=  escreve
                    contador = 0 
                    teclado.press(escreve)

            # Criar campo de texto 
            cv2.rectangle(img, (offset, 450), (830,500), BRANCO, cv2.FILLED)
            cv2.rectangle(img, (offset, 450), (830,500), AZUL, 1)
            cv2.putText(img, texto[-40:], (offset,480), cv2.FONT_HERSHEY_COMPLEX, 1, PRETO, 2)
            cv2.circle(img,(indicador_x,indicador_y), 7, AZUL, cv2.FILLED)

            if info_dados_mao1 == [False, False, False, True] and len(texto)>1:
                texto = texto[:-1]
                sleep(0.15)

    # Função que utiliza as duas maos 
    # Desenhar no quadro branco 
    if len(todas_maos) == 2:
        # Coletar os dedos levantados das duas maos 
        info_dedos_mao1 = dedos_levantados(todas_maos[0])
        info_dedos_mao2 = dedos_levantados(todas_maos[1])

        # Coletar coordenadas do indicado da primeira mao 
        indicador_x, indicador_y, indicador_z = todas_maos[0]['coordenadas'][8]

        # Controlar cor do pincel e apagar quadro com base no numero de dedos levantados 
        if sum(info_dedos_mao2) == 1:
            cor_pincel = AZUL
        elif sum(info_dedos_mao2) == 2:
            cor_pincel = VERDE
        elif sum(info_dedos_mao2) == 3:
            cor_pincel = VERMELHO
        elif sum(info_dedos_mao2) == 4:
            cor_pincel = BRANCO
        else:
            img_quadro = np.ones((resolucao_y, resolucao_x, 3), np.uint8)*255
            
        # Definir espessura do pincel com base na distancia do eixo z, desenhar espessura na tela
        espessura_pincel = int(abs(indicador_z)//3+5)
        cv2.circle(img, (indicador_x, indicador_y), espessura_pincel, cor_pincel, cv2.FILLED)

        # Desenhar enquanto estiver com apenas o indicador da mao 0 levantada
        if info_dedos_mao1 == [True, False, False, False]:
            if x_quadro == 0 and y_quadro == 0:
                x_quadro, y_quadro = indicador_x, indicador_y

            # Desenhar uma linha no quadro nas mesmas coordenadas do dedo 
            cv2.line(img_quadro, (x_quadro, y_quadro), (indicador_x, indicador_y), cor_pincel, espessura_pincel)
            x_quadro, y_quadro = indicador_x, indicador_y

        # Caso o indicador nao esteja levantado zerar coordenadas do quadro
        else:
            x_quadro, y_quadro = 0,0 

        img = cv2.addWeighted(img, 1, img_quadro, 0.2, 0)

    # Exibir imagem e quadro 
    cv2.imshow("Imagem", img)
    cv2.imshow('Quadro', img_quadro)

    # Daley e tecla Esc para fechar o loop
    tecla = cv2.waitKey(1)
    if tecla == 27: break



