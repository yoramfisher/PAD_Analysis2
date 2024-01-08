import sys
import time
import socket
import select
epics_cmd_port = 10030
epics_address = "192.168.11.120"

class DV_Wrapper:
    def __init__(self):
        self.default_type = 'd'
        self.cmd_count = 0;

    # Doesn't look like you can do this
    #def wrap_set(self, command, val, data_type = self.default_type):
    #    print("setpv<{}>:{}:{}".format(data_type, command, val));

    def wrap_set2(self, command, val, data_type = None):
        #The default None value lets us see if the parameter was specified in the call.
        if data_type is None:
            data_type = self.default_type;

        out_str = "#{}:setpv<{}>:{}:{}\r\n".format(self.cmd_count, data_type, command, val);
        self.cmd_count = self.cmd_count + 1;
        return out_str;

    def wrap_get2(self, command, data_type = None):
        if data_type is None:
            data_type = self.default_type;

        out_str = "#{}:getpv<{}>:{}?\r\n".format(self.cmd_count, data_type, command);
        self.cmd_count += 1;
        return out_str;

    def parse_cmd(self, cmd_tup):
        data_type = None;
        if (cmd_tup[0] == 's'): # A set command
            cmd_name = cmd_tup[1];
            cmd_val = cmd_tup[2];
            if (len(cmd_tup) == 4):
                data_type = cmd_tup[3];
            return self.wrap_set2(cmd_name, cmd_val, data_type);
        elif (cmd_tup[0] == 'g'): # A get command
            cmd_name = cmd_tup[1];
            if (len(cmd_tup) == 3):
                data_type = cmd_tup[2];
            return self.wrap_get2(cmd_name, data_type);
        elif (cmd_tup[0] == 'b'): # A busy polling command -- wrapped as a get
            cmd_name = cmd_tup[1];
            if (len(cmd_tup) == 3):
                data_type = cmd_tup[2];
            return self.wrap_get2(cmd_name, data_type);
        else:                   # An unrecognized type
            print("Unrecognized command entry: {}".format(cmd_tup));
            return '';


def sendCommand(currSocket, currStr, timeout = 0.5):
    print("Sending command: {}".format(currStr));
    bytes_sent = currSocket.send(currStr.encode());
    print("Command sent -- total bytes: {}".format(bytes_sent));
    read_list, write_list, err_list = select.select([currSocket], [], [], timeout);
    if (len(read_list) == 0):
        print("No read data.");
        return -1;
    epics_response = currSocket.recv(4096);
    print("Response: {}".format(epics_response.decode()));
    return epics_response.decode();


def main(argv):

    epics_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    epics_socket.connect((epics_address, epics_cmd_port))

    myWrapper = DV_Wrapper()
    sendCommand(epics_socket, myWrapper.wrap_set2("Exposure", 25.0))
    sendCommand(epics_socket, myWrapper.wrap_set2("CaptureMode", 0))
    sendCommand(epics_socket, myWrapper.wrap_set2("q2c_SetFileName", "./yourMOM.raw", "s"))
    sendCommand(epics_socket, myWrapper.wrap_set2("NImages", 25))
    sendCommand(epics_socket, myWrapper.wrap_set2("actionCapture", 1))
   


   
# #
# #
# #
if __name__ == "__main__":


   main(sys.argv[1:])