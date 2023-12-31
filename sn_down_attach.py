import time, os, csv, sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import urlparse, parse_qs

csvfilePath = "downloaded.csv"
NoattaCsvPath = "Noattachmetns.csv"
failedNavRange = "failedNavRange.csv"

# Abhi#456
# Pratik.Gole@cenveo.com

## Download Path, Change for each url downloads
downloadsPath = r"C:\Users\cammy\Downloads\attachments\2022"

os.chdir(downloadsPath)
options = webdriver.ChromeOptions()
prefs = {"download.default_directory": downloadsPath}
options.add_experimental_option("prefs", prefs)

## First login page and then the filtered url
baseUrl = f"https://cenveo.service-now.com/"
url = f"https://cenveo.service-now.com/u_undefined_cenveo_garnishments_list.do?sysparm_userpref_module=1da9aaa0db2faf04b31dd0b2ca96197a"

driver = webdriver.Chrome(options=options)

## Login, then enter Y once login is completed
driver.get(baseUrl)
loginOk = input("Enter Y if login is done - ")
if loginOk == "Y":
    pass
else:
    sys.exit()

driver.get(url)
time.sleep(4)
# sort by number
numBtn = driver.find_element(
    By.XPATH,
    "/html/body/div[1]/div[1]/span/div/div[7]/div[1]/table/thead/tr[1]/th[3]/span/a",
)
numBtn.click()
time.sleep(3)
# go to last page
lastBtn = driver.find_element(
    By.XPATH,
    "/html/body/div[1]/div[1]/span/div/div[7]/div[2]/table/tbody/tr/td[2]/span[1]/button[4]",
)
lastBtn.click()
time.sleep(20)

homeHandle = driver.current_window_handle
xpath = "/html/body/div[1]/div[1]/span/div/div[7]/div[1]/table/tbody/tr/td[3]/a"

# Ignore git codespaces
currentNav = "Last Page"

while "Showing rows 1 to" not in currentNav:
    homeHandle = driver.current_window_handle
    table = driver.find_elements(By.XPATH, xpath)
    if table:
        for trow in table:
            ## Open each ticket in new tab
            try:
                itemNo = trow.text
                ActionChains(driver).key_down(Keys.CONTROL).click(trow).key_up(
                    Keys.CONTROL
                ).perform()
                time.sleep(2)

                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(2)

            ## If failed go back to main tab
            except Exception as e:
                driver.switch_to.window(driver.window_handles[0])
                print("Errored out while getting row text or performing actions record")
                with open(failedNavRange, "a+", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([currentNav, "Errored out while scanning table", e])
                continue

            ## Download all attachments from newly opened page
            try:
                attachEle = driver.find_element(By.ID, "header_attachment_list_label")
                if attachEle.text:
                    attachEle.click()
                    time.sleep(1)
                    downAll = driver.find_element(By.ID, "download_all_button")
                    downAll.click()
                    time.sleep(4)
                    curretItemUrl = driver.current_url
                    qdict = parse_qs(urlparse(curretItemUrl).query)
                    downloadedFileName = (
                        qdict["sysparm_record_target"][0]
                        + "_"
                        + qdict["sys_id"][0]
                        + "_"
                        + "attachments.zip"
                    )
                    newFileName = itemNo + " - " + downloadedFileName
                    numEle = driver.find_element(
                        By.ID,
                        "sys_readonly." + qdict["sysparm_record_target"][0] + ".number",
                    )

                    # Rename here
                    currNumber = numEle.get_attribute("value")
                    if itemNo == currNumber:
                        print("Downloading attachments for -" + itemNo)
                        dl_wait = 0
                        while not os.path.exists(downloadedFileName) and dl_wait < 40:
                            time.sleep(1)
                            dl_wait += 1
                        try:
                            os.rename(downloadedFileName, newFileName)
                            if dl_wait > 40:
                                raise ()
                            with open(csvfilePath, "a+", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerow([str(itemNo), str(downloadedFileName)])
                        except Exception as e:
                            with open(failedNavRange, "a+", newline="") as f:
                                writer = csv.writer(f)
                                writer.writerow(
                                    [
                                        newFileName,
                                        "Failed to rename file",
                                        e,
                                    ]
                                )
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(2)
                else:
                    driver.close()
                    time.sleep(1)
                    with open(NoattaCsvPath, "a+", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([itemNo, "No Attachments"])
                    driver.switch_to.window(driver.window_handles[0])
                    continue
            # If failed keep a record
            except Exception as e:
                print(itemNo, " -Errored out while downloading attachments")
                driver.close()
                with open(NoattaCsvPath, "a+", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [itemNo, "Errored out while downloading attachments", e]
                    )
                driver.switch_to.window(driver.window_handles[0])
                continue

    else:
        print(currentNav, "Table body not found, skipping this entire page")
        with open(failedNavRange, "a+", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([currentNav, "no elements found skipping entire page", e])
        continue
    print(currentNav, "- Done, now moving to back page")
    driver.switch_to.window(homeHandle)
    try:
        if "Showing rows 1 to 10" in currentNav:
            break
        bkbtn = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div[1]/span/div/div[7]/div[2]/table/tbody/tr/td[2]/span[1]/button[2]",
        )
        bkbtn.click()
        time.sleep(3)
        navPag = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div[1]/span/div/div[7]/div[2]/table/tbody/tr/td[2]/span[1]/div/span[1]",
        )
        currentNav = navPag.text
        table = driver.find_elements(By.XPATH, xpath)
    except Exception as e:
        print("First page reached, Task Completed!!!")
