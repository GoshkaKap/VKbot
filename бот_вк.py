import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
import nlpcloud

bot = vk_api.VkApi(token='blablabla')
session_api = bot.get_api()
longpool = VkLongPoll(bot)

def send_some_msg(id, some_text):
    bot.method("messages.send", {"user_id":id, "message":some_text,"random_id":0})

for event in longpool.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            msg = event.text.lower()
            id = event.user_id

            first_check = {
                            'api_version' : 'v1',
                            'main_token' : '2Ws9hR9R1kaZ',
                            'query_details' : 
                                {
                                'source_token' : '687_66edc5e066eef9b1df044d07a635b469', 
                                'text' : msg,
                                'dictionaries' :
                                    {
                                    'rus' : 
                                        [
                                         'heavy',
                                         'expletive'
                                        ]
                                    },
                                'deep_check' : 'no',
                                'translit_check' : 'yes'
                                }
                          }
            
            res = requests.post('https://lf.statusnick.com/api/text/check', json = first_check).json()
            try: 
                if res['result']['final']['check']['check_result'] != [] :
                    send_some_msg(id, 'Ваше обращение не принято к рассмотрению, так как оно содержит ненормативную лексику.')
                else :
                    client = nlpcloud.Client("bart-large-mnli-yahoo-answers", "2919728073d3aa51ed3e04d4e7eb5153eab05b6d")
                    res = client.classification(msg, labels=['собака', 'бродячие', 
                                                             'газ', 'вода', 'труба', 'пар', 'лифт', 'мусор',
                                                             'расселение'], multi_class=True)
                    res2 = client.classification(msg, labels=['пёс', 'бешенные', 'животные',
                                                              'дороги', 'ямы', 
                                                              'прорвало', 'электричество', 'крыша'
                                                              'ветхое', 'фонд'], multi_class=True)
                    #res['scores'] += res2['scores']
                    #res['labels'] += res['labels']
                    
                    if max(res['scores']) - min(res['scores']) <= 0.22 :
                        problem = True
                        hello = ['здравствуйте', 'привет', 'добр' ]
                        bye = ['до свид', 'пока']
                        for i in range(0, len(hello)-1) :
                            if -1 < msg.find(hello[i]) < len(hello) :
                                    problem = False
                                    send_some_msg(id, 'Здравствуйте! \nЯ - бот-помощник главы региона и могу ответить на интересующие Вас вопросы')
                                    break
                            elif i < len(bye):
                                if -1 < msg.find(bye[i]) < len(bye) :
                                    problem = False
                                    send_some_msg(id, 'До свидания! \nНадеюсь, мы смогли решить Ваш вопрос. Буду рад помочь Вам снова')
                                    break
                        if problem :
                            send_some_msg(id, 'Мы Вас не поняли \nПопробуйте сформулировать Вашу проблему иначе')
                    else :
                        index_max = res['scores'].index(max(res['scores']))
                        answer = res['labels'][index_max]
                        score = res['scores'][index_max]

                        animals = ['собака', 'бродячие', 'пёс', 'бешенные', 'животные']
                        ways =    ['дороги и ямы', 'дороги', 'ямы']
                        streets = ['газ', 'вода', 'труба', 'пар', 'лифт', 'мусор', 'прорвало', 'электричество', 'крыша']
                        home =    ['расселение', 'ветхое', 'фонд']
                        
                        for i in range(0, len(streets)-1) :
                            if i < len(animals) :
                                if answer == animals[i] :
                                    send_some_msg(id, 'Благодарим за обращение! \nВ Вашем городе уже работают службы по отлову бродячих животных\npublication.pravo.gov.ru/document/1401202308240001?index=1')
                                    break
                            elif i < len(ways) :
                                if answer == ways[i] :
                                    send_some_msg(id, 'Благодарим за обращение! \nВ регионе уже активно ведутся работы по улучшению дорог \npublication.pravo.gov.ru/document/1400202308250001')
                                    break
                            if answer == streets[i]:
                                    send_some_msg(id, 'Большое спасибо за Ваше сообщение! \nМы передадим его оператору, но для ускорения решения вопроса рекомендуем Вам позвонить в единую диспетчерскую службу по телефону +7(41136)4-41-12')
                                    break
                            elif i < len(home) :
                                if answer == home[i] :
                                    send_some_msg(id, 'Благодарим за обращение! \nВ Вашем районе уже действует программа по расселению ветхого жилья \nwww.алмазный-край.рф/for%20export/1673.pdf')
                                    break
            except: 
                send_some_msg(id, 'Вы вызвали сбой в системе! \nВероятно, Вы использовали стикеры или слишком часто отправляли сообщения')
            