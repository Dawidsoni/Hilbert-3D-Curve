import sys
import math

class Point2d:
	def __init__(self, x, y):
		self.x = x
		self.y = y


class Point3d:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z
		
	def to_string(self):
		return str(self.x) + ", " + str(self.y) + ", " + str(self.z)


class ProgramArgs:
	def __init__(self, argv):
		self.curve_order = int(argv[2])
		self.image_size = float(argv[3])
		self.curve_scale = float(argv[4])
		self.camera_dist = float(argv[5])
		self.curve_pos = Point3d(float(argv[6]), float(argv[7]), float(argv[8]))
		self.ox_angle = float(argv[9])
		self.oy_angle = float(argv[10])	


def generate_postscript(image_size, point_list):
	result = "%!PS-Adobe-2.0 EPSF-2.0\n"
	result += "%%BoundingBox: 0 0 " + str(image_size) + " " + str(image_size) + "\nnewpath\n"
	result += str(point_list[0].x) + " " + str(point_list[0].y) + " moveto\n"
	for it in point_list[1:]:
		result += str(it.x) + " " + str(it.y) + " lineto\n"
	result += ".4 setlinewidth\nstroke\nshowpage\n%%Trailer\n%EOF"	
	return result
	
def get_default_pos(c_order):
	return (1 << (c_order - 1)) - 0.5
	
def get_default_rect_size(c_order):
	return (1 << (c_order - 1)) / 2.0
	
def get_pos_list(c_pos, r_size):
	p_point = Point3d(c_pos.x + r_size, c_pos.y + r_size, c_pos.z + r_size)
	m_point = Point3d(c_pos.x - r_size, c_pos.y - r_size, c_pos.z - r_size)
	result = [] 
	result.append(Point3d(m_point.x, p_point.y, p_point.z))
	result.append(Point3d(m_point.x, p_point.y, m_point.z))
	result.append(Point3d(p_point.x, p_point.y, m_point.z))	
	result.append(Point3d(p_point.x, p_point.y, p_point.z))
	result.append(Point3d(p_point.x, m_point.y, p_point.z))
	result.append(Point3d(p_point.x, m_point.y, m_point.z))
	result.append(Point3d(m_point.x, m_point.y, m_point.z))
	result.append(Point3d(m_point.x, m_point.y, p_point.z))
	return result
	
def permute_list(cur_list, perm):
	result = []
	for i in range(0, len(cur_list)):
		result.append(cur_list[perm[i]])
	return result		
	
def get_child_d(d_list, number):
	if number == 0:
		return permute_list(d_list, [0, 3, 4, 7, 6, 5, 2, 1])
	elif number == 1:
		return permute_list(d_list, [0, 7, 6, 1, 2, 5, 4, 3])
	elif number == 2:
		return permute_list(d_list, [0, 7, 6, 1, 2, 5, 4, 3])
	elif number == 3:
		return permute_list(d_list, [2, 3, 0, 1, 6, 7, 4, 5])
	elif number == 4:
		return permute_list(d_list, [2, 3, 0, 1, 6, 7, 4, 5])
	elif number == 5:
		return permute_list(d_list, [4, 3, 2, 5, 6, 1, 0, 7])
	elif number == 6:
		return permute_list(d_list, [4, 3, 2, 5, 6, 1, 0, 7])
	elif number == 7:
		return permute_list(d_list, [6, 5, 2, 1, 0, 3, 4, 7])
	
def gen_coords(c_order, cur_pos, rect_size, d_list):
	if c_order == 0:
		return [Point3d(cur_pos.x, cur_pos.y, cur_pos.z)]
	result = []
	c_order = c_order - 1
	p_list = get_pos_list(cur_pos, rect_size)
	rect_size = rect_size / 2.0
	for i in range(0, 8):		
		result += gen_coords(c_order, p_list[d_list[i]], rect_size, get_child_d(d_list, i))
	return result
		
def get_hilbert_curve(c_order):
	cur_pos = get_default_pos(c_order)
	rect_size = get_default_rect_size(c_order)
	return gen_coords(c_order, Point3d(cur_pos, cur_pos, cur_pos), rect_size, range(0, 8))
	
def scale_curve_size(point_list, scale):
	for it in point_list:
		it.x *= scale
		it.y *= scale
		it.z *= scale

def set_curve_pos(point_list, cur_pos, new_pos):
	for it in point_list:
		it.x = it.x + (new_pos.x - cur_pos.x)
		it.y = it.y + (new_pos.y - cur_pos.y)
		it.z = it.z + (new_pos.z - cur_pos.z)
	
def rotate_ox_axis(point_list, angle):
	angle_cos = math.cos(math.radians(angle))
	angle_sin = math.sin(math.radians(angle))
	for it in point_list:
		it.y = it.y * angle_cos - it.z * angle_sin
		it.z = it.y * angle_sin + it.z * angle_cos
	
def rotate_oy_axis(point_list, angle):
	angle_cos = math.cos(math.radians(angle))
	angle_sin = math.sin(math.radians(angle))
	for it in point_list:
		it.x = it.x * angle_cos + it.z * angle_sin
		it.z = -it.x * angle_sin + it.z * angle_cos

def transform_curve(point_list, prog_args):
	scale_curve_size(point_list, prog_args.curve_scale)
	c_size = get_default_pos(prog_args.curve_order) * prog_args.curve_scale
	center_pos = Point3d(c_size, c_size, c_size)
	set_curve_pos(point_list, center_pos, Point3d(0.0, 0.0, 0.0))
	rotate_ox_axis(point_list, prog_args.ox_angle)
	rotate_oy_axis(point_list, prog_args.oy_angle)
	left_corner_pos = Point3d(-c_size, -c_size, -c_size)
	set_curve_pos(point_list, left_corner_pos, prog_args.curve_pos)
	
def get_projected_point_list(point_list, cam_dist):
	result = []
	for it in point_list:
		point_dist = it.z + cam_dist
		result.append(Point2d(it.x * (cam_dist / point_dist), it.y * (cam_dist / point_dist)))
	return result

####################TESTS####################

def test_coord(coord, c_order):
	assert (coord >= 0 and coord < (1 << c_order) and coord.is_integer())

def test_coords(c_order, point_list):
	for it in point_list:
		test_coord(it.x, c_order)
		test_coord(it.y, c_order)
		test_coord(it.z, c_order)
		
def test_curve_size(c_order, point_list):
	assert (len(point_list) == pow((1 << c_order), 3))

def test_point_uniqueness(point_list):
	point_set = set()
	for it in point_list:
		assert ((it.to_string() in point_set) == False)
		point_set.add(it.to_string())
		
def test_point_diff(p1, p2):
	is_diff_x = abs(p1.x - p2.x) == 1 and p1.y == p2.y and p1.z == p2.z
	is_diff_y = p1.x == p2.x and abs(p1.y - p2.y) == 1 and p1.z == p2.z
	is_diff_z = p1.x == p2.x and p1.y == p2.y and abs(p1.z - p2.z) == 1
	assert (is_diff_x or is_diff_y or is_diff_z)

def test_point_list(point_list):
	for i in range(1, len(point_list)):
		test_point_diff(point_list[i - 1], point_list[i])

def test_curve(c_order):
	point_list = get_hilbert_curve(c_order)
	test_coords(c_order, point_list)
	test_curve_size(c_order, point_list)
	test_point_uniqueness(point_list)
	test_point_list(point_list)

def test_hilbert():
	for i in range(1, 7):
		test_curve(i)
	print "HILBERT TEST OK!"

####################MAIN####################

def main():
	prog_args = ProgramArgs(sys.argv)
	point_list = get_hilbert_curve(prog_args.curve_order)
	transform_curve(point_list, prog_args)	
	point_list = get_projected_point_list(point_list, prog_args.camera_dist)
	print generate_postscript(prog_args.image_size, point_list)

main()
