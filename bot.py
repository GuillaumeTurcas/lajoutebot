import mysql.connector
import json
import requests
import time
import urllib
import random
from config import TOKEN, hst, usr, psswd, db

URL = "https://api.telegram.org/bot{}/".format(TOKEN)



mydb = mysql.connector.connect(
  host = hst,
  user = usr,
  password = psswd,
  database = db
)

mycursor = mydb.cursor()

'''------------
|The must have|
------------'''

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


'''-----------------
|Commandes telegram|
-----------------'''

def getStart():
    start = """Bienvenue sur le bot officiel de Joute de Vinci !

Les commandes disponibles sont :
- /site pour obtenir l'adresse du site
- /sujet pour obtenir un sujet aléatoire
- /game pour obtenir un sujet et les positions"""

    return start


def ransujet(types):

    if types == "cs":
        mycursor.execute("SELECT sujet FROM sujets WHERE type = 'cs'")  

    else:
        mycursor.execute("SELECT sujet FROM sujets WHERE type = 'dp'")

    sujets = mycursor.fetchall()

    i = len(sujets)
    c = random.randint(0, i-1)
    sujet = str(sujets[c])
    sujet = sujet[2:-3]
    return sujet


def choc(chat, last_update_id, choc = False):
    eq = ['','']
    c = random.randint(0,1)

    game = ["Nom du premier jouteur !", "Nom du second jouteur !", 
            "cs", "À la positive", "À la négative"]

    if choc == False:
        game = ["Nom de l\'équipe 1", "Nom de l\'équipe 2", 
                "dp", "Au Gouvernement", "À l'Opposition"]

    for i in range(0,2):

        send_message(game[i], chat)
        step = 0

        while step == 0 :
            updates = get_updates(last_update_id)
            if len(updates["result"]) > 0:
                last_update_id = get_last_update_id(updates) + 1
                eq[i], chat = retext(updates)
                step += 1
            time.sleep(0.5)

    simul = f"""Bonjours à tous !

Pour le choc de demain entre {eq[0]} et {eq[1]}, le sujet sera:

{ransujet(game[2])}

{game[3]} : {eq[c]}
{game[4]} : {eq[(c+1)%2]}

Bon courage !
"""
    return str(simul)


def retext(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
    return text, chat


'''------------
|Send messages|
------------'''


def echo_all(updates, last_update_id):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]

        if text == "/start":
            text = getStart()

        elif text == "/site":
            text = "https://www.lajoutedevinci.fr"

        elif text == "/sujet":
            text = ransujet('db')

        elif text == "/game":
            text = choc(chat, last_update_id)

        elif text == "/choc":
            text = choc(chat, last_update_id, True)

        elif text == "/welcome":
            text = "Bienvenue sur le groupe telegram de la Joute de Vinci ! "

        elif text == "Qui est le meilleur ?":
            text = "Guillaume Turcas sans hésiter !"

        elif text == "Non tu fais erreur":
            text = "Je ne me trompe jamais"

        elif text == "Quelle est la meilleure des assos ?":
            text = "La Joute de Vinci, c'est une évidence !"

        else :
            break

        send_message(text, chat)


def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            try :
                last_update_id = get_last_update_id(updates) + 1
                echo_all(updates, last_update_id)
            except :
                pass
        time.sleep(0.5)


if __name__ == '__main__':
    main()