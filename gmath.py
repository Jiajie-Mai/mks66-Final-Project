import math
from display import *


  # IMPORANT NOTE

  # Ambient light is represeneted by a color value

  # Point light sources are 2D arrays of doubles.
  #      - The fist index (LOCATION) represents the vector to the light.
  #      - The second index (COLOR) represents the color.

  # Reflection constants (ka, kd, ks) are represened as arrays of
  # doubles (red, green, blue)

AMBIENT = 0
DIFFUSE = 1
SPECULAR = 2
LOCATION = 0
COLOR = 1
SPECULAR_EXP = 4

#lighting functions
def get_lighting(normal, view, ambient, light, symbols, reflect ):

    n = normal[:]
    normalize(n)
    normalize(light[LOCATION])
    normalize(view)
    r = symbols[reflect][1]

    a = calculate_ambient(ambient, r)
    d = calculate_diffuse(light, r, n)
    s = calculate_specular(light, r, view, n)

    i = [0, 0, 0]
    i[RED] = int(a[RED] + d[RED] + s[RED])
    i[GREEN] = int(a[GREEN] + d[GREEN] + s[GREEN])
    i[BLUE] = int(a[BLUE] + d[BLUE] + s[BLUE])
    limit_color(i)

    return i

def get_lighting(normal, view, ambient, light, areflect, dreflect, sreflect, intensity):
    normalize(normal)
    normalize(view)

    a = calculate_ambient(ambient, areflect)
    d = [0,0,0]
    s = [0,0,0]

    for l in range(len(light)):
        normalize(light[l][LOCATION])
        dif = calculate_diffuse(light[l], dreflect, normal)
        spec = calculate_specular(light[l], sreflect, view, normal)
        for ind in range(3):
            d[ind] += dif[ind]
            s[ind] += spec[ind]

    i = [0, 0, 0]
    i[RED] = int(a[RED] + d[RED] + s[RED] + intensity[RED])
    i[GREEN] = int(a[GREEN] + d[GREEN] + s[GREEN] + intensity[GREEN])
    i[BLUE] = int(a[BLUE] + d[BLUE] + s[BLUE] + intensity[BLUE])

    limit_color(i)
    return i

def calculate_ambient(alight, areflect):
    a = [0, 0, 0]
    a[RED] = alight[RED] * areflect[RED]
    a[GREEN] = alight[GREEN] * areflect[GREEN]
    a[BLUE] = alight[BLUE] * areflect[BLUE]
    return a

def calculate_diffuse(light, dreflect, normal):
    d = [0, 0, 0]

    dot = dot_product( light[LOCATION], normal)

    dot = dot if dot > 0 else 0
    d[RED] = light[COLOR][RED] * dreflect[RED] * dot
    d[GREEN] = light[COLOR][GREEN] * dreflect[GREEN] * dot
    d[BLUE] = light[COLOR][BLUE] * dreflect[BLUE] * dot
    return d

def calculate_specular(light, sreflect, view, normal):
    s = [0, 0, 0]
    n = [0, 0, 0]

    result = 2 * dot_product(light[LOCATION], normal)
    n[0] = (normal[0] * result) - light[LOCATION][0]
    n[1] = (normal[1] * result) - light[LOCATION][1]
    n[2] = (normal[2] * result) - light[LOCATION][2]

    result = dot_product(n, view)
    result = result if result > 0 else 0
    result = pow( result, SPECULAR_EXP )

    s[RED] = light[COLOR][RED] * sreflect[RED] * result
    s[GREEN] = light[COLOR][GREEN] * sreflect[GREEN] * result
    s[BLUE] = light[COLOR][BLUE] * sreflect[BLUE] * result
    return s

def limit_color(color):
    if color[RED] > 255:
        color[RED] = 255
    elif color[RED] < 0:
        color[RED] = 0
    if color[GREEN] > 255:
        color[GREEN] = 255
    elif color[GREEN] < 0:
        color[GREEN] = 0
    if color[BLUE] > 255:
        color[BLUE] = 255
    elif color[BLUE] < 0:
        color[BLUE] = 0

#vector functions
#normalize vetor, should modify the parameter
def normalize(vector):
    magnitude = math.sqrt( vector[0] * vector[0] +
                           vector[1] * vector[1] +
                           vector[2] * vector[2])
    for i in range(3):
        vector[i] = vector[i] / magnitude if magnitude > 0 else 0

#Return the dot porduct of a . b
def dot_product(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

#Calculate the surface normal for the triangle whose first
#point is located at index i in polygons
def calculate_normal(polygons, i):

    A = [0, 0, 0]
    B = [0, 0, 0]
    N = [0, 0, 0]

    A[0] = polygons[i+1][0] - polygons[i][0]
    A[1] = polygons[i+1][1] - polygons[i][1]
    A[2] = polygons[i+1][2] - polygons[i][2]

    B[0] = polygons[i+2][0] - polygons[i][0]
    B[1] = polygons[i+2][1] - polygons[i][1]
    B[2] = polygons[i+2][2] - polygons[i][2]

    N[0] = A[1] * B[2] - A[2] * B[1]
    N[1] = A[2] * B[0] - A[0] * B[2]
    N[2] = A[0] * B[1] - A[1] * B[0]

    return N
