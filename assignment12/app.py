from selenium import webdriver

driver = webdriver.Chrome() 
driver.get('http://www.amazon.in')
driver.maximize_window()
driver.find_element_by_xpath("//input[@id='twotabsearchtextbox']").send_keys('iphones')
driver.find_element_by_xpath("//input[@id='nav-search-submit-button']").click()
list = driver.find_elements_by_xpath("//span[@class='a-size-medium a-color-base a-text-normal']")
# 00 products found

print(str(len(list)) + "products found")
for i in list:
    print(i.text)

driver.quit()