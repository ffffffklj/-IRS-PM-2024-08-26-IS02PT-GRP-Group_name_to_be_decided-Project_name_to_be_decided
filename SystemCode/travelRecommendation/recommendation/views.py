import json

import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from rest_framework_jwt.settings import api_settings
from recommendation.similarity import recommend_cities
from recommendation.chat_bot import chatbot_request, chatbot_response


# define class Info as the input of the model
class Info:
    def __init__(self):
        self.type = []
        self.temp = []
        self.price = []
        self.transportation = []
        self.air = []
        self.message = []


# define class City as the final recommendation
class City:
    def __init__(self, option1, option2, option3, option4, option5, description1, description2, description3,
                 description4, description5):
        self.option1 = option1
        self.option2 = option2
        self.option3 = option3
        self.option4 = option4
        self.option5 = option5
        self.description1 = description1
        self.description2 = description2
        self.description3 = description3
        self.description4 = description4
        self.description5 = description5


info = Info()
city = City("", "", "", "", "", "", "", "", "", "")


class InformationView(View):

    # get the information from the buttons and update the class info
    def post(self, request):
        global info
        info.type = []
        info.temp = []
        info.price = []
        info.transportation = []
        info.air = []
        if request.GET.get("type") != "":
            info.type.append(request.GET.get("type"))
        if request.GET.get("temp") != "":
            info.temp.append(request.GET.get("temp"))
        if request.GET.get("price") != "":
            info.price.append(request.GET.get("price"))
        if request.GET.get("transportation") != "":
            info.transportation.append(request.GET.get("transportation"))
        if request.GET.get("air") != "":
            info.air.append(request.GET.get("air"))

        print(info.type, info.temp, info.price, info.transportation, info.air)

        return JsonResponse({'code': 200, 'info': 'infoGet'})


class MessageView(View):

    # get the information from the robot and update the class info
    def get(self, request):
        global info
        info.message = request.GET.get("message")
        infoAdd, reply = chatbot_request(info.message)
        print(infoAdd)

        # append the values of info
        if 'city' in infoAdd:
            for index, city in enumerate(infoAdd['city']):
                info.type.append(infoAdd['city'][index])
        if 'cost' in infoAdd:
            for index, cost in enumerate(infoAdd['cost']):
                info.price.append(infoAdd['cost'][index])
        if 'transport' in infoAdd:
            for index, transport in enumerate(infoAdd['transport']):
                info.transportation.append(infoAdd['transport'][index])
        if 'temperature' in infoAdd:
            for index, temperature in enumerate(infoAdd['temperature']):
                info.temp.append(infoAdd['temperature'][index])
        if 'air' in infoAdd:
            for index, air in enumerate(infoAdd['air']):
                info.air.append(infoAdd['air'][index])
        print(info.type, info.temp, info.price, info.transportation, info.air)

        # check the missing values of info and
        missKeys = set()
        if not info.type:
            missKeys.add("city type")
        if not info.temp:
            missKeys.add("temperature")
        if not info.price:
            missKeys.add("cost")
        if not info.transportation:
            missKeys.add("transportation")
        if not info.air:
            missKeys.add("air quality")

        # generate the reply of the robot and remind user to provide more information
        if reply == "":
            reply = "CHATTY: Could you please add more information on {}? If you think it's enough, type 'enough'.".format(
                ', '.join([word for word in missKeys]))

        return JsonResponse({'code': 200, 'message': reply})


def transform_input(data):
    key_mapping = {
        'type': 'city',
        'temp': 'temp',
        'price': 'cost',
        'transportation': 'transportation',
        'air': 'air quality'
    }

    transformed_data = {key_mapping.get(k, k): v for k, v in data.items() if k in key_mapping}

    return transformed_data


class CityRecommendView(View):

    # use the class info as input and get the class city as output
    def get(self, request):
        global city
        global info
        city_require = info.__dict__
        # transform the class to match the input of function recommend_cities
        user_input = transform_input(city_require)
        df = pd.read_csv("recommendation/FinalDataset.csv")
        cities = recommend_cities(user_input, df, alpha=0.5)
        # update the class city from the output
        city.option1 = cities[0][0]
        city.description1 = chatbot_response(city.option1)
        city.option2 = cities[1][0]
        city.description2 = chatbot_response(city.option2)
        city.option3 = cities[2][0]
        city.description3 = chatbot_response(city.option3)
        city.option4 = cities[3][0]
        city.description4 = chatbot_response(city.option4)
        city.option5 = cities[4][0]
        city.description5 = chatbot_response(city.option5)

        json_city = json.dumps(city.__dict__)

        return JsonResponse({'code': 200, 'city': json_city})
