from time import time, sleep, strftime, localtime
from brainflow.board_shim import BoardShim, BrainFlowInputParams
import sys, random, threading, datetime
import numpy as np
import pandas as pd
import argparse
import keyboard

# Variables to change parameters of the test
BOARDID = 0 #cyton 8ch
REC_TIME = 2000

def csv_export(data):

    # useful prints for debugging 
    # print(data)
    # print(np.shape(data))
    # print(data[1])
    # print(np.shape(data[1]))
    # print(len(data))


    # Create header row
    header = []
    for i in range(1, 10):
        if i == 9:
            header.append('Time') 
        else:
            header.append('CH{}'.format(i))

    #getting rid of useless data channels
    data_del = np.delete(data, slice(8, 21), 1)
    data = data_del

    #convert to pandas dataframe
    data = pd.DataFrame(data, columns=header)

    #rearange col format
    data = data[['Time', 'CH1', 'CH2', 'CH3', 'CH4', 'CH5', 'CH6', 'CH7', 'CH8']]

    #convert dataframe to csv
    data.to_csv("EMG-Recorder/Recordings/" + filename + ".csv", index=False)

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
        board.start_stream(450000, args.streamer_params)
        return board
    else:
        return [board, args.streamer_params]

def Cyton_Board_End(board):
    board.release_session()
    return


def record(stop, board, args):
    start_time = time()
    
    board.start_stream(450000, args)
    sleep(1)

    for x in range(int(REC_TIME)):
        sleep(1)
        if keyboard.is_pressed('q'):
            break
  
    data = board.get_board_data().transpose()[:,1:23] #kill cols
    board.stop_stream()

    csv_export(data)
    Cyton_Board_End(board)


if __name__ == '__main__':
    # File config
    x = datetime.datetime.now()

    global filename 
    filename =  f"{x.strftime('%j')}_{x.strftime('%Y')}_{x.strftime('%f')}" #day of year, year, millisecond
    
    # BCI Config
    board_details = Cyton_Board_Config(False)

    global testing
    testing = False
    stopThread = False
    x = threading.Thread(target=record, args=(lambda: stopThread, board_details[0], board_details[1]))
    x.start()

    