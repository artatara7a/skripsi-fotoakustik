from tkinter import *
from PIL import ImageTk, Image
import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt
import FixPengolahanAudio as fix_audio
import pandas as pd
import serial
import time
import io
from datetime import datetime
import os
import glob


ser = serial.Serial('COM5', 9600)  

frekuensi = []
intensitas_maksimal_frekuensi = []
dc = []
intensitas_maksimal_dc = []

current_time = datetime.now()
time_format = "%Y-%m-%d_%H-%M-%S"
direktori = 'F:\\Skripsi'

def get_timestamp(file):
    return datetime.fromtimestamp(os.path.getctime(file))


def perekaman_sampel():
    def on_submit():
        global waktu, frequency, duty_cycle

        duty_cycle = int(entry_duty_cycle.get())
        frequency = int(entry_frekuensi.get())
        waktu = int(entry_waktu.get())
        
        ser.write("{} {} {}\n".format(frequency, duty_cycle, waktu).encode())    
        time.sleep(1) 
        
        waktu = int(waktu)
        entry_waktu.config(state=DISABLED)        
        frequency = int(frequency)
        entry_frekuensi.config(state=DISABLED)        
        duty_cycle = int(duty_cycle)
        entry_duty_cycle.config(state=DISABLED)        
        
        print("Input Waktu:", waktu)
        print(type(waktu))
        print("Input frekuensi:", frequency)
        print(type(frequency))
        print("Input Duty Cycle:", duty_cycle)
        print(type(duty_cycle))        

        # PEREKAMAN
        if (frequency >= 1 and frequency <= 25000 and 
            duty_cycle >= 1 and duty_cycle <= 100):
            print("\n\tPerekaman dimulai")
            p = pyaudio.PyAudio()
        
            chunk = 2048       
            sample_format = pyaudio.paInt16  
            channels = 1 
            sample_rate = 40000 

            stream = p.open(format=sample_format,
                            channels=channels,
                            rate=sample_rate,
                            frames_per_buffer=chunk,
                            input=True)

            frames = []
            for i in range(0, int(sample_rate / chunk * waktu)):
                data = stream.read(chunk)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()
            
            file_name = f"skripsi_ara-sampel_{current_time.strftime(time_format)}.wav"
            file_name = os.path.join(direktori, file_name)
            wf = wave.open(file_name, "wb")
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(sample_format))
            wf.setframerate(sample_rate)
            wf.writeframes(b"".join(frames))
            wf.close()
            time.sleep(1)
            print("\tPerekaman selesai")
        else:
            print("\nFrekuensi/Duty Cycle tidak valid")
            print("Gunakan frekuensi 1-25000 Hz")
            print("Gunakan duty cycle 1-100 %")
            proses_button.config(state=DISABLED)
            submit_button.config(state=DISABLED)
        return frequency

    # PENGOLAHAN AUDIO
    def pengolahan_audio():
        fix_audio.sampel()
        fix_audio.sampel_filter(on_submit())
        
        pattern = 'skripsi_ara-Grafik Frekuensi Terhadap Intensitas Bunyi-sampel_filter_*.xlsx'
        
        files = glob.glob(os.path.join(direktori, pattern))
        if files:
            files_sorted = sorted(files, key=get_timestamp, reverse=True)
            
            file_terbaru = files_sorted[0]
            timestamp_terbaru = get_timestamp(file_terbaru)
            
            df = pd.read_excel(file_terbaru)
        else:
            print("Tidak ditemukan file Excel dengan timestamp di direktori tersebut.")
            
        dominant_exp_signal = df['Intensitas Bunyi (dB)'][df['Intensitas Bunyi (dB)'].idxmax()]    
        print('\nIntensitas dominan filter:', dominant_exp_signal, 'dB')
        
        dominant_x_axis = df['Frekuensi (kHz)'][df['Intensitas Bunyi (dB)'].idxmax()]
        print('Frekuensi dominan filter:', dominant_x_axis, 'kHz\n')
        
        kategori_I = 0.014*dominant_exp_signal+0.9851
        kategori_II = 0.014*dominant_exp_signal+1.0286

        if kategori_I < 0:
            label_3.config(text="mendekati 0 ppm") #Kategori I
        elif kategori_I == 0:
            label_3.config(text=str(kategori_I) + " (ppm)") #Kategori I
        else:
            label_3.config(text=str(kategori_I) + " (ppm)") #Kategori I                        
        print(kategori_I)

        if kategori_II < 0:
            label_5.config(text="mendekati 0 ppm") #Kategori I
        elif kategori_II == 0:
            label_5.config(text=str(kategori_II) + " (ppm)") #Kategori I
        else:
            label_5.config(text=str(kategori_II) + " (ppm)") #Kategori I                        
        print(kategori_II)
    
    def on_reset():
        entry_waktu.delete(0, 'end') 
        entry_waktu.config(state=NORMAL)    
        entry_frekuensi.delete(0, 'end')  
        entry_frekuensi.config(state=NORMAL)       
        entry_duty_cycle.delete(0, 'end')  
        entry_duty_cycle.config(state=NORMAL)   
        proses_button.config(state=NORMAL)
        submit_button.config(state=NORMAL)
        print("\nInput telah direset, silahkan masukkan input kembali !\n")
    
    gui = Tk()
    gui.title("GUI_PEREKAMAN SAMPEL")
    print("\t\t'GUI_PEREKAMAN SAMPEL'\n")

    label_0 = Label(gui, text="PEREKAMAN SAMPEL", font=("none", 12, "bold"), justify="center")
    label_0.grid(row=0, column=0, padx=25, pady=20, columnspan=3) 
    label_1 = Label(gui, text='''"Besar frekuensi & Duty Cycle yang akan digunakan harus sesuai 
dengan hasil yang didapatkan dari proses modulasi laser sebelumnya"''', font=("none", 10), justify="center")
    label_1.grid(row=1, column=0, padx=25, columnspan=3) 

    waktu = Label(gui, text="Masukkan lama waktu")
    waktu.grid(row=2, column=0, padx=25, pady=10, sticky="w", columnspan=3)   
    entry_waktu = Entry(gui)
    entry_waktu.grid(row=2, column=0, padx=25, pady=10, sticky="E", columnspan=3)     
    frequency = Label(gui, text="Masukkan besar frekuensi")
    frequency.grid(row=3, column=0, padx=25, pady=10, sticky="w", columnspan=3)   
    entry_frekuensi = Entry(gui)
    entry_frekuensi.grid(row=3, column=0, padx=25, pady=10, sticky="E", columnspan=3)  
    duty_cycle = Label(gui, text="Masukkan besar duty cycle")
    duty_cycle.grid(row=4, column=0, padx=25, pady=10, sticky="w")   
    entry_duty_cycle = Entry(gui)
    entry_duty_cycle.grid(row=4, column=1, padx=25, pady=10, sticky="E", columnspan=3)  

    label_2 = Label(gui, text="Kadar timbal terdeteksi (Sampel Kategori I)")
    label_2.grid(row=5, column=0, padx=25, pady=10, sticky="W")   
    label_3 = Label(gui, text="")
    label_3.grid(row=5, column=2, padx=25, pady=10, sticky="E")   
    label_4 = Label(gui, text="Kadar timbal terdeteksi (Sampel Kategori II)")
    label_4.grid(row=6, column=0, padx=25, pady=10, sticky="W")   
    label_5 = Label(gui, text="")
    label_5.grid(row=6, column=2, padx=25, pady=10, sticky="E")   

    submit_button = Button(gui, text="Submit", height=3, width=15, font=("none", 12), command=on_submit)
    submit_button.grid(row=7, column=0, padx=25, pady=10)   
    proses_button = Button(gui, text="Mulai Proses", height=3, width=15, font=("none", 12), command=pengolahan_audio)
    proses_button.grid(row=7, column=1, padx=25, pady=10)   
    reset_button = Button(gui, text="Reset", height=3, width=15, font=("none", 12), command=on_reset)
    reset_button.grid(row=7, column=2, padx=25, pady=10)   

    gui.mainloop()


def modulasi_laser():
    def on_submit():
        global waktu, frequency

        frequency = int(entry_frekuensi.get())
        waktu = int(entry_waktu.get())
              
        # Kirim frekuensi dan duty cycle ke Arduino, dipisahkan dengan spasi
        ser.write("{} {}\n".format(frequency, waktu).encode())  
        # Tunggu 1 detik untuk memastikan pengaturan sudah berjalan di Arduino
        time.sleep(1)
        
        waktu = int(waktu)
        entry_waktu.config(state=DISABLED)        
        frequency = int(frequency)
        frekuensi.append(frequency)
        
        print("Input Waktu:", waktu)
        print(type(waktu))
        print("Input frekuensi:", frequency)
        print(type(frekuensi))

        # PEREKAMAN receivedFrequency  >= 1 && receivedFrequency  <= 25000
        if (frequency >= 1 and frequency <= 25000):
            print("\tPerekaman dimulai")
            p = pyaudio.PyAudio()

            chunk = 20000   
            sample_format = pyaudio.paInt16  
            channels = 1 
            sample_rate = 40000 

            stream = p.open(format=sample_format,
                            channels=channels,
                            rate=sample_rate,
                            frames_per_buffer=chunk,
                            input=True)

            frames = []
            for i in range(0, int(sample_rate / chunk * waktu)):
                data = stream.read(chunk)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            p.terminate()
            
            file_name = f"skripsi_ara-frekuensi_{current_time.strftime(time_format)}.wav"
            file_name = os.path.join(direktori, file_name)
            wf = wave.open(file_name, "wb")
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(sample_format))
            wf.setframerate(sample_rate)
            wf.writeframes(b"".join(frames))
            wf.close()
            time.sleep(1)
            print("\tPerekaman selesai")
        else:
            print("\nFrekuensi tidak valid, Gunakan frekuensi 1-25000 Hz")
            frekuensi.remove(frekuensi[-1])
        return frequency

    # PENGOLAHAN AUDIO
    def pengolahan_audio():
        fix_audio.frekuensi()

        # OTW FREKUENSI TERMODULASI
        fix_audio.frekuensi_filter(on_submit())

        pattern = 'skripsi_ara-Grafik Frekuensi Terhadap Intensitas Bunyi-sampel_filter_*.xlsx'
        files = glob.glob(os.path.join(direktori, pattern))
        if files:
            # Mengurutkan daftar file berdasarkan timestamp (terbaru ke terlama)
            files_sorted = sorted(files, key=get_timestamp, reverse=True)
            
            # Mengambil file pertama dalam daftar yang sekarang adalah yang terbaru
            file_terbaru = files_sorted[0]
            timestamp_terbaru = get_timestamp(file_terbaru)
            
            # Membaca file Excel dengan timestamp terbaru menggunakan pandas
            df = pd.read_excel(file_terbaru)
        else:
            print("Tidak ditemukan file Excel dengan timestamp di direktori tersebut.")
            
        # mencari nilai intensitas terbesarnya
        dominant_exp_signal = df['Intensitas Bunyi (dB)'][df['Intensitas Bunyi (dB)'].idxmax()]
        print('\nIntensitas dominan filter:', dominant_exp_signal, 'dB')
        
        # mencari nilai frekuensi pada intensitas terbesar yang sudah didapatkan sebelumnya
        dominant_x_axis = df['Frekuensi (kHz)'][df['Intensitas Bunyi (dB)'].idxmax()]
        print('Frekuensi dominan filter:', dominant_x_axis, 'kHz\n')
        intensitas_maksimal_frekuensi.append(dominant_exp_signal)
        print('\t===============================================\n')     
        time.sleep(1)

        # menghapus elemen terakhir pada list, karena terjadi dobel akibat pemanggilan fungsi >1 kali
        frekuensi.remove(frekuensi[-1])
        print(frekuensi)
        print(len(frekuensi))
        print(intensitas_maksimal_frekuensi)
        print(len(intensitas_maksimal_frekuensi))  

        # Bikin scatter plot
        plt.scatter(frekuensi, intensitas_maksimal_frekuensi, color='green', linewidth=1)
        plt.xlabel('Frekuensi (Hz)')
        plt.ylabel('Intensitas Bunyi Maksimal (dB)')
        plt.title('Representasi Input Frekuensi')
        plt.tight_layout() 
        # Menyimpan data
        file_name = f"skripsi_ara-Data Frekuensi Terhadap Intensitas Maksimal Bunyi-frekuensi_{current_time.strftime(time_format)}.png"
        file_name = os.path.join(direktori, file_name)
        plt.savefig(file_name)

        file_name = f"skripsi_ara-Data Frekuensi Terhadap Intensitas Maksimal Bunyi-frekuensi_{current_time.strftime(time_format)}.xlsx"
        file_name = os.path.join(direktori, file_name)
        writer = pd.ExcelWriter(file_name, engine = 'xlsxwriter')
        df=pd.DataFrame({'Frekuensi (Hz)':frekuensi,'Intensitas Bunyi Maksimal (dB)':intensitas_maksimal_frekuensi}).to_excel(writer, sheet_name='Sheet1')

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        worksheet = writer.sheets['Sheet1']
        worksheet.insert_image('D2', 'a', options={'image_data':buf})
        writer._save()
        buf.close()

        plt.show()


        # FREKUENSI TERMODULASI
        pattern = 'skripsi_ara-Data Frekuensi Terhadap Intensitas Maksimal Bunyi-frekuensi_*.xlsx'        
        files = glob.glob(os.path.join(direktori, pattern))
        if files:
            files_sorted = sorted(files, key=get_timestamp, reverse=True)
            
            file_terbaru = files_sorted[0]
            timestamp_terbaru = get_timestamp(file_terbaru)
            
            df = pd.read_excel(file_terbaru)
        else:
            print("Tidak ditemukan file Excel dengan timestamp di direktori tersebut.")
        
        n_tertinggi = df['Frekuensi (Hz)'][df['Intensitas Bunyi Maksimal (dB)'].idxmax()]
        print('\nFrekuensi yang akan digunakan:', n_tertinggi, 'Hz\n')
        print('\t====================SELESAI====================\n')
        time.sleep(1)

        label_3.config(text=str(n_tertinggi) + " (Hz)")       

    def on_submit2():
            global waktu2, duty_cycle

            duty_cycle = int(entry_duty_cycle.get())
            frequency2 = int(entry_frekuensi2.get())    
            waktu2 = int(entry_waktu2.get())   
            ser.write("{} {} {}\n".format(frequency2, duty_cycle, waktu2).encode())  
            time.sleep(1) 
            
            waktu2 = int(waktu2)
            entry_waktu2.config(state=DISABLED)                          
            frequency2 = int(frequency2)
            entry_frekuensi2.config(state=DISABLED)                    
            duty_cycle = int(duty_cycle)
            dc.append(duty_cycle)
            
            print("Input frekuensi:", frequency2)
            print(type(frequency2))
            print("Input Waktu:", waktu2)
            print(type(waktu2))
            print("Input Duty Cycle:", duty_cycle)
            print(type(dc))

            # PEREKAMAN
            if (duty_cycle >= 1 and duty_cycle <= 100):
                print("\tPerekaman dimulai")
                p = pyaudio.PyAudio()

                chunk = 2048       
                sample_format = pyaudio.paInt16  
                channels = 1 
                sample_rate = 40000 

                stream = p.open(format=sample_format,
                                channels=channels,
                                rate=sample_rate,
                                frames_per_buffer=chunk,
                                input=True)

                frames = []
                for i in range(0, int(sample_rate / chunk * waktu2)):
                    data = stream.read(chunk)
                    frames.append(data)

                stream.stop_stream()
                stream.close()
                p.terminate()
                
                file_name = f"skripsi_ara-dc_{current_time.strftime(time_format)}.wav"
                file_name = os.path.join(direktori, file_name)
                wf = wave.open(file_name, "wb")
                wf.setnchannels(channels)
                wf.setsampwidth(p.get_sample_size(sample_format))
                wf.setframerate(sample_rate)
                wf.writeframes(b"".join(frames))
                wf.close()
                time.sleep(1)
                print("\tPerekaman selesai")
            else:
                print("\nDuty cycle tidak valid, Gunakan Duty cycle 1-100 %")
                dc.remove(dc[-1])

    # PENGOLAHAN AUDIO UNTUK DUTY CYCLE
    def pengolahan_audio2():
        fix_audio.dc()

        # OTW DUTY CYCLE TERMODULASI
        pattern = 'skripsi_ara-Grafik Frekuensi Terhadap Intensitas Bunyi-dc_*.xlsx'        
        files = glob.glob(os.path.join(direktori, pattern))
        if files:
            files_sorted = sorted(files, key=get_timestamp, reverse=True)
            
            file_terbaru = files_sorted[0]
            timestamp_terbaru = get_timestamp(file_terbaru)
            
            df = pd.read_excel(file_terbaru)            
        else:
            print("Tidak ditemukan file Excel dengan timestamp di direktori tersebut.")
        # mencari nilai intensitas terbesarnya
        n_tertinggi = df['Intensitas Bunyi (dB)'][df['Intensitas Bunyi (dB)'].idxmax()]            
        # mencari nilai frekuensi pada intensitas terbesar yang sudah didapatkan sebelumnya
        intensitas_maksimal_dc.append(n_tertinggi)
        print('Nilai Tertinggi:', n_tertinggi, 'kHz\n')
        print('\t===============================================\n')     
        time.sleep(1)

        print(dc)
        print(len(dc))
        print(intensitas_maksimal_dc)
        print(len(intensitas_maksimal_dc))  

        # Bikin scatter plot
        plt.scatter(dc, intensitas_maksimal_dc, color='green', linewidth=1)
        plt.xlabel('Duty Cycle (%)')
        plt.ylabel('Intensitas Bunyi Maksimal (dB)')
        plt.title('Representasi Input Duty Cycle')
        plt.tight_layout() 
        # Menyimpan data        
        file_name = f"skripsi_ara-Grafik Frekuensi Terhadap Intensitas Maksimal Bunyi-dc_{current_time.strftime(time_format)}.png"
        file_name = os.path.join(direktori, file_name)
        plt.savefig(file_name)

        file_name = f"skripsi_ara-Grafik Frekuensi Terhadap Intensitas Maksimal Bunyi-dc_{current_time.strftime(time_format)}.xlsx"
        file_name = os.path.join(direktori, file_name)
        writer = pd.ExcelWriter(file_name, engine = 'xlsxwriter')
        df=pd.DataFrame({'Duty Cycle (%)':dc,'Intensitas Bunyi Maksimal (dB)':intensitas_maksimal_dc}).to_excel(writer, sheet_name='Sheet1')

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        worksheet = writer.sheets['Sheet1']
        worksheet.insert_image('D2', 'a', options={'image_data':buf})
        writer._save()
        buf.close()

        plt.show()
        

        # DUTY CYCLE TERMODULASI
        pattern = 'skripsi_ara-Grafik Frekuensi Terhadap Intensitas Maksimal Bunyi-dc_*.xlsx'
        files = glob.glob(os.path.join(direktori, pattern))
        if files:
            files_sorted = sorted(files, key=get_timestamp, reverse=True)
            
            file_terbaru = files_sorted[0]
            timestamp_terbaru = get_timestamp(file_terbaru)
            
            df = pd.read_excel(file_terbaru)
        else:
            print("Tidak ditemukan file Excel dengan timestamp di direktori tersebut.")

        n_tertinggi = df['Duty Cycle (%)'][df['Intensitas Bunyi Maksimal (dB)'].idxmax()]
        print('\nDuty Cycle yang akan digunakan:', n_tertinggi, '%\n')
        print('\t====================SELESAI====================\n')
        time.sleep(1)

        label_7.config(text=str(n_tertinggi) + " (%)")

    gui = Tk()
    gui.title("GUI_MODULASI LASER")
    print("\t\t'GUI_MODULASI LASER'\n")

    label_0 = Label(gui, text="MODULASI LASER", font=("none", 12, "bold"), justify="center")
    label_0.grid(row=0, column=0, padx=25, pady=20, columnspan=2) 
    label_1 = Label(gui, text="[ Mencari Frekuensi Terbaik ]", font=("none", 10, "bold"))
    label_1.grid(row=1, column=0, padx=25, columnspan=2, sticky="w") 

    waktu = Label(gui, text="Masukkan lama waktu")
    waktu.grid(row=2, column=0, padx=25, pady=10, sticky="w", columnspan=2)   
    entry_waktu = Entry(gui)
    entry_waktu.grid(row=2, column=0, padx=25, pady=10, sticky="E", columnspan=2)   
    frequency = Label(gui, text="Masukkan besar frekuensi (1-25000 Hz)")
    frequency.grid(row=3, column=0, padx=25, pady=10, sticky="w", columnspan=2)   
    entry_frekuensi = Entry(gui)
    entry_frekuensi.grid(row=3, column=0, padx=25, pady=10, sticky="E", columnspan=2)  


    submit_button = Button(gui, text="Submit", height=3, width=15, font=("none", 12), command=on_submit)
    submit_button.grid(row=4, column=0, padx=25, pady=10)   
    proses_button = Button(gui, text="Mulai Proses", height=3, width=15, font=("none", 12), command=pengolahan_audio)
    proses_button.grid(row=4, column=1, padx=25, pady=10)   

    label_2 = Label(gui, text="Besar frekuensi terbaik")
    label_2.grid(row=5, column=0, padx=25, pady=20, sticky="W")   
    label_3 = Label(gui, text="")
    label_3.grid(row=5, column=1, padx=25, pady=20, sticky="E")   
    

    label_4 = Label(gui, text="[ Mencari Duty Cycle Terbaik ]", font=("none", 10, "bold"))
    label_4.grid(row=6, column=0, padx=25, columnspan=2, sticky="w") 
    label_5 = Label(gui, text="*Besar frekuensi yang akan digunakan == besar frekuensi terbaik", font=("none", 10))
    label_5.grid(row=7, column=0, padx=25, columnspan=2, sticky="w") 

    frequency2 = Label(gui, text="Masukkan besar frekuensi")
    frequency2.grid(row=8, column=0, padx=25, pady=10, sticky="w", columnspan=2)   
    entry_frekuensi2 = Entry(gui)
    entry_frekuensi2.grid(row=8, column=0, padx=25, pady=10, sticky="E", columnspan=2)   
    waktu2 = Label(gui, text="Masukkan lama waktu")
    waktu2.grid(row=9, column=0, padx=25, pady=10, sticky="w", columnspan=2)   
    entry_waktu2 = Entry(gui)
    entry_waktu2.grid(row=9, column=0, padx=25, pady=10, sticky="E", columnspan=2)   
    duty_cycle = Label(gui, text="Masukkan besar duty cycle (1-100 %)")
    duty_cycle.grid(row=10, column=0, padx=25, pady=10, sticky="w")   
    entry_duty_cycle = Entry(gui)
    entry_duty_cycle.grid(row=10, column=1, padx=25, pady=10, sticky="E")  

    submit_button = Button(gui, text="Submit", height=3, width=15, font=("none", 12), command=on_submit2)
    submit_button.grid(row=11, column=0, padx=25, pady=10)   
    proses_button = Button(gui, text="Mulai Proses", height=3, width=15, font=("none", 12), command=pengolahan_audio2)
    proses_button.grid(row=11, column=1, padx=25, pady=10)   

    label_6 = Label(gui, text="Besar duty cycle terbaik")
    label_6.grid(row=12, column=0, padx=25, pady=20, sticky="W")   
    label_7 = Label(gui, text="")
    label_7.grid(row=12, column=1, padx=25, pady=20, sticky="E")   

    gui.mainloop()   
    
    
def perekaman():
    # Membuat jendela GUI
    gui = Tk()
    gui.title("GUI_PEREKAMAN")
    print("\t\t'GUI_PEREKAMAN'\n")

    button_1 = Button(gui, text="MODULASI LASER", height=3, width=30, font=("none", 12), command=modulasi_laser)
    button_1.grid(row=0, column=0, padx=20, pady=10)  # Mengatur posisi
    button_2 = Button(gui, text="PEREKAMAN SAMPEL", height=3, width=30, font=("none", 12), command=perekaman_sampel)
    button_2.grid(row=1, column=0, padx=20, pady=10)  
    
    gui.mainloop()
    
    
# Membuat jendela utama
root = Tk()
root.title("GUI_START")
print("\t\t'GUI_START'\n")

# Menambahkan elemen-elemen GUI
label_1 = Label(root, text="""SISTEM FOTOAKUSTIK SEDERHANA UNTUK DETEKSI KADAR
TIMBAL PADA AIR BERBASIS LASER DIODA DAN
MIKROFON KONDENSER MENGGUNAKAN PYTHON""", font=("none", 15, "bold"), justify="center") 
label_1.grid(row=0, column=0, padx=20, pady=10) 
label_2 = Label(root, text="""JURUSAN FISIKA
FAKULTAS MATEMATIKA DAN ILMU PENGETAHUAN ALAM
UNIVERSITAS LAMPUNG
2023""", font=("none", 15, "bold"), justify="center") 
label_2.grid(row=3, column=0, pady=10) 
# Memuat gambar
image_1 = Image.open("F:\\Skripsi\\unila.png")
# Mengubah ukuran gambar jika diperlukan
image_1 = image_1.resize((150, 150), Image.BILINEAR)  
# Mengonversi gambar menjadi format yang dapat ditampilkan oleh Tkinter
photo = ImageTk.PhotoImage(image_1)
# Menampilkan gambar di dalam label
label_3 = Label(root, image=photo)
label_3.grid(row=1, column=0, pady=10) 

# Membuat tombol untuk memunculkan GUI
button_1 = Button(root, text="START", height=3, width=25, font=("none", 12), command=perekaman)
button_1.grid(row=2, column=0, pady=10)  

# Menjalankan loop utama aplikasi
root.mainloop()
