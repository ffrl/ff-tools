#!/usr/bin/env python2
# By CyrusFox <cyrus at lambdacore.de>
import npyscreen, curses
import socket
import sys
import os
import json
import datetime
import argparse

class ClientList(npyscreen.GridColTitles):
    def __init__(self, *args, **keywords):
        super(ClientList, self).__init__(*args, **keywords)
    
    def set_up_handlers(self):
        super(ClientList, self).set_up_handlers()
        self.handlers = {
                    curses.ascii.NL:   self.show_peer_info,
                    curses.ascii.CR:   self.show_peer_info,
                    curses.KEY_UP:      self.h_move_line_up,
                    curses.KEY_LEFT:    self.h_move_cell_left,
                    curses.KEY_DOWN:    self.h_move_line_down,
                    curses.KEY_RIGHT:   self.h_move_cell_right,
                    "k":                self.h_move_line_up,
                    "h":                self.h_move_cell_left,
                    "j":                self.h_move_line_down,
                    "l":                self.h_move_cell_right,
                    curses.KEY_NPAGE:   self.h_move_page_down,
                    curses.KEY_PPAGE:   self.h_move_page_up,
                    curses.KEY_HOME:    self.h_show_beginning,
                    curses.KEY_END:     self.h_show_end,
                    ord('g'):           self.h_show_beginning,
                    ord('G'):           self.h_show_end,
                    curses.ascii.TAB:   self.h_exit,
                    '^P':               self.h_exit_up,
                    '^N':               self.h_exit_down,
                    #curses.ascii.NL:    self.h_exit,
                    #curses.ascii.SP:    self.h_exit,
                    #ord('x'):       self.h_exit,
                    ord('q'):       self.h_exit,
                    curses.ascii.ESC:   self.h_exit,
                    curses.KEY_MOUSE:    self.h_exit_mouse,
                }
        
        self.complex_handlers = [
                    ]
    
    def show_peer_info(self, h):
        peer = self.values[self.edit_cell[0]][3]
        peer_obj = self.fastd_data["peers"][peer]
        if peer_obj["connection"]:
            message = """Pubkey: {0}
Name: {1}
Address: {2}
MAC-Addresses: {3}
Connected since: {4}
Method: {5}

Connection Stats
RX packets: {6}
RX bytes: {7}
RX reordered packets: {8}
RX reordered bytes: {9}
TX packets: {10}
TX bytes: {11}
TX dropped packets: {12}
TX dropped bytes: {13}
TX error packets: {14}
TX error bytes: {15}""".format(str(peer), peer_obj["name"], peer_obj["address"], str(peer_obj["connection"]["mac_addresses"]), str(datetime.timedelta(milliseconds=int(peer_obj["connection"]["established"]))), peer_obj["connection"]["method"], peer_obj["connection"]["statistics"]["rx"]["packets"], peer_obj["connection"]["statistics"]["rx"]["bytes"], peer_obj["connection"]["statistics"]["rx_reordered"]["packets"], peer_obj["connection"]["statistics"]["rx_reordered"]["packets"], peer_obj["connection"]["statistics"]["rx_reordered"]["bytes"], peer_obj["connection"]["statistics"]["tx"]["packets"], peer_obj["connection"]["statistics"]["tx"]["bytes"], peer_obj["connection"]["statistics"]["tx_dropped"]["packets"], peer_obj["connection"]["statistics"]["tx_dropped"]["bytes"], peer_obj["connection"]["statistics"]["tx_error"]["packets"], peer_obj["connection"]["statistics"]["tx_error"]["bytes"])
            npyscreen.notify_confirm(message, title="Client View", form_color='STANDOUT', wrap=False, wide=False, editw=0)

class FastdTop(npyscreen.NPSAppManaged):
    def onStart(self):
        self.keypress_timeout_default = 10
        self.addForm("MAIN",       MainScreen, name="FastdTop v0.1")
        self.fastd_data = {}
        self.currentform = None
    
    def while_waiting(self):
        self.client = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )
        self.client.connect(args['socket'])
        total_data=[]
        while True:
            data = self.client.recv(8192)
            if not data: break
            total_data.append(data)
        json_string = ''.join(total_data)
        try:
            self.fastd_data = json.loads(json_string.decode('utf-8'))
        except:
            pass
        self.client.close()
    
    def onCleanExit(self):
        if self.client:
            self.client.close()
        
    
    def change_form(self, name):
        self.switchForm(name)
        self.resetHistory()

class MainScreen(npyscreen.ActionFormMinimal):
    def create(self):
        self.keypress_timeout_default = 10
        self.add(npyscreen.TitleText, name = "Server Socket:", value=args['socket'], begin_entry_at=32)
        self.uptime = self.add(npyscreen.TitleFixedText, name = "Uptime:" , value="", begin_entry_at=32)
        self.clients = self.add(npyscreen.TitleFixedText, name = "Configured Peers:" , value="", begin_entry_at=32)
        self.conn_clients = self.add(npyscreen.TitleFixedText, name = "Connected Peers:" , value="Not implemented yet", begin_entry_at=32)
        self.rxpkts = self.add(npyscreen.TitleFixedText, name = "RX packets:" , value="", begin_entry_at=32)
        self.rxbytes = self.add(npyscreen.TitleFixedText, name = "RX bytes:" , value="", begin_entry_at=32)
        self.rxropkts = self.add(npyscreen.TitleFixedText, name = "RX reordered packets:" , value="", begin_entry_at=32)
        self.rxrobytes = self.add(npyscreen.TitleFixedText, name = "RX reordered bytes:" , value="", begin_entry_at=32)
        self.txpkts = self.add(npyscreen.TitleFixedText, name = "TX packets:" , value="", begin_entry_at=32)
        self.txbytes = self.add(npyscreen.TitleFixedText, name = "TX bytes:" , value="", begin_entry_at=32)
        self.txdpdpkts = self.add(npyscreen.TitleFixedText, name = "TX dropped packets:" , value="", begin_entry_at=32)
        self.txdpdbytes = self.add(npyscreen.TitleFixedText, name = "TX dropped bytes:" , value="", begin_entry_at=32)
        self.txerrpkts = self.add(npyscreen.TitleFixedText, name = "TX error packets:" , value="", begin_entry_at=32)
        self.txerrbytes = self.add(npyscreen.TitleFixedText, name = "TX error bytes:" , value="", begin_entry_at=32)
        self.clientsbox = self.add(ClientList, relx = 1, rely=18, column_width=32, select_whole_line = True, col_titles = ['Client','IP-Address','Main MAC-Address','PubKey (Truncated)'])
        self.clientsbox.values = []
    
    def while_waiting(self):
        if self.parentApp.fastd_data:
            self.uptime.value = str(datetime.timedelta(milliseconds=int(self.parentApp.fastd_data["uptime"]))) 
            self.clients.value = len(self.parentApp.fastd_data["peers"])
            self.rxpkts.value = self.parentApp.fastd_data["statistics"]["rx"]["packets"]
            self.rxbytes.value = self.parentApp.fastd_data["statistics"]["rx"]["bytes"]
            self.rxropkts.value = self.parentApp.fastd_data["statistics"]["rx_reordered"]["packets"]
            self.rxrobytes.value = self.parentApp.fastd_data["statistics"]["rx_reordered"]["bytes"]
            self.txpkts.value = self.parentApp.fastd_data["statistics"]["tx"]["packets"]
            self.txbytes.value = self.parentApp.fastd_data["statistics"]["tx"]["bytes"]
            self.txdpdpkts.value = self.parentApp.fastd_data["statistics"]["tx_dropped"]["packets"]
            self.txdpdbytes.value = self.parentApp.fastd_data["statistics"]["tx_dropped"]["bytes"]
            self.txerrpkts.value = self.parentApp.fastd_data["statistics"]["tx_error"]["packets"]
            self.txerrbytes.value = self.parentApp.fastd_data["statistics"]["tx_error"]["bytes"]
            
            
            rows = []
            peer_counter = 1
            for peer in self.parentApp.fastd_data["peers"]:
                peer_obj = self.parentApp.fastd_data["peers"][peer]
                row = []
                if peer_obj["name"]:
                    name = """{0}. {1}""".format(str(peer_counter), str(peer_obj["name"]))
                    row.append(name)
                else:
                    name = """{0}. {1}""".format(str(peer_counter), 'No name set')
                    row.append(name)
                row.append(str(peer_obj["address"]))
                if peer_obj["connection"]:
                    row.append(str(peer_obj["connection"]["mac_addresses"][0]))
                else:
                    row.append('Not connected')
                row.append(str(peer))
                rows.append(row)
                peer_counter += 1
            self.clientsbox.values = rows
            self.clientsbox.fastd_data = self.parentApp.fastd_data
        self.uptime.display()
        self.clients.display()
        self.conn_clients.display()
        self.rxpkts.display()
        self.rxbytes.display()
        self.rxropkts.display()
        self.rxrobytes.display()
        self.txpkts.display()
        self.txbytes.display()
        self.txdpdpkts.display()
        self.txdpdbytes.display()
        self.txerrpkts.display()
        self.txerrbytes.display()
        self.clientsbox.display()
        
    def on_ok(self):
        self.parentApp.switchForm(None)
    
    def change_forms(self, *args, **keywords):
        if self.name == "FastdTop":
            screen_name = "MAIN"
        self.parentApp.change_form(screen_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--socket', help='Fastd socket file', required=True)
    args = vars(parser.parse_args())
    App = FastdTop()
    App.run()

