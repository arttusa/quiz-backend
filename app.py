from flask_cors import CORS, cross_origin
from flask import Flask, jsonify, request, send_from_directory
from random import randrange
import requests
import json
import sqlite3
import base64


app = Flask(__name__, static_folder='client/build', static_url_path='')
cors = CORS(app)

# Main route for game
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')

"""
HTTP GET Returns list of 10 questions where each item is:
{
    answers: [
        "Rusty Nail",
        "Screwdriver",
        "Sex on the Beach",
        "Manhattan"
    ],
    correct_answer: "Rusty Nail",
    question: "Scotch whisky and Drambuie make up which cocktail?"
}
"""
@app.route('/api/questions')
@cross_origin()
def questions():
    questions = fetchQuestions()
    parsedQuestions = parseQuestions(questions)
    return jsonify(parsedQuestions)

"""
HTTP GET Returns list of 10 best scores
"""
@app.route('/api/scoreboard')
@cross_origin()
def scoreboard():
    scoreboard = getScoreboardDB()
    return jsonify(scoreboard)

"""
HTTP POST method which is called with following model
Returns updated scoreboard
{
	"name": "Arttu",
	"score": 9
}
"""
@app.route('/api/addscore', methods=['POST'])
@cross_origin()
def addscore():
    if request.method == 'POST': 
        res = json.loads(request.data) 
        insertScoreDB(res['name'], res['score'])
        updatedScoreboard = getScoreboardDB()
        return jsonify(updatedScoreboard)
    

"""
Fetches questions from Trivia API
"""
def fetchQuestions():
    res = requests.get("https://opentdb.com/api.php?amount=10&category=9&difficulty=medium&type=multiple&encode=base64")
    resJSON = json.loads(res.content)
    return resJSON  

"""
Parses necessary information (question, answers, correct answer) from given data
@param questions is JSON-response that has been fetched from Trivia API
"""
def parseQuestions(questions):
    questionList = questions['results']
    parsedQuestions = []
    for element in questionList:
        answers = element['incorrect_answers']
        for i, answer in enumerate(answers):
            print(answer, type(answer))
            answers[i] = parseBase64(answer)

        answers.insert(randrange(len(answers)+1), parseBase64(element['correct_answer']))
        data = {
            "question": parseBase64(element['question']),
            "answers": answers,
            "correct_answer": parseBase64(element['correct_answer'])
        }
        parsedQuestions.append(data)
    return parsedQuestions
    

"""
Parses input from base64 to UTF-8  
@param input is base64 string
"""
def parseBase64(input):
    message_bytes = base64.b64decode(input)
    message = message_bytes.decode('UTF-8')
    return message

"""
Inserts given data to database
@param name is players name
@param score is players score
"""
def insertScoreDB(name, score):
    conn = sqlite3.connect("scoreboard.db")
    c = conn.cursor()
    c.execute("BEGIN TRANSACTION")
    c.execute("INSERT INTO Scoreboard (Name, Score) VALUES (?, ?)", (name, score))
    c.execute("COMMIT TRANSACTION")


"""
Returns array of top ten results from database
"""
def getScoreboardDB():
    conn = sqlite3.connect("scoreboard.db")
    c = conn.cursor()
    c.execute('SELECT * FROM Scoreboard ORDER BY Score DESC LIMIT 10')
    scoreboard = c.fetchall()
    parsedScoreboard = []
    for score in scoreboard:
        data = {
            "name": score[0],
            "score": score[1]
        }
        parsedScoreboard.append(data)
    return parsedScoreboard


