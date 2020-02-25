from typing import List

class Package:
	"""
	Class that contains information relating to a single package.
	Note: self.deps == List whose nodes can be str or List[str] if there are
	dependencies that can be substituted with another package
	"""
	def __init__(self, name: str, description: str, version: str, deps: List):
		self.name = name
		self.description = description
		self.version = version
		self.deps = deps