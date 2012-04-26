#!/usr/bin/env python
"""
Let's you download an entire course to your hard drive for later use from a
variety of online course websites. 

This script presents a pluggable method for download courses from various 
sites. Additional site support can be added via plugins.

Author: Hardeep Singh (ootz0rz at gee mail dot com)
		< https://github.com/ootz0rz/ >
"""
import sys, os, re, string
import urllib, urllib2, cookielib 
import tempfile
import subprocess
import StringIO
from BeautifulSoup import BeautifulSoup
from plugins import *
from ArgsParser import *

#### config -------------------------------------------------------------------
# absolute path to plugins folder
PLUGINS_PATH = os.path.join(os.getcwd(), "plugins")
#### //config -----------------------------------------------------------------
#### DO NOT MODIFY BELOW THIS LINE

PLUGIN_BASE_INDEX = 1

# init parser
parser = ArgsParser(
	description = "Download online courses!", 
	formatter_class=argparse.RawTextHelpFormatter)

# init wrapper
wrapper = DocWrapper()
wrapper.replace_whitespace = False
wrapper.drop_whitespace = True
wrapper.width = 75
wrapper.expand_tabs = True
wrapper.break_long_words = True

def _doWrap(text):
	return wrapper.fill(textwrap.dedent(text))

# list of plugins
plugins = []

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

def load_plugins():
	"""
	Find plugins, and load them for use.
	"""
	import imp
	global parser, plugins

	# import plugins
	i = 1
	for dirname, dirnames, filenames in os.walk(PLUGINS_PATH):
		for filename in filenames:
			if filename.startswith("plugin-") and filename.endswith(".py"):
				# print "Loading plugin:", filename
				load_path = os.path.join(dirname, filename)
				module = imp.load_source("plugin%s" % i, load_path)

	# init each plugin
	plugins = LinksProvider.get_plugins(parser)

def list_plugins(pname):
	"""
	Display list of plugins to the user, or documentation on a specific plugin.
	"""
	i = PLUGIN_BASE_INDEX
	if pname == 'all':
		print "Listing all loaded plugins..."
		print "Plugins are listed with a number, and optionally a / followed by their <name>"
		print
		for o in plugins:
			_print_plugin_info(o, i)

			i = i + 1
	else:
		# find and display specific plugin
		o = _find_plugin(pname)
		_print_plugin_info(o[0], o[1], True)

def _find_plugin(pname):
	"""
	Find and return a plugin based on its prefix name, or assigned number.

	Will return a tuple: (plugin, index), or None if no such plugin found.
	"""
	try:
		val = int(pname)
	except ValueError:
		val = pname

	i = PLUGIN_BASE_INDEX
	if isinstance(val, int):
		for o in plugins:
			if val == i:
				# _print_plugin_info(o, i, True)
				return (o, i)

			i = i + 1
	else:
		for o in plugins:
			if val == o.prefix:
				# _print_plugin_info(o, i, True)
				return (o, i)

			i = i + 1

	return None

def _print_plugin_info(plugin, number, verbose=False):
	"""
	Print plugin documentation to screen.
	"""
	if len(plugin.prefix) > 0:
		print _doWrap("Plugin #%s/%s: %s (%s)" % (number, plugin.prefix, plugin.name, plugin.desc))
	else:
		print _doWrap("Plugin #%s: %s (%s)" % (number, plugin.name, plugin.desc))

	if verbose:
		print
		print "Plugin Documentation:"
		print _doWrap(plugin.help)

def setup_arguments_parser():
	"""
	Setup command line arguments.

	Note that plugins are allowed to add their own optional arguments
	"""
	global parser

	parser.plugin_add_argument('-p', '--plugin', dest = 'plugin_name', 
		default = None,
		action = 'store',
		help = '''
			-p [#|name], or --plugin [#|name] 

			Name of plugin to use. Use the flag -l all or --list all to view a list of all available site plugins.''')

	parser.plugin_add_argument('-l', '--list', dest = 'plugin_list',
		default = None,
		action = 'store',
		help = '''
			Provide a numbered listing of all plugins found. 

			Valid Parameters for PLUGIN_LIST:
			 * all: for a list of all plugins.

			 * #|name: to see more information on a specific plugin. You may use either the plugin # or the plugin name (if any) that is shown via "-l all"''')

	parser.plugin_add_argument('-o', '--out', dest = 'output_path',
			default = None,
			action = 'store',
			help = '''
				Path to output to. If the path does not exist, it will be created.''')

def main():
	setup_arguments_parser()
	load_plugins()
	args = parser.parse_args()

	if args.plugin_list is not None:
		return list_plugins(args.plugin_list)

	if (args.plugin_name is not None):
		o = _find_plugin(args.plugin_name)

		if o is None:
			print "Could not find the specified plugin:", args.plugin_name
			return

		# run the plugin, then process Downloadables
		cur_plugin = o[0]
		print "Plugin to run:", cur_plugin
		print cur_plugin.start()

if __name__ == "__main__":
	main()

	# do login
	# print cj
	# resp = opener.open('https://www.coursera.org/maestro/auth/api/user/login', login_data) #line 7123 from js
	# print cj
	# resp = opener.open('https://class.coursera.org/nlp/auth/auth_redirector?type=login&subtype=normal', login_data)
	# print cj
	# resp = opener.open('https://class.coursera.org/nlp/lecture/index')
	# print resp.read()[7000:10000]
