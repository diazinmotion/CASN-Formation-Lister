import os
import json
import requests
import csv

from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename

def getInstansi():
    # untuk daftar instansi yang sudah diolah
    __list_instansi = []

    dir_path = os.path.dirname(os.path.realpath(__file__))
    f = open(dir_path + '/source.json', 'w')

    # download list instansi terbaru dari server langsung
    instansi = requests.get("https://data-sscasn.bkn.go.id/spf/getInstansi?jenisPengadaan=2")
    if instansi.status_code == 200:
        f.write(instansi.text)
    
    f.close()

    # baca file json instansi
    dir_path = os.path.dirname(os.path.realpath(__file__))
    f = open(dir_path + '/source.json', 'r')
    data = json.load(f)

    # dapatkan hasil untuk direturn
    for v in data:
        __list_instansi.append(v)

    return __list_instansi

def scrapWeb():
    list = getInstansi()

    with open('results/formasi.csv', 'w', newline='') as csvfile:
        fieldnames = ['instansi', 'jabatan', 'lokasi', 'pendidikan', 'jenis_formasi', 'kebutuhan', 'saingan']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()

        for i in list:
            current_kode = i['kode']
            current_instansi = i['nama']

            # tampilkan log aktivitas
            print('Getting: {0}'.format(current_instansi), end=' ')

            URL = "https://data-sscasn.bkn.go.id/spf?jenisPengadaan=2&instansi={0}".format(current_kode)
            page = requests.get(URL)

            result = BeautifulSoup(page.content, "html.parser")

            if result:
                # dapatkan elemen dalam tbody tabel utama
                main_table = result.find("table", class_="table").find('tbody').find_all('tr')

                # masukkan dalam csv
                for v in main_table:
                    column_list = v.find_all('td')
                    writer.writerow(
                        {
                            'instansi': current_instansi, 
                            'jabatan': column_list[1].text.strip().replace('"', ''), 
                            'lokasi': column_list[2].text.strip().replace('"', ''),
                            'pendidikan': column_list[3].text.strip().replace('"', ''),
                            'jenis_formasi': column_list[4].text.strip().replace('"', ''),
                            'kebutuhan': column_list[6].text.strip().replace('"', ''),
                            'saingan': column_list[7].text.strip().replace('"', ''),
                        }
                    )
                
                print("[SUCCESS -> {0}]".format(len(main_table)))
            else:
                print('[ERROR]')


# main entrypoint
if __name__ == '__main__':
    scrapWeb()
