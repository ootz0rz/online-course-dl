import re
import textwrap
import argparse

# http://code.activestate.com/recipes/358228-extend-textwraptextwrapper-to-handle-multiple-para/
class DocWrapper(textwrap.TextWrapper):
    """Wrap text in a document, processing each paragraph individually"""

    def wrap(self, text):
        """Override textwrap.TextWrapper to process 'text' properly when
        multiple paragraphs present"""
        para_edge = re.compile(r"(\n\s*\n)", re.MULTILINE)
        paragraphs = para_edge.split(text)
        wrapped_lines = []
        for para in paragraphs:
            if para.isspace():
                if not self.replace_whitespace:
                    # Do not take the leading and trailing newlines since
                    # joining the list with newlines (as self.fill will do)
                    # will put them back in.
                    if self.expand_tabs:
                        para = para.expandtabs()
                    wrapped_lines.append(para[1:-1])
                else:
                    # self.fill will end up putting in the needed newline to
                    # space out the paragraphs
                    wrapped_lines.append('')
            else:
                wrapped_lines.extend(textwrap.TextWrapper.wrap(self, para))
        return wrapped_lines

class ArgsParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        kwargs['formatter_class'] = argparse.RawTextHelpFormatter
        argparse.ArgumentParser.__init__(self, *args, **kwargs)

        wrapper = DocWrapper()
        wrapper.replace_whitespace = False
        wrapper.drop_whitespace = True
        wrapper.width = 55
        wrapper.expand_tabs = True
        wrapper.break_long_words = True

        self.wrapper = wrapper

    def plugin_add_argument(self, *args, **kwargs):
        if 'help' in kwargs:
            kwargs['help'] = self.wrapper.fill(
                textwrap.dedent(kwargs['help'][1:])) + '\n'*2

        return self.add_argument(*args, **kwargs)
