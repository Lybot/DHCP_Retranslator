# -*- coding: utf-8 -*-
import sys
from socket import *
import os
import subprocess as sp
from multiprocessing import Process
from threading import Thread

from ParsePacket import *
import time as t
import random
#функция выполнения команды в оболочке


def exec_com(command_string):
    p = sp.Popen(command_string, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
    out, err = str(p.stdout.read()), str(p.stderr.read())
    return out, err #возвращает вывод оболочки и ошибку


class Lceo:
    def sniff_from_output_int(self):
        while True:
            try:
                packet = self.so.recv(4000)
                if packet:
                    parse_packet = ParsePacket(packet)
                    if len(parse_packet) > 1514:
                        continue
                    else:
                        if self.response:
                            self.response = False
                            parse_packet.change_mac(self.current_pc_link[0]["mac"], self.current_pc_link[1]["mac"])
                            parse_packet.change_ip(self.current_pc_link[0]["ip"], self.current_pc_link[1]["ip"])
                            self.so.send(parse_packet.str_packet)
                        else:
                            self.response = True
                            parse_packet.change_mac(self.current_pc_link[1]["mac"], self.current_pc_link[0]["mac"])
                            parse_packet.change_ip(self.current_pc_link[1]["ip"], self.current_pc_link[0]["ip"])
                            self.so.send(parse_packet.str_packet)
            except KeyboardInterrupt:
                sys.exit(1)

    def set_pc_list(self, pc_list):
        self.pc_list = pc_list

    def time_process(self):
        while True:
            try:
                t.sleep(1)
                self.current_pc_link = self.pc_list[random.randint(0, self.pc_list.__len__()-1)]
            except KeyboardInterrupt:
                sys.exit(1)

    def __init__(self, pc_list):
        self.response = False
        self.pc_list = pc_list
        self.current_pc_link = self.pc_list[random.randint(0, self.pc_list.__len__())]
        self.so = socket(AF_PACKET, SOCK_RAW)
        self.so.bind(('eth0', 0x0800, PACKET_OTHERHOST))
        self.sniff_from_output = Thread(target=self.sniff_from_output_int)
        self.sniff_from_output.start()
        self.change_link_process = Thread(target=self.time_process)
        self.change_link_process.start()
        # while True:
        #     try:
        #         print("works")
        #         time.sleep(10)
        #     except KeyboardInterrupt:
        #         sys.exit(1)