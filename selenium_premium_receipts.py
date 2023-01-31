import sys
import time

from selenium import webdriver
from selenium.webdriver.support.ui import Select

if len(sys.argv) > 1:
    end_date = sys.argv[1]

else:
    end_date = time.strftime("%d/%m/%Y")


driver = webdriver.Firefox()

driver.get(
    "http://10.200.41.130:8080/NeftPortal/neft/RollIdentifier.do?empNo=44515&empName=.%20BARNEEDHAR%20VIGNESHWAR%20G&offCode=500200&userId=BARNEEDHAR"
)

select = Select(driver.find_element("name", "role"))
select.select_by_visible_text("Approver")

driver.get(
    "http://10.200.41.130:8080/NeftPortal/neft/TransactionDetailsReportByOfficeCode.do?parameter=searchByOfficeCode&param=colreport"
)


driver.execute_script(
    """var elts = document.getElementsByClassName("tdval");

for(var e = 0; e < elts.length; e++) {
   var elt = elts[e];

   elt.removeAttribute("readonly");
}  ;"""
)

select_date = driver.find_element("name", "fromdate")
select_date.send_keys("01/04/2022")


select_to_date = driver.find_element("name", "todate")
select_to_date.send_keys(end_date)


driver.find_element("xpath", "(//input[@name='fetchReport'])[2]").click()

driver.quit()
