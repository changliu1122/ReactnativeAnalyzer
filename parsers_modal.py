import re
import os
import json
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from webcolors import name_to_rgb,hex_to_rgb
import numpy
from var import REASON

#fix asscalar deprecated problem
def patch_asscalar(a):
    return a.item()
setattr(numpy, "asscalar", patch_asscalar)

def parser_Modal(context,file,bundleFile):
    pattern_Text = r"r\d+.Text"
    patter_button = r"r\d+.Pressable"
    patter_modal = r"r\d+.Modal"
    reason = ""
    text_reg = ""
    button_reg = ""
    button_style=""
    modal_line_number = ""
    style_string=""
    button_arr = []
    style_arr = []
    text_content =""
    modal_text = ""
    isPressable = False
    pressable_text = ""
    with open(context, 'r') as fp:
        lines = fp.readlines()

        for row in lines:
            #modal start line number
            modal_matches = re.findall(patter_modal,row)
            if len(modal_matches)>0:
                modal_line_number=row.split(" ")[0]

            #modal text or button text
            text_matches = re.findall(pattern_Text,row)
            if len(text_matches)>0:
                text_reg = text_matches[0].split(".")[0]
            if text_reg != "" and row.find(text_reg+"['children']") != -1:
                last_row_of_text_children = lines[lines.index(row)-1]
                text_content = last_row_of_text_children.split("=")[-1]
                if (not isPressable) and modal_text =="":
                    modal_text = text_content
                if isPressable:
                    pressable_text = text_content

            # modal buttons
            button_matches = re.findall(patter_button,row)
            if len(button_matches)>0:
                isPressable = True
                button_reg = button_matches[0].split(".")[0]
                button_style = button_reg + "['style']"

            if  button_style != "" and isPressable:
                #found current pressable style
                if button_style in row:

                    #print(lines[lines.index(row) - 1])
                    style_row = lines[lines.index(row) - 1]
                    #print(style_row)
                    if(not "{" in style_row):
                    #case 1: found current pressable style name in bundle file,like
                    #206817          r22 = r22.CookiesValidModal;
                    #206818          r18['style'] = r22;
                    #then check this name in bundle file
                        style_name = style_row.split(".")[-1].replace(";","").strip()
                        style_string = "['"+style_name+"']"

                        #check bundle file
                        with open(bundleFile, 'r') as f:
                            bundleFile_lines = f.readlines()
                            for bundleFile_row in bundleFile_lines:
                                if style_string !="" and style_string in bundleFile_row:
                                    #print("row from bundle file")
                                    style_detail = bundleFile_lines[bundleFile_lines.index(bundleFile_row)-1].split("=")[-1].replace(";","").strip()
                                    #print(style_detail)
                                    style_arr.append(style_detail)
                    else:
                    #case 2: style directly displayed in modal context, like
                    #r13 = {'padding': 4, 'margin': 40, 'borderColor': 'black', 'borderWidth': 2};
                    #r10['style'] = r13;
                        print("style is directly in current file")
                        style_detail = style_row.split("=")[-1].replace(";","").strip()
                        style_arr.append(style_detail)


            #one button snippet is done
            if isPressable and button_reg != "" and row.find(button_reg+"['children']") != -1:
                button_arr.append(pressable_text)
                isPressable = False


# when the row is a space, one context of modal is done
            if row.isspace() and not modal_text == "" :
                #print("#######")

                buttons = ""
                for b in button_arr:
                    buttons =  buttons + b
                styles = ""
                for s in style_arr:
                    styles = styles + s


                # check validity of modal 
                isInValid = validityCheck(modal_text,button_arr,style_arr,reason)

                print("reason before dic  ",reason)
                #must be sensitive modal
                #must fullfilled all rules
                #show invalid modal
                if isInValid["invalid"] :
                    dic = {
                        "file":"apktool_output/assets/index.android.bundle",
                        "type":"privacy consent",
                        "line number": modal_line_number,
                        "content": modal_text,
                        "button":buttons,
                        "style": styles,
                        "reason":isInValid["reason"]
                        #"valid": v

                    }

                    json_object = json.dumps(dic, indent=4)
                    file.write(json_object + "," +"\n")
                else:
                    print("valid modal")

                text_reg = ""
                button_reg = ""
                modal_line_number = ""
                button_arr = []
                text_content =""
                modal_text = ""
                isPressable = False
                pressable_text = ""
                style_arr = []
                reason=""


def checkButtonNameInValid(arr):
    res_IsInvalid = False
    res_reason = ""
    #here check both decline and accept
    isDeclineExist = False
    isAcceptExist = False
    declineReg=r"decline|reject|disagree|deny|refuse|ablehnen|nein"
    acceptReg=r"accept|agree|consent|allow|ok|okay|confirm|bestätigen|akzeptieren|zustimmen|zulassen|annehmen|erlauben"
    declineRegPattern = re.compile(declineReg, re.I)
    acceptRegPattern = re.compile(acceptReg, re.I)

    for b in arr:
        b = str(b).replace("'","").replace(";","").strip()
        declineRegRes = re.match(declineRegPattern,b)
        acceptRegRes = re.match(acceptRegPattern,b)
        if declineRegRes :
            isDeclineExist=True
        if acceptRegRes :
            isAcceptExist=True
        print("modal button : ",b)
    print("isDeclineExist",isDeclineExist)
    print("isAcceptExist",isAcceptExist)

    if isDeclineExist and isAcceptExist:
        res_IsInvalid=False
        res_reason="valid"
    if isDeclineExist and (not isAcceptExist):
        res_IsInvalid=True
        res_reason="no accept button"
    if isAcceptExist and (not isDeclineExist):
        res_IsInvalid=True
        res_reason="no decline button"
    if (not isAcceptExist) and (not isDeclineExist):
        res_IsInvalid=True
        res_reason="no decline button and no accept button"
    return {
        "invalid": res_IsInvalid,
        "reason": res_reason
    }




def checkButtonStyleInValid(style_arr, reason):
    #make sure there are two buttons

    height_arr = []
    width_arr = []
    color_arr = []
    for style in style_arr:
        #these are styles in one modal
        #one modal has two button

        #conver json to dic by replacing the' to "
        jsonString = style.replace("'",'"')

        style_dic = json.loads(jsonString)
        if "height" in style_dic:
            height_arr.append(style_dic["height"])
            print(style_dic["height"])
        if "width" in style_dic:
            width_arr.append(style_dic["width"])
        if "backgroundColor" in style_dic:
            color_arr.append(style_dic["backgroundColor"])


#size dividien /, should not >+=
    area_arr = []
    if len(height_arr) == len(width_arr):
        for i in range(0,len(height_arr)):
            area_arr.append(height_arr[i] * width_arr[i])
            print(height_arr[i] * width_arr[i])
    
    if len(area_arr)<2:
        reason =reason+ "\n  only one button"
        #return True
    btn_a = area_arr[0]
    btn_b = area_arr[1]
    if (btn_a/btn_b > 1.5) or (btn_b/btn_a > 1.5) :
        
        reason =reason+ "\n the difference of the two buttons'size is over 1.5 factor, invalid"
        #return True
    

    color_rgb_a = colorToRGB(color_arr[0])
    color_rgb_b = colorToRGB(color_arr[1])
    print(color_rgb_a.red)
    print(color_rgb_a.green)
    print(color_rgb_a.blue)
    print(color_rgb_b.red)
    print(color_rgb_b.green)
    print(color_rgb_b.blue)
    #color convert to number and differ should be < 30
    # Red Color
    color1_rgb = sRGBColor(color_rgb_a.red,color_rgb_a.green, color_rgb_a.blue)

    # Blue Color
    color2_rgb = sRGBColor(color_rgb_b.red,color_rgb_b.green, color_rgb_b.blue)

    # Convert from RGB to Lab Color Space
    color1_lab = convert_color(color1_rgb, LabColor)

    # Convert from RGB to Lab Color Space
    color2_lab = convert_color(color2_rgb, LabColor)

    # Find the color difference
    delta_e = delta_e_cie2000(color1_lab, color2_lab)

    if delta_e > 30:
        reason = reason+ "\n the difference between 2 color of two buttons is : " + str(delta_e) +" invalid!"
    print("reasons: ",  reason)
    if  reason == "":
        return {
            "isInvalid": False,
            "reason": reason
        }
    else:
        return {
            "isInvalid": True,
            "reason": reason
        }



def checkModalSensitivity(text):
    sensitiveInfo = r"cookie|cookies|privacy|consent|gdpr|Datenschutz|PrivatsphäreCookie|Zustimmung|Einwilligung|Einverständnis|Tracking"
    text = str(text).replace("\\n","").replace("'","").strip()

    reg = re.compile(sensitiveInfo, re.I)
    result = re.match(reg,text)

    print("sensitivity ", result)
    if result:
        return True
    else:
        return False


def colorToRGB(colorStr):
    if "#" in colorStr:
      return  hex_to_rgb(colorStr)
    else:
        return name_to_rgb(colorStr)
    
def validityCheck(modal_text,button_arr,style_arr,reason):
    res_IsInvalid = False
    res_reason = reason
    #first step:  check if modal is  privacy related
    if checkModalSensitivity(modal_text): 
        #second step: should be more than one button
        if len(button_arr) >= 2:
            #third step: if both decline and accept button exist
            button_name_Invalid = checkButtonNameInValid(button_arr)
            # if both decline and accept button exist, check style
            if not button_name_Invalid["invalid"]:
                #last step:  styles of buttons
                button_style_Invalid = checkButtonStyleInValid(style_arr,reason)
                res_IsInvalid = button_style_Invalid["isInvalid"]
                res_reason = button_style_Invalid["reason"]
            else:
                res_IsInvalid = button_name_Invalid["invalid"]
                res_reason = button_name_Invalid["reason"]
        else:
            res_IsInvalid = True
            res_reason = "only one button"

    else:
        res_IsInvalid = False
        res_reason = "not relevant"
        
    return {
            "invalid": res_IsInvalid,
            "reason": res_reason
        }