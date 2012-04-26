from plugins import *

class PluginCoursera(LinksProvider):
    """
    Log in to Coursera, and download the specified enrolled course.
    """
    name = "Coursera"
    desc = "Coursera Course Downloader"
    help = '''See -h for flag usage, look for flags prefixed with 'sera'. Specifically, you must provide the username, password and course short-hand.'''
    prefix = "sera"

    def __init__(self, argsparser):
        argsparser.plugin_add_argument(
            '-%s_u' % self.prefix, 
            '--%s_user' % self.prefix, 
            dest = '%s_user' % self.prefix,
            action = 'store',
            default = None,
            help = '''
                [%s][REQUIRED] Username to log in to Coursera.''' % self.name)

        argsparser.plugin_add_argument(
            '-%s_p' % self.prefix, 
            '--%s_pass' % self.prefix, 
            dest = '%s_pass' % self.prefix,
            action = 'store',
            default = None,
            #------------------------------------------------------
            help = '''
                [%s][REQUIRED] Password to log in to Coursera.''' % self.name)

        argsparser.plugin_add_argument(
            '-%s_c' % self.prefix, 
            '--%s_course' % self.prefix, 
            dest = '%s_course' % self.prefix,
            action = 'store',
            default = None,
            #------------------------------------------------------
            help = '''
                [%s][REQUIRED] Course short-hand name to download.

                Look at the URL for the course after logging in to see what the short-hand is.

                Ex: for Natural Language Programming, it's "nlp"''' % self.name)

        self.argsparser = argsparser
