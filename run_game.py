#! /usr/bin/env python

import sys
sys.path.append('libs')

import pygame
import pygame.font
import pygame.gfxdraw  # Required by gfxdraw module


if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption('Balancer Of Circles')
    #screen = pygame.display.set_mode((800, 600))
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    # Needs to be done her, because boc.* assumes that pygame.display is set
    from boc.game import Game
    from boc.music import music_mgr

    music_mgr.play_background_music()
    Game(screen).run()
