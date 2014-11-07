from __future__ import division

import os
import requests
import gzip
from math import sin, cos, pi

import numpy as np
import matplotlib.pylab as plt
from mpl_toolkits.mplot3d import Axes3D

######################################################################
####################### Methods and Constants #######################
######################################################################

DPI = 96

def rotateX(x, y, z, theta):
	rads = theta * pi / 180
	y = cos(rads) * y - sin(rads) * z
	z = sin(rads) * y + cos(rads) * z
	return x,y,z

def rotateY(x, y, z, theta):
	rads = theta * pi / 180
	x = cos(theta) * x + sin(theta) * z
	z = -sin(theta) * x + cos(theta) * z
	return x,y,z

def make_figure_and_subplot(projection='rectilinear'):
	fig = plt.figure(figsize=(1024/DPI, 1024/DPI), dpi=DPI)
	ax = fig.add_subplot(111, projection=projection)
	ax.set_axis_bgcolor('black')
	return fig, ax

# strips first row item from collection
strip_first = lambda rows: map(lambda row: row[1:], rows)
make_float = lambda rows: map(lambda row: map(lambda point: float(point), row), rows)

if __name__ == "__main__":

	######################################################################
	##################### Download/Parse Data ############################
	######################################################################

	# download file if it doesn't exist
	if not os.path.isfile("johri-al-northwestern-part[A].gz"):
		print "downloading johri-al-northwestern-part[A].gz"
		headers = {'X-TechChallenge': 'true'}
		response = requests.get("http://2014.fallchallenge.org/", headers=headers)
		with open("johri-al-northwestern-part[A].gz", "w") as f:
			f.write(response.content)

	# extract to ssv (space separated values) file
	if not os.path.isfile("johri-al-northwestern-part[B].ssv"):
		print "extracting data.gz into johri-al-northwestern-part[B].ssv"
		f = gzip.open('johri-al-northwestern-part[A].gz', 'rb')
		file_content = f.read()
		with open("johri-al-northwestern-part[B].ssv", "w") as f2:
			f2.write(file_content)

	# read into memory
	with open("johri-al-northwestern-part[B].ssv") as f:
		print "reading johri-al-northwestern-part[B].ssv into memory"
		data = f.read()

	rows = map(lambda row: row.split(), data.splitlines())
	points = make_float(strip_first(filter(lambda row: row[0] == "point", rows)))
	faces = make_float(strip_first(filter(lambda row: row[0] == "face", rows)))

	# rotate 15 degrees around X axis and -30 around Y axis
	points = map(lambda (x,y,z): rotateX(x,y,z,15), points)
	points = map(lambda (x,y,z): rotateY(x,y,z,-30), points)
	points = np.array(points)

	# project points into 2 dimensions
	projected_points = map(lambda (x,y,z): [
		(5 * x) / (1 / (z - 2)), # x projection
		(5 * y) / (1 / (z - 2))  # y projection
	], points)
	projected_points = np.array(projected_points)

	######################################################################
	############################# Plot Data ##############################
	######################################################################

	plt.axis('off')

	# 3d plot
	print "creating 3 dimensional plot"
	fig1, ax1 = make_figure_and_subplot('3d')
	for face in faces:
		face_points = np.array((points[face[0]], points[face[1]], points[face[2]]))
		ax1.plot_wireframe(face_points[:,0], face_points[:,1], face_points[:,2])
	plt.savefig("johri-al-northwestern-final-image1.png", bbox_inches='tight', facecolor='black', edgecolor='none')

	# 2d plot
	print "creating 2 dimensional plot"
	fig2, ax2 = make_figure_and_subplot()
	ax2.scatter(projected_points[:,0], projected_points[:,1])
	for face in faces:
		pt1, pt2, pt3 = projected_points[face[0]], projected_points[face[1]], projected_points[face[2]]
		ax2.plot([pt1[0], pt2[0]], [pt1[1], pt2[1]])
		ax2.plot([pt2[0], pt3[0]], [pt2[1], pt3[1]])
		ax2.plot([pt1[0], pt3[0]], [pt1[1], pt3[1]])
	plt.savefig("johri-al-northwestern-final-image2.png", bbox_inches='tight', facecolor='black', edgecolor='none')
