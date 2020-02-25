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
	package_names = [package.name for package in packages.values()]
	package_names.sort()
	return render_template("index.html", package_names=package_names)


@app.route("/packages/<path:package_name>", methods=["GET"])
def package_site(package_name):
	if package_name not in packages:
		return render_template("package_not_found.html", name=package_name)
	else:
		return render_template("package.html", package=packages[package_name])


def clean_dependency(line: str) -> str:
	""" Removes version information (if any) from a dependency string """
	return re.sub(" \(.*\)", "", line)


def parse_dependencies(line: str, strict_deps: List[str], sub_deps: List[str]):
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
			sub_deps.append(sub_dependencies)
		else:
			strict_deps.append(clean_dependency(dependency))


def parse_file():
	"""
	Parses the contents of dpkg/status into a list of packages. We need to
	traverse the file twice so we can find all the packages that aren't listed
	in the file themselves (only as dependencies) and know we shouldn't link to
	them.
	"""
	if os.access("/var/lib/dpkg/status", os.R_OK):
		filepath = "/var/lib/dpkg/status"
	else:
		filepath = "example_dpkg_status"
	with open(filepath) as f:
		lines = f.readlines()

	# Traverse file once to initialise all packages
	for line in lines:
		if re.match("Package: ", line): #re.match only searches the beginning of the line
			name = line[line.find(" ") + 1:-1]
			packages[name] = Package(name)

	# Traverse file again to find add all the other parsed data
	strict_deps = []
	sub_deps = []
	for line in lines:
		if re.match("Package: ", line): #re.match only searches the beginning of the line
			name = line[line.find(" ") + 1:-1]
		elif re.match("Version: ", line):
			version = line[line.find(" ") + 1:-1]
		elif re.match("(Pre-)?Depends: ", line):
			parse_dependencies(line, strict_deps, sub_deps)
		elif re.match("Description: ", line): #TODO most descriptions contain multiple lines...
			description = line[line.find(" ") + 1:-1]

			strict_deps.sort()
			for dep in sub_deps:
				strict_deps.append(sorted(dep))
			packages[name].add_data(
										version=version,
										description=description,
										deps=strict_deps
									)
			sub_deps, strict_deps = [], []


def get_reverse_deps():
	for package in packages.values():
		for dependency in package.deps:
			if type(dependency) == str:
				try: #some packages are only listed as dependencies
					packages[dependency].add_reverse_dep(package.name)
				except:
					pass
			else:
				for dep in dependency:
					try: #some packages are only listed as dependencies
						packages[dep].add_reverse_dep({package.name: dependency})
					except:
						pass


if __name__ == "__main__":
	parse_file()
	get_reverse_deps()
	app.run(host="0.0.0.0", port=5000, debug=True)
