from plugins import *

import sys, os, re, string
import urllib, urllib2, cookielib 
from BeautifulSoup import BeautifulSoup

class PluginCoursera(LinksProvider):
	"""
	Log in to Coursera, and download the specified enrolled course.
	"""
	name = "Coursera"
	desc = "Coursera Course Downloader"
	help = '''See -h for flag usage, look for flags prefixed with 'sera'. Specifically, you must provide the username, password and course short-hand.'''
	prefix = "sera"

	base = "https://www.coursera.org/" # main site
	base_course = "https://class.coursera.org/" # courses
	end_clogin = "/auth/auth_redirector?type=login&subtype=normal" # course login
	URLs = {
		"LOGIN": base + "maestro/auth/api/user/login", # site login

		"COURSE": {
			"lectures": base_course + "%s" + "/lecture/index"
		}
	}

	def __init__(self, argsparser):
		argsparser.plugin_add_argument(
			'-sera_u', 
			'--sera_user', 
			dest = 'sera_user',
			action = 'store',
			default = None,
			help = '''
				[%s][REQUIRED] Username to log in to Coursera.''' % self.name)

		argsparser.plugin_add_argument(
			'-sera_p', 
			'--sera_pass', 
			dest = 'sera_pass',
			action = 'store',
			default = None,
			#------------------------------------------------------
			help = '''
				[%s][REQUIRED] Password to log in to Coursera.''' % self.name)

		argsparser.plugin_add_argument(
			'-sera_c', 
			'--sera_course', 
			dest = 'sera_course',
			action = 'store',
			default = None,
			#------------------------------------------------------
			help = '''
				[%s][REQUIRED] Course short-hand name to download.

				Look at the URL for the course after logging in to see what the short-hand is.

				Ex: for Natural Language Programming, it's "nlp"''' % self.name)

		self.argsparser = argsparser

	def start(self):
		"""
		Start gathering data from the specified Coursera course to download
		"""
		self._check_args()

		self._login()

		return self.get_downloadables()

	def get_downloadables(self):
		return []

	def _login(self):
		"""
		Login to Coursera course.
		"""
		cj = self.cj = cookielib.CookieJar()
		opener = self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		login_data = self.login_data = urllib.urlencode({
			'email_address' : self.args.sera_user, 
			'password' : self.args.sera_pass, 
			'csrf_token' : ""
		})

		# do login
		# print cj
		resp = opener.open(self.URLs['LOGIN'], login_data) #line 7123 from js
		# print cj
		resp = opener.open(self._get_course_main_url() + self.end_clogin, login_data)
		# print cj
		# resp = opener.open('https://class.coursera.org/nlp/lecture/index')
		print self._get_course_url('lectures')
		# print resp.read()#[7000:10000]

	def _get_course_main_url(self):
		return self.base_course + self.course

	def _get_course_url(self, key):
		return self.URLs['COURSE'][key] % self.course

	def _check_args(self):
		"""
		Check that all arguments are provided and valid.
		"""
		args = self.args = self.argsparser.parse_args()

		if args.sera_user is None:
			raise AttributeError("--%s: Username is required." % "sera_user")

		if args.sera_pass is None:
			raise AttributeError("--%s: Password is required." % "sera_pass")

		if args.sera_course is None:
			raise AttributeError("--%s: Course short-hand is required." % "sera_course")

		self.course = args.sera_course

