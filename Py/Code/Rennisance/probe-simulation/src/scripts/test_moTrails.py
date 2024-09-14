from direct.showbase.ShowBase import ShowBase

from panda3d.core import *

from direct.motiontrail.MotionTrail import MotionTrail
class Main(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disable_mouse()
        self.ship = self.loader.loadModel("models/smiley")
        self.ship.reparentTo(self.render)
        self.camera.setPos(0, 15, 5)
        self.camera.lookAt(self.render)
        self.keyMap = {'left':False, 'right':False}
        self.accept('a', self.updateKeyMap, extraArgs=['left', True])
        self.accept('a-up', self.updateKeyMap, extraArgs=['left', False])
        self.accept('d', self.updateKeyMap, extraArgs=['right', True])
        self.accept('d-up', self.updateKeyMap, extraArgs=['right', False])
        self.setupMotionTrail()
        self.taskMgr.add(self.move)

    def updateKeyMap(self, key, value):
        self.keyMap[key] = value

    def move(self, task):
        if self.keyMap['left']:
            self.ship.setPos(self.ship.getPos()+(0.2, 0,0))
        if self.keyMap['right']:
            self.ship.setPos(self.ship.getPos()-(0.2, 0,0))
        return task.cont

    def setupMotionTrail(self):

        shipTrail = MotionTrail("shipTrail", self.ship)

        flame_colors = (
            Vec4(0, 0.0, 1.0, 1),
            Vec4(0, 0.2, 1.0, 1),
            Vec4(0, 0.7, 1.0, 1),
            Vec4(0.0, 0.0, 0.2, 1),
        )

        center = self.render.attach_new_node("center")
        around = center.attach_new_node("around")
        around.set_z(1)
        res = 8
        for i in range(res + 1):
            center.set_r((360 / res) * i)
            vertex_pos = around.get_pos(self.render)
            shipTrail.add_vertex(vertex_pos)

            start_color = flame_colors[i % len(flame_colors)] * 1.7
            end_color = Vec4(1, 1, 0, 1)
            shipTrail.set_vertex_color(i, start_color, end_color)
        shipTrail.update_vertices()

        shipTrail.register_motion_trail()

main = Main()
main.run()