import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres', '0100013181','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertTrue(res.status_code==200 or res.status_code==404)
        self.assertTrue(data['success'] == True or data['success'] == False)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])        
    
    def test_delete_question(self):
        res = self.client().delete('/questions/23')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
       
    def test_404_requesting_delete_question(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['message'],'Not Found')
   
    def test_post_add_question(self):
        res = self.client().post('/questions', json={'question':'Can You Test ?' , 'answer':'Yes I Can.' , 'difficulty':5 ,'category':4 })
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)

    def test_400_requseting_post_add_question(self):
        res = self.client().post('/questions',json={'question':'Can You Test ?' , 'category':4 })
        data = json.loads(res.data)
        self.assertEqual(res.status_code,400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],400)
        self.assertEqual(data['message'],'Bad Request')      

    def test_404_requesting_post_add_question_with_not_existed_category(self):
        res = self.client().post('/questions',json={'question':'Can You Test ?' , 'answer':'Yes I Can.' , 'difficulty':5 , 'category':1000 })
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['message'],'Not Found')     

    def test_post_search_questions(self):
        res = self.client().post('/questions', json={'searchTerm' : 'boxer' })
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'] >= 0)       
        self.assertTrue(data['questions'] or data['questions'] == [])     

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])       
        self.assertTrue(data['questions'])   
        self.assertEqual(data['current_category']['id'] , 4 )

    def test_404_requesting_questions_of_not_existed_category(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['message'],'Not Found')

    def test_post_quizzes(self):
        res = self.client().post('/quizzes',json={ 'previous_questions' : [9,12],"quiz_category" : 
              {
              "id": 4,
              "type": "History"
              }})
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)          
        self.assertTrue(data['question'])  
        self.assertEqual(data['question']['category'],4)
        self.assertTrue(data['question']['id'] != 9 and data['question']['id'] != 12 )  

    def test_400_requesting_quizzes_with_missing_arguments(self):
        res = self.client().post('/quizzes',json={ "quiz_category" : 
              {
              "id": 4,
              "type": "History"
              }})
        data = json.loads(res.data)
        self.assertEqual(res.status_code,400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],400)
        self.assertEqual(data['message'],'Bad Request')      
        
        
                 
          
        

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()