from typing import List

class Package:
	"""
	Class that contains information relating to a single package.
	Note:
	self.deps == List whose nodes can be str or List[str] if there are
	dependencies that can be substituted with another package
	self.reverse_deps == List who can be str or dict (key: str (dependent
	package name), value: List[str] (substitutable packages))
	"""
	def __init__(self, name: str, description: str, version: str, deps: List):
		self.name = name
		self.description = description
		self.version = version
		self.deps = deps
		self.reverse_deps = []

	def __lt__(self, other):
		return self.name < other.name
	
	def add_reverse_dep(self, package):
		"""
		Add reverse dependency. Usually package is str. If a reverse dependency
		can be substituted with another it will be dict. See above.
		"""
		if type(package) == str: #add strict dependencies to beginning of list
			self.reverse_deps.insert(0, package)
		else: #add substitutional dependencies to end of list
			self.reverse_deps.append(package)