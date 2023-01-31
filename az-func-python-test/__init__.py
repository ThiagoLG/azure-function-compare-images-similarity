import azure.functions as func
import base64
import numpy as np
import cv2
import pyodbc as pyo
import pandas as pd
import json


def readb64(uri):
    encoded_data = uri
    nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def getDatabaseItems():
    strings_connection = ("Driver={SQL Server};"
                          "Server=thiago-ghebra.database.windows.net,1433;"
                          "Database=db_beer_catalog;"
                          "Uid=db_beer_master;"
                          "Pwd=xxxx;"
                          "Encrypt=yes;"
                          "TrustServerCertificate=no;"
                          "Connection Timeout=30;")

    cnn = pyo.connect(strings_connection)
    print('opened. selecting...')

    query = "SELECT * FROM dbo.breweries"
    df = pd.read_sql(query, cnn)
    cnn.close()

    print(df.head(10))
    print('done')

    return func.HttpResponse(
        json.dumps({
            "data": df.to_json(orient='records')
        }),
        mimetype="application/json",
        status_code=200
    )


def main(req: func.HttpRequest) -> func.HttpResponse:

    return getDatabaseItems()

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

    if doc1 and doc2:
        # leitura das imagens recebidas
        original = readb64(doc1)
        image_to_compare = readb64(doc2)

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
            f"{percentage}",
            status_code=200
        )
    else:
        return func.HttpResponse(
            "Problema na leitura dos documentos enviados, por favor, confira os dados e tente novamente",
            status_code=200
        )
