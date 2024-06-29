import constant
from datetime import datetime
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

# 分析使用者傳入的文字訊息，並返回一個用於進一步處理的資料結構
def analyze_text(text:str):
    datalst = [None,None,None,None,None] # 0縣市 , 1區域 , 2星期 , 3時間 , 4程度
    keyword_lst = text.split()
    while len(keyword_lst) > 0:
        keyword = keyword_lst.pop(0)
        if keyword in constant.taiwan_regions:
            datalst[0] = keyword
        elif '區' in keyword or '鄉' in keyword or '鎮' in keyword:
            if datalst[0] !=None:
                region  = datalst[0]
                if keyword in constant.taiwan_district.get(region):
                    datalst[1] = keyword
            elif len(keyword_lst)>1 : #如果還沒判斷區域，則先略過  
                keyword_lst.append(keyword)
        elif keyword in constant.weekdays_chinese:
            if datalst[2] !=None:
                datalst[2].append(keyword)
            else:
                datalst[2] = [keyword] 
        elif keyword in constant.daytimes_chinese:
            if datalst[3] !=None:
                datalst[3].append(keyword)
            else:
                datalst[3] = [keyword]
        elif keyword in constant.level_chinese:
            if datalst[4] !=None:
                datalst[4].append(keyword)
            else:
                datalst[4] = [keyword]
    return datalst            

# 將符合需求的元素資料取出
def analyze_reslut(element:WebElement):
    # 0球隊名稱 , 1縣市區域 , 2打球時間 , 3地點 , 4.聯絡人 5.程度 6. 下一次打球時日期 7.費用 ８. 聯絡資訊
    datalst = [None,None,None,None,None,None,None,None,None]

    try:# 0球隊名稱
        name = element.find_element('css selector','td.name').text 
        if name:
            datalst[0]= name
    except NoSuchElementException:
        pass    

    try:#1縣市區域
        area = element.find_element('css selector','td:nth-child(2)').text
        if area:
            datalst[1]= area
    except NoSuchElementException:
        pass   
    
    try:#2打球時間
        play_time = element.find_element('css selector','td:nth-child(3)').text
        if play_time:
            datalst[2]= play_time
    except NoSuchElementException:
        pass  


    try:#3地點 #holder > div:nth-child(8) > div:nth-child(2) > div > table > tbody > tr:nth-child(1) > td:nth-child(4)
        play_area = element.find_element('css selector','td:nth-child(4)').text 
        if play_area:
            datalst[3]= play_area

    except NoSuchElementException:
        pass  

    try:#4.聯絡人
        contack_person =element.find_element('css selector','td.contact_person1').text 
        if contack_person:
            datalst[4]= contack_person
    except NoSuchElementException:
        pass  
    
    try:#5.程度
        level =element.find_element('css selector','td.level').text 
        if level:
            datalst[5]= level
    except NoSuchElementException:
        pass    

    try:#6. 下一次打球時日期 
        next_date = element.find_element('css selector','td.next_play_date').text
        if next_date:
            datalst[6]= next_date

    except NoSuchElementException:
        pass  

    try:#7.費用
        fee =element.find_element('css selector','td.fee_once').text 
        if fee:
            datalst[7]= fee
    except NoSuchElementException:
        pass   

    try:#８. 聯絡資訊
        href = element.find_element('css selector','a').get_attribute("href")
        if href:
            datalst[8]= href
    except NoSuchElementException:
        pass   
    return datalst

# 將結果 組成 使用者要看的內容        
def analyze_return(resutlst:list):
    # 0球隊名稱 , 1縣市區域 , 2打球時間 , 3地點 , 4.聯絡人 5.程度 6. 下一次打球時日期 7.費用 ８. 聯絡資訊
    title = ['球隊名稱','縣市區域','打球時間','地點','聯絡人','程度','下一次打球時日期','費用','聯絡資訊']
    content = ''
    for index in range(len(resutlst)):
        if resutlst[index]!=None:
            content += f'{title[index]}:{resutlst[index]}\n'
    return content        

#篩選符合需求的結果
def filter_data(element:WebElement):
    try:
        # 取得下次打球日期，判斷是否資訊過舊
        next_date_str = element.find_element('css selector','td.next_play_date').text
        next_date = datetime.strptime(next_date_str, '%Y-%m-%d')
        today = datetime.today().date()
        if next_date.date()> today:
            try:# 判斷提示資訊，判別是否已滿團 或者 場地暫停開房
                tip_tag = element.find_elements('css selector','a')
                for index in range(len(tip_tag)):
                    div_tag_style = tip_tag[index].find_element('css selector','div').get_attribute('style')
                    if 'red' in div_tag_style or 'purple' in div_tag_style:
                        return False
            except  NoSuchElementException:
                return True     

        else:
            return False    
    except AttributeError:
        return False
