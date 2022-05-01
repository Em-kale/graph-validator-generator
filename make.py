
from selenium import webdriver 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import os 
import time
import re 

class ValidatorScraper():
    def __init__(self):
        self.url = "https://near-staking.com/" 
        #Set initial wait time for page to load, auto adjusts if too quick
        self.sleepValue = 1
        self.validators = [] 

        #make it so the browser GUI isn't activated
        chrome_options = Options()
        chrome_options.add_argument("--dns-prefetch-disable")
        chrome_options.add_argument("--headless")
 
        #initialize driver options=chrome_options
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    def getValidators(self):    #give page some time to load
        time.sleep(self.sleepValue)

        #Get all three main links: account account transaction hash, update transaction hash
        #We only care about update transaction hash, but unfortunately, no way to isolate it
        validators = self.driver.find_elements(By.XPATH, "//a[@class='MuiTypography-root MuiLink-root MuiLink-underlineNone MuiTypography-colorInherit']")
        
             #If less than 3 list elements, page didn't load enough, retry with longer loading time 
        if(len(validators) < 30):
            self.sleepValue = self.sleepValue + 1   
            self.getValidators() 
        else: 
            for i in validators:
                self.validators.append(i.get_attribute("href").split("/")[4])

    def safeRefresh(self): 
            try:
                self.driver.refresh()
            except TimeoutException as ex:
                self.safeRefresh()

    def run(self):
        try:
            self.driver.get(self.url)
        except TimeoutException as ex:
            self.safeRefresh()
         

        self.getValidators()
        
        self.driver.quit()
        return self.validators



class BlockScraper():
    def __init__(self, account):
        #get account and save to var
        self.account = account 
        self.url = f'https://explorer.near.org/accounts/{self.account}'
        
        #Initial values for the things we are going to look for
        self.hashLink = None 
        self.block = 0 

        #Set initial wait time for page to load, auto adjusts if too quick
        self.sleepValue = 1
        
        #make it so the browser GUI isn't activated
        chrome_options = Options()
        chrome_options.add_argument("--dns-prefetch-disable")
        chrome_options.add_argument("--headless")


        #initialize driver options=chrome_options
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)


    def safeRefresh(self): 
        try:
            self.driver.refresh()
        except TimeoutException as ex:
            self.safeRefresh()

    #Get link to page with block number of last deployment, click it
    def getBlockLink(self, type):
        #give page some time to load
        time.sleep(self.sleepValue)

        #Get all three main links: account account transaction hash, update transaction hash
        #We only care about update transaction hash, but unfortunately, no way to isolate it
        links = self.driver.find_elements(By.XPATH, "//div[@class='c-CardCellText-eLcwWo ml-auto align-self-center col-md-12 col-auto']/span/a")
        
        #If less than 3 list elements, page didn't load enough, retry with longer loading time 
        if(len(links) < 3):
            if(self.sleepValue < 10):
                self.sleepValue = self.sleepValue + 1
                self.safeRefresh()
                self.getBlockLink(type)
        else: 
            if type=='transaction':
                #navigate to transaction page
                links[2].click()
                time.sleep(self.sleepValue)
                self.getBlockLink('block')
            elif type=='block':
                links[2].click()
                time.sleep(self.sleepValue + 2)
                

                block = self.driver.find_element(By.TAG_NAME, "h1")
                self.block = block.text.split("#")[1]

            self.sleepValue=1; 
        
    def run(self): 
        try:
            self.driver.get(self.url)
        except TimeoutException as ex:
            print(ex)
            self.safeRefresh()
         
        
        self.getBlockLink('transaction')

        if self.block != 0:
            print(self.block)

        self.driver.quit()
        return self.block


class GraphMaker(): 
    def __init__(self): 
        self.data=[]
        self.vscraper = ValidatorScraper()

    def makeGraph(self, account): 
        #check if subgraph exists, if it doesn't make the directory 
        os.system(f"./graph_check.sh {account}")

    #make changes to template we copied
    def editTemplateCopy(self, name, block): 
        splitName = name.split(".") 
        #update subgraph.yaml
        yaml = open(f'generated_graphs/{name}/subgraph.yaml', 'r')
        yamlList = yaml.readlines() 
        yamlList[1] = f"description: NEAR Validator - {name}\n"
        yamlList[2] = f"repository: https://github.com/VitalPointAI/subgraph-{splitName[0]}-{splitName[1]}-near.git\n"
        yamlList[10] = f"      account: {name}\n"
        yamlList[11] = f"      startBlock: {block}\n"
        
        yaml = open(f'generated_graphs/{name}/subgraph.yaml', 'w')
        yaml.writelines(yamlList)
        yaml.close()

        #update package.json
       
        strippedName = re.sub('[^A-Za-z]+', '', splitName[0])
        json = open(f'generated_graphs/{name}/package.json', 'r')
        jsonList = json.readlines() 
        jsonList[1] = f'  "name":"near-validator-{splitName[0]}-{splitName[1]}-near",\n'
        jsonList[3] = '   "author": "Emmitt Luhning",\n'
        jsonList[4] = f'  "repository": "https://github.com/VitalPointAI/subgraph-{splitName[0]}-{splitName[1]}-near.git",\n'
        jsonList[9] = f'    "deploy": "graph deploy vitalpointai/{strippedName}validator --ipfs https://api.thegraph.com/ipfs/ --node https://api.thegraph.com/deploy/"\n'
        json = open(f'generated_graphs/{name}/package.json', 'w')
        json.writelines(jsonList)
        json.close()

    def deploy_to_hosted_service(self):
        os.system("")

    def run(self): 
        exclusionString = input("Enter validators to exclude, separate only by one space between each: ")
        self.enteredAccount = input("Enter Github account associated with hosted service: ")
        self.enteredPass = input("Enter Password: ")
        excluded = exclusionString.split(" ")
        for i in self.vscraper.run():
            excludedFlag = False
            for j in excluded:
                if(i==j):
                    excludedFlag = True; 
            if excludedFlag == False:
                print(i)
                bscraper = BlockScraper(i)
                self.data.append((i, bscraper.run()))
                self.makeGraph(i)
        print(self.data)
        for i in self.data:
            self.editTemplateCopy(i[0], i[1])
        print("PROCESS FINISHED")
    
    

maker = GraphMaker() 
maker.run()
