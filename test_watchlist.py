import unittest

from app import app, db, Movie, User, forge, initdb, admin


class WatchlistTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(
            WTF_CSRF_ENABLED = False,
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )
        db.create_all()
        user = User(name='Test', user_name='test')
        user.set_password('123')
        movie = Movie(title="Test Movie Title", year='2019')
        db.session.add_all([user, movie])
        db.session.commit()

        self.client = app.test_client()
        self.runner = app.test_cli_runner()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_app_exist(self):
        self.assertIsNotNone(app)

    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    def test_404_page(self):
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)
        self.assertIn('Page Not Found - 404', data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code, 404)

    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn("Test's Watchlist", data)
        self.assertIn("Test Movie Title", data)
        self.assertEqual(response.status_code, 200)

    def login(self):
        self.client.post(
            '/login', 
            data = dict(user_name='test', password='123'),
            follow_redirects = True
        )
        # response = self.client.post(
        #     '/login', 
        #     data = dict(user_name='test', password='123'),
        #     follow_redirects = True
        # )
        # return response.get_data(as_text=True)

    def test_create_item(self):
        # data = self.login() 
        # self.assertIn('Login success.', data)
        self.login() 
        response = self.client.post(
            '/', 
            data = dict(title='New Movie', year='2019'), 
            follow_redirects = True
        )
        data = response.get_data(as_text=True)
        self.assertIn('New Movie', data)
        self.assertIn('Item created.', data)

        response = self.client.post(
            '/',
            data = dict(title='', year='2019'),
            follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)

        response = self.client.post(
            '/',
            data = dict(title='New Movie', year=''),
            follow_redirects = True
        )
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.', data)
        self.assertIn('Invalid input.', data)

    def test_edit_item(self):
        self.login()

        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('Edit item', data)
        self.assertIn('Test Movie Title', data)
        self.assertIn('2019', data)

        response = self.client.post(
            '/movie/edit/1', 
            data = dict(title='Edited Movie Title', year='2019'),
            follow_redirects = True
        )
        data = response.get_data(as_text=True)
        self.assertIn('Edited Movie Title', data)
        self.assertIn('Item updated.', data)
        self.assertNotIn('Test Movie Title', data)

        response = self.client.post(
            '/movie/edit/1', 
            data = dict(title='', year='2020'),
            follow_redirects = True
        )
        data = response.get_data(as_text=True)
        self.assertIn('Invalid input.', data)
        self.assertNotIn('Item updated.', data)

        response = self.client.post(
            '/movie/edit/1', 
            data = dict(title='Edited Movie Title Again', year=''),
            follow_redirects = True
        )
        data = response.get_data(as_text=True)
        self.assertIn('Invalid input.', data)
        self.assertNotIn('Item updated.', data)

    def test_delete_item(self):
        self.login()
        response = self.client.post('/movie/delete/1', follow_redirects = True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted.', data)
        self.assertNotIn('Test Movie Title', data)

    def test_login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout', data)
        self.assertNotIn('<form method="post">', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)

    def test_login(self):
        self.login()
        response = self.client.post(
            '/login', 
            data = dict(user_name='test', password='123'),
            follow_redirects = True
        )
        data = response.get_data(as_text=True)
        self.assertIn('Login success.', data)
        self.assertIn('Logout', data)
        self.assertIn('<form method="post">', data)
        self.assertIn('Delete', data)
        self.assertIn('Edit', data)

        response = self.client.post(
            '/login',
            data = dict(user_name='test', password='456'),
            follow_redirects = True
        )
        data = response.get_data(as_text=True)
        self.assertNotIn('Login success.', data)
        self.assertIn('Incorrect username or password.', data)

    def test_logout(self):
        self.login()
        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('GoodBye.', data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('<form method="post">', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)

    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn('Made data.', result.output)
        self.assertNotEqual(Movie.query.count(), 0)

    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database.', result.output)

    def test_admin_command(self):
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(
            args=['admin', 
                  '--username', 'testname',
                  '--password', '123']
        )
        self.assertIn('Creating administrator...', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().user_name, 'testname')
        self.assertTrue(User.query.first().validate_password('123'))

        result = self.runner.invoke(
            args=['admin',
                  '--username', 'test_admin_update', 
                  '--password', '456']
        )
        self.assertIn('Done.', result.output)
        self.assertNotIn('Creating administrator...', result.output)
        self.assertEqual(User.query.first().user_name, 'test_admin_update')
        self.assertTrue(User.query.first().validate_password('456'))
        self.assertFalse(User.query.first().validate_password('123'))


if __name__ == "__main__":
    unittest.main()