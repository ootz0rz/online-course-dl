Online Course Downloader
================

Download online courses from various online course websites.

Currently supports:
 * Coursera 
 * Udacity (soon, hopefully)

Sample usage:
	Download the Natural Language Processing course from Coursera:
	`python online-course-dl.py -p sera -sera_u YOUR_USERNAME -sera_p YOUR_PASS -sera_c nlp`

	Download using wget instead of the python downloader (MUST faster!):
	`python online-course-dl.py -p sera -sera_u YOUR_USERNAME -sera_p YOUR_PASS -sera_c nlp -w wget`

	( Windows can get wget from: http://gnuwin32.sourceforge.net/packages/wget.htm )

Run `python online-course-dl.py -h` to see all available options.

To view a list of plugins, run `python online-course-dl.py -l all`. To view information on a specific plugin, run `python online-course-dl.py -l sera` (this will view information about the Coursera plugin)



Feel free to send pull requests for fixes, features, or new site plugins :)
