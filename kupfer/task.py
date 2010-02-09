import sys
import threading

import gobject

from kupfer import scheduler, pretty

class Task (object):
	"""Represent a task that can be done in the background"""
	def __init__(self, name=None):
		self.name = name

	def __unicode__(self):
		return self.name

	def start(self, finish_callback):
		raise NotImplementedError

class ThreadTask (Task):
	"""Run in a thread"""
	def __init__(self, name=None):
		Task.__init__(self, name)
		self.finish_callback = None

	def thread_do(self):
		"""Override this to run what should be done in the thread"""
		raise NotImplementedError

	def thread_finish(self):
		"""This finish function runs in the main thread after thread
		completion, and can be used to communicate with the GUI.
		"""
		pass

	def thread_finally(self, exc_info):
		"""Always run at thread finish"""
		pass

	def _thread_finally(self, exc_info):
		try:
			self.thread_finally(exc_info)
		finally:
			self.finish_callback(self)

	def _run_thread(self):
		try:
			self.thread_do()
			gobject.idle_add(self.thread_finish)
		except:
			exc_info = sys.exc_info()
			raise
		else:
			exc_info = None
		finally:
			gobject.idle_add(self._thread_finally, exc_info)

	def start(self, finish_callback):
		self.finish_callback = finish_callback
		thread = threading.Thread(target=self._run_thread)
		thread.start()


class TaskRunner (pretty.OutputMixin):
	"""Run Tasks in the idle Loop"""
	def __init__(self, end_on_finish):
		self.tasks = set()
		self.end_on_finish = end_on_finish
		scheduler.GetScheduler().connect("finish", self._finish_cleanup)

	def _task_finished(self, task):
		self.output_debug("Task finished", task)
		self.tasks.remove(task)

	def add_task(self, task):
		"""Register @task to be run"""
		self.tasks.add(task)
		task.start(self._task_finished)

	def _finish_cleanup(self, sched):
		if self.end_on_finish:
			self.tasks.clear()
			return
		if self.tasks:
			self.output_info("Uncompleted tasks:")
			for task in self.tasks:
				self.output_info(task)

