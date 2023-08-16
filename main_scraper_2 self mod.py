from bs4 import BeautifulSoup
import pandas as pd

from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta



def setup_browser():
    options = Options()
    options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    driver_path = r"C:\Users\kayug\Desktop\myvenv1\drivers\geckodriver.exe"
    #options.add_argument("--headless")
    browser = webdriver.Firefox(service=Service(driver_path), options=options)
    return browser

def open_browser(browser):
    l_by_id = ["gh-la", #sets language to Eng
               "gh-eb-Geo-a-en"] #   language_toggle_2]
    l_by_css = [".gh-eb-Geo-flag.gh-sprRetina", #language_toggle_1
                ".gh-eb-li-a.gh-icon",#sets ship to US(toggle click)(1)
                ".menu-button__button.btn.btn--secondary", #sets ship to US (menu click & select)(2.1)
                ".menu-button__item span[data-country='USA|US']", #sets ship to US (menu click & select)(2.2)
                ".shipto__close-btn"] #close ship to
    wait = WebDriverWait(browser, 10)
    url = "https://www.ebay.com/"
    browser.get(url)
    ebay_home_logo = browser.find_element(By.ID, l_by_id[0])
    ebay_home_logo.click()
    language_toggle_1 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, l_by_css[0])))
    language_toggle_1.click()
    sleep(2)
    language_toggle_2 = wait.until(EC.element_to_be_clickable((By.ID, l_by_id[1])))
    language_toggle_2.click()
    sleep(2)  # for stable functioning
    for element in l_by_css[1:]:
        element_finder_id = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,element)))
        element_finder_id.click()
        sleep(1)

def set_parameter(search_word, browser):
    l_el_id = ["_nkw",#enter_keywords_bar
               "s0-1-17-4[0]-7[1]-_in_kw", #keywords_option_bar
               "s0-1-17-5[1]-[2]-LH_Sold", #sold_list_box
               "s0-1-17-6[3]-[2]-LH_BIN", #buy_it_now_box
               "s0-1-17-6[4]-[1]-LH_ItemCondition", #used_box
               "s0-1-17-6[7]-[4]-LH_LocatedIn", #located_in_box
               "s0-1-17-6[7]-5[@field[]]-_salic"] #located_in_bar
    l_el_css = [".btn.btn--primary"] #enter_button
    wait = WebDriverWait(browser, 10)
    advanced_setting = wait.until(EC.element_to_be_clickable((By.ID, "gh-as-a"))) #advanced_setting
    advanced_setting.click()
    for i in range(len(l_el_id)):
        element_finder = browser.find_element(By.ID, l_el_id[i])
        if i == 0:
            element_finder.click()
            element_finder.send_keys(search_word)
        elif i == 1:
            select_keywords_option = Select(element_finder)
            select_keywords_option.select_by_visible_text("Exact words, any order")
        elif i == 6:
            select_located_in = Select(element_finder)
            select_located_in.select_by_visible_text("Japan")
        else:
            element_finder.click()

    enter_button = browser.find_element(By.CSS_SELECTOR, l_el_css[0])
    enter_button.click()


def date_extraction(browser):
    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")
    soup_all = soup.find_all("div", attrs={"class": "s-item__info clearfix"}) # 各商品の文章要素全体
    item_date = None  # item_dateをループ外で使うために
    agg_list = []
    i = 0
    while i < num_item_look_up//60: #ページをめくる回数
        for j in range(len(soup_all)):  # 商品の名前と日付を取得するループ
            item_x = soup_all[j]
            item_name_0 = item_x.find("span", attrs={"role": "heading"})
            item_date_0 = item_x.find("span", attrs={"class": "POSITIVE"})
            if item_date_0:
                item_date = item_date_0.text.split(" ", 2)[2]
            else:
                print("読み込み中")  # もしデータが日付ではなかった場合の抜け道
            item_date = str(item_date)  # Noneをstrに
            item_name = item_name_0.text
            temp_dict = {}
            temp_dict[item_date] = item_name
            agg_list.append(temp_dict)  # 日付が同じものがオーバーライドされないために

        try:  # 次へボタンのクリック
            next_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".pagination__next.icon-link"))
            )

            # Scroll to the Next button and click it
            sleep(8) #ここが早すぎるとすぐにブロックされる
            browser.execute_script("arguments[0].scrollIntoView();", next_button)
            next_button.click()
        except Exception as e:
            print("An error occurred while clicking the Next button:", e)
        i += 1
    return agg_list
def data_sorting(agg_list):
    one_month_ago = datetime.now() - timedelta(days=30)

    # 同じワードを含むものを抽出
    month_list = [{date: item} for temp_dict in agg_list for date, item in temp_dict.items() if
                  date != "None" and datetime.strptime(date, '%b %d, %Y') > one_month_ago]
    all_list = []
    counter = 1
    items = [item_names for temp_dict in month_list for item_names in temp_dict.values()]
    print("month_list", month_list)
    print("items",items)

    for index_1, item_1 in enumerate(items):  # 取得してきたデータの商品名部分のみ抽出
        split_item_1 = set(item_1.split())
        # print("iteration1")
        # print("itemsリスト", items)
        # print(len(items[index_1 + 1:]))
        for index_2, item_2 in enumerate(items[index_1 + 1:], start=index_1 + 1):
            split_item_2 = set(item_2.split())
            # print("iteration2")
            # print("split_item_2:",split_item_2)
            # print("split_item_1:",split_item_1)
            common_words = split_item_2.intersection(split_item_1)
            # print("common_words:", common_words)
            # print("ナムコ", len(common_words))
            if len(common_words) >= num_co_words:
                # print("passed the if 1")
                # print("all_list:", all_list)
                if not any(item_2 in d.values() for d in all_list):
                    # print("item_1の名前", item_1)
                    # print("item_2の名前", item_2)
                    # print("入ったアイテムの名前", item_2)
                    # print("入ったアイテムのインデックス番号", items.index(item_2))
                    # print("index_2の値", index_2)
                    # print("入ったアイテム", month_list[index_2])
                    all_list.append(month_list[index_2])
                    index_item_2 = all_list.index((month_list[index_2]))
                    # print("①直後のall_listの状況", all_list)

                    if not any(item_1 in d.values() for d in all_list):
                        # print("counterの数", counter)
                        # print("入ったアイテムの名前", item_1)
                        # print("入ったアイテムのインデックス番号", items.index(item_1))
                        # print("index_1の値", index_1)
                        # print("入ったアイテム", month_list[index_1])
                        #all_list.insert(index_item_2,month_list[index_1])
                        modified_dict = {k: f"({counter})、{v}" for k, v in month_list[index_1].items()}
                        all_list.insert(index_item_2, modified_dict)
                        counter += 1
                        # print("②直後のall_listの状況", all_list)
                elif item_1 == item_2:
                    # print("入ったアイテムの名前", item_2)
                    # print("入ったアイテムのインデックス番号", items.index(item_2))
                    # print("index_2の値", index_2)
                    # print("入ったアイテム", month_list[index_2])
                    all_list.append(month_list[index_2])
            #         print("③直後のall_listの状況", all_list)
            # print("ループ後のall_listの状況", all_list)

    print(all_list)
    print(len(all_list))
    return all_list
def sort_for_csv(all_list):
    final_data = []
    for sub_dict in all_list:
        for date, item in sub_dict.items():
            temp_dict = {}
            temp_dict["Date Sold"] = date
            temp_dict["Name of Item"] = item
            final_data.append(temp_dict)
    print(final_data)
    return final_data

def import_to_csv(final_data):
    df = pd.DataFrame(final_data)
    df.index = df.index+1
    df.to_csv(f"{csv_file_name}.csv", encoding = "utf-8-sig",index_label="Index")



while True:
    search_word = input("検索キーワードを入力してください")

    possible_num_to_look_up = [60,120,180,240,300,360,420,480,520,600]
    while True:
        num_item_look_up = int(input("検索する商品数を選択してください: 60,120,180,240,300,360,420,480,520,600"))
        if num_item_look_up in possible_num_to_look_up:
            num_item_look_up= num_item_look_up
            break
        else:
            print("検索する商品数を選択肢の中から選んでください")

    while True:
        num_co_words = input("検索する重複単語数はいくつですか？")
        if int(num_co_words):
            num_co_words = int(num_co_words)
            break
        else:
            print("整数を入力してください")

    print("検索キーワード:",search_word)
    print("検索する商品数",num_item_look_up)
    print("検索する重複単語数:",num_co_words)

    while True:
        start_look_up = int(input("検索を開始しますか？: 1,yes 2,no"))
        if start_look_up ==1 or start_look_up==2:
            browser = setup_browser()
            open_browser(browser)
            set_parameter(search_word, browser)
            agg_list = date_extraction(browser)
            all_list = data_sorting(agg_list)
            final_data = sort_for_csv(all_list)
            break
        else:print("整数の1か2を入力してください。")

    print("検索結果", len(all_list))
    while True:
        proceed_import = input("検索結果をcsvファイルに出力しますか？: 1,yes 2,設定値を入力しなおす 3,プログラムを終了する")
        if int(proceed_import) ==1:
            csv_file_name = input("出力するファイル名を設定してください:")
            import_to_csv(final_data)
            exit()
        elif int(proceed_import) ==2:
            break
        elif int(proceed_import) ==3:
            exit()
        else:
            print("整数の1,2,3から選択してください")



