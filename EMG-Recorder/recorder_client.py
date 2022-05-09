from time import time, sleep, strftime, localtime
from brainflow.board_shim import BoardShim, BrainFlowInputParams
import sys, random, threading, datetime
import numpy as np
import pandas as pd
import argparse, socket, pickle

# Variables to change parameters of the test
BOARDID = 0 #cyton 8ch
START_DELAY = 20 # 20 Seconds
REC_TIME = 5 

def record_procedure(stop, board, args):
   
    start_time = time()

    board.start_stream(450000, args)
    sleep(1)

    # board.insert_marker(0.666) # insert marker api call for future reference
    
    for x in range(int(REC_TIME)):
        sleep(1)

  
    data = board.get_board_data().transpose()[:,1:9]
    board.stop_stream()
    
    # print(data)
    # print(np.shape(data))
    # print(data[1])
    # print(np.shape(data[1]))
    # print(len(data))
  
    # Create header row
    header = []
    for i in range(1, 9):
        # if i == 1:
        #     header.append('Time') 
        # else:
            header.append('CH{}'.format(i))

    data = pd.DataFrame(data, columns=header)
    data.to_csv("EMG-Recorder/Recordings/" + filename + ".csv", index=False)
    Cyton_Board_End(board)



def Cyton_Board_Config(purpose):
    
    BoardShim.enable_dev_board_logger()

    parser = argparse.ArgumentParser()
    # use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
    parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False, default=0)
    parser.add_argument('--ip-port', type=int, help='ip port', required=False, default=0)
    parser.add_argument('--ip-protocol', type=int, help='ip protocol, check IpProtocolType enum', required=False, default=0)
    parser.add_argument('--ip-address', type=str, help='ip address', required=False, default='')
    parser.add_argument('--serial-port', type=str, help='serial port', required=False, default='')
    parser.add_argument('--mac-address', type=str, help='mac address', required=False, default='')
    parser.add_argument('--other-info', type=str, help='other info', required=False, default='')
    parser.add_argument('--streamer-params', type=str, help='streamer params', required=False, default='')
    parser.add_argument('--serial-number', type=str, help='serial number', required=False, default='')
    parser.add_argument('--board-id', type=int, help='board id, check docs to get a list of supported boards', required=True)
    parser.add_argument('--file', type=str, help='file', required=False, default='')
    args = parser.parse_args()

    params = BrainFlowInputParams()
    params.ip_port = args.ip_port
    params.serial_port = args.serial_port
    params.mac_address = args.mac_address
    params.other_info = args.other_info
    params.serial_number = args.serial_number
    params.ip_address = args.ip_address
    params.ip_protocol = args.ip_protocol
    params.timeout = args.timeout
    params.file = args.file
    
    # Cyton Board Object
    board = BoardShim(args.board_id, params)

    # Start Acquisition
    board.prepare_session()

    # if purpose=true we're running the whole thing
    # else we're just running the demo
    if purpose:
        board.start_stream(45000, args.streamer_params)
        return board
    else:
        return [board, args.streamer_params]

def Cyton_Board_End(board):
    board.release_session()
    return

if __name__ == '__main__':
    # File config
    x = datetime.datetime.now()

    global filename 
    filename = "bruh"
    filename =  f"{x.strftime('%j')}_{x.strftime('%Y')}_{x.strftime('%f')}" #day of year, year, millisecond
    
    # BCI Config
    board_details = Cyton_Board_Config(False)

    global testing
    testing = False
    stopThread = False
    x = threading.Thread(target=record_procedure, args=(lambda: stopThread, board_details[0], board_details[1]))
    x.start()

    