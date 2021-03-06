#!/usr/bin/python3
## ----------------------------------------------------------------------------
## Python Dependencies
import os
from copy import deepcopy
import datetime
import time
import urllib
import urllib.request
import requests
import json, argparse
from fpdf import FPDF
import shutil
from tinydb import TinyDB, Query

## ----------------------------------------------------------------------------
session = requests.Session()
db = TinyDB('db.json')

def getAccountDetails(username):
    baseUrl = "https://volition-node-beta.pancakehermit.com/accounts/" + username

    response = session.get(baseUrl)
    details = response.json()
    dumps(details,file_name=username+'/details.json')
    return details

def getAccountAssets(username):
    baseUrl = "https://volition-node-beta.pancakehermit.com/accounts/" + username + "/inventory/assets"

    response = session.get(baseUrl)
    assets = response.json()

    assetUrl = "https://volition-node-beta.pancakehermit.com/assets/"
    
    for i in range(0,len(assets["inventory"])):
        #print(assets["inventory"][i])
        response = session.get(assetUrl + assets["inventory"][i]["assetID"])
        fullAsset = response.json()
        #print(fullAsset)
        assets["inventory"][i].update({"fields" : fullAsset["asset"]["fields"]})

    dumps(assets,file_name=username+'/assets.json')
    return assets

def getAssetName(asset):
    assetUrl = "https://volition-node-beta.pancakehermit.com/assets/"

    #print(asset)
    response = session.get(assetUrl + asset)
    assetName = response.json()
    #print(assetName)
    assetName = assetName["asset"]["fields"]["name"]["value"]
    #print(assetName)
    #assetName = assetName[]

    return assetName


def getBlocks():
    baseUrl = "https://volition-node-beta.pancakehermit.com/blocks/"

    response = session.get(baseUrl)
    blocks = response.json()
    dumps(blocks,file_name='blocks.json')
    #print(blocks)
    return blocks

def createLog(blocks):
    #print(blocks["blocks"]["blocks"][0])
    t, blockNo = 0, len(blocks["blocks"]["blocks"][block]["transactions"])
    printProgressBar(t,blockNo)
    with open('log.txt','a') as f:
        for block in range(0,len(blocks["blocks"]["blocks"])):
            t +=1
            printProgressBar(t,blockNo)
            for transaction in range(0,len(blocks["blocks"]["blocks"][block]["transactions"])):
                body = blocks["blocks"]["blocks"][block]["transactions"][transaction]["body"]
                bodySplit=body.split(",")
                #print(body[0])
                if("accountName" in bodySplit[0]):
                    recipient = (bodySplit[0].split(":"))[1]
                    if ("SEND_VOL" in body):
                        amount = bodySplit[1].split(":")[1]
                        #print(amount)
                        if("accountName" in bodySplit[3]):
                            sender = (bodySplit[3].split(":"))[1]
                            #print(sender)
                            f.write(blocks["blocks"]["blocks"][block]["time"]+" : "+recipient+" received "+str(amount)+" VOL from "+sender+"\n\n")
                        else:
                            f.write(blocks["blocks"]["blocks"][block]["time"]+" : "+blocks["blocks"]["blocks"][block]["transactions"][transaction]["body"]+"\n\n")

                    elif ("SEND_ASSETS" in body):
                        sender = body.split('"accountName\":')
                        sender = sender[2].split(",")
                        sender = sender[0]
                        #print(sender)
                        assets = body.split("[")
                        assets = assets[1].split("]")
                        assets = assets[0]
                        assets = assets.replace('"','')
                        assets = assets.split(",")
                        #print(assets)
                        for asset in assets:
                            f.write(blocks["blocks"]["blocks"][block]["time"]+" : "+recipient+" received "+getAssetName(asset)+" from "+sender+"\n\n")
                            #print(getAssetName(asset))
                        
                ''' else:
                        f.write(blocks["blocks"]["blocks"][block]["time"]+" : "+blocks["blocks"]["blocks"][block]["transactions"][transaction]["body"]+"\n\n")

                else:
                    f.write(blocks["blocks"]["blocks"][block]["time"]+" : "+blocks["blocks"]["blocks"][block]["transactions"][transaction]["body"]+"\n\n")
                '''
    return

def updateLog():
    if not os.path.exists("blocks.json"):
        blocks = getBlocks()
        newBlocks = blocks
        blocksLen = 0
        newBlocksLen = len(newBlocks["blocks"]["blocks"])
    else:
        with open("blocks.json",'r') as f:
            blocks_load = f.read()
            blocks = json.loads(blocks_load)
            newBlocks = getBlocks()
            blocksLen = len(blocks["blocks"]["blocks"])
            newBlocksLen = len(newBlocks["blocks"]["blocks"])

            
    t, blockNo = 0, newBlocksLen - blocksLen
    if blockNo != 0:
        printProgressBar(t,blockNo)
    with open('log.txt','a') as f:
        for block in range(blocksLen,newBlocksLen):
            t+=1
            printProgressBar(t,blockNo)
            for transaction in range(0,len(newBlocks["blocks"]["blocks"][block]["transactions"])):
                body = newBlocks["blocks"]["blocks"][block]["transactions"][transaction]["body"]
                bodySplit=body.split(",")
                #print(body[0])
                if("accountName" in bodySplit[0]):
                    recipient = (bodySplit[0].split(":"))[1]
                    if ("SEND_VOL" in body):
                        amount = bodySplit[1].split(":")[1]
                        #print(amount)
                        if("accountName" in bodySplit[3]):
                            sender = (bodySplit[3].split(":"))[1]
                            #print(sender)
                            f.write(newBlocks["blocks"]["blocks"][block]["time"]+" : "+recipient+" received "+str(amount)+" VOL from "+sender+"\r\n"+"\r\n")
                        else:
                            f.write(newBlocks["blocks"]["blocks"][block]["time"]+" : "+newBlocks["blocks"]["blocks"][block]["transactions"][transaction]["body"]+"\r\n"+"\r\n")

                    elif ("SEND_ASSETS" in body):
                        sender = body.split('"accountName\":')
                        sender = sender[2].split(",")
                        sender = sender[0]
                        #print(sender)
                        assets = body.split("[")
                        assets = assets[1].split("]")
                        assets = assets[0]
                        assets = assets.replace('"','')
                        assets = assets.split(",")
                        #print(assets)
                        for asset in assets:
                            f.write(newBlocks["blocks"]["blocks"][block]["time"]+" : "+recipient+" received "+getAssetName(asset)+" from "+sender+"\r\n"+"\r\n")
                            #print(getAssetName(asset))
                        
                ''' else:
                        f.write(newBlocks["blocks"]["blocks"][block]["time"]+" : "+newBlocks["blocks"]["blocks"][block]["transactions"][transaction]["body"]+"\r\n"+"\r\n")

                else:
                    f.write(newBlocks["blocks"]["blocks"][block]["time"]+" : "+newBlocks["blocks"]["blocks"][block]["transactions"][transaction]["body"]+""\r\n"+"\r\n")
                '''
    return 

def extractFields(card):
    #card = '"1-C-90-3":{"fields":{"setID":{"type":"NUMERIC","value":1,"mutable":false},"assetType":{"type":"STRING","value":"C","mutable":false},"assetID":{"type":"NUMERIC","value":90,"mutable":false},"version":{"type":"NUMERIC","value":3,"mutable":false},"alternate":{"type":"STRING","value":"","mutable":false},"name":{"type":"STRING","value":"You\'re Comin\' With Me","mutable":false},"layout":{"type":"STRING","value":"trap.1, T","mutable":true},"layout_prefix":{"type":"STRING","value":"trap.1","mutable":false},"layout_color":{"type":"STRING","value":"T","mutable":false},"group":{"type":"STRING","value":"<@T-Group>","mutable":false},"totalclout":{"type":"NUMERIC","value":6,"mutable":true},"clout":{"type":"STRING","value":"3<$icon_y:-20%><@T><$> 3<$icon_y:-20%><@O><$>","mutable":true},"TYPE":{"type":"STRING","value":"","mutable":false},"supertype":{"type":"STRING","value":"","mutable":false},"type":{"type":"STRING","value":"Trap","mutable":false},"subtype":{"type":"STRING","value":"","mutable":false},"rules":{"type":"STRING","value":"If one or more of your mortals were destroyed this turn, you may destroy up to 2 mortals.","mutable":true},"RULESCRAFT":{"type":"STRING","value":"","mutable":false},"attack":{"type":"STRING","value":"","mutable":true},"defense":{"type":"STRING","value":"","mutable":true},"slot":{"type":"STRING","value":"","mutable":true},"set":{"type":"STRING","value":"The Most Beta","mutable":false},"rarity":{"type":"STRING","value":"<$95% #0033ff>UNCOMMON<$>","mutable":true},"setNumber":{"type":"STRING","value":"195/200","mutable":false},"ARTIST":{"type":"STRING","value":"Arty McArtison","mutable":true},"IMAGE":{"type":"STRING","value":"https://i.imgur.com/u4fudnh.jpg","mutable":true},"image-overlay":{"type":"STRING","value":"","mutable":false},"image-overlay2":{"type":"STRING","value":"","mutable":true},"flavor":{"type":"STRING","value":"Bring me pain and I\'ll bring you with.","mutable":false},"RARITY":{"type":"STRING","value":"uncommon","mutable":true},"MAX_SLOTS":{"type":"NUMERIC","value":0,"mutable":false},"USED_SLOTS":{"type":"NUMERIC","value":0,"mutable":true},"C_ART":{"type":"NUMERIC","value":0,"mutable":true},"ACLOUT":{"type":"NUMERIC","value":0,"mutable":true},"BCLOUT":{"type":"NUMERIC","value":0,"mutable":true},"DCLOUT":{"type":"NUMERIC","value":0,"mutable":true},"ECLOUT":{"type":"NUMERIC","value":0,"mutable":true},"GCLOUT":{"type":"NUMERIC","value":0,"mutable":true},"TCLOUT":{"type":"NUMERIC","value":3,"mutable":true},"OCLOUT":{"type":"NUMERIC","value":3,"mutable":true}'
    #print(card.find("fields"))
    fieldsDict = {}
    if card.find("fields") != -1:
        cardChopped = card[card.find("fields")+9 :] #Use method to count how many characters are needed to be inserted
        #print(cardChopped)
        fields = cardChopped.split("},")
        #print(fields)
        fieldNo = cardChopped.count("{")
        for i in range(0,fieldNo):
            fieldName = (cardChopped.split("},")[i]).split(":")[0]
            fieldsDict.update({fieldName : {}})
            fieldsChopped = fields[i][fields[i].find('"type":"') :]
            fieldsChopped = fieldsChopped.split("}")[0]
            fieldType = fieldsChopped.split(',"')[0]
            fieldType = fieldType.split(":")
            fieldValue = '"' + fieldsChopped.split(',"')[1]
            fieldValueName = fieldValue.split(":")[0]
            fieldValue = fieldValue[fieldValue.find('"value":') +8 :]
            fieldMutable = '"' + fieldsChopped.split(',"')[2]
            fieldMutable = fieldMutable.split(":")
            #print(fieldValue)
            fieldsDict[fieldName].update( {fieldType[0] : fieldType[1]} )
            fieldsDict[fieldName].update({fieldValueName : fieldValue})
            fieldsDict[fieldName].update({fieldMutable[0] : fieldMutable[1]})
        #print(fieldsDict)
    return fieldsDict


def updateDB():
    if not os.path.exists("blocks.json"):
        blocks = getBlocks()
        newBlocks = blocks
        blocksLen = 0
        newBlocksLen = len(newBlocks["blocks"]["blocks"])
    else:
        with open("blocks.json",'r') as f:
            blocks_load = f.read()
            blocks = json.loads(blocks_load)
            newBlocks = getBlocks()
            blocksLen = len(blocks["blocks"]["blocks"])
            newBlocksLen = len(newBlocks["blocks"]["blocks"])

    if not os.path.exists("db.json"):
        blocksLen = 0
    elif os.stat("db.json").st_size == 0:
        blocksLen = 0
            
    t, blockNo = 0, newBlocksLen - blocksLen
    if blockNo != 0:
        printProgressBar(t,blockNo)
    database = ""
    with open('schema.txt','a') as f:
        #
        #newIndex = 850
        #
        for block in range(blocksLen,newBlocksLen):
            t+=1
            value = ""
            printProgressBar(t,blockNo)
            fields = ["setID","assetType","assetID","version","alternate","name","layout","layout_prefix","layout_color","group","totalclout","clout","TYPE","supertype","type","subtype","rules","RULESCRAFT","attack","defense","slot","set","rarity","setNumber","ARTIST","IMAGE","image-overlay","flavor","RARITY","MAX_SLOTS","USED_SLOTS","C_ART","ACLOUT","BCLOUT","DCLOUT","ECLOUT","GCLOUT","TCLOUT","OCLOUT"]
            fields2 = ["type","value","mutable"]
            for transaction in range(0,len(newBlocks["blocks"]["blocks"][block]["transactions"])):
                body = newBlocks["blocks"]["blocks"][block]["transactions"][transaction]["body"]
                if ("PUBLISH_SCHEMA" in body):
                    releaseVal = body[(body.find("release")+9) : (body.find("}}",body.find("release")+9))]
                    cards = body[(body.find("definitions")+14) : (body.find("}}}},",body.find("definitions")+14))+3]
                    cards = cards.split("}}},")
                    for i in range(0,len(cards)):
                        cards[i]= str(cards[i])+"}"
                    #print(cards)
                    #print("\n")
                    for card in range(0,len(cards)):
                        cardID = cards[card].split(":")[0]
                        if cardID.find("-C-") != -1:
                            #print(cardID)
                            if cardID.split("-")[1] == 'C':
                                cardDict = {}
                                cardDict.update({cardID : {}})
                                cardDict[cardID].update({"fields" : extractFields(cards[card])})
                                #print(cardID)
                                #print("\n")
                                cardDict.update({"release" : releaseVal})
                                #print(cardDict)
                                f.write(str(cardDict)+"\r\n"+"\r\n")
                                db.insert(cardDict)
                        
                    #f.write(body+"\r\n"+"\r\n") #To include other transactions and assets too
        database = db
        #print(db)
    return database

def query():
    
    #test = Query()
    #test1 = db.search(test.release == '"Volition","major":0,"minor":0,"revision":8')
    #print(test1)
    #return response
    return

# Print iterations progress
def printProgressBar (
        iteration, 
        total, 
        prefix = 'Progress:', 
        suffix = 'Complete', 
        decimals = 1, 
        length = 50, 
        fill = '█'):

    time.sleep(0.1)
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

#---------------------------------

def getArguments():
    global baseUrl
    parser = argparse.ArgumentParser(description='Volition API data handling script')
    parser.add_argument('-u','--username', help='Specific username', required=False)
    parser.add_argument('-log','--log', help='Download the full log', action='store_true', required=False)
    parser.add_argument('-db','--db', help='Update the database', action='store_true', required=False)
    parser.add_argument('-d','--dateRange',help='Specify a date range: dd-mm-yyyy:dd-mm-yyyy',required=False)
    parser.add_argument('-r','--report',help='Generate League table report',action='store_true',required=False)
    
    args = vars(parser.parse_args())
    return args
#-----------------------------------------------------------------------------

#---------------------------------

class PDF(FPDF):
    def header(self,logo):
        # Logo
        self.image(logo, 10, 8, 33)
        #self.image('team_uk_logo.jpeg', 10, 8, 33)
        # Times bold 15
        self.set_font('Times', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(100, 10, 'League Table', 1, 0, 'C')
        # Line break
        self.ln(20)

        # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Times', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

        #Chapter title
    def chapter_title(self, title):
        # Arial 12
        self.set_font('Times', 'B', 12)
        # Background color
        self.set_fill_color(200, 220, 255)
        # Line break
        self.ln(10)
        # Title
        self.cell(0, 6, '%s' % (title), 0, 1, 'L', 1)
        # Line break
        self.ln(0)

        #Chapter body
    def chapter_body(self, content_dict):
        # Times 12
        self.set_font('Times', '', 12)
        # Output justified text
        for field in content_dict:
            self.cell(0, 5, field+": "+content_dict[field], 1, 1)
        # Line break
        self.ln()

        #Print chapter
    def print_chapter(self, title, content, logo):
        self.add_page('L', format = 'a4', logo = logo)
        self.chapter_title(title)
        self.chapter_body(content)

    def print_list(self,data):
        self.cell()

    def fancy_table(this,header,data):
        #Colors, line width and bold font
        this.set_fill_color(255,0,0)
        this.set_text_color(255)
        this.set_draw_color(128,0,0)
        this.set_line_width(.3)
        this.set_font('Times','B')
        #Header
        w=[]
        column_no = len(header)
        page_width = 277 #magic number for A4 in mm
        column_width = page_width/column_no
        for i in range(0,column_no):
            w.append(column_width)
        for i in range(0,column_no):
            this.cell(w[i],7,header[i],1,0,'C',1)
        this.ln()
        #Color and font restoration
        this.set_fill_color(224,235,255)
        this.set_text_color(0)
        this.set_font('Times')
        #Data
        fill=0
        for row in data:
            for i in range(0,column_no):
                this.cell(w[i],6,row[i],'LR',0,'C',fill)
                #print(row[i])
            this.ln()
            fill=not fill
        this.cell(sum(w),0,'','T')

    def dynamic_table(this,header,data):
        #Colors, line width and bold font
        this.set_fill_color(255,0,0)
        this.set_text_color(255)
        this.set_draw_color(128,0,0)
        this.set_line_width(.3)
        this.set_font('Times','B')
        #Header
        w=[]
        column_no = len(header)
        page_width = 277 #magic number for A4 in mm
        column_width = page_width/column_no
        for i in range(0,column_no):
            w.append(column_width)
        for i in range(0,column_no):
            this.cell(w[i],7,header[i],1,0,'C',1)
        this.ln()
        #Color and font restoration
        this.set_fill_color(224,235,255)
        this.set_text_color(0)
        this.set_font('Times')
        #Data
        fill=0
        for row in data:
            for i in range(0,column_no):
                this.multi_cell(w[i],6,row[i],1,'L',fill)
                fill=not fill
                this.multi_cell(w[i],6,row[i+1],1,'L',fill)
                fill=not fill
                this.ln()
        this.cell(sum(w),0,'','T')
        return

#---------------------------------

def output_pdf(pages, filename):
    pdf = FPDF()
    pdf.set_font('Times','B',12)
    for image in pages:
        pdf.add_page('L')
        pdf.set_xy(0,0)
        pdf.image(image, x = None, y = None, w = 0, h = 0, type = '', link = '')
    pdf.output(filename, 'F')
    return


#---------------------------------


#-----------------------------------------------------------------------------
def main():
    username = ""
    args = getArguments()
    
    if args["username"]:
        username = args["username"]
        if not os.path.exists(username):
            os.mkdir(username)
        getAccountDetails(username)
        getAccountAssets(username)

    if args["log"]:
        updateLog()


    if args["db"]:
        database = updateDB()
        print(database)

	
#-----------------------------------------------------------------------------
def pp(c):
    print( json.dumps(c, indent=4) )

def dumps(page, pretty = True, file_name = "results.json"):
    try:
        if pretty: page = json.dumps(page, indent=4)
        with open(file_name,"w+") as file:
            file.write(page)
    finally:
        return page

def handle_resp(resp, root=""):
    if resp.status_code != 200: 
        print(resp.text)
        return None
    node = resp.json()
    if root in node: node = node[root]
    if node == None or len(node) == 0: return None
    return node

def get_url(url, root=""):
    resp = iq_session.get(url)
    return handle_resp(resp, root)

def post_url(url, params, root=""):
    resp = iq_session.post(url, json=params)
    return handle_resp(resp, root)

def get_epoch(epoch_ms):
    dt_ = datetime.datetime.fromtimestamp(epoch_ms/1000)
    return dt_.strftime("%Y-%m-%d %H:%M:%S")

def get_applicationId(publicId):
    url = f'{iq_url}/api/v2/applications?publicId={publicId}'
    apps = get_url(url, "applications")
    if apps == None: return None
    return apps[0]['id']

def get_reportId(applicationId, stageId):
    url = f"{iq_url}/api/v2/reports/applications/{applicationId}"
    reports = get_url(url)
    for report in reports:
        if report["stage"] in stageId:
            return report["reportHtmlUrl"].split("/")[-1]

def get_policy_violations(publicId, reportId):
    url = f'{iq_url}/api/v2/applications/{publicId}/reports/{reportId}/policy'
    return get_url(url)

def get_recommendation(component, applicationId, stageId):
    url = f'{iq_url}/api/v2/components/remediation/application/{applicationId}?stageId={stageId}'
    return post_url(url, component)

def get_last_version(component):
    url = f"{iq_url}/api/v2/components/versions"
    return post_url(url, component)
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    main()

