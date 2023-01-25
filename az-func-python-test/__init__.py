import logging

import azure.functions as func
import base64
import numpy as np
import cv2

def readb64(uri):
    encoded_data = uri
    nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def main(req: func.HttpRequest) -> func.HttpResponse:

    # variáveis de documentos
    doc1 = ''
    doc2 = ''

    # realiza a leitura através do corpo da requisição
    try:
        req_body = req.get_json()
        doc1 = req_body.get('doc1')
        doc2 = req_body.get('doc2')
    except ValueError:
        return func.HttpResponse(
            f'Não foi possível processar os documento enviado.',
            status_code=400
        )

    # processamento do documento 1
    if doc1:
        try:
            file1 = ''
        except ValueError:
            return func.HttpResponse(
                'Não foi possível processar o documento evniado.',
                status_code=400
            )
    else:
        return func.HttpResponse(
            'Documento 1 não recebido',
            status_code=200
        )

    # processamento do documento 2
    if doc2:
        try:
            file2 = ''
        except ValueError:
            return func.HttpResponse(
                'Não foi possível processar o documento enviado.',
                status_code=400
            )
    else:
        return func.HttpResponse(
            'Documento 2 não recebido',
            status_code=200
        )

    # leitura das imagens recebidas
    original_img = readb64(doc1)
    image_to_compare_img = readb64(doc2)

    # converte para grayscale
    original = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
    image_to_compare = cv2.cvtColor(image_to_compare_img, cv2.COLOR_BGR2GRAY)

    # realiza a leitura da imagem e obtém pontos chave para comparação
    sift = cv2.xfeatures2d.SIFT_create()
    kp_1, desc_1 = sift.detectAndCompute(original, None)
    kp_2, desc_2 = sift.detectAndCompute(image_to_compare, None)

    # parâmetros par comparação
    index_params = dict(algorithm=0, trees=5)
    search_params = dict()
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(desc_1, desc_2, k=2)

    # array para armazenar pontos de semelhança
    good_points = []

    # percorre todas as correspondências entre as imagens para calcular a semelhança
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_points.append(m)

    # calcula a quantidade de pontos de semelhança
    number_keypoints = 0
    if len(kp_1) <= len(kp_2):
        number_keypoints = len(kp_1)
    else:
        number_keypoints = len(kp_2)

    percentage = len(good_points) / number_keypoints * 100

    # retorna a porcentagem de semelhança -
    return func.HttpResponse(
        f"Percentual de semelhança: {percentage}%",
        status_code=200
    )
