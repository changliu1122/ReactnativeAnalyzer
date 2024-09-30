import re

def parser_TextWithTextInput_to_xml(context,file):
    pattern_TextInput = r"r\d+.Text"
    pattern_TextInput = r"r\d+.TextInput"
    TextStartxml = ""
    TextInputXML = ""
    TextEndXML = ""
    rootTag = '' 
    tag_value = ""
    lines = context.replace(" ", "").split('\n')
    filteredList = []
    for line in lines:
        if line != "":
            filteredList.append(line)
    for i in range(len(filteredList)):  
        lineWithText = re.findall(pattern_TextInput,filteredList[i])
        if len(lineWithText) > 0:
            rootTag = lineWithText[0].replace(".Text","")
        if rootTag != "" and filteredList[i].find(rootTag+"['children']") != -1:
            tag_value = filteredList[i - 1][filteredList[i-1].index(".")+1:len(filteredList[i-1])]
        TextStartxml =f'''
<Text 
    value : {tag_value}'''            
        lineWithTextInput = re.findall(pattern_TextInput,filteredList[i])
        
        if len(lineWithTextInput) > 0:
            rootTag = lineWithTextInput[0].replace(".TextInput","")

        if rootTag != "" and filteredList[i].find(rootTag+"['value']") != -1:

            tag_value = filteredList[i - 1][filteredList[i-1].index(".")+1:len(filteredList[i-1])]
        TextInputXML = f'''
    <TextInput
        value : {tag_value}
    />
        '''
    TextEndXML = f'''
/>
                '''
    file.write(TextStartxml + TextInputXML + TextEndXML )

#receive one snippet of textinput context
def parser_TextInput_to_xml(context,file_TextInputXML):
    pattern_TextInput = r"r\d+.TextInput"

    
    rootTag = '' 
    tag_value = ""
    tag_placeholder=""
    #here the context is a whole string of textinput context
    #conver back to lines
    lines = context.replace(" ", "").split('\n')

    #if it is not array, cannot get last line above
    filteredList = []
    for line in lines:
        if line != "":
            filteredList.append(line)

    for i in range(len(filteredList)):  
        lineWithTextInput = re.findall(pattern_TextInput,filteredList[i])
        
        if len(lineWithTextInput) > 0:
            rootTag = lineWithTextInput[0].replace(".TextInput","")

        if rootTag != "" and filteredList[i].find(rootTag+"['value']") != -1:

            tag_value = filteredList[i - 1][filteredList[i-1].index(".")+1:len(filteredList[i-1])]
           
        if rootTag != "" and filteredList[i].find(rootTag+"['placeholder']") != -1:

            tag_placeholder = filteredList[i - 1][filteredList[i-1].index("'")+1:len(filteredList[i-1]) - 2]
        #else:
            #check text tag before this textinput tag
    return createInputXml(tag_value,tag_placeholder,file_TextInputXML)

def createInputXml(value,placeholder,file_TextInputXML):
    xml = "<TextInput" +"\n" + "     value : " + value+" (user type in their information here) " + "\n" + "     placeholder : "+placeholder + "\n" \
            + "  />"
    file_TextInputXML.write(xml+"\n")
