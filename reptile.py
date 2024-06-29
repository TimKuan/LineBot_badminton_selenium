from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import util

def reptile(datalst:list):
    option = webdriver.ChromeOptions() 
    option.add_argument('--headless') # 無頭模式，開發完成之後再使用，可以完全背景執行，有機會變快。但無頭模式在某些網站會不能爬。
    option.add_argument("--window-size=1200,800") #設置視窗大小為寬度 1200px，高度 800px
    option.add_experimental_option('excludeSwitches', ['enable-automation']) # 開發者模式。可以避開某些防爬機制，有開有保佑
    option.add_argument(
            "--user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'")
    driver = webdriver.Chrome(options=option) # 啟動 chromedriver
    url = 'https://badminton.pintu.tw/search.php' # 指定網址
    driver.implicitly_wait(5) # 等待伺服器反應最多 5 秒，如果在時間到之前反應就提早結束等待
    driver.get(url) # 進入指定網址

    for index in range(len(datalst)): # 0縣市 , 1區域 , 2星期 , 3時間 , 4程度
        try:
            if datalst[index] != None:
                if index ==0:# 0縣市
                    city_drop_down = driver.find_element('css selector',"#city")
                    select = Select(city_drop_down)
                    select.select_by_visible_text(datalst[index])
                elif index ==1:# 1區域
                    District_drop_down = driver.find_element('css selector',"#area")
                    select = Select(District_drop_down)
                    select.select_by_visible_text(datalst[index])
                elif index ==2:# 2星期
                    weeklst = datalst[index]
                    for days in weeklst:
                        driver.find_element('css selector', f"input[type='checkbox'][value={days}]").click()
                elif index ==3:# 3時間
                    daylst = datalst[index]
                    for times in daylst:
                        driver.find_element('xpath', f"//input[@type='checkbox' and @value={times}]").click()
                elif index ==4:# 4程度
                    levels = datalst[index]
                    for lv in levels:
                        driver.find_element('xpath', f"//input[@type='checkbox' and @value={lv}]").click()          
        except NoSuchElementException:
            print('element not found')
            continue  
    #開始搜尋
    driver.find_element('css selector',"#form > button").click()
    driver.implicitly_wait(10) 
    #取得資料
    result = []
    try:
        elements = driver.find_elements('css selector','#holder > div:nth-child(8) > div:nth-child(2) > div > table > tbody > tr')
        if len(elements)>0:
          for i in range(len(elements)):
              element = elements[i]
              try:
                  #判別下次打球日期是否是今天之後 和 是否暫停開放場地 或者 報名人數已滿 
                  if util.filter_data(element):
                      result.append(util.analyze_reslut(element))
              except NoSuchElementException as e:
                  print("Element not found:", e)
                  continue
              if len(result) >=6:
                  break
        else:
            elements = driver.find_elements('css selector','#holder > div:nth-child(8) > div:nth-child(2) > div > font')
            result = elements[0].text
                  
    except NoSuchElementException:
         result= '場地皆已滿，請搜尋其他條件的場地'
    finally:
        # 在完成後關閉當前視窗
        driver.close()

        # 確保在結束時退出 WebDriver 會話
        driver.quit()          

    return result



