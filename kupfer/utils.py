from os import path
import locale

from kupfer import pretty

def get_dirlist(folder, depth=0, include=None, exclude=None):
	"""
	Return a list of absolute paths in folder
	include, exclude: a function returning a boolean
	def include(filename):
		return ShouldInclude
	"""
	from os import walk
	paths = []
	def include_file(file):
		return (not include or include(file)) and (not exclude or not exclude(file))
		
	for dirname, dirnames, fnames in walk(folder):
		# skip deep directories
		head, dp = dirname, 0
		while not path.samefile(head, folder):
			head, tail = path.split(head)
			dp += 1
		if dp > depth:
			del dirnames[:]
			continue
		
		excl_dir = []
		for dir in dirnames:
			if not include_file(dir):
				excl_dir.append(dir)
				continue
			abspath = path.join(dirname, dir)
			paths.append(abspath)
		
		for file in fnames:
			if not include_file(file):
				continue
			abspath = path.join(dirname, file)
			paths.append(abspath)

		for dir in reversed(excl_dir):
			dirnames.remove(dir)

	return paths

def locale_sort(seq, key=unicode):
	"""Return @seq of objects with @key function as a list sorted
	in locale lexical order

	>>> locale.setlocale(locale.LC_ALL, "C")
	'C'
	>>> locale_sort("abcABC")
	['A', 'B', 'C', 'a', 'b', 'c']

	>>> locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
	'en_US.UTF-8'
	>>> locale_sort("abcABC")
	['a', 'A', 'b', 'B', 'c', 'C']
	"""
	locale_cmp = lambda s, o: locale.strcoll(key(s), key(o))
	seq = seq if isinstance(seq, list) else list(seq)
	seq.sort(cmp=locale_cmp)
	return seq

def spawn_async(argv, in_dir="."):
	import gobject
	pretty.print_debug(__name__, "Spawn commandline", argv, in_dir)
	try:
		return gobject.spawn_async (argv, working_directory=in_dir,
				flags=gobject.SPAWN_SEARCH_PATH)
	except gobject.GError, exc:
		pretty.print_debug(__name__, "spawn_async", argv, exc)

def app_info_for_commandline(cli, name=None, in_terminal=False):
	import gio
	flags = gio.APP_INFO_CREATE_NEEDS_TERMINAL if in_terminal else gio.APP_INFO_CREATE_NONE
	if not name:
		name = cli
	item = gio.AppInfo(cli, name, flags)
	return item

def launch_commandline(cli, name=None, in_terminal=False):
	import launch
	app_info = app_info_for_commandline(cli, name, in_terminal)
	pretty.print_debug(__name__, "Launch commandline (in_terminal=", in_terminal, "):", cli, sep="")
	return launch.launch_application(app_info, track=False)

def launch_app(app_info, files=(), uris=(), paths=()):
	import launch

	# With files we should use activate=False
	return launch.launch_application(app_info, files, uris, paths,
			activate=False)

def show_path(path):
	"""Open local @path with default viewer"""
	from gio import File
	# Implemented using gtk.show_uri
	gfile = File(path)
	if not gfile:
		return
	url = gfile.get_uri()
	show_url(url)

def show_url(url):
	"""Open any @url with default viewer"""
	from gtk import show_uri, get_current_event_time
	from gtk.gdk import screen_get_default
	from glib import GError
	try:
		return show_uri(screen_get_default(), url, get_current_event_time())
	except GError, exc:
		pretty.print_error(__name__, "gtk.show_uri:", exc)
