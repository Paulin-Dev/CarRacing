#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Built-in imports
from os import system, get_terminal_size
from platform import system as getOS
from random import random, shuffle
from sys import exit as sys_exit
from sys import stdout
from threading import Thread
from time import sleep, perf_counter


# Constants
TERMINAL_WIDTH      = get_terminal_size().columns
TERMINAL_HEIGHT     = get_terminal_size().lines
CAR_WIDTH           = 33
CAR_HEIGHT          = 6

END_WIDTH           = TERMINAL_WIDTH-CAR_WIDTH+2

TOP_LEFT_CORNER     = b'\xe2\x94\x8c'.decode()
TOP_RIGHT_CORNER    = b'\xe2\x94\x90'.decode()
BOTTOM_LEFT_CORNER  = b'\xe2\x94\x94'.decode()
BOTTOM_RIGHT_CORNER = b'\xe2\x94\x98'.decode()

HORIZONTAL_BAR      = b'\xe2\x94\x80'.decode()
VERTICAL_BAR        = b'\xe2\x94\x82'.decode()

FULL_BLOCK          = b'\xe2\x96\x88'.decode()

RED                 = '\33[31m'
GREEN               = '\33[32m'
YELLOW              = '\33[33m'
BLUE                = '\33[34m'
PURPLE              = '\33[35m'
RESET               = '\33[0m'


# typing
class Car: pass


class Display:
    def move(self, x: int, y: int) -> None:
        stdout.write(f'\033[{y};{x}H')

    def hide_cursor(self) -> None:
        stdout.write('\033[?25l')

    def show_cursor(self) -> None:
        stdout.write('\033[?25h')


class Game(Display):
    def __init__(self, cars_number: int, laps: int) -> None:
        self.__result      = []
        self.__cars_number = cars_number
        self.laps          = laps

    def display_finish_line(self) -> None:
        for i in range(TERMINAL_HEIGHT):
            self.move(TERMINAL_WIDTH-5, i)
            if i % 2 == 0:
                stdout.write(f'{FULL_BLOCK*2}  {FULL_BLOCK*2}')
            else:
                stdout.write(f'  {FULL_BLOCK*2}  ')

    def display_podium(self) -> None:
        # width: 20
        self.move((TERMINAL_WIDTH//2)-10, TERMINAL_HEIGHT-(4+self.__cars_number))
        stdout.write(TOP_LEFT_CORNER + HORIZONTAL_BAR*20 + TOP_RIGHT_CORNER)
        for index, (car, time) in enumerate(self.__result):
            self.move((TERMINAL_WIDTH//2)-10, TERMINAL_HEIGHT-(2+self.__cars_number)+index )
            stdout.write(f'{f"Car {car.car_number} : {round(time, 3)}":^22}')
        self.move((TERMINAL_WIDTH//2)-10, TERMINAL_HEIGHT-(1))
        stdout.write(BOTTOM_LEFT_CORNER + HORIZONTAL_BAR*20 + BOTTOM_RIGHT_CORNER)

    def is_over(self) -> bool:
        return len(self.__result) == self.__cars_number

    def add_car(self, car: Car, time: float) -> None:
        self.__result.append((car, time))


class Car(Thread, Display):
    def __init__(self, car_number: int, y: int, game: Game, color: str) -> None:
        super().__init__(daemon=True)

        if not 0 <= car_number <= 9:
            raise ValueError('Incorrect car number!')
        else:
            self.car_number = car_number
        
        self.__car = [
            "   -           __                ",
            " --          ~( @\   \           ",
            "---   _________]_[__/_>________  ",
        f"     /  ____ \ <>  {car_number}  |  ____  \ ",
            "    =\_/ __ \_\_______|_/ __ \__D",
            "        (__)             (__)    "
        ]
        self.__x        = 0
        self.__y        = y
        self.__start    = None
        self.__game     = game
        self.__overflow = 0       

    def __erase(self) -> None:
        for i in range(len(self.__car)):
            if self.__overflow == 0:
                self.move(self.__x-(1 if self.__x > 0 else 0), self.__y+i)
                stdout.write(' '*CAR_WIDTH)
            else:
                self.move(self.__x-(1 if self.__x > 0 else 0), self.__y+i)
                stdout.write(' '*(self.__x))
                self.move(self.__overflow-1, self.__y+i)
                stdout.write(' '*(CAR_WIDTH-self.__x+2))

    def __display(self) -> None:
        if self.__start is None:
            self.__start = perf_counter()
            
        if self.__overflow > 0:
            if self.__overflow >= TERMINAL_WIDTH:
                self.__overflow -= 1
                self.__erase()
                self.__overflow = 0
                self.__x = 0
            else:
                self.__overflow += 1
        
        if self.__x >= END_WIDTH:
            self.__overflow = self.__x
            self.__x = 0
        
        self.__erase()
        
        for index, line in enumerate(self.__car):
            if self.__overflow == 0:
                self.move(self.__x, self.__y+index)
                stdout.write(f'{line}\n')
            else:
                self.move(0, self.__y+index)
                stdout.write(f'{line[len(line)-self.__x:]}\n')
                self.move(self.__overflow, self.__y+index)
                stdout.write(f'{line[:len(line)-self.__x]}\n')

    def __forward(self) -> None:
        self.__x += 1
        try:
            sleep(random()*3 / 100)
        except KeyboardInterrupt:
            sys_exit(1)

    def run(self) -> None:
        for lap in range(self.__game.laps):
            for i in range(TERMINAL_WIDTH+2):
                if lap+1 == self.__game.laps:
                    if i == 0:
                        self.__game.display_finish_line()
                    elif self.__x >= END_WIDTH:
                        break
                self.__display()
                self.__forward()
            
        self.__game.add_car(self, perf_counter()-self.__start)


def main(cars_number: int) -> None:
    if getOS() == 'Windows':
        system('cls')
    else:
        system('clear')

    if cars_number < 2:
        raise ValueError('You need at least 2 cars to start a race!')
    
    nb = 0
    for i in range(cars_number):
        if 4 + nb*CAR_HEIGHT + (nb-(1 if nb > 0 else 0))*9 + CAR_HEIGHT+9 <= TERMINAL_HEIGHT-1:
            nb += 1
    
    game = Game(nb, 3)
    
    display = Display()
    display.hide_cursor()
    
    colors = [RED, GREEN, BLUE, YELLOW, PURPLE]
    shuffle(colors)

    for car in range(nb):
        Car(car_number=car, y=5+15*car, game=game, color=colors[car]).start()
        
    try:
        while not game.is_over():
            sleep(.5)
        game.display_podium()
    except KeyboardInterrupt:
        pass
    finally:
        display.move(0, TERMINAL_HEIGHT)
        display.show_cursor()


if __name__ == '__main__':
    main(4)