try:
    import tkinter
except ImportError:
    import Tkinter as tkinter

from tkcalendar import *
import os.path, time
import glob
import datetime
from datetime import datetime
import pandas as pd
import numpy as np
import itertools
from dateutil.parser import parse
from tkinter.filedialog import askdirectory

# desired_width=320
desired_width=640

pd.set_option('display.width', desired_width)

np.set_printoptions(linewidth=desired_width)

pd.set_option('display.max_columns',20)


def start_label():
    var1.set(startText)
    var0.set(' ')


def gen_excel():
    """ Convert the dates selected in widget to local date and time. Filters the absolute paths of the text files which fall within
    the start and end dates"""

    if but1_clicked and but2_clicked and but3_clicked:

        start = datetime.fromtimestamp(start_unix)      
        end_date_hrs = 86399
        end = datetime.fromtimestamp(end_unix + end_date_hrs)

        if rbValue.get() == 1:

            NoiseLog_path = glob.glob(r'\\filestore.edh.co.za\FS-Production\Logs\Sport\FlightScope_X3\*\Post-burnin\*\NoiseLog.csv')

        if rbValue.get() == 2:

            NoiseLog_path = []
            files1 =  glob.glob(r'C:\Users\cameron.donkin\Mevo+ Noise Logs\Post-*\NoiseLog.txt')

            for f in files1:             
                NoiseLog_path.append(f)

        limited  = [ f for f in NoiseLog_path if ((datetime.strptime(time.ctime(os.path.getctime(f)), "%a %b %d %H:%M:%S %Y")) >= start and (datetime.strptime(time.ctime(os.path.getctime(f)), "%a %b %d %H:%M:%S %Y")) <= end)]

        if limited:
            date_time = [datetime.strptime(time.ctime(os.path.getctime(x)), "%a %b %d %H:%M:%S %Y") for x in limited]
            timestamp = [time.mktime(dt.timetuple()) for dt in date_time]
            tuple_list = []

            for log, date, un in zip(limited, date_time, timestamp):
                tuple_list.append((log, date, un))

            df = pd.DataFrame(tuple_list, columns=['Noise Log Path', 'Date and Time', 'Unix Timestamp'])

            def x3_ser_gen(log_path):
                ''' Extract the radar's serial numbers from text file'''
                f = open(log_path)
                data = []
                for line in f:
                    data_line = line.rstrip().split('\t')
                    data.append(data_line)
                serial_only = data[0]
                return serial_only

            def x3_values_gen(log_path):
                ''' Extract the radar's SNR values from text file '''
                f = open(log_path)
                data = []
                for line in f:
                    data_line = line.rstrip().split('\t')
                    data.append(data_line)

                # extract Noise values, which will be used as values for dictionary
                ab = itertools.chain(data[4] + data[8] + data[12])
                return list(ab)


            def gen_ser(log_path):

                path_list = log_path.split('\\')
                return path_list[-2]


            def gen_val(c):

                f = open(c)
                data_line = f.readline()
                new_str = data_line.split(';')
                new_str = new_str[:-1]
                new_str = new_str[2:]

                new_str = [w.replace('nan', '0') for w in new_str]

                if len(new_str) == 13:
                    new_str = new_str[1:]
                if len(new_str) == 7:
                    new_str = new_str[1:]
                if len(new_str) == 5:
                    new_str = new_str[1:]

                new_str = [ float(i) if '.' in i else int(i) for i in new_str]
                return new_str


            if rbValue.get() == 1:
                df['Sensor ID'] = df['Noise Log Path'].map(x3_ser_gen)

                df['Noise Values'] = df['Noise Log Path'].map(x3_values_gen)

            if rbValue.get() == 2:

                df['Sensor ID'] = df['Noise Log Path'].map(gen_ser)
                df['Noise Values'] = df['Noise Log Path'].map(gen_val)

            x3_keys = df['Sensor ID'].tolist()
            x3_values = df['Noise Values'].tolist()

            if rbValue.get() == 1:

                flat_list = []

                for x in x3_values:
                    flat_list.append(','.join(x))

                x3_val_propx = []

                for x in flat_list:
                    newStr = ""
                    for item in x:
                        if ';' in item:
                            str = item.replace(';', ',')
                            newStr += str
                        else:
                            newStr += item
                    x3_val_propx.append(newStr)

                x3_val_prop4 = []

                for x in x3_val_propx:
                    b = x.split(',')
                    x3_val_prop4.append(b)

                x3_val_prop5 = []

                for x in x3_val_prop4:
                    item_li = [float(i) for i in x]
                    x3_val_prop5.append(item_li)


            if rbValue.get() == 1:
                merged = list(itertools.chain(*x3_keys))
                ser_li = [b[11:] for b in merged]
                ser = pd.Series(ser_li)
                val = pd.Series(x3_val_prop5)

            else:

                ser = pd.Series(x3_keys)
                val = pd.Series(x3_values)

            df['X3 Serial Number'] = ser.values
            df['X3 Noise Values'] = val.values

            df.drop(['Sensor ID', 'Noise Values'], axis=1, inplace=True)

            dict_values = []

            for i in range(len(df)):
                dict_values.append((int(df['Unix Timestamp'][i]), df['X3 Noise Values'][i]))

            main_li  = []

            for i in range(len(dict_values)):
                li= []
                for x in dict_values[i][1]:
                    li.append(x)
                li.append(dict_values[i][0])
                main_li.append(li)

            dictionary = dict(zip(df['X3 Serial Number'], main_li))

            d = pd.DataFrame.from_dict(dictionary, orient='index')

            d = d.replace(r'^\s*$', 'None', regex=True)

            if rbValue.get() == 1:

                column_li = [['Noise','Noise','Noise','Noise','Noise','Noise','Noise','Noise', 'Signal','Signal','Signal','Signal','Signal','Signal','Signal','Signal','Deltas','Deltas','Deltas','Deltas','Deltas','Deltas','Deltas','Deltas', 'Unix Timestamp'],
                             ['Main','Azim','Elev','TR','Freq1', 'Freq2', 'Mic', 'Mean', 'Main','Azim','Elev','TR','Freq1', 'Freq2','Mic', 'Mean', 'Main','Azim','Elev','TR','Freq1', 'Freq2', 'Mic', 'Mean', '']]

            if rbValue.get() == 2:

                column_li = [['Noise','Noise','Noise','Noise', 'Signal','Signal','Signal','Signal','Deltas','Deltas','Deltas','Deltas', 'Unix Timestamp', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],  ## addded
                             ['Main','Azim','Elev','Spin','Main','Azim','Elev','Spin', 'Main','Azim','Elev','Spin','','y','y','y','y','y','y','y','y']]

            d.index.names = ['Sensor ID']

            d.columns = column_li
            d.drop('x', axis = 1, level=0, inplace = True)
            d.sort_values(by='Unix Timestamp', inplace=True)

            if rbValue.get() == 1:

                d.drop('Unix Timestamp', axis=1, inplace=True)

                output_file = select_folder + '/' + 'X3_SNR_Logs.xlsx'

                writer = pd.ExcelWriter(output_file)

                # creates workbook
                d.to_excel(writer,'X3_SNR_Logs')

                #saves workbook to file in python file directory
                writer.save()

                os.startfile(output_file)

            if rbValue.get() == 2:

                d.drop('Unix Timestamp', axis=1, level=0, inplace = True)
                output_file = select_folder + '/' + 'Mevo2_SNR_Logs.xlsx'
                writer = pd.ExcelWriter(output_file)

                #creates workbook
                d.to_excel(writer,'Mevo2_SNR_Logs')

                #saves workbook to file in python file directory
                writer.save()

                # open the file in its default application
                os.startfile(output_file)

        else:
            var0.set('No SNR test done on these days')
            var4.set(' ')

    else:
        var0.set(start_up_text)
        var1.set(startText)
        var2.set(endText)
        var3.set(folderText)


def start_to_unix(val):
    """ convert the date (selected in the widget) to number of seconds that have elapsed since the Unix epoch
    and save it to a global variable"""

    p = parse(val)
    global start_unix
    start_unix = time.mktime(p.timetuple())
    print('start_unix')
    print(start_unix)

def end_to_unix(val):
    """ convert the date (selected in the widget) to number of seconds that have elapsed since the Unix epoch
    and save it to a global variable"""
    p = parse(val)

    global end_unix

    end_unix = time.mktime(p.timetuple())
    print(end_unix)


def cal_start():
    """ open the calendar widget and extracts the date value selected """

    # clear all notification labels
    var0.set('')
    var1.set('')
    var4.set('')
    var3.set('')
    var2.set('')

    global but1_clicked

    but1_clicked = True

    def start_val():

        var3.set('')

        global datval
        datval = cal.get_date()

        start_to_unix(datval)

        top.destroy()
        var1.set('')
        var2.set(endText)

    if rbValue.get() == 1 or rbValue.get() == 2: 

        top = tkinter.Toplevel(mainWindow)
        top.geometry('350x350+650+200')
        cal = Calendar(top, font = 'Arial 14', selectmode='day', year=2019, month=5, day=17)
        cal.pack(fill = 'both', expand=True)
        btn3 = tkinter.Button(top, text ='Click Me', command=start_val)
        btn3.pack()

    else:
        var0.set("1. Select the product's SNR Logs to be generated.")

def cal_end():
    """ open the calendar widget and extract the end date selected"""
    var4.set('')

    global but2_clicked

    but2_clicked = True

    if but1_clicked: # check if the start date button is clicked

        def end_val():
            """ Grab the date selected in the calendar widget and save it to a global variable """
            global datval

            datval = cal.get_date()
            end_to_unix(datval)
            top.destroy()
            var2.set('')
            var3.set(folderText)

    if rbValue.get() == 1 or rbValue.get() == 2:

        top = tkinter.Toplevel(mainWindow)
        top.geometry('350x350+650+200')
        cal = Calendar(top, font = 'Arial 14', selectmode='day', year=2019, month=5, day=17)
        cal.pack(fill = 'both', expand=True)
        btn3 = tkinter.Button(top, text ='Click Me', command=end_val)
        btn3.pack()

    else:
        var0.set(start_up_text)
        var1.set(startText)

def output_dir():
    """ Check if start and end button is clicked, if so open file dialogue box to select the output folder of the csv file """

    global but3_clicked
    but3_clicked = True

    if but1_clicked and but2_clicked: 

        global select_folder
        select_folder = askdirectory(title='Select Folder')
        var3.set('')
        var4.set(genText)

    else:
        var1.set(startText)
        var2.set(endText)

################################## Tkinter GUI ########################################

mainWindow = tkinter.Tk()

mainWindow.title('FS SNR Logs Report')
mainWindow.geometry('480x300+50+50')
mainWindow['pady'] = 10


start_up_text = "1. Select the product's SNR Logs to be generated."

var0 = tkinter.StringVar()
rbLabel = tkinter.Label(mainWindow, textvariable=var0, fg='red', pady=5)
rbLabel.grid(row=0, column=0)

var0.set(start_up_text)

productFrame = tkinter.LabelFrame(mainWindow, text='Product')
productFrame.grid(row=1,column=0, columnspan=2, sticky='new', padx=50, pady=10)

rbValue = tkinter.IntVar()
# rbValue.set(1)

X3_b1 = tkinter.Radiobutton(productFrame, text='X3', value=1, variable=rbValue, command=start_label)
X3_b1.grid(row=0, column=0, sticky='w')
M2_b2 = tkinter.Radiobutton(productFrame, text='Mevo+', value=2, variable=rbValue, command=start_label)
M2_b2.grid(row=1, column=0, sticky='w')

rightFrame = tkinter.Frame(mainWindow)
rightFrame.grid(row=2, column=1)

startText = '2. Select Start Date of SNR Logs'

var1 = tkinter.StringVar()
startLabel = tkinter.Label(mainWindow, textvariable=var1, fg="red", pady=10)
startLabel.grid(row=2, column=0)

but1_clicked = False

btn1 = tkinter.Button(mainWindow, text='Start Date', width=20, command=cal_start)
btn1.grid(row=3, column=0)

endText = '3. Select the End Date of SNR Logs'

var2 = tkinter.StringVar()
endLabel = tkinter.Label(mainWindow, textvariable=var2, fg="red", pady=10)
endLabel.grid(row=4, column=0)

but2_clicked = False

btn2 = tkinter.Button(mainWindow, text='End Date', width=20, command=cal_end)
btn2.grid(row=5, column=0)

folderText = '4. Select CSV File Output Folder'

but3_clicked = False

var3 = tkinter.StringVar()
selectLabel = tkinter.Label(mainWindow, textvariable=var3, fg="red", pady=10)
selectLabel.grid(row=2, column=1, sticky='w')

btn3 = tkinter.Button(mainWindow, text='Select Output Folder', command=output_dir)
btn3.grid(row=3, column=1, sticky='w')

genText = '5. Generate CSV File'

var4 = tkinter.StringVar()
genLabel = tkinter.Label(mainWindow, textvariable=var4, fg="red", pady=10)
genLabel.grid(row=4, column=1, sticky='w')

btn4 = tkinter.Button(mainWindow, text='Generate CSV  File', command=gen_excel)
btn4.grid(row=5, column=1, sticky='w')

# configure the columns
mainWindow.columnconfigure(0, weight=5)
mainWindow.columnconfigure(1, weight=5)

# configure the rows
mainWindow.rowconfigure(0, weight=30)
mainWindow.rowconfigure(1, weight=5)
mainWindow.rowconfigure(2, weight=1)
mainWindow.rowconfigure(3, weight=5)
mainWindow.rowconfigure(4, weight=10)
mainWindow.rowconfigure(5, weight=10)

mainWindow.mainloop()


################################## Tkinter GUI ########################################
