#!/usr/bin/env python
"""
Let's you download an entire course to your hard drive for later use from a
variety of online course websites. 

This script presents a pluggable method for download courses from various 
sites. Additional site support can be added via plugins (see plugins.py)

Author: Hardeep Singh (ootz0rz at gee mail dot com)
		< https://github.com/ootz0rz/ >

Some code based on John Lehmann's Coursera Downloader:
		< https://github.com/jplehmann/coursera >
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
		default = os.getcwd(),
		action = 'store',
		help = '''
			Path to output to. If the path does not exist, it will be created. By default, this is the CWD.''')

	parser.plugin_add_argument('-w', '--wget', dest = 'wget_bin',
		default = None,
		action = 'store',
		help = '''
			Path to wget executable, if available.''')

def main():
	"""
	Program entry point.
	"""
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

		dls = cur_plugin.start()
		_start_downloads(dls, cur_plugin.cj, args.output_path, args.wget_bin)
		

def _start_downloads(dlist, cookiejar, output_path, wget_bin):
	"""
	Download every 'Downloadable' given in the list dlist.
	"""
	print "Got (%d) links from plugin, starting downloads..." % len(dlist)

	# should we write out a cookies file?
	cookies_file = ""
	if wget_bin is not None:
		cookies_file = create_cookies_txt(cookiejar)

	try:
		for dl in dlist:
			print "Downloading", dl
			full_path = os.path.join(output_path, dl.sub_folder)
			full_path = os.path.join(full_path, dl.output_name)

			download_file(
				dl.url,
				full_path,
				cookiejar,
				cookies_file,
				wget_bin
			)
	finally:
		if len(cookies_file) > 0:
			os.remove(cookies_file)


def create_cookies_txt(cookiejar):
	"""
	Write a temporary Netscape cookies.txt file to disk, and return the 
	location.
	"""
	import tempfile
	from contextlib import closing
	# spec: http://www.cookiecentral.com/faq/#3.5

	tmp = tempfile.mkstemp(prefix="ocd-cj")
	path = tmp[1]
	fd = tmp[0]

	print fd, path
	
	with open(path, 'w') as f:
		NETSCAPE_HEADER = "# Netscape HTTP Cookie File\n"
  		f.write(NETSCAPE_HEADER);
		for c in cookiejar:
			f.write(_get_cookie_line(c))
			f.write('\n')

	return path

def _get_cookie_line(c):
	"""
	Given a cookie, format it in the netscape cookies.txt spec
	"""
	cookie_line = '%(domain)s\t%(flag)s\t%(path)s\t%(secure)s\t%(expiration)s\t%(name)s\t%(value)s'

	return cookie_line % {
			"domain": 		c.domain,
			"flag": 		"TRUE",
			"path": 		c.path,
			"secure": 		"TRUE" if c.secure else "FALSE",
			"expiration": 	c.expires,
			"name": 		c.name,
			"value":		c.value
		}

def download_file(url, fn, cookiejar, cookies_file, wget_bin):
	"""
	Downloads file and removes current file if aborted by user.
	"""
	try:
		# create the path if need be
		basedir = os.path.dirname(fn)
		if not os.path.isdir(basedir):
			os.makedirs(basedir)

		if wget_bin is not None:
			download_file_wget(wget_bin, url, fn, cookies_file)
		else:
			download_file_nowget(url, fn, cookiejar)

	except KeyboardInterrupt, e: 
		print "\nKeyboard Interrupt -- Removing partial file:", fn
		os.remove(fn)

		raise e

def download_file_wget(wget_bin, url, fn, cookies_file):
	"""
	Downloads a file using wget.  Could possibly use python to stream files to
	disk, but wget is robust and gives nice visual feedback.
	"""
	cmd = [wget_bin, url, "-O", fn, "--load-cookies", cookies_file, "--no-check-certificate"]
	print "Executing wget:", cmd 
	retcode = subprocess.call(cmd)

def download_file_nowget(url, fn, cookiejar):
	"""
	'Native' python downloader -- slower than wget.
	"""
	print "Downloading %s -> %s" % (url, fn)
	urlfile = get_opener(cookiejar).open(url)
	chunk_sz = 1048576
	bytesread = 0
	f = open(fn, "wb")

	while True:
		data = urlfile.read(chunk_sz)
		if not data:
			print "."
			break

		f.write(data)
		bytesread += len(data)
		print "\r%d bytes read" % bytesread,
		sys.stdout.flush()

def get_opener(cookiejar):
	"""
	Use cookie jar to create a url opener.
	"""
	return urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))

if __name__ == "__main__":
	main()
