# Based on http://martyalchin.com/2008/jan/10/simple-plugin-framework/
class PluginMount(type):
	def __init__(self, name, bases, attrs):
		if not hasattr(self, 'plugins'):
			# This branch only executes when processing the mount point itself.
			# So, since this is a new plugin type, not an implementation, this
			# class shouldn't be registered as a plugin. Instead, it sets up a
			# list where plugins can be registered later.
			self.plugins = []
		else:
			# This must be a plugin implementation, which should be registered.
			# Simply appending it to the list is all that's needed to keep
			# track of it later.
			self.plugins.append(self)

	def get_plugins(self, *args, **kwargs):
		return [p(*args, **kwargs) for p in self.plugins]

def enum(*sequential, **named):
	enums = dict(zip(sequential, range(len(sequential))), **named)
	return type('Enum', (), enums)
	
class Downloadable:
	"""
	A 'Downloadable' instance. This contains all the information required to 
	let the main application download the specified file.
	"""
	# Types for file_type
	File_Types = enum(
		# Just download, no extras
		'FILE', 

		# Try to download it
		'HTML', 

		# If this is set, then url is not used and instead we save the value of
		# 'contents' to disk.
		'STRING')

	def __init__(self, 
		url="", 
		output_name="", 
		sub_folder="", 
		file_type=File_Types.FILE, 
		contents=""):
		# The file to download
		self.url = url

		# The file name to save as
		self.output_name = output_name

		# The sub-path to download the file to, if any
		self.sub_folder = sub_folder

		# The type of file this is. By default, we assume this is a "normal" file.
		self.file_type = file_type

		# This is only used if file_type is set to File_Types.STRING
		self.contents = contents


class LinksProvider:
	"""
	Mount point for plugins. All plugins should be stored in the /plugins/
	folder, and extend from this class. The file name for the main plugin
	should be in the format "plugin-[prefix or plugin name].py"

	Plugins implementing this class require the following attributes:

	name = ""
		Plugin Name

	desc = ""
		Plugin Description

	help = ""
		Help text to display when this plugin is listed via the '-l' flag

	prefix = ""
		A unique, short prefix to use instead of a number for -l. 

		You should also prefix all command line arguments for your plugin with 
		this.

	And the following methods:

	__init__(self, argsparser):
		argsparser      -   An instance of ArgsParser. If you intend to use any
							of the arguments, might want to keep an instance of
							this saved somewhere so you can reference the 
							values given, if any.

							Note that EVERY ARGUMENT added *MUST* be optional.
							Do not use single letter arguments, they must all
							be in the --arg_name format.

							Specifically, --[prefix]_arg

							Make sure to use the method: plugin_add_argument()
							It takes the same parameters as 
								argparse.ArgumentParser.add_argument()
							but will format the "help" parameter for you.

		Do all your plugin initialization here

	start(self):
		Runs the plugin. Should return a list of "Downloadable" objects for the
		main application to download.

	get_downloadablesself):
		Returns the list of "Downloadable" objects.
	"""
	__metaclass__ = PluginMount

	name = ""
	desc = ""
	help = ""
	prefix = ""

	def __init__(self, argsparser):
		pass

	def start(self):
		return self.get_downloadables()

	def get_downloadables(self):
		return []
