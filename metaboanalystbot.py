from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import requests
import os
import time
import base64

result = []
def check_for_errors(driver):
    try:
        error_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div/ul/li/span[2]"))
        )
        error_message = error_element.text
        print("An error occurred on the page：", error_message)
        return error_message
    except:
        print("There is no error message on the page")
        return True 

def crawler():
    csv_file_path = r"D:\User\Adison\desktop\MBweb\uploads\Adjusted_Label_Table.csv"
    data_prefix = os.path.splitext(os.path.basename(csv_file_path))[0]
    output_folder = r"D:\User\Adison\desktop\metaboanalyst_download"
    os.makedirs(output_folder, exist_ok=True)
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    driver.get("https://www.metaboanalyst.ca/MetaboAnalyst/upload/StatUploadView.xhtml")
    time.sleep(3)

    try:
        dropdown_label = driver.find_element(By.XPATH, "/html/body/div[3]/form/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[2]/td[2]/div/span")
        dropdown_label.click()
        time.sleep(1)
        options = driver.find_elements(By.CSS_SELECTOR, "ul[id$=':j_idt23_items'] > li")
        options[1].click()
    except Exception as e:
        print("can't find Samples in columns(paired)", e)
        driver.quit()
        return
    time.sleep(1)
    try:
        labels = driver.find_elements(By.XPATH, "//label[contains(text(), 'Peak intensities')]")
        if labels:
            labels[0].click()
        else:
            print("can't find『Peak intensities』")
    except Exception as e:
        print("can't find『Peak intensities』", e)
        driver.quit()
        return
    time.sleep(1)
    try:
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/form/table/tbody/tr[3]/td/table/tbody/tr/td[1]/table/tbody/tr[3]/td[2]/table/tbody/tr/td/span/span[1]/input"))
        )
        file_input.send_keys(csv_file_path)
        print("file upload success")
    except Exception as e:
        print("can't find the upload box：", e)
        driver.quit()
        return
    time.sleep(1)
    try:
        driver.find_element(By.XPATH, "/html/body/div[3]/form/table/tbody/tr[3]/td/table/tbody/tr/td[2]/button").click()
    except Exception as e:
        print("can't find submit button：", e)
        driver.quit()
        return
    time.sleep(10)
    try:
        global result
        tbody = driver.find_element(By.TAG_NAME, "tbody")
        rows = tbody.find_elements(By.TAG_NAME, "tr")
        result = "\n".join([row.text for row in rows])
        print(result)
    except Exception as e:
        print("can't get submit status report-1：", e)
        driver.quit()
        return
    try:
        driver.find_element(By.XPATH, "/html/body/div[3]/form/table/tbody/tr[3]/td/table/tbody/tr/td[2]/button").click()
    except Exception as e:
        print("can't find Proceed button：", e)
        driver.quit()
        return
    try:
        driver.find_element(By.XPATH,"/html/body/div[3]/table/tbody/tr[2]/td/form/table[2]/tbody/tr/td[2]/button").click()
    except Exception as e:
        print("can't find Data flitering's proceed button")
    time.sleep(3)
    try:
        driver.find_element(By.XPATH, "/html/body/div[3]/form/table/tbody/tr[5]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td[1]/div").click()
    except Exception as e:
        print("can't find normalization by sum button：", e)
        driver.quit()
        return
    time.sleep(1)
    try:
        driver.find_element(By.XPATH, "/html/body/div[3]/form/table/tbody/tr[5]/td/table/tbody/tr[4]/td/table/tbody/tr[3]/td[1]/div").click()
    except Exception as e:
        print("can't find log transformation button：", e)
        driver.quit()
        return
    time.sleep(1)
    try:
        driver.find_element(By.XPATH, "/html/body/div[3]/form/table/tbody/tr[5]/td/table/tbody/tr[6]/td/table/tbody/tr[3]/td[1]/div").click()
    except Exception as e:
        print("can't find auto scalling button：", e)
        driver.quit()
        return
    time.sleep(1)
    try:
        driver.find_element(By.XPATH, "/html/body/div[3]/form/table/tbody/tr[6]/td/table/tbody/tr/td[1]/button").click()
    except Exception as e:
        print("can't find Normalize button：", e)
        driver.quit()
        return
    time.sleep(1)
    try:
        driver.find_element(By.XPATH, "/html/body/div[3]/form/table/tbody/tr[6]/td/table/tbody/tr/td[2]/button").click()
    except Exception as e:
        print("can't find View button：", e)
        driver.quit()
        return
    time.sleep(3)
    # 抓取彈窗 HTML
    dialog = driver.find_element(By.XPATH, "/html/body/div[12]")
    html = dialog.get_attribute("innerHTML")
    soup = BeautifulSoup(html, "lxml") 

    # 定義目標圖片
    targets = {
        "Normalization": f"{data_prefix}_Normalization.png",
        "Sample Normalization": f"{data_prefix}_sample_normalization.png"
    }

    html_output = ""

    # 處理每個目標圖片
    for alt_text, file_name in targets.items():
        img_tag = soup.find("img", alt=alt_text)
        if img_tag:
            src = img_tag.get("src")
            img_url = urljoin(driver.current_url, src)
            save_path = os.path.join(output_folder, file_name)

        try:
            r = requests.get(img_url)
            with open(save_path, "wb") as f:
                f.write(r.content)
            html_output += f'<img src="{file_name}" alt="{file_name}"><br>\n'
        except Exception as e:
            print(f"download failed：{img_url}，error：{e}")
    else:
        print(f"can't find photo（alt='{alt_text}'）")

# 點擊 Statistics
    try:
        arrow_icon = driver.find_element(By.XPATH, "/html/body/div[4]/div/form/div/ul/li[4]/div/span[1]")  # 假設向下箭頭是button元素
        ActionChains(driver).move_to_element(arrow_icon).click().perform()
    except Exception as e:
        print("can't find drop down button：", e)
        driver.quit()
        return
    time.sleep(1)  # 等待 UI 展開
    try:
        fold_change = driver.find_element(By.XPATH, "/html/body/div[4]/div/form/div/ul/li[4]/ul/li[1]/div/span[3]/span")
        fold_change.click()
        check_for_errors(driver)
    except Exception as e:
        print("can't find Fold_change button：", e)
        driver.quit()
        return

# 等待 canvas 載入完成
    canvas = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "chart_canvas"))
    )

# 透過 JS 把 canvas 轉成 base64 圖片資料
    canvas_base64 = driver.execute_script("""
        var canvas = document.getElementById("chart_canvas");
        return canvas.toDataURL("image/png").substring(22); // 移除 data:image/png;base64, 的前綴
    """)

# 儲存圖片為 PNG
    output_path = os.path.join(output_folder, "FoldChangeChart.png")
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(canvas_base64))
    time.sleep(1)
#點擊T-test
    try:
        fold_change = driver.find_element(By.XPATH, "/html/body/div[4]/div/form/div/ul/li[4]/ul/li[2]/div")
        fold_change.click()
        check_for_errors(driver)
    except Exception as e:
        print("can't find T-test button：", e)
        driver.quit()
        return
# 透過 JS 把 canvas 轉成 base64 圖片資料
    canvas_base64 = driver.execute_script("""
        var canvas = document.getElementById("chart_canvas");
        return canvas.toDataURL("image/png").substring(22); // 移除 data:image/png;base64, 的前綴
    """)

# 儲存圖片為 PNG
    output_path = os.path.join(output_folder, "T-testChart.png")
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(canvas_base64))
    time.sleep(1)
#點擊ANOVA
    try:
        fold_change = driver.find_element(By.XPATH, "/html/body/div[4]/div/form/div/ul/li[4]/ul/li[4]/div")
        fold_change.click()
        check_for_errors(driver)
    except Exception as e:
        print("can't find ANOVA button：", e)
        driver.quit()
        return
# 透過 JS 把 canvas 轉成 base64 圖片資料
    canvas_base64 = driver.execute_script("""
        var canvas = document.getElementById("chart_canvas");
        return canvas.toDataURL("image/png").substring(22); // 移除 data:image/png;base64, 的前綴
    """)

# 儲存圖片為 PNG
    output_path = os.path.join(output_folder, "ANOVAChart.png")
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(canvas_base64))
    time.sleep(2)
# 關閉瀏覽器
    driver.quit()
def get_submit_status_report():
    try: 
        return result
    except Exception as e:
        print("can't get submit status report:", e)
        return None

    """ try:
        driver.find_element(By.ID, "form1:viewBn").click()
    except Exception as e:
        print("找不到View按鈕：", e)
    # 抓取彈窗 HTML
    dialog = driver.find_element(By.ID, "j_idt116")
    html = dialog.get_attribute("innerHTML")
    soup = BeautifulSoup(html, "lxml") 

# 定義目標圖片
targets = {
    "Normalization": f"{data_prefix}_Normalization.png",
    "Sample Normalization": f"{data_prefix}_sample_normalization.png"
}

html_output = ""

# 處理每個目標圖片
for alt_text, file_name in targets.items():
    img_tag = soup.find("img", alt=alt_text)
    if img_tag:
        src = img_tag.get("src")
        img_url = urljoin(driver.current_url, src)
        save_path = os.path.join(output_folder, file_name)

        try:
            r = requests.get(img_url)
            with open(save_path, "wb") as f:
                f.write(r.content)
            print(f"圖片下載成功：{file_name}")
            html_output += f'<img src="{file_name}" alt="{file_name}"><br>\n'
        except Exception as e:
            print(f"下載失敗：{img_url}，錯誤：{e}")
    else:
        print(f"⚠️ 找不到圖片（alt='{alt_text}'）")

# 儲存 HTML 預覽
html_file_path = os.path.join(output_folder, "images.html")
with open(html_file_path, "w", encoding="utf-8") as f:
    f.write(html_output)
print(f"📝 HTML 預覽完成：{html_file_path}") """


