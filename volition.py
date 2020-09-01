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
    with open('log.txt','a') as f:
        for block in range(0,len(blocks["blocks"]["blocks"])):
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

def updateLog(blocks,newBlocks):
    with open('log.txt','a') as f:
        newLen = len(newBlocks["blocks"]["blocks"]) - len(blocks["blocks"]["blocks"])
        if newLen == 0:
            newIndex = 0
        else:
            newIndex = len(blocks["blocks"]["blocks"])
            
        #print(newIndex)
        #print(newLen)
        for block in range(newIndex,len(newBlocks["blocks"]["blocks"])):
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

def updateDB(blocks):
    database = ""
    print(database)
    return database

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
    t, graphNo = 0, 4
    printProgressBar(t,graphNo)
    username = ""
    args = getArguments()


    t +=1
    printProgressBar(t,graphNo)

    
    if args["username"]:
        username = args["username"]
        if not os.path.exists(username):
            os.mkdir(username)
        getAccountDetails(username)
        getAccountAssets(username)
        #getPlayerStats(username)

    t +=1
    printProgressBar(t,graphNo)

    if args["log"]:
        if not os.path.exists("blocks.json"):
            blocks = getBlocks()
            newBlocks = blocks
        else:
            with open("blocks.json",'r') as f:
                blocks_load = f.read()
            blocks = json.loads(blocks_load)
            newBlocks = getBlocks()
            
        #if not os.path.exists("log.txt"):
        #    createLog(blocks)
        #else:
        #    updateLog(blocks,newBlocks)

        updateLog(blocks,newBlocks)


    t +=1
    printProgressBar(t,graphNo)


    if args["db"]:
        if not os.path.exists("blocks.json"):
            blocks = getBlocks()
            newBlocks = blocks
        else:
            with open("blocks.json",'r') as f:
                blocks_load = f.read()
            blocks = json.loads(blocks_load)
            newBlocks = getBlocks()
        database = updateDB(newBlocks)
        print(database)

    t +=1
    printProgressBar(t,graphNo)

	
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

