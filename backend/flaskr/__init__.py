import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys
import random
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from models import setup_db, Question, Category
from array import array


QUESTIONS_PER_PAGE = 10
def paginated_questions(request,Selection):  
  page = request.args.get('page',1,type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = page * QUESTIONS_PER_PAGE
  current_list =  [Quest.format() for Quest in Selection ]
  ret = current_list[start:end]
  return ret

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def After_Request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories',methods=['GET'])  
  def get_categories():
      Cats = Category.query.all()
      formatted_Cats = {}
      for Cat in Cats : 
         formatted_Cats[Cat.id] = Cat.type  
      return jsonify({
        'success' : True,
        'categories' : formatted_Cats
      })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions' , methods=['GET'])
  def get_questions():
      Selection = Question.query.order_by(Question.id).all()
      if len(Selection) == 0:
        abort(404)
      formatted_Quest = paginated_questions(request,Selection)             
      formatted_Cats = {}
      for Cat in Category.query.all():
         formatted_Cats[Cat.id] = Cat.type       
         
      return jsonify({
        'success' : True,
        'questions' : formatted_Quest,
        'total_questions':len(Question.query.all()),
        'categories' : formatted_Cats,
        'current_category': None,
      })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>' , methods=['DELETE']) 
  def delete_question(id):
      question =  Question.query.filter(Question.id == id).one_or_none()
      if question == None:
          abort(404)
      try:
        question.delete()
        return jsonify({
          'success' : True
        }) 
      except: 
        abort(422) 
      

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions',methods=['POST'])
  def add_search_questions():     
      body = request.get_json()
      search_Term = body.get('searchTerm',None)
      if search_Term == None:
         question = body.get('question',None)
         answer = body.get('answer',None)
         difficulty = body.get('difficulty',None)
         category = body.get('category',None)
         if question == None or answer == None or difficulty == None or category == None:
            abort(400)
         temp = Category.query.get(int(category))
         if temp == None:
            abort(404)

         try:
            new_question = Question(question,answer,category,difficulty)
            new_question.insert()
            return jsonify({
              'success' : True
            })
         except:    
            abort(422)  
      else:
         related_questions = Question.query.filter(Question.question.ilike('%' + search_Term + '%')).all()
         formatted_questions = [quest.format() for quest in related_questions]
         return jsonify({
           'success' : True,
           'questions' : formatted_questions ,
           'total_questions' : len(related_questions),
           'current_category': None
         }) 
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions',methods=['GET'])
  def get_questions_by_cat(id):
      category = Category.query.filter(Category.id==id).one_or_none()
      if category == None:
        abort(404)
      related_questions = Question.query.filter(Question.category == str(category.id)).all()
      formatted_Questions = [quest.format() for quest in related_questions]
      return jsonify({
        'success' : True,
        'questions' : formatted_Questions,
        'total_questions' : len(related_questions),
        'current_category' : category.format()
      })
      
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST'])
  def quizzes():
      body = request.get_json()
      prev_Questions = body.get('previous_questions',None)
      current_Cat = body.get('quiz_category',None)
      if prev_Questions == None or current_Cat == None:
        abort(400)
      related_questions = Question.query.filter(Question.category == current_Cat['id']
                          ).filter(Question.id.notin_(prev_Questions)).all()
      if len(related_questions) == 0:
         return jsonify({
           'success' : True,
           'question' : None
         })            
      question = related_questions[random.randrange(0,len(related_questions))]  
      return jsonify({
        'success' : True,
        'question' : question.format()
      })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
        'success' : False,
        'error' : 404,
        'message' : 'Not Found'
      }) , 404    
 
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
        'success' : False,
        'error' : 400,
        'message' : 'Bad Request'
      }) , 400    
  

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
        'success' : False,
        'error' : 422,
        'message' : 'Un Processable'
      }) , 422    

  @app.errorhandler(405) 
  def not_allowed(error):
      return jsonify({
        'success' : False,
        'error' : 405,
        'message' : 'Not Allowed'
      }) , 405   

  
  return app

    