from plugins import *

import sys, os, re, string
import urllib, urllib2, cookielib 
import unicodedata
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
			"lectures": base_course + "%s" + "/lecture/index" # video lectures
		}
	}

	def __init__(self, argsparser):
		LinksProvider.__init__(self, argsparser)

		self.cache = {}
		self.pages = {}

		self.argsparser = argsparser

		argsparser.plugin_add_argument('-sera_u', '--sera_user', 
			dest = 'sera_user',
			action = 'store',
			default = None,
			help = '''
				[%s][REQUIRED] Username to log in to Coursera.''' % self.name)

		argsparser.plugin_add_argument('-sera_p', '--sera_pass', 
			dest = 'sera_pass',
			action = 'store',
			default = None,
			help = '''
				[%s][REQUIRED] Password to log in to Coursera.''' % self.name)

		argsparser.plugin_add_argument('-sera_c', '--sera_course', 
			dest = 'sera_course',
			action = 'store',
			default = None,
			help = '''
				[%s][REQUIRED] Course short-hand name to download.

				Look at the URL for the course after logging in to see what the short-hand is.

				Ex: for Natural Language Programming, it's "nlp"''' % self.name)

	def start(self):
		"""
		Start gathering data from the specified Coursera course to download
		"""
		self._check_args()
		self._login()

		self._get_page_by_key('lectures')

		return self.get_downloadables()

	def get_downloadables(self):
		o = []

		o = o + self._get_downloadables_from__video_lectures()

		return o

	def _get_page_by_key(self, key, force=False):
		"""
		Download the course page specified by the given key, then return the
		page as a BeautifulSoup 'soup'

		If force=True, force re-download of page
		"""
		if key in self.pages and not force:
			return self.pages[key]

		url = self._get_course_key_url(key)
		resp = self.opener.open(url)

		print "_get_page_by_key[%s]: %s" % (key, url)

		self.pages[key] = BeautifulSoup(resp.read())

		return self.pages[key]

	def _get_downloadables_from__video_lectures(self, soup=None, force=False):
		"""
		Given some video lecture soup-y goodness, get all the stuff out of it
		that we need to download.

		If force=True, force re-parsing of page
		"""
		key = 'lectures'
		if key in self.cache and not force:
			return self.cache[key]

		if soup is None:
			soup = self.pages[key]

		o = []
		
		print "Get Downloadables[%s]..." % (key)

		item_list = soup("div", "item_list")[0]
		list_header_links = item_list('h3', 'list_header')
		lists = item_list('ul', 'item_section_list')

		# we should have a full pairing of each list_header_link and 
		# item_section_list
		assert len(list_header_links) == len(lists), "We don't have a matching set of downloads per header :("

		# find all downloadables per title
		i = 0
		file_name_format = "%02d - %s"
		for ul in lists:
			header = list_header_links[i]
			folder = file_name_format % (i + 1, self.__get_file_from_header(header.string))

			# print '_' * 80
			# print i, 'folder:', folder

			# get all list items for this section
			j = 0
			for li in ul('li', 'item_row'):
				# get file name
				li_lecture_link = li('a', 'lecture-link')[0]
				
				# filename/title and link so we can download any content that
				# may pop up during the video itself
				li_title = file_name_format % (j + 1, self.__get_file_from_header(li_lecture_link.contents[0]))
				li_href = li_lecture_link['href']
				assert len(li_title) > 0, "Couldn't get lecture title"

				# print '-' * 30
				# print i, j, "title:", li_title
				# print i, j, "link:", li_href

				# if len(li_href) > 0:
					# TODO stuff to get the content that pops up while watching
					# one of the videos
					# print

				# set all the resources as downloadable
				for li_res in li.div('a'):
					li_res_extension = self._get_file_type_from_title(li_res['title'])
					li_res_href = li_res['href']
					li_res_fname = li_title + "." + li_res_extension

					# print i, j, li_res_fname#, "<--", li_res_href 

					ndb = Downloadable(
							url = li_res_href,
							output_name = li_res_fname,
							sub_folder = os.path.join(key, os.path.join(folder, li_title))
						)
					o.append(ndb)

				j = j + 1

			i = i + 1

		return o

	def _get_file_type_from_title(self, title):
		"""
		Given a title from one of the 'div.item_resource > a' links, return
		the suitable file extension to use.
		"""
		title = title.lower()

		if title == "ppt" or title == "pdf":
			return title

		if "subtitles" in title:
			if "text" in title:
				return "txt"
			if "srt" in title:
				return "srt"

		if "video" in title:
			if "mp4" in title:
				return "mp4"

		return "unknown"

	def __get_file_from_header(self, header_string):
		"""
		Given the header string, return a string that would be a valid 
		file/folder name.
		"""
		header_string = header_string.replace(":", "-")
		header_string = unicodedata.normalize('NFKD', header_string).encode('ascii', 'ignore')
		header_string = unicode(re.sub('[^\w\s-]', '', header_string).strip().lower())

		return header_string

	def _login(self):
		"""
		Login to Coursera course.
		"""
		cj = self.cj
		opener = self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		login_data = self.login_data = urllib.urlencode({
			'email_address' : self.args.sera_user, 
			'password' : self.args.sera_pass, 
			'csrf_token' : ""
		})

		# log in to the site
		resp = opener.open(self.URLs['LOGIN'], login_data)

		# log in to the course: we need dem course cookehs!
		resp = opener.open(self._get_course_main_url() + self.end_clogin, login_data)

		# do login
		# print cj
		# resp = opener.open(self.URLs['LOGIN'], login_data) #line 7123 from js
		# print cj
		# resp = opener.open(self._get_course_main_url() + self.end_clogin, login_data)
		# print cj
		# resp = opener.open('https://class.coursera.org/nlp/lecture/index')
		# print self._get_course_key_url('lectures')
		# print resp.read()#[7000:10000]

	def _get_course_main_url(self):
		return self.base_course + self.course

	def _get_course_key_url(self, key):
		return self.URLs['COURSE'][key] % self.course

	def _check_args(self):
		"""
		Check that all arguments are provided and valid.
		"""
		args = self.args = self.argsparser.parse_args()

		errFmt = "--%s: %s"
		if args.sera_user is None:
			raise AttributeError(errFmt % ("sera_user", "Username is required."))

		if args.sera_pass is None:
			raise AttributeError(errFmt % ("sera_pass", "Password is required."))

		if args.sera_course is None:
			raise AttributeError(errFmt % ("sera_course", "Course short-hand is required."))

		self.course = args.sera_course

