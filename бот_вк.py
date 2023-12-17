import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
import nlpcloud
import time

bot = vk_api.VkApi(token='token')
session_api = bot.get_api()
longpool = VkLongPoll(bot)       

#Мы подключились к нашему боту

def what(msg) : # функция для получения тематики текста
    client = nlpcloud.Client("bart-large-mnli-yahoo-answers", "token")
    res = client.classification(msg, labels=['собака', 'бродячие', 
                                             'газ', 'вода', 'труба', 'пар', 'лифт работает', 'мусор',
                                             'расселение', 'расселят'], multi_class=True)
    res2 = client.classification(msg, labels=['кошка', 'крыса', 'животные',
                                              'плохие дороги', 'ямы', 
                                              'прорвало', 'электричество', 'крыша'
                                              'ветхое', 'жильё'], multi_class=True)
    return([res,res2])

def send_some_msg(id, some_text): #функция для упрощения отправки сообщений
    text = ''
    for i in some_text :
        text += i

    bot.method("messages.send", {"user_id":id, "message":text,"random_id":0})

for event in longpool.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            # Ниже представлено основное решение
            msg = event.text.lower()
            id  = event.user_id          #записываем данные о сообщении и отправителе

            first_check =  { #создаём словарь для отправки его в сервис
                            'api_version'   : 'v1',
                            'main_token'    : 'token',
                            'query_details' : 
                                {
                                'source_token' : 'token', 
                                'text'         : msg,
                                'dictionaries' :
                                    {
                                     'rus' : 
                                            [
                                             'heavy',
                                             'expletive'
                                            ]
                                    },
                                'deep_check'     : 'no',
                                'translit_check' : 'yes'
                                }
                          }
            
            res = requests.post('https://lf.statusnick.com/api/text/check', json = first_check).json() #проверяем текст на наличие ненормативной лексики
            lose = False
            try :
                if res['result']['final']['check']['check_result'] != [] : #если запрещённые слова имеются, то данный if выполнится
                    lose = True
                    send_some_msg(id, ['Ваше обращение не принято к рассмотрению, так как оно содержит ненормативную лексику.'])
            except KeyError: #KeyError будет вызван, если отправлен стикер
                lose = True
                send_some_msg(id, ['Вы вызвали сбой в системе! \n',
                                   'Бот принимает только текст'])
            if lose == False : #если у сообщения можно определить тематику, данный if выполнится
                often = False
                try:
                    res = what(msg)
                    res2 = res[1]
                    res = res[0]            #Получили вероятность каждой темы
                except requests.exceptions.HTTPError :
                    try:
                        time.sleep(35)                  #requests.exceptions.HTTPError будет вызван, если к серверу обращаются слишком часто
                        res = what(msg)
                        res2 = res[1]
                        res = res[0]
                    except requests.exceptions.HTTPError :
                        send_some_msg(id, ['Вы слишком часто отправляете сообщения!'])
                        often = True

                if often == False : #когда мы имеем вероятности тем, if выполнится
                    animals = sum(res['scores'][0:2] + res2['scores'][0:3])   / len(res['scores'][0:2] + res2['scores'][0:3])                            
                    ways    = sum(res2['scores'][3:5])                        / len(res2['scores'][3:5])                                                   
                    streets = sum(res['scores'][2:8] + res2['scores'][5:8])   / (len(res['scores'][2:8] + res2['scores'][5:8]) - 1)         
                    home    = sum(res['scores'][8:10] + res2['scores'][8:10]) / len(res['scores'][8:10] + res2['scores'][8:10])

                    scores = [animals, ways, streets, home]      #находим общую вероятность каждой темы и записываем в список
                    if  max(scores) - min(scores) < 0.065:     #если боту плохо удалось определить тему, if выполнится
                        hello = ['здравствуйте', 'привет', 'добр' ]
                        bye   = ['до свид', 'пока']

                        problem = True
                        for i in range(0, len(hello)-1) : #проверяем, является ли сообщение приветствием или прощанием
                            if -1 < msg.find(hello[i]) < len(hello) :
                                    problem = False
                                    send_some_msg(id, ['Здравствуйте! \n',
                                                       'Я - бот-помощник главы региона и могу ответить на интересующие Вас вопросы'])
                                    break   
                            elif i < len(bye):
                                if -1 < msg.find(bye[i]) < len(bye) :
                                    problem = False
                                    send_some_msg(id, ['До свидания! \n',
                                                       'Надеюсь, мы смогли решить Ваш вопрос. Буду рад помочь Вам снова'])
                                    break
                        if problem :   #если сообщение не является приветствием или прощанием, произойдёт следующее:
                            send_some_msg(id, ['Мы Вас не поняли \n',
                                               'Попробуйте сформулировать Вашу проблему иначе'])
                    else :                        
                        index_max = scores.index(max(scores)) #определяем тему 

                        if   index_max == 0 :                           #организуем ответ по каждой теме
                            send_some_msg(id, ['Благодарим за обращение! \n',
                                               'В Вашем городе уже работают службы по отлову бродячих животных \n',
                                               'publication.pravo.gov.ru/document/1401202308240001?index=1'])
                        elif index_max == 1 :
                            send_some_msg(id, ['Благодарим за обращение! \n',
                                               'В регионе уже активно ведутся работы по улучшению дорог \n',
                                               'publication.pravo.gov.ru/document/1400202308250001'])
                        elif index_max == 2:
                            send_some_msg(id, ['Большое спасибо за Ваше сообщение! \n',
                                               'Мы передадим его оператору, но для ускорения решения вопроса рекомендуем Вам позвонить в единую диспетчерскую службу по телефону +7(41136)4-41-12'])
                        elif index_max == 3 :
                            send_some_msg(id, ['Благодарим за обращение! \n',
                                               'В Вашем районе уже действует программа по расселению ветхого жилья \n',
                                               'www.алмазный-край.рф/for%20export/1673.pdf'])
