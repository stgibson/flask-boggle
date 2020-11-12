from unittest import TestCase
from app import app
from flask import session, json
from boggle import Boggle

class FlaskTests(TestCase):
    def test_show_game_page(self):
        with app.test_client() as client:
            resp = client.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(session["highscore"], 0)
            self.assertEqual(session["num_of_times_played"], 0)
            self.assertIn("Your highest score: 0", html)
            self.assertIn("You have played 0 times", html)

    def test_show_game_page_with_stats(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["highscore"] = 14
                change_session["num_of_times_played"] = 3

            resp = client.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(session["highscore"], 14)
            self.assertEqual(session["num_of_times_played"], 3)
            self.assertIn("Your highest score: 14", html)
            self.assertIn("You have played 3 times", html)

    def test_start_game(self):
        with app.test_client() as client:
            resp = client.get("/game?dimensions=7")
            
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(session["board"]), 7)
            
            for row in session["board"]:
                self.assertEqual(len(row), 7)

                for cell in row:
                    self.assertIsInstance(cell, str)

    def test_check_guess(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                board = []
                for i in range(5):
                    row = []
                    for j in range(5):
                        row.append("A")
                    board.append(row)
                
                change_session["board"] = board

            resp = client.post("/guess", json={ "guess": "a" })
            data = json.loads(resp.data)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data["result"], "ok")

            resp = client.post("/guess", json={ "guess": "aaa" })
            data = json.loads(resp.data)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data["result"], "not-word")

            resp = client.post("/guess", json={ "guess": "ask" })
            data = json.loads(resp.data)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data["result"], "not-on-board")

    def test_update_stats(self):
        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session["highscore"] = 14
                change_session["num_of_times_played"] = 3

            resp = client.post("/stats", json={ "score": 10 })
            data = json.loads(resp.data)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data["highscore"], 14)
            self.assertEqual(data["num_of_times_played"], 4)
            self.assertEqual(session["highscore"], 14)
            self.assertEqual(session["num_of_times_played"], 4)

            resp = client.post("/stats", json={ "score": 20 })
            data = json.loads(resp.data)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(data["highscore"], 20)
            self.assertEqual(data["num_of_times_played"], 5)
            self.assertEqual(session["highscore"], 20)
            self.assertEqual(session["num_of_times_played"], 5)