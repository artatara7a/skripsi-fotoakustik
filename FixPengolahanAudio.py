import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
import pandas as pd
import io
from datetime import datetime
import os
import glob


current_time = datetime.now()
time_format = "%Y-%m-%d_%H-%M-%S"
direktori = 'F:\\Skripsi'

def get_timestamp(file):
    return datetime.fromtimestamp(os.path.getctime(file))

def frekuensi():
    global exp_signal, x_axis
    
    pattern = 'skripsi_ara-frekuensi_*.wav'
    files = glob.glob(os.path.join(direktori, pattern))
    if files:
        files_sorted = sorted(files, key=get_timestamp, reverse=True)
        
        file_terbaru = files_sorted[0]
        timestamp_terbaru = get_timestamp(file_terbaru)
        
        # Membaca file Excel dengan timestamp terbaru menggunakan pandas
        freq_sample, sig_audio = wavfile.read(file_terbaru)
    else:
        print("Tidak ditemukan file Wav dengan timestamp di direktori tersebut.")
    # Output the parameters: Signal Data Type, Sampling Frequency and Duration
    print('\nShape of Signal:', sig_audio.shape)   
    print('Signal Datatype:', sig_audio.dtype)
    print('Signal duration:', round(sig_audio.shape[0] / float(freq_sample), 2), 'seconds')

    # Normalize the signal values
    pow_audio_signal = sig_audio / np.power(2, 15)
    # Membuat sumbu waktu yang tepat selama 1 detik
    time_axis = np.linspace(0, 1000, len(pow_audio_signal))

    # Visualize the signal
    plt.subplot(2,1,1) 
    plt.plot(time_axis, pow_audio_signal, color='blue')
    plt.xlabel('Waktu (ms)')
    plt.ylabel('Amplitudo')
    plt.title('Audio Dalam Domain Waktu')

    #data amplitudo
    sig_audio = sig_audio / np.power(2, 15)

    # Extracting the length and the half–length of the signal to input to the Fourier transform
    sig_length = len(sig_audio)
    half_length = np.ceil((sig_length + 1) / 2.0).astype(np.int_)
    # We will now be using the Fourier Transform to form the frequency domain of the signal
    signal_freq = np.fft.fft(sig_audio) # sinyal domain waktu

    # Normalize the frequency domain and square it 
    signal_freq = abs(signal_freq[0:half_length]) / sig_length 
    signal_freq **= 2   
    transform_len = len(signal_freq)

    # The Fourier transformed signal now needs to be adjusted for both even and odd cases
    if sig_length % 2:
        signal_freq[1:len(signal_freq)] *= 2
    else:
        signal_freq[1:len(signal_freq)-1] *= 2
    # Extract the signal's strength in decibels (dB) 
    exp_signal = 10 * np.log10(signal_freq)
    #exp_signal = 10 * np.log10(signal_freq/1e-12)
    x_axis = np.arange(0, half_length, 1) * (freq_sample / sig_length) / 1000.0
    
    dominant_exp_signal = exp_signal[np.argmax(exp_signal)]
    dominant_x_axis = x_axis[np.argmax(exp_signal)]
    print(f"Intensitas dominan: {dominant_exp_signal} dB")
    print(f"Frekuensi dominan: {dominant_x_axis} kHz\n")

    plt.subplot(2,1,2) 
    plt.plot(x_axis, exp_signal, color='green', linewidth=1)
    plt.xlabel('Frekuensi (kHz)')
    plt.ylabel('Intensitas Bunyi (dB)')
    plt.title('Audio Dalam Domain Frekuensi')
    plt.tight_layout()

    # Menyimpan data
    file_name = f"skripsi_ara-Grafik-frekuensi_{current_time.strftime(time_format)}.png"
    file_name = os.path.join(direktori, file_name)
    plt.savefig(file_name)

    file_name = f"skripsi_ara-Grafik Waktu Terhadap Amplitudo-frekuensi_{current_time.strftime(time_format)}.xlsx"
    file_name = os.path.join(direktori, file_name)
    writer = pd.ExcelWriter(file_name, engine = 'xlsxwriter')
    
    df=pd.DataFrame({'Waktu':time_axis,'Amplitudo':pow_audio_signal}).to_excel(writer, sheet_name='Sheet1')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    worksheet = writer.sheets['Sheet1']
    worksheet.insert_image('D2', 'a', options={'image_data':buf})
    writer._save()
    buf.close()

    file_name = f"skripsi_ara-Grafik Frekuensi Terhadap Intensitas Bunyi-frekuensi_{current_time.strftime(time_format)}.xlsx"
    file_name = os.path.join(direktori, file_name)
    writer = pd.ExcelWriter(file_name, engine = 'xlsxwriter')
    
    df=pd.DataFrame({'Frekuensi (kHz)':x_axis,'Intensitas Bunyi (dB)':exp_signal}).to_excel(writer, sheet_name='Sheet1')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    worksheet = writer.sheets['Sheet1']
    worksheet.insert_image('D2', 'a', options={'image_data':buf})
    writer._save()
    buf.close()

    plt.show()

def frekuensi_filter(frequency):
    # mencari intensitas suara pada frekuensi input menggunakan band pass filter
    max_y = exp_signal[frequency-10:frequency+11]
    # mencari frekuensi input menggunakan band pass filter
    freq_x = x_axis[frequency-10:frequency+11]

    frequency = frequency/1000
    
    plt.plot(freq_x, max_y, color='green', linewidth=1)
    plt.xlabel('Frekuensi (kHz)')
    plt.ylabel('Intensitas Bunyi (dB)')
    plt.title('Audio Filter '+str(frequency)+' kHz')
    plt.tight_layout()

    # Menyimpan data
    file_name = f"skripsi_ara-Grafik Frekuensi Terhadap Intensitas Bunyi-sampel_filter_{current_time.strftime(time_format)}.png"
    file_name = os.path.join(direktori, file_name)
    plt.savefig(file_name)

    file_name = f"skripsi_ara-Grafik Frekuensi Terhadap Intensitas Bunyi-sampel_filter_{current_time.strftime(time_format)}.xlsx"
    file_name = os.path.join(direktori, file_name)
    writer = pd.ExcelWriter(file_name, engine = 'xlsxwriter')
    
    df=pd.DataFrame({'Frekuensi (kHz)':freq_x,'Intensitas Bunyi (dB)':max_y}).to_excel(writer, sheet_name='Sheet1')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    worksheet = writer.sheets['Sheet1']
    worksheet.insert_image('D2', 'a', options={'image_data':buf})
    writer._save()
    buf.close()   

    plt.show() 
    

def dc():
    global exp_signal, x_axis
    
    pattern = 'skripsi_ara-dc_*.wav'
        
    files = glob.glob(os.path.join(direktori, pattern))
    if files:
        files_sorted = sorted(files, key=get_timestamp, reverse=True)
        
        file_terbaru = files_sorted[0]
        timestamp_terbaru = get_timestamp(file_terbaru)
        
        freq_sample, sig_audio = wavfile.read(file_terbaru)
    else:
        print("Tidak ditemukan file Wav dengan timestamp di direktori tersebut.")
    
    print('\nShape of Signal:', sig_audio.shape)   
    print('Signal Datatype:', sig_audio.dtype)
    print('Signal duration:', round(sig_audio.shape[0] / float(freq_sample), 2), 'seconds')

    pow_audio_signal = sig_audio / np.power(2, 15)
    time_axis = np.linspace(0, 1000, len(pow_audio_signal))

    plt.subplot(2,1,1) 
    plt.plot(time_axis, pow_audio_signal, color='blue')
    plt.xlabel('Waktu (ms)')
    plt.ylabel('Amplitudo')
    plt.title('Audio Dalam Domain Waktu')

    sig_audio = sig_audio / np.power(2, 15) 

    sig_length = len(sig_audio)
    half_length = np.ceil((sig_length + 1) / 2.0).astype(np.int_)
    signal_freq = np.fft.fft(sig_audio)

    signal_freq = abs(signal_freq[0:half_length]) / sig_length
    signal_freq **= 2
    transform_len = len(signal_freq)

    x = signal_freq[1:transform_len]
    if sig_length % 2:
        x *= 2
    else:
        x *= 2
    exp_signal = 10 * np.log10(signal_freq)
    x_axis = np.arange(0, half_length, 1) * (freq_sample / sig_length) / 1000.0
    
    dominant_exp_signal = exp_signal[np.argmax(exp_signal)]
    dominant_x_axis = x_axis[np.argmax(exp_signal)]
    print(f"Intensitas dominan: {dominant_exp_signal} dB")
    print(f"Frekuensi dominan: {dominant_x_axis} kHz")

    plt.subplot(2,1,2) 
    plt.plot(x_axis, exp_signal, color='green', linewidth=1)
    plt.xlabel('Frekuensi (kHz)')
    plt.ylabel('Intensitas Bunyi (dB)')
    plt.title('Audio Dalam Domain Frekuensi')
    plt.tight_layout() 

    # Menyimpan data
    file_name = f"skripsi_ara-Grafik-dc_{current_time.strftime(time_format)}.png"
    file_name = os.path.join(direktori, file_name)
    plt.savefig(file_name)

    file_name = f"skripsi_ara-Grafik Waktu Terhadap Amplitudo-dc_{current_time.strftime(time_format)}.xlsx"
    file_name = os.path.join(direktori, file_name)
    writer = pd.ExcelWriter(file_name, engine = 'xlsxwriter')
    
    df=pd.DataFrame({'Waktu':time_axis,'Amplitudo':pow_audio_signal}).to_excel(writer, sheet_name='Sheet1')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    worksheet = writer.sheets['Sheet1']
    worksheet.insert_image('D2', 'a', options={'image_data':buf})
    writer._save()
    buf.close()

    file_name = f"skripsi_ara-Grafik Frekuensi Terhadap Intensitas Bunyi-dc_{current_time.strftime(time_format)}.xlsx"
    file_name = os.path.join(direktori, file_name)
    writer = pd.ExcelWriter(file_name, engine = 'xlsxwriter')
    
    df=pd.DataFrame({'Frekuensi (kHz)':x_axis,'Intensitas Bunyi (dB)':exp_signal}).to_excel(writer, sheet_name='Sheet1')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    worksheet = writer.sheets['Sheet1']
    worksheet.insert_image('D2', 'a', options={'image_data':buf})
    writer._save()
    buf.close()

    plt.show()

def sampel():
    global exp_signal, x_axis
    
    pattern = 'skripsi_ara-sampel_*.wav'        
    files = glob.glob(os.path.join(direktori, pattern))
    if files:
        files_sorted = sorted(files, key=get_timestamp, reverse=True)
        
        file_terbaru = files_sorted[0]
        timestamp_terbaru = get_timestamp(file_terbaru)
        
        freq_sample, sig_audio = wavfile.read(file_terbaru)
    else:
        print("Tidak ditemukan file Wav dengan timestamp di direktori tersebut.")
    
    print('\nShape of Signal:', sig_audio.shape)   
    print('Signal Datatype:', sig_audio.dtype)
    print('Signal duration:', round(sig_audio.shape[0] / float(freq_sample), 2), 'seconds')

    pow_audio_signal = sig_audio / np.power(2, 15)
    pow_audio_signal = pow_audio_signal
    time_axis = np.linspace(0, 1000, len(pow_audio_signal))

    plt.subplot(2,1,1) 
    plt.plot(time_axis, pow_audio_signal, color='blue')
    plt.xlabel('Waktu (ms)')
    plt.ylabel('Amplitudo')
    plt.title('Audio Dalam Domain Waktu')  

    sig_audio = sig_audio / np.power(2, 15) 

    sig_length = len(sig_audio)
    half_length = np.ceil((sig_length + 1) / 2.0).astype(np.int_)
    signal_freq = np.fft.fft(sig_audio)

    signal_freq = abs(signal_freq[0:half_length]) / sig_length

    print(signal_freq)
    file_name = f"NON_FFT_{current_time.strftime(time_format)}.xlsx"
    file_name = os.path.join(direktori, file_name)
    writer = pd.ExcelWriter(file_name, engine = 'xlsxwriter')
    
    df=pd.DataFrame({'FFT':signal_freq}).to_excel(writer, sheet_name='Sheet1')
    
    signal_freq **= 2
    transform_len = len(signal_freq)

    if sig_length % 2:
        signal_freq[1:len(signal_freq)] *= 2
    else:
        signal_freq[1:len(signal_freq)-1] *= 2
    
    exp_signal = 10 * np.log10(signal_freq)
    x_axis = np.arange(0, half_length, 1) * (freq_sample / sig_length) / 1000.0
    dominant_exp_signal = exp_signal[np.argmax(exp_signal)]
    dominant_x_axis = x_axis[np.argmax(exp_signal)]
    print(f"Intensitas dominan: {dominant_exp_signal} dB")
    print(f"Frekuensi dominan: {dominant_x_axis} Hz\n")
    print('\t====================SELESAI====================\n')

    plt.subplot(2,1,2) 
    plt.plot(x_axis, exp_signal, color='green', linewidth=1)
    plt.xlabel('Frekuensi (kHz)')
    plt.ylabel('Intensitas Bunyi (dB)')
    plt.title('Audio Dalam Domain Frekuensi')
    plt.tight_layout() 

    # Menyimpan data
    file_name = f"skripsi_ara-Grafik-sampel_{current_time.strftime(time_format)}.png"
    file_name = os.path.join(direktori, file_name)
    plt.savefig(file_name)

    file_name = f"skripsi_ara-Grafik Waktu Terhadap Amplitudo-sampel_{current_time.strftime(time_format)}.xlsx"
    file_name = os.path.join(direktori, file_name)
    writer = pd.ExcelWriter(file_name, engine = 'xlsxwriter')
    
    df=pd.DataFrame({'Waktu':time_axis,'Amplitudo':pow_audio_signal}).to_excel(writer, sheet_name='Sheet1')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    worksheet = writer.sheets['Sheet1']
    worksheet.insert_image('D2', 'a', options={'image_data':buf})
    writer._save()
    buf.close()
    
    file_name = f"skripsi_ara-Grafik Frekuensi Terhadap Intensitas Bunyi-sampel_{current_time.strftime(time_format)}.xlsx"
    file_name = os.path.join(direktori, file_name)
    writer = pd.ExcelWriter(file_name, engine = 'xlsxwriter')
    
    df=pd.DataFrame({'FFT':signal_freq,'Frekuensi (kHz)':x_axis,'Intensitas Bunyi (dB)':exp_signal}).to_excel(writer, sheet_name='Sheet1')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    worksheet = writer.sheets['Sheet1']
    worksheet.insert_image('D2', 'a', options={'image_data':buf})
    writer._save()
    buf.close()

    plt.show()    

def sampel_filter(frequency):    
    #15176
    # mencari intensitas suara pada frekuensi input menggunakan band pass filter
    max_y = exp_signal[frequency-10:frequency+11]   #max_y = exp_signal[15176-10:15176+11]
    # mencari frekuensi input menggunakan band pass filter
    freq_x = x_axis[frequency-10:frequency+11]  #freq_x = x_axis[15176-10:15176+11]

    frequency = frequency/1000
    
    plt.plot(freq_x, max_y, color='green', linewidth=1)
    plt.xlabel('Frekuensi (kHz)')
    plt.ylabel('Intensitas Bunyi (dB)')
    plt.title('Audio Filter '+str(frequency)+' kHz')
    plt.tight_layout()

    # Menyimpan data
    file_name = f"skripsi_ara-Grafik Frekuensi Terhadap Intensitas Bunyi-sampel_filter_{current_time.strftime(time_format)}.png"
    file_name = os.path.join(direktori, file_name)
    plt.savefig(file_name)

    file_name = f"skripsi_ara-Grafik Frekuensi Terhadap Intensitas Bunyi-sampel_filter_{current_time.strftime(time_format)}.xlsx"
    file_name = os.path.join(direktori, file_name)
    writer = pd.ExcelWriter(file_name, engine = 'xlsxwriter')
    
    df=pd.DataFrame({'Frekuensi (kHz)':freq_x,'Intensitas Bunyi (dB)':max_y}).to_excel(writer, sheet_name='Sheet1')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    worksheet = writer.sheets['Sheet1']
    worksheet.insert_image('D2', 'a', options={'image_data':buf})
    writer._save()
    buf.close()   

    plt.show() 
