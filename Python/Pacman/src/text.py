import pygame
from vector import Vector2
from constants import *
from typing import Dict, Tuple, Optional


class Text(object):
    def __init__(self, text: str, color: Tuple[int, int, int], x: int, y: int, size: int, time: Optional[int] = None, identifier: Optional[int] = None, visible: Optional[bool] = True) -> None:
        self.identifier = identifier
        self.text = text
        self.color = color
        self.size = size
        self.visible = visible
        self.position = Vector2(x, y)
        self.timer = 0
        self.lifespan = time
        self.label = None
        self.destroy = False
        self.setupFont(f"{RESOURCES_FOLDER_NAME}/PressStart2P-Regular.ttf")
        self.createLabel()

    def setupFont(self, fontpath: str) -> None:
        self.font = pygame.font.Font(fontpath, self.size)

    def createLabel(self) -> None:
        self.label = self.font.render(self.text, 1, self.color)

    def setText(self, newtext: str) -> None:
        self.text = str(newtext)
        self.createLabel()

    def update(self, dt: float) -> None:
        if self.lifespan is not None:
            self.timer += dt
            if self.timer >= self.lifespan:
                self.timer = 0
                self.lifespan = None
                self.destroy = True

    def render(self, screen: pygame.surface.Surface) -> None:
        if self.visible:
            x, y = self.position.asTuple()
            assert self.label, "YDA"
            screen.blit(self.label, (x, y))


class TextGroup(object):
    def __init__(self) -> None:
        self.nextid = 10
        self.alltext: Dict[int, Text] = {}
        self.setupText()
        self.showText(READYTXT)

    def addText(self, text: str, color: Tuple[int, int, int], x: int, y: int, size: int, time: Optional[int] = None, identifier: Optional[int] = None) -> int:

        assert identifier is None, "YDA for typing"
        self.nextid += 1
        self.alltext[self.nextid] = Text(text, color, x, y, size, time=time, identifier=identifier)
        return self.nextid

    def removeText(self, id: int) -> None:
        self.alltext.pop(id)

    def setupText(self) -> None:
        size = TILEHEIGHT
        self.alltext[SCORETXT] = Text("0".zfill(8), WHITE, 0, TILEHEIGHT, size)
        self.alltext[LEVELTXT] = Text(str(1).zfill(3), WHITE, 23 * TILEWIDTH, TILEHEIGHT, size)
        self.alltext[READYTXT] = Text("READY!", YELLOW, 11.25 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False)
        self.alltext[PAUSETXT] = Text("PAUSED!", YELLOW, 10.625 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False)
        self.alltext[GAMEOVERTXT] = Text("GAMEOVER!", YELLOW, 10 * TILEWIDTH, 20 * TILEHEIGHT, size, visible=False)
        self.addText("SCORE", WHITE, 0, 0, size)
        self.addText("LEVEL", WHITE, 23 * TILEWIDTH, 0, size)

    def update(self, dt: float) -> None:
        for tkey in list(self.alltext.keys()):
            self.alltext[tkey].update(dt)
            if self.alltext[tkey].destroy:
                self.removeText(tkey)

    def showText(self, id: int) -> None:
        self.hideText()
        self.alltext[id].visible = True

    def hideText(self) -> None:
        self.alltext[READYTXT].visible = False
        self.alltext[PAUSETXT].visible = False
        self.alltext[GAMEOVERTXT].visible = False

    def updateScore(self, score: int) -> None:
        self.updateText(SCORETXT, str(score).zfill(8))

    def updateLevel(self, level: int) -> None:
        self.updateText(LEVELTXT, str(level + 1).zfill(3))

    def updateText(self, id: int, value: str) -> None:
        if id in self.alltext.keys():
            self.alltext[id].setText(value)

    def render(self, screen: pygame.surface.Surface) -> None:
        for tkey in list(self.alltext.keys()):
            self.alltext[tkey].render(screen)
