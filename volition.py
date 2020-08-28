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

## ----------------------------------------------------------------------------
session = requests.Session()

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

def getClubDetails(clubname):
    baseUrl = "https://api.chess.com/pub/club/" + clubname

    response = session.get(baseUrl)
    clubDetails = response.json()
    dumps(clubDetails,file_name=clubname+'/details.json')
    #print(members)
    return clubDetails

def getClubLogo(clubname):
    baseUrl = "https://api.chess.com/pub/club/" + clubname

    response = session.get(baseUrl)
    clubDetails = response.json()
    clubLogo = clubDetails["icon"]
    filename = clubLogo.split(".")
    extension = filename[-1]

    r = requests.get(clubLogo,stream=True)
    if r.status_code == 200:
        r.raw.decode_content = True
        logo = clubname+"/"+clubname+"."+str(extension)
        #print(logo)
        with open(logo,'wb') as f:
            shutil.copyfileobj(r.raw,f)
            clubLogo = logo
    else:
        print("\nError downloading the club's logo. Replacing it with default")
        clubLogo = 'defaultLogo.jpeg'
    
    #print(clubLogo)
    return clubLogo


def getClubMembers(clubname):
    baseUrl = "https://api.chess.com/pub/club/" + clubname + "/members"

    response = session.get(baseUrl)
    members = response.json()
    dumps(members,file_name=clubname+'/members.json')
    #print(members)
    return members

def getClubMatches(clubname):
    baseUrl = "https://api.chess.com/pub/club/" + clubname + "/matches"

    response = session.get(baseUrl)
    matches = response.json()
    dumps(matches,file_name=clubname+'/matches.json')
    #print(matches)
    return matches

def getResults(clubname,members,scope_finished,scope_in_progress):
    #print(scope_finished)
    clubUrl = "https://api.chess.com/pub/club/" + clubname
    results = {}
    
    for match in scope_finished:
        baseUrl = match["@id"]
        response = session.get(baseUrl)
        team_match = response.json()
        if not os.path.exists(clubname+"/club_matches_finished"):
            os.mkdir(clubname+"/club_matches_finished")
        dumps(team_match,file_name=clubname+'/club_matches_finished/'+match["name"]+'.json')
        for team in team_match["teams"]:
            if team_match["teams"][team]["@id"] == clubUrl:
                for player in team_match["teams"][team]["players"]:
                    if "played_as_black" in player:
                        if player["played_as_black"] == "win" and player["username"] in members:
                            members[player["username"]] += 1
                        if player["played_as_black"] == ("insufficient" or "agreed" or "repetition" or "stalemate" or "50move" or "threecheck" or "timevsinsufficient") and player["username"] in members:
                            members[player["username"]] += 0.5
                    if "played_as_white" in player:
                        if player["played_as_white"] == "win" and player["username"] in members:
                            members[player["username"]] += 1
                        if player["played_as_white"] == ("insufficient" or "agreed" or "repetition" or "stalemate" or "50move" or "threecheck" or "timevsinsufficient") and player["username"] in members:
                            members[player["username"]] += 0.5

    #print(scope_in_progress)
    for match in scope_in_progress:
        baseUrl = match["@id"]
        response = session.get(baseUrl)
        team_match = response.json()
        if not os.path.exists(clubname+"/club_matches_in_progress"):
            os.mkdir(clubname+"/club_matches_in_progress")
        dumps(team_match,file_name=clubname+'/club_matches_in_progress/'+match["name"]+'.json')
        for team in team_match["teams"]:
            if team_match["teams"][team]["@id"] == clubUrl:
                for player in team_match["teams"][team]["players"]:
                    if "played_as_black" in player:
                        if player["played_as_black"] == "win" and player["username"] in members:
                            members[player["username"]] += 1
                        if player["played_as_black"] == ("insufficient" or "agreed" or "repetition" or "stalemate" or "50move" or "threecheck" or "timevsinsufficient") and player["username"] in members:
                            members[player["username"]] += 0.5
                    if "played_as_white" in player:
                        if player["played_as_white"] == "win" and player["username"] in members:
                            members[player["username"]] += 1
                        if player["played_as_white"] == ("insufficient" or "agreed" or "repetition" or "stalemate" or "50move" or "threecheck" or "timevsinsufficient") and player["username"] in members:
                            members[player["username"]] += 0.5

    ranking = []
    for player in members:
        points = [members[player]]
        ranking.append([player] + points)
    ##########################################################################
    ranking.sort(key = lambda ranking : ranking[1], reverse = True)
    ##########################################################################
    #print(ranking)
                            
    results = ranking
    dumps(results,file_name=clubname+'/results.json')
    return results

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

def generateLeagueTable(clubname,results, start_date, end_date,logo):
    pdf = PDF()
    pdf.alias_nb_pages()
    #components = final
    header = ['Position','Member','Daily rating','Points']
    data = []
    for i in range(1,len(results)+1):
        if results[i-1][1] > 0:
            aux = [str(i),results[i-1][0],str(getPlayerStats(results[i-1][0])["chess_daily"]["last"]["rating"]),str(results[i-1][1])]
            data.append(aux)
    #print(data)
    pdf.print_chapter("League Table for "+clubname+"'s Club Daily Matches","",logo)
    pdf.set_font('Times','',12)
    pdf.set_text_color(0,0,0)
    instructions = "Current standings from "+str(start_date)+" to "+str(end_date)
    pdf.multi_cell(0,7,instructions,0)
    pdf.ln(5)
    pdf.set_font('Times','',12)
    pdf.fancy_table(header,data)

    if not data:
        print("\nThere was no data available")
        raise SystemExit
    details = getPlayerDetails(data[0][1])
    #print(details)
    stats = getPlayerStats(data[0][1])

    pdf.print_chapter('Player of the Month',"",logo)
    pdf.set_font('Times','B',24)
    pdf.set_text_color(0,0,0)
    content1 = "This month's Player of the Month was: "+str(data[0][1])
    pdf.multi_cell(0,7,content1,0)
    pdf.ln(5)
    if "avatar" in details:
        pdf.image(details["avatar"], 230, 50, 33, type='jpeg')
    else:
        pdf.image("defaultLogo.jpeg",230,50,33, type='jpeg')
    pdf.set_font('Times','B',18)
    content2 = str(data[0][1])+" achieved "+str(data[0][3])+" points in Daily Matches representing our club"
    pdf.multi_cell(0,7,content2,0)
    pdf.ln(10)
    content3 = "Getting to know "+details["username"]+ " better:"
    pdf.multi_cell(0,7,content3,0)
    pdf.ln(5)
    if "name" in details:
        content4 = "Name: "+details["name"]
        pdf.multi_cell(0,7,content4,0)
        pdf.ln(5)
    content5 = "Joined on "+ time.strftime('%d-%b-%Y', time.localtime(details["joined"]))
    pdf.multi_cell(0,7,content5,0)
    pdf.ln(5)
    content6 = "Daily rating: "+str(stats["chess_daily"]["last"]["rating"])+" (current), "+str(stats["chess_daily"]["best"]["rating"])+ " (best)"
    pdf.multi_cell(0,7,content6,0)
    pdf.ln(5)
    if "chess960_daily" in stats:
        content7 = "Daily 960 rating: "+str(stats["chess960_daily"]["last"]["rating"])+" (current), "+str(stats["chess960_daily"]["best"]["rating"])+ " (best)"
        pdf.multi_cell(0,7,content7,0)
        pdf.ln(5)
    if "chess_rapid" in stats:
        content8 = "Rapid rating: "+str(stats["chess_rapid"]["last"]["rating"])+" (current), "+str(stats["chess_rapid"]["best"]["rating"])+ " (best)"
        pdf.multi_cell(0,7,content8,0)
        pdf.ln(5)
    if "chess_blitz" in stats:
        content9 = "Blitz rating: "+str(stats["chess_blitz"]["last"]["rating"])+" (current), "+str(stats["chess_blitz"]["best"]["rating"])+ " (best)"
        pdf.multi_cell(0,7,content9,0)
        pdf.ln(5)
    if "chess_bullet" in stats:
        content10 = "Bullet rating: "+str(stats["chess_bullet"]["last"]["rating"])+" (current), "+str(stats["chess_bullet"]["best"]["rating"])+ " (best)"
        pdf.multi_cell(0,7,content10,0)
        pdf.ln(5)
    if "tactics" in stats:
        content11 = "Tactics rating: "+str(stats["tactics"]["highest"]["rating"])+" (highest)"
        pdf.multi_cell(0,7,content11,0)
        pdf.ln(5)
    if "puzzle_rush" in stats:
        content6 = "Puzzle Rush score: "+str(stats["puzzle_rush"]["best"]["score"])+" (record)"
        pdf.multi_cell(0,7,content6,0)
        pdf.ln(5)
    


    pdf.set_font('Times','',12)
    pdf.set_text_color(0,0,0)
    #insert avatar
    #insert ratings
    
    pdf.output(clubname+'/leagueTable.pdf', 'F')
    #print("PDF generated -> leagueTable.pdf")




def getArguments():
    global baseUrl
    parser = argparse.ArgumentParser(description='Volition API data handling script')
    parser.add_argument('-u','--username', help='Specific username', required=False)
    parser.add_argument('-log','--log', help='Download the full log', action='store_true', required=False)
    parser.add_argument('-c','--club', help='Specific club', required=False)
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
    club = ""
    scope_finished = {}
    scope_in_progress = {}
    args = getArguments()
    if args["dateRange"]:
        dateRange = args["dateRange"].split(":",1)
        first = dateRange[0].split("-",2)
        last = dateRange[1].split("-",2)
        start_date = dateRange[0]
        start_epoch = round(datetime.datetime(int(first[2]),int(first[1]),int(first[0])).timestamp())
        end_date = dateRange[1]
        end_epoch = round(datetime.datetime(int(last[2]),int(last[1]),int(last[0])).timestamp())

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

    if args["club"]:
        club = args["club"]
        if not os.path.exists(club):
            os.mkdir(club)
        clubDetails = getClubDetails(club)
        clubLogo = getClubLogo(club)
        members = getClubMembers(club)
        matches = getClubMatches(club)
        if args["dateRange"]:
            scope_finished = list(filter(lambda match: (match["start_time"] >= start_epoch) and (match["start_time"] <= end_epoch), matches["finished"]))
            scope_in_progress = matches["in_progress"]

    t +=1
    printProgressBar(t,graphNo)

    if args["report"]:
        if args["club"]:
            if args["dateRange"]:
                t, graphNo = 0, 5
                printProgressBar(t,graphNo)
                members = {}
                clubMembers = getClubMembers(club)
                for member in clubMembers["weekly"]:
                    members.update({member["username"] : 0})
                for member in clubMembers["monthly"]:
                    members.update({member["username"] : 0})
                for member in clubMembers["all_time"]:
                    members.update({member["username"] : 0})
                matches = getClubMatches(club)

                t +=1
                printProgressBar(t,graphNo)

                scope_finished = list(filter(lambda match: (match["start_time"] >= start_epoch) and (match["start_time"] <= end_epoch), matches["finished"]))

                t +=1
                printProgressBar(t,graphNo)
                
                scope_in_progress = matches["in_progress"]

                t +=1
                printProgressBar(t,graphNo)

                results = getResults(club,members,scope_finished,scope_in_progress)

                t +=1
                printProgressBar(t,graphNo)
                
                generateLeagueTable(club,results,start_date,end_date,getClubLogo(club))

                t +=1
                printProgressBar(t,graphNo)


  

    #####Present League Table by tiers ranked based on points
    #####Additional features like player of the week, most improved player, top ranking by time control, etc.
    


	
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

