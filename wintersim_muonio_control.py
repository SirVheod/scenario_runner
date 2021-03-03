#!/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""
Welcome to WinterSim Muonio control.

Use ARROWS or WASD keys for control.

    W            : throttle
    S            : brake
    A/D          : steer left/right
    Q            : toggle reverse
    Space        : hand-brake
    P            : toggle autopilot
    M            : toggle manual transmission
    ,/.          : gear up/down
    CTRL + W     : toggle constant velocity mode at 60 km/h

    L            : toggle next light type
    SHIFT + L    : toggle high beam
    Z/X          : toggle right/left blinker
    I            : toggle interior light

    TAB          : change sensor position
    ` or N       : next sensor
    [1-9]        : change to sensor [1-9]
    G            : toggle radar visualization
    C            : change weather (Shift+C reverse)
    Backspace    : change vehicle

    V            : Select next map layer (Shift+V reverse)
    B            : Load current selected map layer (Shift+B to unload)

    R            : toggle recording images to disk

    CTRL + R     : toggle recording of simulation (replacing any previous)
    CTRL + P     : start replaying last recorded simulation
    CTRL + +     : increments the start time of the replay by 1 second (+SHIFT = 10 seconds)
    CTRL + -     : decrements the start time of the replay by 1 second (+SHIFT = 10 seconds)

    F1           : toggle HUD
    H/?          : toggle help
    ESC          : quit
"""

from __future__ import print_function

# ==============================================================================
# -- imports -------------------------------------------------------------------
# ==============================================================================

import carla

# These are required
from WinterSim.wintersim_sensors import CollisionSensor, LaneInvasionSensor, GnssSensor, IMUSensor
from WinterSim.wintersim_scenario_control import World, KeyboardControl, CameraManager
from WinterSim.wintersim_hud import HUD_WINTERSIM as HUD
from WinterSim.wintersim_hud import Weather

import os
import argparse
import logging
import time
import pygame

# ==============================================================================
# -- Global functions ----------------------------------------------------------
# ==============================================================================

def get_actor_display_name(actor, truncate=250):
    name = ' '.join(actor.type_id.replace('_', '.').title().split('.')[1:])
    return (name[:truncate - 1] + u'\u2026') if len(name) > truncate else name

# ==============================================================================
# -- game_loop() ---------------------------------------------------------------
# ==============================================================================

def game_loop(args):
    pygame.init()
    pygame.font.init()
    world = None

    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(2.0)

        display = pygame.display.set_mode(
            (args.width, args.height),
            pygame.HWSURFACE | pygame.DOUBLEBUF)

        hud = HUD(args.width, args.height, display)
        hud.make_sliders()
        world = World(client.get_world(), hud, args)
        controller = KeyboardControl(world, args.autopilot)

        clock = pygame.time.Clock()

        world.preset = world._weather_presets[0]                            # start weather preset
        hud.update_sliders(world.preset[0])                                 # update sliders to positions according to preset
        controller = KeyboardControl(world, args.autopilot)
        weather = Weather(client.get_world().get_weather())

        world.camera_manager.specific_camera_angle(1)                        # change camera angle
        #world.specific_weather_preset(20)                                   # change to specific weather preset for testing

        friction = float(args.fr)
        if friction != 2.0:
            # If friction is not 2.0 (default), Update vehicle wheel physics
            world.update_frictionDirectly(friction)

        # constant_velocity = bool(args.c)
        # if constant_velocity:
        #     # If --c argument given, enable constant velocity
        #     world.player.enable_constant_velocity(carla.Vector3D(7, 0, 0))
        #     world.constant_velocity_enabled = True

        while True:
            clock.tick_busy_loop(60)
            if controller.parse_events(client, world, clock, hud):
                return
            world.tick(clock, hud)
            world.render(display)

            if hud.is_hud:
                for s in hud.sliders: 
                    if s.hit:                                           # if slider is being touched
                        s.move()                                        # move slider
                        weather.tick(hud, world.preset[0])              # update weather object
                        client.get_world().set_weather(weather.weather) # send weather
                for s in hud.sliders:
                    s.draw(display, s)
                    
            pygame.display.flip()

    finally:
        #if (world and world.recording_enabled):
            #client.stop_recorder()

        if world is not None:
            world.destroy()

        pygame.quit()

# ==============================================================================
# -- main() --------------------------------------------------------------------
# ==============================================================================

def main():
    argparser = argparse.ArgumentParser(
        description='CARLA Manual Control Client')
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='debug',
        help='print debug information')
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-a', '--autopilot',
        action='store_true',
        help='enable autopilot')
    argparser.add_argument(
        '--res',
        metavar='WIDTHxHEIGHT',
        default='1280x720',
        help='window resolution (default: 1280x720)')

    # WinterSim added argument
    argparser.add_argument(
        '--fr',
        metavar='Friction',
        default='2.0',
        help='Friction value (Default: 2.0)')

    # WinterSim added argument
    argparser.add_argument(
        '--c',
        action='store_true',
        help='enable constant velocity')

    args = argparser.parse_args()

    args.rolename = 'hero'      # Needed for CARLA version
    args.filter = "vehicle.*"   # Needed for CARLA version
    args.gamma = 2.2            # Needed for CARLA version
    args.width, args.height = [int(x) for x in args.res.split('x')]

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    logging.info('listening to server %s:%s', args.host, args.port)
    print(__doc__)

    try:
        game_loop(args)

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')
    except Exception as error:
        logging.exception(error)

if __name__ == '__main__':
    main()