from typing import List

class Dependency:
	def __init__(self, name: str, show_link: bool):
		self.name = name
		self.link = show_link

	def __lt__(self, other):
		return self.name <= other.name

class Package:
	"""
	Class that contains information relating to a single package.
	Note:
	self.deps == List whose nodes can be str or List[str] if there are
	dependencies that can be substituted with another package
	self.reverse_deps == List who can be str or dict (key: str (dependent
	package name), value: List[str] (substitutable packages))
	"""
	def __init__(self, name: str):
		self.name = name
		self.strict_reverse_deps = []
		self.sub_reverse_deps = {}

	def __lt__(self, other):
		return self.name <= other.name

	def add_data(self, description: str, version: str, deps: List):
		self.description = description
		self.version = version
		self.deps = deps
	
	def add_reverse_dep(self, package):
		"""
		Add reverse dependency. Usually package is str. If a reverse dependency
		can be substituted with another it will be dict. See above.
		"""
		if type(package) == Dependency:
			self.strict_reverse_deps.append(package)
		else:
			self.sub_reverse_deps[list(package.keys())[0]] = list(package.values())[0]