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
        self.add_handlers({
            curses.ascii.NL: self.show_peer_info,
            curses.ascii.CR: self.show_peer_info
        })
    
    def show_peer_info(self, h):
        peer = self.values[self.edit_cell[0]][3]
        peer_obj = self.fastd_data["peers"][peer]
        if peer_obj["connection"]:
            message = ""
            message += "Pubkey: {0}\n".format(str(peer))
            message += "Name: {0}\n".format(str(peer_obj["name"]))
            message += "Address: {0}\n".format(str(peer_obj["address"]))
            message += "MAC-Addresses: {0}\n".format(str(peer_obj["connection"]["mac_addresses"]))
            message += "Connected since: {0}\n".format(str(datetime.timedelta(milliseconds=int(peer_obj["connection"]["established"]))))
            message += "Method: {0}\n".format(str(peer_obj["connection"]["method"]))
            message += "\nConnection Stats\n"
            message += "RX packets: {0}\n".format(str(peer_obj["connection"]["statistics"]["rx"]["packets"]))
            message += "RX bytes: {0}\n".format(str(peer_obj["connection"]["statistics"]["rx"]["bytes"]))
            message += "RX reordered packets: {0}\n".format(str(peer_obj["connection"]["statistics"]["rx_reordered"]["packets"]))
            message += "RX reordered bytes: {0}\n".format(str(peer_obj["connection"]["statistics"]["rx_reordered"]["bytes"]))
            message += "TX packets: {0}\n".format(str(peer_obj["connection"]["statistics"]["tx"]["packets"]))
            message += "TX bytes: {0}\n".format(str(peer_obj["connection"]["statistics"]["tx"]["bytes"]))
            message += "TX dropped packets: {0}\n".format(str(peer_obj["connection"]["statistics"]["tx_dropped"]["packets"]))
            message += "TX dropped bytes: {0}\n".format(str(peer_obj["connection"]["statistics"]["tx_dropped"]["bytes"]))
            message += "TX error packets: {0}\n".format(str(peer_obj["connection"]["statistics"]["tx_error"]["packets"]))
            message += "TX error bytes: {0}\n".format(str(peer_obj["connection"]["statistics"]["tx_error"]["bytes"]))
            npyscreen.notify_confirm(message, title="Peer Information", form_color='STANDOUT', wrap=False, wide=False, editw=0)

class FastdTop(npyscreen.NPSAppManaged):
    def onStart(self):
        self.keypress_timeout_default = 10
        self.addForm("MAIN",       MainScreen, name="FastdTop v0.1")
        self.fastd_data = {}
        self.currentform = None
    
    def while_waiting(self):
        self.client = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )
        try:
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
        except:
            pass
    
    def onCleanExit(self):
        if self.client:
            self.client.close()
        
    
    def change_form(self, name):
        self.switchForm(name)
        self.resetHistory()

class MainScreen(npyscreen.ActionFormMinimal):
    OK_BUTTON_TEXT = "EXIT"
    def create(self):
        self.keypress_timeout_default = 10
        self.add(npyscreen.TitleFixedText, name = "Server Socket:", value=args['socket'], begin_entry_at=32)
        self.uptime = self.add(npyscreen.TitleFixedText, name = "Uptime:" , value="", begin_entry_at=32)
        self.peers = self.add(npyscreen.TitleFixedText, name = "Known Peers:" , value="", begin_entry_at=32)
        self.conn_peers = self.add(npyscreen.TitleFixedText, name = "Connected Peers:" , value="", begin_entry_at=32)
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
        self.add(npyscreen.FixedText, value = "Press ENTER on peer(s) to get more information", begin_entry_at=1, rely=18)
        self.clientsbox = self.add(ClientList, relx = 1, rely=19, column_width=32, select_whole_line = True, col_titles = ['Peers','IP-Address','Main MAC-Address','PubKey (Truncated)'])
        self.clientsbox.values = []
    
    def while_waiting(self):
        if self.parentApp.fastd_data:
            self.uptime.value = str(datetime.timedelta(milliseconds=int(self.parentApp.fastd_data["uptime"]))) 
            self.peers.value = str(len(self.parentApp.fastd_data["peers"]))
            self.rxpkts.value = str(self.parentApp.fastd_data["statistics"]["rx"]["packets"])
            self.rxbytes.value = str(self.parentApp.fastd_data["statistics"]["rx"]["bytes"])
            self.rxropkts.value = str(self.parentApp.fastd_data["statistics"]["rx_reordered"]["packets"])
            self.rxrobytes.value = str(self.parentApp.fastd_data["statistics"]["rx_reordered"]["bytes"])
            self.txpkts.value = str(self.parentApp.fastd_data["statistics"]["tx"]["packets"])
            self.txbytes.value = str(self.parentApp.fastd_data["statistics"]["tx"]["bytes"])
            self.txdpdpkts.value = str(self.parentApp.fastd_data["statistics"]["tx_dropped"]["packets"])
            self.txdpdbytes.value = str(self.parentApp.fastd_data["statistics"]["tx_dropped"]["bytes"])
            self.txerrpkts.value = str(self.parentApp.fastd_data["statistics"]["tx_error"]["packets"])
            self.txerrbytes.value = str(self.parentApp.fastd_data["statistics"]["tx_error"]["bytes"])
            
                        
            rows = []
            peer_counter = 1
            connected_peers = 0
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
                    connected_peers +=1
                    if peer_obj["connection"]["mac_addresses"]:
                        row.append(str(peer_obj["connection"]["mac_addresses"][0]))
                    else:
                        row.append('No MAC-Address found')
                else:
                    row.append('No connection info')
                row.append(str(peer))
                rows.append(row)
                peer_counter += 1
            self.clientsbox.values = rows
            self.clientsbox.fastd_data = self.parentApp.fastd_data
            self.conn_peers.value = str(connected_peers)
        self.uptime.display()
        self.peers.display()
        self.conn_peers.display()
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

