import azure.functions as func
import cv2
import json
from .utils.db_utils import *
from .utils.file_utils import *
from .repos.breweries_repo import *

# main function called when the azfunc receive a request
def main(req: func.HttpRequest) -> func.HttpResponse:
    
    # get all data from breweries table
    try:
        cnn = get_connection()
        all_breweries_data = get_all_breweries_data(cnn, True)

        return func.HttpResponse(
            json.dumps({
                "data": all_breweries_data
            }),
            mimetype="application/json",
            status_code=200
    )
    except ValueError:
        return func.HttpResponse(
            f'Error while try get all data from breweries',
            status_code=400
        )    


    # init vars to control received doc
    pic_to_compare = ''

    # read docs from req body
    try:
        req_body = req.get_json()
        pic_to_compare = req_body.get('picture_file')
    except ValueError:
        return func.HttpResponse(
            f'Error trying read received picture.',
            status_code=400
        )

    # actions if pic_to_compare exist and if its valid
    if pic_to_compare:

        # convert images to file
        original = readb64(pic_to_compare)
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
