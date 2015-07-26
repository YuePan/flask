import os
import simple
import unittest
import tempfile

class SimpleTestCase(unittest.TestCase):
	
	def setUp(self):
		self.db_fd, simple.app.config['DATABASE'] = tempfile.mkstemp()
		simple.app.config['TESTING'] = True
		self.app = simple.app.test_client()
		simple.init_db()
		
	def tearDown(self):
		os.close(self.db_fd)
		os.unlink(simple.app.config['DATABASE'])
		
	def test_empty_db(self):
		rv = self.app.get('/')
		assert bytes('No entries here so far', 'utf-8') in rv.data
		
	def login(self, username, password):
		return self.app.post('/login', data=dict(
			username=username,
			password=password
		), follow_redirects=True)
		
	def logout(self):
		return self.app.get('/logout', follow_redirects=True)
	
	def test_login_logout(self):
		rv = self.login('admin', 'default')
		assert bytes('You were logged in', 'utf-8') in rv.data
		rv = self.logout()
		assert bytes('You were logged out', 'utf-8') in rv.data
		rv = self.login('adminx', 'default')
		assert bytes('Invalid username', 'utf-8') in rv.data
		rv = self.login('admin', 'defaultx')
		assert bytes('Invalid password', 'utf-8') in rv.data
	
	def test_message(self):
		self.login('admin', 'default')	
		rv = self.app.post('/add', data=dict(
			title='<Hello>',
			text='<strong>HTML</strong> allowed here'
		), follow_redirects=True)
		assert bytes('No entries here so far', 'utf-8') not in rv.data
		assert bytes('&lt;Hello&gt;', 'utf-8') in rv.data
		assert bytes('<strong>HTML</strong> allowed here', 'utf-8') in rv.data
		
		
if __name__ == '__main__':
	unittest.main()
	