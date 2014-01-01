import Levenshtein
import sqlite3
import time
import threading
import random
import re

def ask_question():
    conn = sqlite3.connect("clues.db")
    c = conn.cursor()
    rows = int(c.execute("SELECT Count(*) FROM clues").fetchone()[0])
    clueid = str(random.randint(0, rows - 1))
    clue = c.execute("SELECT value, category, clue, answer \
                      FROM clues \
                      JOIN documents ON clues.id = documents.id \
                      JOIN classifications ON clues.id = classifications.clue_id \
                      JOIN categories ON classifications.category_id = categories.id \
                      WHERE clues.id = (?)", [clueid]).fetchone()

    print(clue)
    #rivia.answer = clue[3]
    trivia.answer = clean_answer(clue[3])
    hint = ""
    for chr in trivia.answer:
        hint = hint + re.sub(r'[a-zA-Z0-9]', "*", chr)
    trivia.hint = hint

    trivia.value = int(str(clue[0]).replace(",", ""))
    if trivia.value == 0:
       trivia.value = 5000
    trivia.question = "Question: ${}. [ {} ] {} \nHint: {}".format(trivia.value, clue[1], clue[2], hint)
    trivia.e.output = trivia.question
    trivia.gameon = True
    trivia.bot.botSay(trivia.e)
    trivia.timer = threading.Timer(trivia.qtime, failed_answer)
    trivia.timer.start()

def question_time(self, e):
    try:
       trivia.qtime = int(e.input)
    except:
       pass
question_time.command = "!qtime"

def failed_answer():
    e = trivia.e
    trivia.timer.cancel()
    trivia.gameon = False
    e.output = "FAIL! no one guessed the answer: {}".format(trivia.answer)
    trivia.bot.botSay(e)
    if not trivia.stoptrivia:
        trivia.qtimer=threading.Timer(10, ask_question)
        trivia.qtimer.start()


def play_trivia(self, e):
#    if trivia.gameon == True:
#       e.output = "Trivia is already running"
#       return e
    trivia.bot = self
    trivia.e = e
    e.output = "Trivia started! Use !strivia to stop"
    trivia.points = {}
    trivia.stoptrivia = False
    self.botSay(e)
    ask_question()
play_trivia.command = "!trivia"


def trivia_q(self, e):
    trivia.bot = self
    trivia.e = e
    ask_question()
    trivia.stoptrivia = True
trivia_q.command = "!triviaq"

def stop_trivia(self, e):
#    trivia.answer = ""
#    trivia.question = ""
#    trivia.hint = ""
    if trivia.gameon == True:
        trivia.stoptrivia = True
        e.output = "Trivia Stopped after the answer is given"
        return e
    else:
        trivia.gameon = False
        trivia.timer.cancel()
        trivia.qtimer.cancel()
        e.output = "Trivia stopped"
        return e
stop_trivia.command = "!strivia"

def show_points(self, e):
    e.output = str(trivia.points)
    return e
show_points.command = "!score"

def reset_score(self, e):
    trivia.points = {}
#reset_score.command = "!resetscore"

def clean_answer(answer):
    #gets rid of articles like 'The' Answer, 'An' Answer, 'A' cat, etc.
    #also removes a few cases like Answer (alternate answer) - removes anything in ()
    answer = answer.lower()
    if answer[0:4] == "the ":
       answer = answer[4:]
    if answer[0:3] == "an ":
       answer = answer[3:]
    if answer[0:2] == "a ":
       answer = answer[2:]
    
    answer = answer.replace('"', "")
    answer = re.sub(r'\(.*?\)', '', answer)
    
    return answer.strip()


def make_hint(self, e):
    if trivia.gameon == False:
       return
    trivia.value = round(trivia.value / 2)
    hint = ""
    i = 0
    for chr in trivia.hint:
       if random.randint(0, 3) == 1 or i == 0:
           hint = hint + trivia.answer[i]
       else:
           hint = hint + chr
       i += 1
    trivia.hint = hint
    e.output = "Hint ${}: {}".format(trivia.value, hint)
    return e
make_hint.command = "!hint"


def trivia():
    pass
trivia.gameon = False
trivia.stoptrivia = False
trivia.qtime = 30
trivia.points = {}

def answer_grabber(self, e):
  
    if trivia.gameon == True:
        print(e.input)
        ratio = Levenshtein.ratio(e.input.lower(), trivia.answer)
#    if ratio > 0.95:
        print(ratio)
        if ratio > 0.90:
            trivia.gameon = False 
            trivia.timer.cancel()

            try:
                x = trivia.points[e.nick]
            except:
                trivia.points[e.nick] = 0
            trivia.points[e.nick] = trivia.points[e.nick] + trivia.value
            
            e.output = "Winrar! {} [ {} pts ] got the answer: {}".format(e.nick, trivia.points[e.nick], trivia.answer)
            self.botSay(e)

            if trivia.stoptrivia == True:
                trivia.gameon = False
                trivia.stoptrivia = False
            else: 
               trivia.qtimer=threading.Timer(10, ask_question)
               trivia.qtimer.start()

answer_grabber.lineparser = True

