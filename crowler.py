import csv
import requests
from bs4 import BeautifulSoup
import validators
import pandas as pd

html_filename = "output.html"
def clean_text(text):
    return text.strip().replace('\t', '').replace('\f', '').replace('\r', '').replace('\n', '').replace('خطبه نماز جمعه', '')
def update_html_table(csv_filename='khotbeh_data.csv', html_filename='output.html'):
    try:
        # خواندن داده‌های CSV
        with open(csv_filename, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            data = list(reader)


        # ساخت کد HTML
        html_content = """
        <!DOCTYPE html>
        <html lang="fa">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>جدول خطبه‌ها</title>
            <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    font-family: Arial, sans-serif;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: center;
                }
                th {
                    background-color: #f4f4f4;
                }
            </style>
        </head>
        <body>
            <h1 style="text-align: center;">جدول خطبه‌ها</h1>
            <table>
        """

        # اضافه کردن سرصفحه جدول
        if data:
            headers = data[0]
            html_content += "<tr>"
            for header in headers:
                html_content += f"<th>{header}</th>"
            html_content += "</tr>"

        # اضافه کردن سطرهای داده
        for row in data[1:]:
            html_content += "<tr>"
            for cell in row:
                html_content += f"<td>{cell}</td>"
            html_content += "</tr>"

        # بستن تگ‌های HTML
        html_content += """
            </table>
        </body>
        </html>
        """

        # نوشتن کد HTML در فایل
        with open(html_filename, mode='w', encoding='utf-8') as file:
            file.write(html_content)

        print("فایل HTML با موفقیت به‌روزرسانی شد.")
    except Exception as e:
        print(f"خطایی رخ داد: {e}")

# تعریف نام فایل CSV
filename = 'khotbeh_data.csv'
with open(filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['تاریخ خطبه', 'عنوان خطبه', 'نام امام جمعه', 'متن خطبه'])

# گرفتن نام شهر از کاربر
#city_name = input("لطفاً نام شهر مورد نظر خود را جهت دریافت خطبه ها وارد کنید: ")
city_name = 'کرج'
# لینک پایه
base_url = "https://karbar.ejna.ir/khotbeh-search?q="
# ترکیب نام شهر با لینک
final_url = base_url + city_name
print(final_url)



# صفحه نتایج شهر جستجو شده و سپس وارد اولین لینک جستجو شدن
response = requests.get(final_url)
html_content = response.content
soup = BeautifulSoup(html_content, 'html.parser')
all_tags = soup.find_all(True)  
for tag in all_tags:
    if tag.has_attr('href'):  
        href_value = tag['href'] 
        if 'khotbeh?khotbehId' in href_value :  
             break
base_url = "https://karbar.ejna.ir"
final_url = base_url + href_value
print (final_url)




# ورود به صفحه اولین نتیجه صفحه جستجو و پیدا کردن تگ آرشیو خطبه های آن شهر
response = requests.get(final_url)
html_content = response.content
soup = BeautifulSoup(html_content, 'html.parser')
all_tags = soup.find_all(True)  
for tag in all_tags:
    if tag.has_attr('href'):  
        href_value = tag['href']  
        if 'khotbeh-archive' in href_value :  
             break
base_url = "https://karbar.ejna.ir"
final_url = base_url + href_value





#ورود به لینک آرشیو خطبه های آن شهر 
response = requests.get(final_url)
html_content = response.content
soup = BeautifulSoup(html_content, 'html.parser')
all_tags = soup.find_all(True)  




# شروع حلقه چک صفحات
pn = 0 # pagenumber
href_values = []
id_list = []  
data = []


while True:
    pn += 1
    print(f"صفحه{pn}")  
    url = f"{final_url}&page={pn}"

    if not validators.url(url): # چک کردن وجود یا عدم وجود صفحه برای رسیدن به آخرین صفحه 
        print("لینک معتبر نیست.")
    else:
        try:
            response = requests.get(url, timeout=5)  # ارسال درخواست GET
            if response.status_code == 200:
                print("لینک وجود دارد و درخواست موفق بود.")
            else:
                print(f"لینک وجود ندارد یا خطایی رخ داد: {response.status_code}")
                break
        except requests.exceptions.RequestException as e:
            print(f"مشکلی در اتصال به لینک رخ داد: {e}")
            break

    
    response = requests.get(url) # در صورتی که لینک وجود داشت وارد صفحه می شود
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    all_tags = soup.find_all(True)

    if not soup.find(class_="khotbeh-archive-item"): #چک می کند ببیند آیا آیتم آرشیوی در آن صفحه هست یا نه 
        break
        

    id_list.clear()

    for tag in all_tags: # پیدا کردن تمام لینک های خطبه ها در صفحه فعلی آرشیو
        if tag.has_attr('href'):  
            href_value = tag['href'] 
            if 'khotbeh?khotbehId' in href_value :     
                href_values.append(href_value)
                id_list.append(href_value.split('=')[1])
             
   

 


    for i in range(len(id_list)): # وارد شدن به تک تک صفحه خطبه های پیدا شده در صفحه فعلی آرشیوی
        print(f"خطبه{i+1}")

        url = "https://karbar.ejna.ir/khotbeh?khotbehId=" + id_list[i]
        response = requests.get(url)
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')
        all_tags = soup.find_all(True)
        khdate = ''
        khtitle = ''
        khname = ''
        khtext = ''
        kh12 = 0
        for tag in all_tags:
            
            if tag.has_attr('class'):
             
                if tag['class'] == ['khotbeh-date']:
                    khdate = clean_text(tag.text)
                       
                if tag['class'] == ['khotbeh-title-parent']:          
                    khtitle = clean_text(tag.text)
                
                if tag['class'] == ['imamjomeh-details-field', 'imamjomeh-name']:  
                    khname = clean_text(tag.text)
                               
                if tag['class'] == ['khotbeh-text']:             
                    if kh12 == 0:
                        khtext += (f"\n\n <b>خطبه اول  </b> \n\n {tag.text}")
                        kh12 = 1
                    else:
                        khtext += (f"\n\n <b>خطبه دوم  </b> \n\n {tag.text}")

        data = [khdate ,khtitle , khname, f"\n <h1>خطبه{((pn-1)*12)+(i+1)}</h1> \n" + khtext  ]   # insert in csv file
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file) 
            writer.writerow(data)
                
                
        update_html_table(csv_filename='khotbeh_data.csv', html_filename='output.html') # update html file


print(f'تعداد کل صفحات{pn}')
print(f'تعداد کل خطبه ها{len(href_values)}')
print('پایان')

