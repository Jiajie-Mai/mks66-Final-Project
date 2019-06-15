import mdl
from display import *
from matrix import *
from draw import *
import os

is_anim = False
num_frames = 1
base = "basename"
knobs = []

"""======== first_pass( commands ) ==========
  Checks the commands array for any animation commands
  (frames, basename, vary)
  Should set num_frames and basename if the frames
  or basename commands are present
  If vary is found, but frames is not, the entire
  program should exit.
  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """

  #Thank you Andrew Shao for helping me fix my script to implement new intensity feature
def first_pass( commands ):

    global num_frames
    global base
    global is_anim
    frames = False
    basename = False

    for command in commands:
        c = command['op']
        args = command['args']

        if c == 'frames':
            frames = True
            is_anim = True
            num_frames = args[0]

        elif c == 'basename':
            is_anim = True
            found_basename = True
            base = args[0]

        elif c == 'vary':
            is_anim = True
            if not frames: return

"""======== second_pass( commands ) ==========
  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).
  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.
  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ====================Thank you Hui Min for giving me a hand at the second pass"""
def second_pass( commands):
    global knobs
    global num_frames

    for i in range(int(num_frames)):
        knobs.append({})

    for command in commands:
        c = command['op']
        args = command['args']

        if c == 'vary':
            knob = command['knob']
            curr = args[2]
            if len(args) > 4 and args[4] <= 0: return
            increment = (args[3] - args[2]) / (args[1] - args[0] + 1)

            for i in range(int(args[0]), int(args[1])+1):
                if len(args) > 4:
                    if isinstance(args[4],float):
                        if increment < 0:
                            curr = ((increment * (i-args[1]-1)) ** args[4])
                        else:
                            curr = (increment * (i+1)) ** args[4]
                        knobs[i][knob] = curr
                    elif  args[4] == 'sin':
                        if increment < 0:
                            curr = math.sin((increment * (i-args[1]-1) * math.pi/2))
                        else:
                            curr = math.sin((increment * (i+1) * math.pi/2))
                        knobs[i][knob] = curr
                    elif args[4] == 'cos':
                        if increment < 0:
                            curr = 1-math.cos((increment * (i-args[1]-1) * math.pi/2))
                        else:
                            curr = 1-math.cos((increment * (i+1) * math.pi/2))
                        knobs[i][knob] = curr
                    elif args[4] == 'tan':
                        if increment < 0:
                            curr = math.tan((increment * (i-args[1]-1) * math.pi/4))
                        else:
                            curr = math.tan((increment * (i+1) * math.pi/4))
                        knobs[i][knob] = curr
                    elif args[4] == 'ln':
                        if increment < 0:
                            curr = (2-math.log((increment * (i-args[1]-1) * math.e))) ** -1
                        else:
                            curr = (2-math.log((increment * (i+1) * math.e))) ** -1
                        knobs[i][knob] = curr
                else:
                    knobs[i][knob] = curr
                    curr += increment


def run(filename):
    """
    This function runs an mdl script
    """

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    first_pass(commands)
    second_pass(commands)

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    deflight = [[0.5,
              0.75,
              1],
             [255,
              255,
              255]]
    lights = []
    areflect = [0.1,
                0.1,
                0.1]
    dreflect = [0.5,
                0.5,
                0.5]
    sreflect = [0.5,
                0.5,
                0.5]
    consts = [areflect[0],dreflect[0],sreflect[0],areflect[1],dreflect[1],
                  sreflect[1],areflect[2],dreflect[2],sreflect[2]]
    default = consts[:]
    color = [0, 0, 0]

    tmp = new_matrix()
    ident( tmp )

    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    zbuffer = new_zbuffer()
    tmp = []
    step_3d = 20
    consts = ''
    coords = []
    coords1 = []

    for frame in range(int(num_frames)):
        if "shading" in symbols.keys():
            shading = symbols["shading"][1]
        else:
            shading = "flat"

        for knob in knobs[frame]:
            symbols[knob][1] = knobs[frame][knob]

        for command in commands:
            #print command
            c = command['op']
            args = command['args']
            if (not args == None):
                args = args[:]
            if (c in ["move", "scale", "rotate"]) and (not args == None) and ("knob" in command) and (not command["knob"] == None):
                knob = command["knob"]
                for i in range(len(args)):
                    if not isinstance(args[i], basestring):
                        args[i] = args[i] * symbols[knob][1]



            if c == 'box':
                intensity = [0,0,0]
                if command['constants'] != None:
                    consts = symbols[command['constants']][1]
                    areflect = [consts['red'][0],consts['green'][0],consts['blue'][0]]
                    dreflect = [consts['red'][1],consts['green'][1],consts['blue'][1]]
                    sreflect = [consts['red'][2],consts['green'][2],consts['blue'][2]]
                    if len(consts['blue']) > 3:
                        intensity[0] = consts['blue'][3]
                        intensity[1] = consts['blue'][4]
                        intensity[2] = consts['blue'][5]
                else:
                    areflect = [default[0],default[3],default[6]]
                    dreflect = [default[1],default[4],default[7]]
                    sreflect = [default[2],default[5],default[8]]
                if command['cs'] != None:
                    coords = command['cs']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, lights, areflect, dreflect, sreflect, shading, intensity)
                tmp = []
            elif c == 'sphere':
                intensity = [0,0,0]
                if command['constants'] != None:
                    consts = symbols[command['constants']][1]
                    areflect = [consts['red'][0],consts['green'][0],consts['blue'][0]]
                    dreflect = [consts['red'][1],consts['green'][1],consts['blue'][1]]
                    sreflect = [consts['red'][2],consts['green'][2],consts['blue'][2]]
                    if len(consts['blue']) > 3:
                        intensity[0] = consts['blue'][3]
                        intensity[1] = consts['blue'][4]
                        intensity[2] = consts['blue'][5]
                else:
                    areflect = [default[0],default[3],default[6]]
                    dreflect = [default[1],default[4],default[7]]
                    sreflect = [default[2],default[5],default[8]]
                if command['cs'] != None:
                    coords = command['cs']
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, lights, areflect, dreflect, sreflect, shading, intensity)
                tmp = []
            elif c == 'torus':
                intensity = [0,0,0]
                if command['constants'] != None:
                    consts = symbols[command['constants']][1]
                    areflect = [consts['red'][0],consts['green'][0],consts['blue'][0]]
                    dreflect = [consts['red'][1],consts['green'][1],consts['blue'][1]]
                    sreflect = [consts['red'][2],consts['green'][2],consts['blue'][2]]
                    if len(consts['blue']) > 3:
                        intensity[0] = consts['blue'][3]
                        intensity[1] = consts['blue'][4]
                        intensity[2] = consts['blue'][5]
                else:
                    areflect = [default[0],default[3],default[6]]
                    dreflect = [default[1],default[4],default[7]]
                    sreflect = [default[2],default[5],default[8]]
                if command['cs'] != None:
                    coords = command['cs']
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, lights, areflect, dreflect, sreflect, shading, intensity)
                tmp = []
            elif c == 'line':
                if command['constants'] != None:
                    consts = symbols[command['constants']][1]
                    areflect = [consts['red'][0],consts['green'][0],consts['blue'][0]]
                    dreflect = [consts['red'][1],consts['green'][1],consts['blue'][1]]
                    sreflect = [consts['red'][2],consts['green'][2],consts['blue'][2]]
                if command['cs0'] != None:
                    coords = command['cs0']
                if command['cs1'] != None:
                    coords1 = command['cs1']
                add_edge(tmp,
                         args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'ambient':
                ambient = args[:]
            elif c == 'light':
                col = symbols[command['light']][1]['color']
                loca = symbols[command['light']][1]['location']
                light = [loca,col]
                lights.append(light)
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
        if is_anim:
            if not os.path.exists('anim'):
                os.mkdir('anim')
            save_extension(screen, ("./anim/" + base + ("%03d" % int(frame)) + ".png"))

        tmp = new_matrix()
        ident( tmp )
        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        lights = []
        step_3d = 20

    if is_anim:
        make_animation(base)
        # end operation loop
