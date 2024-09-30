import re

def findModal(source,dis,root_path):
    dis_file = open( root_path+dis, "w")
    startPrint = False
    EndMark =""
    modal_pattern = r"r\d+.Modal"
    with open(source, 'r') as fp:
        lines = fp.readlines()
        for row in lines:
            modal_matches = re.findall(modal_pattern,row)
            if len(modal_matches) > 0:
                modal_line = modal_matches[0]
                line_split = modal_line.split(".")
                print(line_split[0])
                EndMark = line_split[0]+"['children']"
                startPrint = True
            if startPrint == True:
                dis_file.write(row)
                if row.find(EndMark) != -1:
                        # at the end, check if
                        dis_file.write("\n")
                        startPrint = False
    dis_file.close



def findTextInput(source,dis,endMark,keyWord,root_path):
    dis_file = open( root_path+dis, "w")
    startPrint = False
    EndMark = endMark
    
    with open(source, 'r') as fp:
        lines = fp.readlines()
        for row in lines:
            if row.find(keyWord) != -1:
                startPrint = True
            if startPrint == True:
                #from here is textinput context, check each line to see if there is placeholder 
                dis_file.write(row)
                if row.find(EndMark) != -1:
                        # at the end, check if
                        dis_file.write("\n")
                        startPrint = False
    dis_file.close()


def findAppContext(source,root_path):
    lineNumber = 1
    file = open( root_path+"/AppContext.txt", "w")

    startPrint = False
    AppEntry = 'Original name: App,'
    EndMark = 'case'
    
    with open(source, 'r') as fp:
        lines = fp.readlines()
        for row in lines:
            if row.find(AppEntry) != -1:
                startPrint = True
            if startPrint == True :
                if row.find(EndMark) == -1:
                    l = "          ".join([str(lineNumber),row.strip()])+"\n"                    
                    file.write(l)
                else:
                    break   
            lineNumber = lineNumber + 1       
    file.close()