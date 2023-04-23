import cv2
import mediapipe as mp

# Inicializar o módulo de detecção de mãos do mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence  = 0.5)

# Mapear os nomes das jogadas para seus respectivos índices
jogadas = {0: "Pedra", 1: "Papel", 2: "Tesoura",3:"Não Existe"}

# Função para detectar as mãos no frame
def detectar_maos(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    maos = hands.process(frame_rgb)
    return maos

# Função para determinar a jogada a partir das landmarks das mãos
def determinar_jogada(mao):
    landmarks = mao.landmark
    pulso = landmarks[0]
    dedo_indicador = landmarks[8]
    dedo_medio = landmarks[12]
    
    # Calcular a distância entre o polegar e os outros dedos
    distancia_polegar_indicador = ((pulso.x - dedo_indicador.x)**2 + (pulso.y - dedo_indicador.y)**2)**0.5
    distancia_polegar_medio = ((pulso.x - dedo_medio.x)**2 + (pulso.y - dedo_medio.y)**2)**0.5   
    distancia_tesoura = ((dedo_medio.x - dedo_indicador.x)**2 + (dedo_medio.y - dedo_indicador.y)**2)**0.5
    
    # Printar a distancia de cada dedo - Tesoura 
    print("distancia_polegar_medio",distancia_polegar_medio)
    print("distancia_tesoura",distancia_tesoura)
    
    # Determinar a jogada com base nas distâncias
    if distancia_polegar_medio < distancia_polegar_indicador and distancia_polegar_medio <= 0.2:
        return jogadas[0] # Pedra
    elif distancia_polegar_indicador > 0.4 and distancia_polegar_medio >= 0.2:
        return jogadas[1] # Papel
    elif distancia_tesoura < 0.2 and distancia_polegar_medio < 0.8:
        return jogadas[2] # Tesoura
    else:
        return jogadas[3] # Não existe
    
# Função para determinar o vencedor
def determinar_vencedor(jogada1, jogada2):
    if jogada1 == jogada2:
        return "Empate"
    elif (jogada1 == "Pedra" and jogada2 == "Tesoura") or (jogada1 == "Papel" and jogada2 == "Pedra") or (jogada1 == "Tesoura" and jogada2 == "Papel"):
        return "Jogador 1 venceu!"
    else:
        return "Jogador 2 venceu!"

# Abrir o vídeo
#video = cv2.VideoCapture("pedra-papel-tesoura.mp4")
video = cv2.VideoCapture(0)

while True:
    ret, frame = video.read()
    if not ret:
        break
    
    # Detectar as mãos no frame
    resultados = detectar_maos(frame)
    
    if resultados.multi_hand_landmarks:
        # Extrair as landmarks das mãos
        maos = resultados.multi_hand_landmarks
        jogada_jogador1 = None
        jogada_jogador2 = None
        
        for mao in maos:
                       # Determinar a jogada para cada mão
            jogada = determinar_jogada(mao)
            # Obter as coordenadas do centro da mão
            x, y = int(mao.landmark[0].x * frame.shape[1]), int(mao.landmark[0].y * frame.shape[0])
            # Desenhar um círculo na mão
            cv2.circle(frame, (x, y), 30, (255, 0, 0), -1)
            
            # Atribuir a jogada ao jogador correspondente (jogador 1 ou jogador 2)
            if not jogada_jogador1:
                jogada_jogador1 = jogada
            else:
                jogada_jogador2 = jogada
        
        # Determinar o vencedor
        if jogada_jogador1 and jogada_jogador2:
            vencedor = determinar_vencedor(jogada_jogador1, jogada_jogador2)
            # Desenhar as jogadas na tela
            cv2.putText(frame, f"Jogador 1: {jogada_jogador1}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Jogador 2: {jogada_jogador2}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.putText(frame, vencedor, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
             
        else:
            # Caso não haja jogada detectada para algum dos jogadores
            cv2.putText(frame, "Aguardando jogadas...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
    cv2.imshow("Jogo Pedra, Papel e Tesoura", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()