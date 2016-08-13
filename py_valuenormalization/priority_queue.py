from heapq import *
import itertools

REMOVED					= '<removed-task>'		# placeholder for a removed task

class MyPriorityQueue:
	def __init__(self):
		self.pq					= []					# list of entries arranged in a heap
		self.entry_finder		= {}					# mapping of tasks to entries
		self.counter			= itertools.count()		# unique sequence count

	def add_task(self, task, priority=0):
		'Add a new task or update the priority of an existing task'
		if task in self.entry_finder:
			self.remove_task(task)
		count					= next(self.counter)
		entry = [(priority, task), count, task]
		self.entry_finder[task]	= entry
		heappush(self.pq, entry)

	def remove_task(self, task):
		'Mark an existing task as REMOVED.  Raise KeyError if not found.'
		entry = self.entry_finder.pop(task)
		entry[-1] = REMOVED
		return entry[0][0]

	def pop_task(self):
		'Remove and return the lowest priority task. Raise KeyError if empty.'
		while self.pq:
			(priority, tmp_task), count, task = heappop(self.pq)
			if task is not REMOVED:
				del self.entry_finder[task]
				return (priority, task)
		raise KeyError('Trying to pop from an empty priority queue.')

	def is_empty(self):
		'Checks whether there are any non-REMOVED elements in this queue.'
		for entry in self.pq:
			if entry[-1] is not REMOVED:
				return False
		return True

