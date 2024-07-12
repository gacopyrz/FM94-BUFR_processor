###################################################################################################
# PROGRAM read_FM94-BUFR.py
# (c) Gacopyrz, 2024 on MIT license
# Źródłem pochodzenia danych jest Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy.
# The source data were taken from Instytut Meteorologii i Gospodarki Wodnej – Państwowy Instytut Badawczy (IMGW-PIB).
# Dane Instytutu Meteorologii i Gospodarki Wodnej – Państwowego Instytutu Badawczego zostały przetworzone.
# The data taken from IMGW-PIB were been preprocessed.
#
# version 0-00-002 10.07.2024
# version 0-00-003 11.07.2024
# version 0-00-004 12.07.2024
# Description:
# The program reads data from FM94-BUFR type files (*.buf) according to [Manual_on_Codes].
# The program is tested for radar operating current.buf files provided by IMGW-PIB taken from the adress:
# https://danepubliczne.imgw.pl/pl/datastore/getfiledown/Oper/Polrad/Produkty/GSA/gsa_compo_pcz.cappi_buf/current.buf
#**************************************************************************************************
# reference call of the program: python3 read_FM94-BUFR.py <[filename.buf]>
# files *.buf are stored in ./dane/ subfolder
#___________________________________________________________________________________________________
# References:
#
# [Manual_on_Codes.pdf] Manual on Codes International Codes Volume I.2 2019 edition Updated in 2022 (WMO-No. 306)
#
# [OPERA_FM94-BUFR.pdf] OPERA FM94-BUFR Encoding and Decoding by Helmut Paulitsch, Jürgen Fuchsberger, Konrad Köck with the support of the OPERA group, May 2010
##################################################################################################


import struct
import sys
import bitstring # https://bitstring.readthedocs.io/en/stable/
from bitstring import Bits
import numpy as np
import matplotlib.pyplot as plt

OCTET_SIZE=8 # 1 octet = 8 bits = 1 byte
SECTION_0_SIZE=8 # section 0 size in octets
SECTION_0_BITSIZE=SECTION_0_SIZE*OCTET_SIZE # section 0 size in bits

file_path="/home/mirek/Meteorologia/dane/24_07_12/BRZ/"
if len(sys.argv)>1:
    j=sys.argv[1] # file name as initial argument
    file_name=f'{j}'
else:
    file_name=f'./dane/current(ref).buf' # if no arguments are given for program call

f=open(file_path+file_name,"rb")


file_binary=f.read() #binary file content

print(f'Processing file: {file_name}')

file_bitfield=Bits(file_binary) #rzutowanie pliku binarnego na typ Bits

# checking if "file_bitfield" contains proper header "BUFR" and footer "7777"

header=file_bitfield[0:OCTET_SIZE*4] # "BUFR" first 4 bytes of file_bitfield
footer=file_bitfield[-(OCTET_SIZE*4):] # "7777" last 4 bytes of file_bitfield


if (header.tobytes().decode("ascii")=="BUFR" and footer.tobytes().decode("ascii")=="7777"):
    pass
    #print("file_bitfield header and footer OK")
else:
    print(f"Reading error! File {nazwa_pliku} is not of FM94_BUFR type file!")
    exit()

# Section 0 (Indicator section) description:
# Octet No.   Contents
#    1–      BUFR (coded according to the CCITT International Alphabet No. 5)
#   5–7     Total length of BUFR message (including Section 0)
#    8       BUFR edition number (4)

#Section 0 encoding

section_0_field=file_bitfield[0:OCTET_SIZE*SECTION_0_SIZE]
total_length_of_BUFR_message=section_0_field[5*OCTET_SIZE:7*OCTET_SIZE].uint # octets 5-7 of section 0

if (len(file_binary)==total_length_of_BUFR_message):
    pass
    #print (f"total length of BUFR mesage = {total_length_of_BUFR_message}. Length control: OK")
else:
    print(f"File length error! ")
    exit()

BUFR_edition_number=section_0_field[7*OCTET_SIZE:8*OCTET_SIZE].uint # octet 8 of section 0
#print (f'BUFR edition number: {BUFR_edition_number}')

"""
Section 1 (Identification section) description see [OPERA_FM94-BUFR.pdf p.8.]
(CAUTION! do not use description of Section 1 from [Manual_on_Codes.pdf] p. 267 it is wrong!):
Octet number    description
1-3   Length of section, in octets
4     BUFR master table (zero if standard WMO FM 94 BUFR tables are used – permits BUFR to be used to represent data from other disciplines, and with their own versions of master tables and local tables)
5     Originating/generating subcenter (Code table 0 01 034)
6     Originating/generating centre (Code table 0 01 033)
7     Update sequence number (zero for original BUFR messages; incremented for updates)
8     Bit 1 = 0 No optional section, = 1 Optional section included, Bits 2 –8 set to zero (reserved)
9     Data Category type (see BUFR Table A, section 2.4.1)
10    Data Category sub-type (defined by local data processing centres)
11    Version number of master tables used (currently 2 for WMO FM 94 BUFR tables)
12    Version number of local tables used to augment the master table in use
13    Year of century (most typical for BUFR message content)
14    Month
15    Day
16    Hour
17    Minute
18-    Reserved for local use by data processing centres
"""
#Section 1 encoding:

SECTION_1_START_INDEX=SECTION_0_BITSIZE

length_of_section_1=file_bitfield[SECTION_1_START_INDEX:SECTION_1_START_INDEX+3*OCTET_SIZE].uint
#print (f'length of section 1: {length_of_section_1} octets')

SECTION_1_BITSIZE=OCTET_SIZE*length_of_section_1

# creation bitfield for section 1
section_1_field=file_bitfield[SECTION_1_START_INDEX:SECTION_1_START_INDEX+SECTION_1_BITSIZE]

# SECTION_1_START_INDEX (i.e. global index) is used  for indexing the file_bitfield.
# For indexing items within section_1_field array, the local indexing begining from 0 is performed

BUFR_master_table=section_1_field[0+3*OCTET_SIZE:4*OCTET_SIZE].uint
if BUFR_master_table==0:
    pass
    #print (f'Standard WMO FM 94 BUFR tables are used')
else:
    print (f'WARNING! Not standard Master table is used')

octet5=section_1_field[4*OCTET_SIZE:5*OCTET_SIZE].uint # octet 5 of section 1
#print(f'Originating/generating subcenter: {octet5}')
octet6=section_1_field[5*OCTET_SIZE:6*OCTET_SIZE].uint # octet 6 of section 1
#print(f'Originating/generating centre: {octet6}')
octet7=section_1_field[6*OCTET_SIZE:7*OCTET_SIZE].uint # octet 7
#print(f'Update sequence number: {octet7}')


#Checking if there is section 2 (optional section) in the file
section2_flag=section_1_field[7*OCTET_SIZE:7*OCTET_SIZE+1].uint # octet 8 bit 1 (older). Bit 1 = 0 No optional section, = 1 Optional section included, Bits 2 –8 set to zero (reserved)
if section2_flag==0:
    SECTION_2_BITSIZE=0
else:
    print("ERROR: file contains section 2. Can't process it now")
    SECTION_2_START_INDEX=SECTION_1_START_INDEX+SECTION_1_BITSIZE
    length_of_section_2=file_bitfield[SECTION_2_START_INDEX:SECTION_2_START_INDEX+3*OCTET_SIZE].uint
    SECTION_2_BITSIZE=SECTION_2_START_INDEX+length_of_section_2*OCTET_SIZE
    exit()

octet9=section_1_field[8*OCTET_SIZE:9*OCTET_SIZE].uint # octet 9 Data Category type (value "6" means radar data)
#print(f'Data Category type: {octet9}')
octet10=section_1_field[9*OCTET_SIZE:10*OCTET_SIZE].uint # octet 10
#print(f'Data Category sub-type: {octet10}')
octet11=section_1_field[10*OCTET_SIZE:11*OCTET_SIZE].uint # octet 11
#print(f'Version number of master tables used: {octet11}')
octet12=section_1_field[11*OCTET_SIZE:12*OCTET_SIZE].uint # octet 12
#print(f'Version number of local tables used: {octet12}')
year=section_1_field[12*OCTET_SIZE:13*OCTET_SIZE].uint # octet 13
month=section_1_field[13*OCTET_SIZE:14*OCTET_SIZE].uint # octet 14
day=section_1_field[14*OCTET_SIZE:15*OCTET_SIZE].uint # octet 15
hour=section_1_field[15*OCTET_SIZE:16*OCTET_SIZE].uint # octet 16
minute=section_1_field[16*OCTET_SIZE:17*OCTET_SIZE].uint # octet 17

print(f'Observation date: 20{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}')

# Section 3 encoding

SECTION_3_START_INDEX=SECTION_1_START_INDEX+SECTION_1_BITSIZE+SECTION_2_BITSIZE

length_of_section_3=file_bitfield[SECTION_3_START_INDEX:SECTION_3_START_INDEX+3*OCTET_SIZE].uint
SECTION_3_BITSIZE=length_of_section_3*OCTET_SIZE
#print (f'length of section 3: {length_of_section_3} octets')

# creation bitfield for section 1
section_3_field=file_bitfield[SECTION_3_START_INDEX:SECTION_3_START_INDEX+SECTION_3_BITSIZE]
#print(f'octet_number | octet_value')
for octet_number in range(4,length_of_section_3,2):
    octet_value1=section_3_field[(octet_number-1)*OCTET_SIZE:(octet_number)*OCTET_SIZE]
    octet_value2=section_3_field[(octet_number)*OCTET_SIZE:(octet_number+1)*OCTET_SIZE]

    #print(f'{octet_number:12d} | {octet_value1[0:2].uint:7d} | {octet_value1[2:].uint:7d} | {octet_value2.uint:7d}')


# Section 4 encoding
SECTION_4_START_INDEX=SECTION_3_START_INDEX+SECTION_3_BITSIZE
length_of_section_4=file_bitfield[SECTION_4_START_INDEX:SECTION_4_START_INDEX+3*OCTET_SIZE].uint
SECTION_4_BITSIZE=length_of_section_4*OCTET_SIZE
#print (f'length of section 4: {length_of_section_4} octets')

section_4_field=file_bitfield[SECTION_4_START_INDEX:SECTION_4_START_INDEX+SECTION_4_BITSIZE]
offset=4*OCTET_SIZE

tekst=["Rok","Miesiąc","Dzień","Godzina","Minuta","lat1","lon1","lat2","lon2","lat3","lon3","lat4","lon4","Projection type","lat centr","lon centr","height of statn","pix size on horiz.1","pix size on horiz.2","Number of pixels per row ","Number of pixels per col.","Radar rainfall intensity","Delayed descriptor replication factor","Radar rainfall intensity","Radar rainfall intensity","Radar rainfall intensity","Radar rainfall intensity","Radar rainfall intensity","Radar rainfall intensity","Radar rainfall intensity","Radar rainfall intensity","Radar rainfall intensity","Radar rainfall intensity"]
reference_offset=[0,0,0,0,0,-9000,-18000,-9000,-18000,-9000,-18000,-9000,-18000,0,-9000,-18000,-400,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
message_bitlength =[12,4,6,5,6,15,16,15,16,15,16,15,16,3,15,16,15,16,16,12,12,12,8,12,12,12,12,12,12,12,12,12,12]
scale=[1,1,1,1,1,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,1,0.01,0.01,1,10,10,1,1,0.036,1,0.036,0.036,0.036,0.036,0.036,0.036,0.036,0.036,0.036,0.036]
f=["5d","5d","5d","5d","5d","5.2f","5.2f","5.2f","5.2f","5.2f","5.2f","5.2f","5.2f",">5d","5.2f","5.2f",">5d",">5d",">5d",">5d",">5d","8.7f",">5d","8.7f","8.7f","8.7f","8.7f","8.7f","8.7f","8.7f","8.7f","8.7f","8.7f"]
for index in range(len(tekst)):
    #print(f'{tekst[index]:>25s}: {(section_4_field[offset:offset+message_bitlength[index]].uint+reference_offset[index])*scale[index]:{f[index]}}')
    offset+=message_bitlength[index]
# processing of message 3-21-193
total_number_of_rows=section_4_field[offset:offset+16].uint
offset+=16
#print(f'total_number_of_rows: {total_number_of_rows}')
table_of_values=[]
for row in range(total_number_of_rows):
    actual_row_number=section_4_field[offset:offset+12].uint
    offset+=12
    #print(f'actual_row_number {actual_row_number}')
    total_number_of_parcels=section_4_field[offset:offset+8].uint
    offset+=8
    #print(f'total_number_of_parcels: {total_number_of_parcels}')
    for parcel in range(total_number_of_parcels):
        number_of_compressed_groups=section_4_field[offset:offset+8].uint
        offset+=8
        #print(f'number_of_compressed_groups: {number_of_compressed_groups}')
        for group in range(number_of_compressed_groups):
            number_of_elements=section_4_field[offset:offset+16].uint
            offset+=16
            #print(f'number_of_elements_in_group: {number_of_elements}')
            value_of_element_of_group=section_4_field[offset:offset+8].uint
            offset+=8
            #print(f'value_of_element_of_compressed group: {value_of_element_of_group}')
            for element in range(number_of_elements):
                table_of_values.append(value_of_element_of_group)
        number_of_uncompressed_groups=section_4_field[offset:offset+8].uint
        offset+=8
        #print(f'number_of_uncompressed_groups: {number_of_uncompressed_groups}')
        for group in range(number_of_uncompressed_groups):
            value_of_element_of_group=section_4_field[offset:offset+8].uint
            offset+=8
            # print(f'value_of_element_of_uncompressed_group: {value_of_element_of_group}')
            table_of_values.append(value_of_element_of_group)
#print(f'row: {row} len(table_of_values): {len(table_of_values)}')

rainfall_matrix=np.array(table_of_values)
rainfall_matrix[rainfall_matrix == 255] = 0
rainfall_matrix=np.reshape(rainfall_matrix, (-1, 400))# reshape matrix from 1D to 400 columns x 400 rows
plt.imsave("/home/mirek/Meteorologia/png/2024_07_12/"+file_name[:-3]+"png",rainfall_matrix*25, cmap="Blues",vmin=0,vmax=255,dpi=100)




