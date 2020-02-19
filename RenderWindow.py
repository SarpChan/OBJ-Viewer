

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from PIL import Image

import numpy as np


####### Keys:

### Farbaenderung: S Schwarz, W Weiss, G Gelb, B Blau, R Rot
### Objektwahl: Ohne Mod Objekt, Shift Hintergrund, Alt Schatten
### Weitere Keys: ESC Schliessen, O Orthogonale Sicht, P Zentralperspektive, H Schatten an/aus

####### Maus:

### Links Drehen
### Mittel Zoom
### Rechts Verschieben

###### Resizable

# author: Sarp Can (scanx001)


class RenderWindow:


    def __init__(self):

        # save current working directory
        cwd = os.getcwd()

        # Initialize the library
        if not glfw.init():
            return

        # restore cwd
        os.chdir(cwd)


        glfw.window_hint(glfw.DEPTH_BITS, 32)

        # Variablen inits

        #Kamera Variablen
        self.fov = 45
        self.near = 0.1
        self.far = 30
        self.ortho = False
        self.perspect = True



        #Fenster Variablen

        self.width, self.height = 640, 480
        self.aspect = self.width / float(self.height)
        self.window = glfw.create_window(self.width, self.height, "OBJ to Model", None, None)
        self.exitNow = False
        self.resizing = False

        #Objekt Variablen
        self.scale = 1
        self.boundBox = []
        self.ObjektVBO = None
        self.center = []
        self.data = []
        self.diffuse = [1.0, 1.0, 1.0, 1.0]
        self.specular = [1.0, 1.0, 1.0, 0.8]
        self.ambient = [0, 1.0, 1.0, .2]
        self.shiny = 70.0

        #Drehung Variablen
        self.radius = 0
        self.turn = False
        self.angle = 0
        self.axis = np.array([1, 0, 0])
        self.orientierung = np.matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        self.startP = np.array([0.0, 0.0, 0.0])

        #Maus Variablen
        self.oldX = 0
        self.oldY = 0
        self.newX = 0
        self.newY = 0

        #Licht und Schatten
        self.color = [0.8, 0.8, 0.8]
        self.bgColor = [1, 1, 1, 1]
        self.toggleShadow = True
        self.shadowColor = [0.4, 0.4, 0.4, 1.0]
        self.licht2 = [-1000, 2000, 500]
        self.licht = [1000, 2000, 3000]
        self.p = [1.0, 0, 0, 0, 0, 1.0, 0, -1.0 / self.licht[1], 0, 0, 1.0, 0, 0, 0, 0, 0]
        self.p2 = [1.0, 0, 0, 0, 0, 1.0, 0, -1.0 / self.licht2[1], 0, 0, 1.0, 0, 0, 0, 0, 0]

        #Translation - Benutzt Maus Variablen
        self.move = False

        #Zoom - Benutzt Maus Variablen
        self.zoom = False



        if not self.window:
            glfw.terminate()
            return


        glfw.make_context_current(self.window)




        #Callbacks

        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_cursor_pos_callback(self.window, self.onMouseMove)
        glfw.set_framebuffer_size_callback(self.window, self.onResize)


    def normaleBerechnen(self, faces, norms, verts):

        if norms:
            # Wenn die obj Datei Normalen enthaelt, werden die uebernommen

            neuVert = int(faces[len(faces) -1][0]) - 1
            neuNorm = int(faces[len(faces) -1][2]) - 1
            self.data.append(verts[neuVert] + norms[neuNorm])

        else:
            # berechne Normale, wenn keine vorhanden
            # ein face besteht aus 3 Punkten, deswegen wird dieser Teil nur ausgefuehrt
            # wenn die Laenge der Faces Modulo 3 = 0 ist, also 3 unbearbeitete Faces vorliegen
            tempIndex = len(faces)
            if tempIndex % 3 == 0 and tempIndex != 0:
                p1 = np.array(verts[int(faces[tempIndex - 3][0] - 1)])
                p2 = np.array(verts[int(faces[tempIndex -2][0] - 1)])
                p3 = np.array(verts[int(faces[tempIndex -1][0] - 1)])

                richtungsvek1 = p2 - p1

                richtungsvek2 = p3 - p1

                n = np.cross(richtungsvek1, richtungsvek2)

                normal = n.tolist()

                self.data.append(p1.tolist() + normal)
                self.data.append(p2.tolist() + normal)
                self.data.append(p3.tolist() + normal)






    # Ziehe Vertices, Normalen und Faces aus dem obj (texturen koennen auch gezogen,
    # wuerden aber nie weiter verarbeitet werden)

    def verarbeiteOBJ(self, filename):
        verts = []
        norms = []
        faces = []
        #text = []

        for lines in open(filename):

            if lines.split():
                check = lines.split()[0]
                if check == 'v':
                    verts.append( map(float, lines.split()[1:] ))
                if check == 'vn':
                    norms.append( map(float, lines.split()[1:] ))
                #elif check == 'vt':
                #   text.append(np.array( map(float, lines.split()[1:] )))
                if check == 'f':
                    ohneF = lines.split()[1:]

                    # Faces muessen noch von Slashes - wenn vorhanden- befreit werden
                    for face in ohneF:

                        if(face.__contains__('//')):
                            temp = map(float, face.split('//'))
                            # kein vt -> textur = 0 setzen , Hier der Standard. Texturen gehen nicht.
                            temp.insert(1, 0.0)
                            faces.append(temp)
                            self.normaleBerechnen(faces, norms, verts)

                        elif(face.__contains__('/')):
                            faces.append(map(float, face.split('/')))
                            self.normaleBerechnen(faces, norms, verts)

                        else:
                            temp =[float(face)]
                            # kein vn und vt ->  textur = 0 setzen. Vorher wurde auch Normale 0 gesetzt,
                            # aber Normalen werden in normaleBerechnen berechnet
                            temp.insert(1, 0.0)
                            faces.append(temp)
                            self.normaleBerechnen(faces, norms, verts)

        self.ObjektVBO = vbo.VBO(np.array(self.data, 'f'))

        return verts


        #Gibt Dateiverarbeitung weiter und setzt anschliessend wichtige Attribute fuer die Kamera
    def readFile(self, string):

        verts= self.verarbeiteOBJ(string)


        # Bounding Box erstellen
        self.boundBox = [map(min, zip(*verts)),
                         map(max, zip(*verts))]

        # Center finden
        self.center =  [(self.boundBox[1][0] + self.boundBox[0][0]) / 2,
                        (self.boundBox[1][1] + self.boundBox[0][1]) /2,
                        (self.boundBox[1][2] + self.boundBox[0][2]) /2 ]

        # Skalierfaktor
        self.scale = 2/max(list(np.array(self.boundBox[1]) - np.array(self.boundBox[0])))




    def projectOnSphere(self, x,y,r):
        # VL Arcball
        x,y = x- self.width/2.0, self.height/2.0 - y
        a = min(r*r, x**2 + y**2)
        z = np.sqrt(r*r - a)
        l = np.sqrt(x**2 + y**2 + z**2)

        return x/l, y/l, z/l

    def rotate(self, angle, axis):
        #VL Arcball

        c, mc = np.cos(float(angle)), 1 - np.cos(float(angle))
        s = np.sin(angle)
        l = np.sqrt(np.dot(np.array(axis), np.array(axis)))

        x, y, z = np.array(axis) / l
        r = np.matrix(
            [[x * x * mc + c, x * y * mc - z * s, x * z * mc + y * s, 0],
             [x * y * mc + z * s, y * y * mc + c, y * z * mc - x * s, 0],
             [x * z * mc - y * s, y * z * mc + x * s, z * z * mc + c, 0],
             [0, 0, 0, 1]])

        return r.transpose()

    def onMouseMove(self, win, xpos, ypos):
        transX, transY = 0,0

        if self.oldX:
            transX = xpos - self.oldX
            transY = ypos - self.oldY

        if(self.move):
            # durch breite/ hoehe teilen, um nicht zu schnell zu verschieben
            if xpos - self.oldX != 0:
                self.newX = self.newX + transX / 100
            if ypos - self.oldY != 0:
                self.newY = self.newY - transY / 100

        elif(self.turn):
            # moveP -> Wo auf der Kugel befindet sich die Maus bei Bewegung

            moveP = self.projectOnSphere(xpos, ypos, self.radius)
            self.angle = np.arccos(np.dot(self.startP, moveP))
            self.axis = np.cross(self.startP, moveP)



        elif(self.zoom):
            # Faktoren leicht vergroessert, damit skalieren natuerlicher ist
            if self.oldY > ypos:
                self.scale = self.scale * 1.01
            if self.oldY < ypos:
                self.scale = self.scale * 0.99

        self.oldX = xpos
        self.oldY = ypos

    def onResize(self, win, width, height):
        # Fenster resize

        self.width = width
        if height > 0:
            self.height = height
        else:
            self.height = 1

        self.aspect = self.width/ float(self.height)

        #sieheVL

        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        gluPerspective(self.fov, self.aspect, self.near, self.far)
        glMatrixMode(GL_MODELVIEW)

        glfw.swap_buffers(win)



    def onMouseButton(self, win, button, action, mods):

        self.radius = min(self.width, self.height) / 2.0

        if (button == glfw.MOUSE_BUTTON_RIGHT):
            if (action == glfw.PRESS):
                self.move = True
            elif(action == glfw.RELEASE):
                self.move = False
                
        elif(button == glfw.MOUSE_BUTTON_LEFT):
            if (action == glfw.PRESS):
                self.turn = True
                xpos, ypos = glfw.get_cursor_pos(win)
                self.startP = self.projectOnSphere(xpos, ypos, self.radius)

            elif(action == glfw.RELEASE):
                # Orientierung updaten
                # sonst bei naechster drehung reset auf AusgangsPos
                self.turn = False
                self.orientierung = self.orientierung * self.rotate(self.angle, self.axis)
                self.angle = 0
                
        elif(button == glfw.MOUSE_BUTTON_MIDDLE):
            if (action == glfw.PRESS):
                self.zoom = True
            elif(action == glfw.RELEASE):
                self.zoom = False


    def onKeyboard(self, win, key, scancode, action, mods):
        if action == glfw.PRESS:

            # Keys, die immer funktionieren sollen, auch wenn mod gedrueckt wird
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True
            if key == glfw.KEY_O:
                self.ortho = True
                self.perspect = False
            if key == glfw.KEY_P:
                self.ortho = False
                self.perspect =True
            if key == glfw.KEY_H:
                #Toggle Schatten
                self.toggleShadow = not self.toggleShadow

        # Keys, die nur funktionieren sollen, wenn kein Mod gedrueckt ist
        if mods != glfw.MOD_SHIFT and mods != glfw.MOD_ALT:
            if key == glfw.KEY_B:
                self.color=[0,0,1]
            if key == glfw.KEY_S:
                self.color=[0,0,0]
            if key == glfw.KEY_G:
                self.color=[1,1,0]
            if key == glfw.KEY_W:
                self.color=[1,1,1]
            if key == glfw.KEY_R:
                self.color=[1,0,0]

        # Keys, die nur funktionieren sollen, wenn Shift gedrueckt ist
        if mods == glfw.MOD_SHIFT:
            if key == glfw.KEY_B:
                self.bgColor=[0,0,1,1]
            if key == glfw.KEY_S:
                self.bgColor=[0,0,0,1]
            if key == glfw.KEY_G:
                self.bgColor=[1,1,0,1]
            if key == glfw.KEY_W:
                self.bgColor=[1,1,1,1]
            if key == glfw.KEY_R:
                self.bgColor=[1,0,0,1]

        # Keys, die nur funktionieren sollen, wenn Alt gedrueckt ist
        if mods == glfw.MOD_ALT:
            if key == glfw.KEY_B:
                self.shadowColor=[0,0,1,1]
            if key == glfw.KEY_S:
                self.shadowColor=[0,0,0,1]
            if key == glfw.KEY_G:
                self.shadowColor=[1,1,0,1]
            if key == glfw.KEY_W:
                self.shadowColor=[1,1,1,1]
            if key == glfw.KEY_R:
                self.shadowColor=[1,0,0,1]

    def run(self):

        self.readFile("squirrel.obj")
        while not glfw.window_should_close(self.window) and not self.exitNow:

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            #Farbe
            glClearColor(self.bgColor[0], self.bgColor[1], self.bgColor[2], self.bgColor[3])
            glColor(self.color[0], self.color[1], self.color[2])

            glLoadIdentity()

            # Licht und Schatten
            glShadeModel(GL_SMOOTH)
            glEnable(GL_LIGHT0)
            glLightfv(GL_LIGHT0, GL_POSITION, self.licht)
            glLightfv(GL_LIGHT0, GL_DIFFUSE, self.ambient)
            glLightfv(GL_LIGHT0, GL_DIFFUSE, self.diffuse)
            glLightfv(GL_LIGHT0, GL_SPECULAR, self.specular)
            glLightfv(GL_LIGHT0, GL_SPOT_EXPONENT, self.shiny)

            #2. Licht

            #glEnable(GL_LIGHT1)
            #glLightfv(GL_LIGHT1, GL_POSITION, self.licht2)
            #glLightfv(GL_LIGHT1, GL_DIFFUSE, self.ambient)
            #glLightfv(GL_LIGHT1, GL_DIFFUSE, self.diffuse)
            #glLightfv(GL_LIGHT1, GL_SPECULAR, self.specular)
            #glLightfv(GL_LIGHT1, GL_SPOT_EXPONENT, self.shiny)


            #Objektmaterial
            glEnable(GL_LIGHTING)
            glMaterial(GL_FRONT_AND_BACK, GL_SPECULAR, self.specular)
            glMaterial(GL_FRONT_AND_BACK, GL_DIFFUSE, self.diffuse)
            glMaterial(GL_FRONT_AND_BACK, GL_AMBIENT, self.ambient)
            glMaterial(GL_FRONT_AND_BACK, GL_SHININESS, self.shiny)


            glEnable(GL_DEPTH_TEST)
            glEnable(GL_NORMALIZE)
            glEnable(GL_COLOR_MATERIAL)

            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()

            # Welche Perspektive? Zentral oder Ortho
            if (self.perspect):
                gluPerspective(self.fov, self.aspect, self.near, self.far)
                gluLookAt(0, 0, 4 + self.scale, 0, 0, 0, 0, 1, 0)
            else:
                glOrtho(-1.5, 1.5, -1.5, 1.5, -1.0, 1.0)


            glMatrixMode(GL_MODELVIEW)
            self.ObjektVBO.bind()
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_NORMAL_ARRAY)


            glVertexPointer(3, GL_FLOAT, 24, self.ObjektVBO)
            glNormalPointer(GL_FLOAT, 24, self.ObjektVBO + 12)

            # Transformationen auf dem Objekt (Macht leider auch Transformation
            # auf Schatten)

            glTranslate(self.newX, self.newY, 0)
            glMultMatrixf(self.orientierung * self.rotate(self.angle, self.axis))
            glScale(self.scale, self.scale, self.scale)
            glTranslate(-self.center[0], -self.center[1], -self.center[2])


            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glDrawArrays(GL_TRIANGLES, 0, len(self.data))

            # Bodenschatten
            if(self.toggleShadow):
                #Schatten soll nicht beleuchtet werden
                glDisable(GL_LIGHTING)
                glDisable(GL_LIGHT0)

                glMatrixMode(GL_MODELVIEW)

                # Verschiebe Licht auf Ursprung (und alles andere mit), die Y-Komponente aber so, als haette das Objekt
                # vorher auf y = 0 gestanden. Nach Schattenobjektberechnung wieder zurueck

                glTranslatef(self.licht[0], self.licht[1] - np.sqrt(self.boundBox[0][1]**2), self.licht[2] )
                glMultMatrixf(self.p)
                glTranslatef(-self.licht[0], -self.licht[1] +np.sqrt(self.boundBox[0][1]**2) , -self.licht[2])

                glColor4fv(self.shadowColor)

                glPolygonMode(GL_FRONT, GL_FILL)
                glDrawArrays(GL_TRIANGLES, 0, len(self.data))

                ### 2. Schatten

                #glMatrixMode(GL_MODELVIEW)
                #
                #glTranslatef(self.licht2[0], self.licht2[1] - np.sqrt(self.boundBox[0][1] ** 2), self.licht2[2])
                #glMultMatrixf(self.p2)
                #glTranslatef(-self.licht2[0], -self.licht2[1] + np.sqrt(self.boundBox[0][1] ** 2), -self.licht2[2])
                #
                #glColor4fv(self.shadowColor)
                #
                #glPolygonMode(GL_FRONT, GL_FILL)
                #glDrawArrays(GL_TRIANGLES, 0, len(self.data))

            self.ObjektVBO.unbind()
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_NORMAL_ARRAY)




            glfw.swap_buffers(self.window)
            # Poll for and process events
            glfw.poll_events()
        # end
        glfw.terminate()




# main() function
def main():
    print("Simple glfw render Window")
    rw = RenderWindow()
    rw.run()


# call main
if __name__ == '__main__':
    main()