import os
import re
from typing import List

from flask import Flask, jsonify, request, render_template

from Package import Package

app = Flask(__name__)
packages = {}	# Global list of all packages. Could use a DB, but this will do.
				# Using a dict for random access


@app.route("/", methods=["GET"])
def index():
	return render_template("index.html")


def clean_dependency(line: str) -> str:
	""" Removes version information (if any) from a dependency string """
	return re.sub(" \(.*\)", "", line)


def parse_dependencies(line: str, deps: List[str]):
	"""
	Appends all dependencies in line to deps. Typical dependencies will be
	appended as strings. Dependencies that can be substituted with another
	package will be appended as List[str].
	"""
	line = line[line.find("Depends: ") + 9:-1] #line can begin with "Pre-Depends"
	dependencies = line.split(", ")
	for dependency in dependencies:
		if " | " in dependency: #if there are substitutional depedencies
			sub_dependencies = dependency.split(" | ")
			sub_dependencies = [clean_dependency(dep) for dep in sub_dependencies]
			deps.append(sub_dependencies)
		else:
			deps.append(clean_dependency(dependency))


def parse_file():
	"""
	Parses the contents of dpkg/status into a list of packages.
	"""
	if os.access("/var/lib/dpkg/status", os.R_OK):
		filepath = "/var/lib/dpkg/status"
	else:
		filepath = "example_dpkg_status"
	with open(filepath) as f:
		lines = f.readlines()

	deps = []
	for line in lines:
		if re.match("Package: ", line): #re.match only searches the beginning of the line
			name = line[line.find(" "):-1]
		elif re.match("Version: ", line):
			version = line[line.find(" "):-1]
		elif re.match("(Pre-)?Depends: ", line):
			parse_dependencies(line, deps)
		elif re.match("Description: ", line): #TODO most descriptions contain multiple lines...
			description = line[line.find(" "):-1]
			packages[name] = Package(
										name=name,
										version=version,
										description=description,
										deps=deps
									)
			deps = []


if __name__ == "__main__":
	parse_file()
	app.run(host="0.0.0.0", port=5000, debug=True)