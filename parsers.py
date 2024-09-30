import os
from parsers_modal import parser_Modal
from parseTextToXML import parser_TextInput_to_xml,parser_TextWithTextInput_to_xml
import re
import json

def parser(root_path):

        resultFileJSON = open( root_path+"/result.json", "w")
        resultFileJSON.write("[")

        src_file_path = "apktool_output/assets/index.android.bundle"
        sensitiveInfo ={
            "username":"username|firstname|lastname|familyname|vorname|nachname|user_name|uname|benutzer|benutzername|benutzer_name",
            "password":"password|pass_word|pwd|kennwort|kenn_wort",
            "email":"email|mail"
        }


#make one text input block a single string element in array
        arrTextInput = []
        arrText = []
        
        with open(root_path+"/TextInputContext.txt","r") as fp:
                textInputString = ""
                isPlaceholderExist = False
                lines = fp.readlines()
                for row in lines:

                    if "['placeholder']" in row:
                        isPlaceholderExist = True
                    if row.isspace():
                        #with placeholder 
                        if isPlaceholderExist == True:
                            arrTextInput.append(textInputString)
                        else:
                        #without placeholder means it was wraped with text component
                            arrText.append(textInputString)
                        textInputString = ""
                        isPlaceholderExist = False         
                    else:
                        textInputString= textInputString + row   

        #check which textinput snippet does not have placeholder
        
        lineNumber = r"\d*"
        TextTagStartIndex = 0
        realLineNum = 0
        for a in arrText:
            nums = re.findall(lineNumber,a)
            lineNumberOfTextInput = nums[0]
            #get the line number, and find its parent tag (text tag)
            with open(root_path+"/AppContext.txt","r") as fp:
                lines = fp.readlines()
                for row in lines:
                    if row.find(lineNumberOfTextInput) != -1:
                        realLineNum = lines.index(row)
                        #from this line, go backwards until text tag is found
                        for r in reversed(range(realLineNum)):
                            backRow = lines[r]
                            if backRow.find(".Text") != -1:
                                TextTagStartIndex = r
                                break
                        
                        break
                textString=""
                for index in range(TextTagStartIndex,realLineNum):
                    textString = textString + lines[index]

                arrText[arrText.index(a)]= textString + a


        # now we have two array, one for textinput with placeholder, one without


        # after parse to xml 
        # check if contains sensitive info


        # check button in modal
        parser_Modal(root_path+"/ModalContext.txt",resultFileJSON,root_path+"/bundle_output.txt")

        # Textinput arr
        file_TextInputXML = open( root_path+"/TextInputXML.txt", "w")
        for t in arrTextInput:
            #check if there is placeholder first
            #print("arrTextInput",t)

            # check if contains sensitive info
            for key,value in sensitiveInfo.items():
                findMatch = re.search(value,t)
                
                if findMatch:
                    indexOfResultLineNumber = re.findall(lineNumber,t)
                    dic = {
                        "file":src_file_path,
                        "type":"TextInput",
                        "line number": indexOfResultLineNumber[0],
                        "category":key
                    }
                    
                    json_object = json.dumps(dic, indent=4)
                    resultFileJSON.write(json_object + "," + "\n")
                    
                    parser_TextInput_to_xml(t,file_TextInputXML)   
        file_TextInputXML.close()


        # Text tag arr
        file_TextWithTextInputXML = open( root_path+"/TextWithTextInputXML.txt", "w")
        for txt in arrText:
            #print("arrText",txt)
            # check if contains sensitive info
            for key,value in sensitiveInfo.items():
                findMatch = re.search(value,txt)
                
                if findMatch:
                    indexOfResultLineNumber = re.findall(lineNumber,txt)
                    dic = {
                        "file":src_file_path,
                        "type":"Text",
                        "line number": indexOfResultLineNumber[0],
                        "category":key
                    }
                    
                    json_object = json.dumps(dic, indent=4)
                    if txt == arrText[-1]:
                        resultFileJSON.write(json_object + "\n")
                    else:
                        resultFileJSON.write(json_object + "," + "\n")
                    parser_TextWithTextInput_to_xml(txt,file_TextWithTextInputXML)
        file_TextWithTextInputXML.close()


        resultFileJSON.write("]")
        resultFileJSON.close()





