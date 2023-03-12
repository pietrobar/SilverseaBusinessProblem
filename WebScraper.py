import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

#URL = "https://www.rssc.com/cruises?source=featured"
URL = "https://www.rssc.com/cruises/"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def generator(start=0):
    num = start
    while True:
        yield num
        num += 1


def getCruises(url):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup.find_all("li", class_="cruiseList_item")

def getCruiseSummary(url):
    #To extract only prices it can be used directly bs4 since the page is not using JavaScript
    driver.get(url)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    cruiseSummary = {"ship":"","departs":"","itinerary":{},"suites":{},"hotels":{}}
    
    ship = soup.find("li",class_="-ship")
    ship = ship.find("div",class_="-primaryInfo").getText() + " " + ship.find("div",class_="-secondaryInfo").getText()
    cruiseSummary["ship"] = ship
    
    departs = soup.find("li", class_="-departs")
    departs = departs.find("div",class_="-primaryInfo").getText() + " " + departs.find("div",class_="-secondaryInfo").getText()
    cruiseSummary["departs"] = departs
    
    
    days = soup.find_all("td", class_="c179_table_body_row_cell -content")
    
    for day in days:
        progressive = day.find(class_="-day").getText()[1:]
        date = day.find(class_="-date").find(class_="-primaryInfo").getText() 
        city = day.find(class_="-port-city").getText()[1:][:-1]
        country = day.find(class_="-port-country").getText()[1:]

        cruiseSummary["itinerary"][progressive] = {"date":date,"city":city,"country":country}
        
    suites = soup.find(id="suites").find_all("li", class_="listing_item")
    suites = [x for x in suites if x.has_attr("data-fare")]
    
    for suite in suites:
        
        s_type = suite.find(class_="c299_header").getText()
        size = suite.find(class_="-size").find(class_="-primaryInfo").getText()
        fare = suite.find(class_="-fare").find(class_="-primaryInfo").getText()
        availability = suite.find(class_="-availability").find(class_="-secondaryInfo").getText()
        
        cruiseSummary["suites"][s_type] = {"size":size,"fare":fare,"availability":availability}
    

    hotelpre = soup.find(class_="c188_body").find(class_="label -tiny text-uppercase").getText()
    hotelpost = soup.find(class_="c249_body").find(class_="label -tiny text-uppercase").getText()
    
    cruiseSummary["hotels"]["pre"] = hotelpre
    cruiseSummary["hotels"]["post"] = hotelpost

    return cruiseSummary
        
    

def extractCruiseID(cruise):
    return cruise.select_one("div > input").get("id").split("-")[1]

def scrape():
    #GET FIRST PAGE
    cruises = []
    cruises.extend(getCruises(URL))
    #ALL OTHER PAGES
    # gen = generator(2)
    # while True:
    #     url = URL+"?pageNumber="+str(next(gen)) #or with second type of URL &pageNumber=
    #     print(url)
    #     cs = getCruises(url)
    #     if len(cs)>0:
    #         cruises.extend(cs)
    #     else:
    #         break
    
    
    
    for cruise in cruises:
        cruises_id = extractCruiseID(cruise)
        
        print(getCruiseSummary(URL+cruises_id+"/summary"))
        break

scrape()

