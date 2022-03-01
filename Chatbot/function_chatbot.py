import json
import requests
from requests.exceptions import HTTPError

my_headers = {'Authorization' : 'Bearer GUrPRVm8IIgIkclxZQ8wp9ptzoGsY()jYrNYYMtMi)xPo8fSSb0AxGxX4mT9)e0rDzgYG5s4TbfKkCqvuP)ALX0=====2',
              'Accept-Language' : 'th'}

def place_request(question_from_dailogflow_dict):
    #Print intent that recived from dialogflow.
    print(json.dumps(question_from_dailogflow_dict, indent=4 ,ensure_ascii=False))
    categorycodes = question_from_dailogflow_dict["queryResult"]["outputContexts"][0]["parameters"]["categorycodes"]
    province = question_from_dailogflow_dict["queryResult"]["outputContexts"][0]["parameters"]["province"]

    keyword_att = question_from_dailogflow_dict["queryResult"]["outputContexts"][0]["parameters"]["keyword_att"]
    if keyword_att != [] and "ATTRACTION" not in categorycodes:
        categorycodes.append("ATTRACTION")

    keyword_rest = question_from_dailogflow_dict["queryResult"]["outputContexts"][0]["parameters"]["keyword_rest"]
    if keyword_rest != [] and "RESTAURANT" not in categorycodes:
        categorycodes.append("RESTAURANT")

    keyword_acc = question_from_dailogflow_dict["queryResult"]["outputContexts"][0]["parameters"]["keyword_acc"]
    if keyword_acc != [] and "ACCOMMODATION" not in categorycodes:
        categorycodes.append("ACCOMMODATION")

    event_dict = {}
    event_dict["name"] = "process_rec"
    event_dict["parameters"] = {"province":province,"categorycodes":categorycodes}
    event_dict["parameters"]["keyword_att"] = ""
    event_dict["parameters"]["keyword_rest"] = ""
    event_dict["parameters"]["keyword_acc"] = ""
    for i in set(categorycodes):
        if i == "ATTRACTION":
            event_dict["parameters"]["keyword_att"] = keyword_att
        elif i == "RESTAURANT":
            event_dict["parameters"]["keyword_rest"] = keyword_rest
        else:
            event_dict["parameters"]["keyword_acc"] = keyword_acc

    event_from_bot = {"followupEventInput": event_dict}
    event_from_bot = json.dumps(event_from_bot, indent=4)

    return event_from_bot

def place_recommendation(question_from_dailogflow_dict):

    province = question_from_dailogflow_dict["queryResult"]["outputContexts"][0]["parameters"]["province"]
    categorycodes = question_from_dailogflow_dict["queryResult"]["outputContexts"][0]["parameters"]["categorycodes"]

    answer_total = []

    for c in set(categorycodes):
        if c == "ATTRACTION":
            considering = question_from_dailogflow_dict["queryResult"]["outputContexts"][0]["parameters"]["keyword_att"]
        elif c == "RESTAURANT":
            considering = question_from_dailogflow_dict["queryResult"]["outputContexts"][0]["parameters"]["keyword_rest"]
        else:
            considering = question_from_dailogflow_dict["queryResult"]["outputContexts"][0]["parameters"]["keyword_acc"]


        for key in set(considering):
            answer = {
            "payload": {
              "line": {
                "template": {
                  "imageSize": "cover",
                  "imageAspectRatio": "rectangle",
                  "type": "carousel",
                  "columns": []
                },
                "type": "template",
                "altText": "this is a carousel template"
              }
            }
          }
            url_search = f'https://tatapi.tourismthailand.org/tatapi/v5/places/search?keyword={key}&location=&categorycodes={c}&provinceName={province}&radius=20&numberOfResult=10&pagenumber=1&destination=&filterByUpdateDate=2019/09/01-2022/01/31'
            try:
                response_place = requests.get(url_search,headers=my_headers).json()
            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')  # Python 3.6
                answer_from_bot = {"fulfillmentText": f"ไม่พบสถานที่ที่ตรงกับลักษณะเด่น {key} ของคุณค่ะ"}
                answer_from_bot = json.dumps(answer_from_bot, indent=4)
                return answer_from_bot
            except Exception as err:
                print(f'Other error occurred: {err}')  # Python 3.6
                answer_from_bot = {"fulfillmentText": f"ไม่พบสถานที่ที่ตรงกับลักษณะเด่น {key} ของคุณค่ะ"}
                answer_from_bot = json.dumps(answer_from_bot, indent=4)
                return answer_from_bot
            else:
                print(response_place)
                for i in range(0,len(response_place["result"])):
                    url_detail = f"https://tatapi.tourismthailand.org/tatapi/v5/{c}/{response_place['result'][i]['place_id']}"
                    response_detail = requests.get(url_detail,headers=my_headers).json()

                    if response_detail['result']["thumbnail_url"] != "":
                        image = response_detail['result']["thumbnail_url"]
                    elif response_detail['result']["web_picture_urls"] != None:
                        image = response_detail['result']["web_picture_urls"][0]
                    elif response_detail['result']["mobile_picture_urls"] != None:
                        image = response_detail['result']["mobile_picture_urls"][0]
                    else:
                        image = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png"

                    title = response_place['result'][i]['place_name']
                    if len(title) > 45:
                        title = response_place['result'][i]['place_name'][:45] + "..."

                    col = {"actions":[],"defaultAction":{},"imageBackgroundColor": "#FFFFFF","title": title,
                              "thumbnailImageUrl":image,
                              "text": c}

                    uri = "https://thai.tourismthailand.org/home"
                    col["actions"].append({

                        "uri":uri,"label":"รายละเอียด","type":"uri"
                    })
                    col["defaultAction"] = {
                        "type":"uri","label":"รายละเอียด","uri":"https://thai.tourismthailand.org/home"
                    }
                    answer["payload"]["line"]["template"]["columns"].append(col)
                answer_total.append(answer)

    print(answer_total)
    answer_from_bot = {"fulfillmentMessages": answer_total}
    answer_from_bot = json.dumps(answer_from_bot, indent=4)
    return answer_from_bot

def trip_recommendation(question_from_dailogflow_dict):
    number_date = int(question_from_dailogflow_dict["queryResult"]["outputContexts"][0]["parameters"]["number_date"])
    thai_region = question_from_dailogflow_dict["queryResult"]["outputContexts"][0]["parameters"]["thai_region"]
    url_trip_rec = f'https://tatapi.tourismthailand.org/tatapi/v5/routes?numberofday={number_date}&geolocation=&region={thai_region}'
    answer = {
        "payload": {
            "line": {
                "template": {
                  "imageSize": "cover",
                  "imageAspectRatio": "rectangle",
                  "type": "carousel",
                  "columns": []
                },
                "type": "template",
                "altText": "this is a carousel template"
              }
            }
          }
    try:
        response_trip = requests.get(url_trip_rec,headers=my_headers).json()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
        answer_from_bot = {"fulfillmentText": f"ไม่พบทริปการเดินทางค่ะ"}
        answer_from_bot = json.dumps(answer_from_bot, indent=4)
        return answer_from_bot
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
        answer_from_bot = {"fulfillmentText": f"ไม่พบทริปการเดินทางค่ะ"}
        answer_from_bot = json.dumps(answer_from_bot, indent=4)
        return answer_from_bot
    else:
        count = 0
        print(response_trip)
        for i in range(len(response_trip['result'])):
            if count > 9:
                break

            image = response_trip['result'][i]["thumbnail_url"]
            if image == "":
                image = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png"

            title_trip = response_trip['result'][i]['route_name']
            if len(title_trip) > 45:
                title_trip = response_trip['result'][i]['route_name'][:45] + "..."

            intro_trip = response_trip['result'][i]['route_introduction']
            if len(intro_trip) > 45:
                intro_trip = response_trip['result'][i]['route_introduction'][:45] + "..."

            col = {"actions":[],"defaultAction":{},"imageBackgroundColor": "#FFFFFF","title": title_trip,"thumbnailImageUrl":image,"text": intro_trip}
            uri = "https://thai.tourismthailand.org/home"

            col["actions"].append({"uri":uri,"label":"รายละเอียด","type":"uri"})
            col["defaultAction"] = {"type":"uri","label":"รายละเอียด","uri":"https://thai.tourismthailand.org/home"}
            answer["payload"]["line"]["template"]["columns"].append(col)
            count += 1

    answer_from_bot = {"fulfillmentMessages": [answer]}
    answer_from_bot = json.dumps(answer_from_bot, indent=4)
    return answer_from_bot






