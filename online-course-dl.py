#!/usr/bin/env python
"""
Let's you download an entire course to your hard drive for later use from a
variety of online course websites. 

This script presents a pluggable method for download courses from various 
sites. Additional site support can be added via plugins.

Based on John Lehmann's "coursera-dl"
	<https://github.com/jplehmann/coursera>

Author: Hardeep Singh (ootz0rz at gee mail dot com)
		< https://github.com/ootz0rz/ >
"""
import sys, os, re, string
import urllib, urllib2, cookielib 
import tempfile
import subprocess
import argparse
import StringIO
from BeautifulSoup import BeautifulSoup

# init parser
parser = argparse.ArgumentParser(description = "Download online courses!", formatter_class=argparse.RawTextHelpFormatter)

email_address = ''
password = ''
csrf_token = ''

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
login_data = urllib.urlencode({
	'email_address' : email_address, 
	'password' : password, 
	'csrf_token' : csrf_token
})

if __name__ == "__main__":
	def setup_arguments_parser():
		'''
		Setup command line arguments.

		Note that plugins are allowed to add their own optional arguments
		'''
		global parser
		import textwrap

		# positional arguments
		parser.add_argument('plugin', 
			action = 'store', 
			#------------------------------------------------------
			help = textwrap.dedent('''
				Name of plugin to use. Use the flag -l or --list to
				view a list of all available site plugins.''')[1:])

		# required arguments

		# optional arguments
		parser.add_argument('-p', '--p_args', dest = 'plugin_args',
			action = 'store',
			default = None,
			#------------------------------------------------------
			help = textwrap.dedent('''
				Arguments to send to the plugin. Please see plugin-
				specific documentation for more 
				information. 

				(DEFAULT: %(default)s)''')[1:])

		parser.add_argument('-l', '--list', dest = 'plugin_list',
			action = 'store',
			default = 'all',
			#------------------------------------------------------
			help = textwrap.dedent('''
				Provide a numbered listing of all plugins found. 

				Parameters:
				-l %(default)s, --list %(default)s
				    for a list of all plugins.
				-l #, or --list #
				    to see more information on a specific plugin.

				(DEFAULT: %(default)s)''')[1:])

	setup_arguments_parser()
	args = parser.parse_args()

	# do login
	print cj
	resp = opener.open('https://www.coursera.org/maestro/auth/api/user/login', login_data) #line 7123 from js
	print cj
	resp = opener.open('https://class.coursera.org/nlp/auth/auth_redirector?type=login&subtype=normal', login_data)
	print cj
	resp = opener.open('https://class.coursera.org/nlp/lecture/index')
	# print resp.read()[7000:10000]
