import Levenshtein
import sqlite3
import time
import threading
import random
import re


def play_trivia(self, e):
    if trivia.gameon or trivia.delaytimer:
        e.output = "Trivia is already running"
        return e
    trivia.bot = self
    trivia.e = e

    e.output = "Trivia started! Use !strivia to stop"
    trivia.points = {}  # Currently we reset all points before starting recurring trivia
    trivia.questions_asked = 0
    trivia.stoptrivia = False
    self.botSay(e)
    ask_question()

play_trivia.command = "!trivia"


def trivia():
    pass
trivia.gameon = False
trivia.stoptrivia = False
trivia.autohint = True
trivia.qtime = 30
trivia.qdelay = 7
trivia.points = {}
trivia.questions_asked = 0
trivia.delaytimer = None


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
    trivia.answer = clean_answer(clue[3])
    hint = ""
    for char in trivia.answer:
        hint = hint + re.sub(r'[a-zA-Z0-9]', "*", char)
    trivia.hint = hint

    trivia.value = int(str(clue[0]).replace(",", ""))
    if trivia.value == 0:
        trivia.value = 5000
    trivia.questions_asked += 1
    trivia.question = "Question {}: ${}. [ {} ] {} \nHint: {}".format(
                                                                     trivia.questions_asked,
                                                                     trivia.value,
                                                                     clue[1],
                                                                     clue[2],
                                                                     hint
                                                                     )
    trivia.e.output = trivia.question
    trivia.gameon = True
    trivia.qtimestamp = time.time()
    trivia.bot.botSay(trivia.e)
    if trivia.autohint:
        trivia.timer = threading.Timer(round(trivia.qtime / 2), first_hint)
    else:
        trivia.timer = threading.Timer(trivia.qtime, failed_answer)
    trivia.timer.start()


def tq(self, e):
    e.output = trivia.question
    return e
tq.command = "!tq"


def clean_answer(answer):
    #gets rid of articles like 'The' Answer, 'An' Answer, 'A' cat, etc.
    #also removes a few cases like Answer (alternate answer) - removes anything in ()
    #gets rid of the "" marks in "answer"
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


def trivia_q(self, e):
    if trivia.gameon or trivia.delaytimer:
        e.output = "Trivia is already running"
        return e
    #Current method of getting only 1 question
    trivia.bot = self
    trivia.e = e
    trivia.questions_asked = 0
    ask_question()
    trivia.stoptrivia = True
trivia_q.command = "!triviaq"


def question_time(self, e):
    try:
        if int(e.input) >= 5:
            if int(e.input) <= 120:
                trivia.qtime = int(e.input)
            else:
                trivia.qtime = 120
        else:
            trivia.qtime = 5
    except:
        print("failed")
        pass
question_time.command = "!qtime"


def question_delay(self, e):
    try:
        if int(e.input) >= 1:
            if int(e.input) <= 30:
                trivia.qdelay = int(e.input)
            else:
                trivia.qdelay = 30
        else:
            trivia.qtime = 1
    except:
        pass
question_delay.command = "!qdelay"


def first_hint():
    trivia.value = round(trivia.value / 2)
    trivia.hint = perc_hint(30, trivia.hint, trivia.answer)
    trivia.e.output = "Hint1 ${}: {}".format(trivia.value, trivia.hint)
    trivia.bot.botSay(trivia.e)
    trivia.timer = threading.Timer(round(trivia.qtime / 6), second_hint)
    trivia.timer.start()


def second_hint():
    trivia.value = round(trivia.value / 2)
    trivia.hint = perc_hint(45, trivia.hint, trivia.answer)
    trivia.e.output = "Hint2 ${}: {}".format(trivia.value, trivia.hint)
    trivia.bot.botSay(trivia.e)
    trivia.timer = threading.Timer(round(trivia.qtime / 6), third_hint)
    trivia.timer.start()


def third_hint():
    trivia.value = round(trivia.value / 2)
    trivia.hint = perc_hint(75, trivia.hint, trivia.answer)
    trivia.e.output = "Hint3 ${}: {}".format(trivia.value, trivia.hint)
    trivia.bot.botSay(trivia.e)
    trivia.timer = threading.Timer(round(trivia.qtime / 6), failed_answer)
    trivia.timer.start()


def auto_hint(self, e):
    if e.input == "on":
        trivia.autohint = True
    if e.input == "off":
        trivia.autohint = False
auto_hint.command = "!autohint"


def perc_hint(revealpercent, hint, answer):
    letters = [0]
    for i in range(round(len(trivia.answer) * (revealpercent / 100))):
        letters.append(random.randint(0, len(trivia.answer)))
    i = 0
    hint = ""
    for char in trivia.answer:
        if i in letters:
            hint += trivia.answer[i]
        else:
            hint += trivia.hint[i]
        i += 1

    return hint


def failed_answer():
    e = trivia.e
    trivia.timer.cancel()
    trivia.gameon = False
    e.output = "FAIL! no one guessed the answer: {}".format(trivia.answer)
    trivia.bot.botSay(e)
    if not trivia.stoptrivia:
        trivia.delaytimer = threading.Timer(trivia.qdelay, ask_question)
        trivia.delaytimer.start()


def stop_trivia(self, e):
    if trivia.gameon:
        if e.input == "cancel":
            e.output = "Trivia will continue"
            trivia.stoptrivia = False
            return e
        else:
            trivia.stoptrivia = True
            e.output = "Trivia Stopped after the answer is given"
            return e
    else:
        trivia.gameon = False
        trivia.timer.cancel()
        trivia.delaytimer.cancel()
        trivia.delaytimer = None
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


def make_hint(self, e):
    if not trivia.gameon:
        return
    if trivia.autohint:
        e.output = "Hint ${}: {}".format(trivia.value, trivia.hint)
        return e
    trivia.value = round(trivia.value / 2)
    hint = ""
    i = 0
    for char in trivia.hint:
        if random.randint(0, 3) == 1 or i == 0:
            hint = hint + trivia.answer[i]
        else:
            hint = hint + char
        i += 1
    trivia.hint = hint
    e.output = "Hint ${}: {}".format(trivia.value, hint)

    return e
make_hint.command = "!hint"


def answer_grabber(self, e):
    # There's no need to continuously compute levenshtein ratio of everything or !hint
    if trivia.gameon and e.input.lower() != "!hint":

        ratio = Levenshtein.ratio(e.input.lower(), trivia.answer)
        print((e.input + " " + str(ratio)))  # Show the ratio of the guess for tuning

        if ratio >= 0.90:
            trivia.gameon = False
            trivia.timer.cancel()

            try:
                trivia.points[e.nick]
            except:
                trivia.points[e.nick] = [0, 0]  # Points, Number of questions
            trivia.points[e.nick][0] = trivia.points[e.nick][0] + trivia.value
            trivia.points[e.nick][1] += 1

            tmr = "{:.2f}".format(time.time() - trivia.qtimestamp)

            e.output = "Winrar in {} seconds! {} [ ${} in {} ] got the answer: {}".format(
                                                                                        tmr,
                                                                                        e.nick,
                                                                                        trivia.points[e.nick][0],
                                                                                        trivia.points[e.nick][1],
                                                                                        trivia.answer
                                                                                        )
            self.botSay(e)

            if trivia.stoptrivia:
                trivia.gameon = False
                trivia.delaytimer = None
            else:
                trivia.delaytimer = threading.Timer(trivia.qdelay, ask_question)
                trivia.delaytimer.start()

answer_grabber.lineparser = True

