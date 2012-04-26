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

class Downloader:
    """
    A 'downloader' instance. This contains all the information required to let
    the main application download the specified file.
    """
    
    url = ""

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

    Start():
        Runs the plugin. Should return a list of "Downloader" objects for the
        main application to download.

    GetDownloaders():
        Returns the list of "Downloader" objects.

    """
    __metaclass__ = PluginMount

    name = ""
    desc = ""
    help = ""
    prefix = ""

    def __init__(self, argsparser):
        pass
