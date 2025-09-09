import math
from obj import format_obj
import random
import os

def next_filename(base_name="output_ver", ext=".txt"):
    version = 1
    while True:
        filename = f"{base_name}{version}{ext}"
        if not os.path.exists(filename):  # stop when we find a free name
            return filename
        version += 1

class vec2():
    #simple 2d vector, used for points, implemented dot product
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def dot(self, vec):
        return vec.x * self.x + vec.y * self.y

    def __add__(self,vec):
        return vec2(self.x + vec.x, self.y + vec.y)

    def __str__(self):
        return f"({self.x}, {self.y})"

class vec3():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def dot(self, vec):
        return vec.x * self.x + vec.y * self.y + self.z* vec.z


    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

def interpolate(t1, t2, y1, y2, iv): #remove dx dy from parameters
    #standard interpolation t is iv, y is dv,  t1 > t2

    #interpolates on the given iv
    match iv:
        case "t":
            if t1 == t2:
                start_y, end_y = sorted((y1, y2))
                return [(t1, y) for y in range(start_y, end_y + 1)]

            start, end = sorted((t1, t2))
            inter_points = [(a, int((a - t1) * (y2-y1)/(t2-t1) + y1)) for a in range(start, end+1)]

        case "y":
            if y1 == y2:
                start_t, end_t = sorted((t1, t2))
                return [(t, y1) for t in range(start_t, end_t + 1)]
            
            start, end = sorted((y1,y2))
            inter_points = [(int((a - y1) * (t2-t1)/(y2-y1) + t1), a) for a in range(start, end+1)]

                        
    return inter_points
                    
class side():
    #for a side between two vertices, a, and b are 2d vector vertices(will probs switch to 3d eventually)
    def __init__(self, vec_a, vec_b):
        #points list and length attributes
        self.dx = abs(vec_a.x - vec_b.x)
        self.dy = abs(vec_a.y - vec_b.y)

        self.length = math.sqrt(self.dx**2 + self.dy**2)

        #creating a list of points along side by interpolation, outline optimizes iv/dv for no. horizontal/vertical points, points does not
        if self.dy > self.dx:
        #logic to define iv based on no.points on each axis
            self.outline_list = interpolate(vec_a.x, vec_b.x, vec_a.y, vec_b.y, "y")
        
        else:
            self.outline_list = interpolate(vec_a.x, vec_b.x, vec_a.y, vec_b.y, "t")

        self.points_list = interpolate(vec_a.x, vec_b.x, vec_a.y, vec_b.y, "y")

        self.last = self.points_list[-1]
        self.first = self.points_list[0]

#partitions triangle and returns a tuple of the longest side and the other two sides conjoined
def partition_triangle(a ,b, c):
    
    #creating two side
    v0, v1, v2 = sorted([a, b, c], key=lambda v: (v.y, v.x))
    q, mid, p = v0, v1, v2
    
    longest_side = side(p, q)
    longest = longest_side.points_list
    check_index = int(len(longest)/2)
    
    i = side(q, mid)
    j = side(p, mid)
    shorter = i.points_list + j.points_list[1:]

    #defining sides as left or right
    if longest[check_index][0] < shorter[check_index][0]:
        left = longest
        right = shorter

    else:
        left = shorter
        right = longest


    return (left, right, p.y, q.y)

def drawTriangle(triangle_list, vertex_list, canvas):
    
    draw_col = "  0   0   0"

    #generate random rgb
    for index in range(len(triangle_list)):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        rgb = f"{r:3} {g:3} {b:3}"
        

        triangle = triangle_list[index]
        a = vertex_list[triangle[0]]
        b = vertex_list[triangle[1]]
        c = vertex_list[triangle[2]]

        ab = side(a,b)
        bc = side(b,c)
        ac = side(a,c)
        outline = ab.outline_list + bc.outline_list + ac.outline_list

        fill_tuple = partition_triangle(a,b,c)
        left = fill_tuple[0]
        right = fill_tuple[1]
        ymax = fill_tuple[2]
        ymin = fill_tuple[3]

        #draws fill
        for y in range(ymin, ymax):
            for x in range(left[y - ymin][0], right[y-ymin][0]):
                print(f"{x}, {y}")
                canvas[y][x] = rgb
                
        #draws triangle outline
        for point in outline:
            x = point[0]
            y = point[1]
            canvas[y][x] = draw_col
    
    return canvas

def drawFan(non_list, vertex_list, canvas):
   #sorts shape vertex indices into triangle fans, creates a triangle list and calls drawTriangle
    triangle_list = []

    for shape in non_list:
        #the center is the lowest point, and the rest are sorted by x, this may need to be bettered. Edit: Didn't work + obj is already ordered
        #print(shape)
        #center = min(shape, key = lambda i:vertex_list[i].y)
        #print(center)
        #sorted_indices.remove(center)

        center = shape[0]
        sorted_indices = shape[1:]

        
        triangle_list.append([center, sorted_indices[0], sorted_indices[1]])

        for i in range(2, len(sorted_indices)):
            triangle = [center, sorted_indices[i-1], sorted_indices[i]]
            triangle_list.append(triangle)

    canvas = drawTriangle(triangle_list, vertex_list, canvas)
    
    return canvas

def project(vertices, w, h):
    NEAR_Z = 1
    instance_trans = vec3(0, 0, 4)

    xs = [v.x for v in vertices]
    ys = [v.y for v in vertices]
    min_x, max_x = min(xs), max(xs)
    dx = max_x - min_x
    min_y, max_y = min(ys), max(ys)
    dy = max_y - min_y

    #normalize to canvas with margin
    corigin = vec2(w/2, h/2)
    margin = 0.2
    xnco = (w-1)*(1 - margin * 2)/dx
    ynco = (h-1)*(1 - margin * 2)/dy

    projected = [vec2
        (int(vec.x * NEAR_Z/(vec.z + instance_trans.z) * xnco + corigin.x), 
        int(vec.y * NEAR_Z/(vec.z + instance_trans.z) * ynco  + corigin.y)) 
             for vec in vertices]

    return projected

#standard rasterizer, have not implemented a color list to index from yet
def rasterizer(shapes_list, vertex_list, canvas_w, canvas_h):
    grid = [canvas_w, canvas_h]
    max_col = "255"
    def_col = "255 255 255"
    
    header = f"P3 {grid[0]} {grid[1]}\n{max_col}\n"
    canvas = [[def_col for _ in range(grid[0])] for _ in range(grid[1])]

    #sort shapes into triangles and non triangles, nons are auto drawn as fans
    triangle_list = [shape for shape in shapes_list if len(shape) == 3]
    non_list = [shape for shape in shapes_list if len(shape) != 3]

    canvas = drawTriangle(triangle_list, vertex_list, canvas)
    canvas = drawFan(non_list, vertex_list, canvas)

    drawToPPM(header, canvas)


def rasterize_obj(obj_file_name, canvas_w, canvas_h):
    vertex_list, shapes_list = format_obj(obj_file_name)
    vertex_list = project([vec3(a[0], a[1], a[2]) for a in vertex_list], canvas_w, canvas_h)

    rasterizer(shapes_list, vertex_list, canvas_w, canvas_h)


def drawToPPM(header, canvas):
    filename = next_filename("0909/cube_test_ver", ".ppm")
    with open(filename, "w") as file:
        file.write(header)
        for row in canvas:
            for item in row:
                file.write(item)
                file.write("   ")
            file.write("\n")
                              
noshapes = 2
shape_sides = 4

#shapes list is a 2d list of the index of shape vertices, vertex list is a list of vertices
#FANS TEST
shapes_list = [[i, i+1, i+2, i+3] for i in range(0, noshapes*shape_sides, 4)]
vertex_list = [vec2(random.randint(0,499), random.randint(0,499)) for a in range(4*noshapes)]

#TRIANGLES TEST
#shapes_list = [[i, i+1, i+2] for i in range(0, notriangles*3, 3)]
#vertex_list = [vec2(random.randint(0,499), random.randint(0,499)) for a in range(3*notriangles)]


w = 200
h = w

#rasterizer(shapes_list, vertex_list, w, h)

rasterize_obj("cube.obj", w, h)

#To do: currently the color is randomly generated within each instance of a triangle, create a color list