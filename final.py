import sys
import subprocess
import os
import re
from parsers import parser
from findContext import findAppContext,findTextInput,findModal


#script entrance
if __name__ == "__main__":
    usernameCategory=["username","user_name","uname","benutzer","benutzername","benutzer_name"]
    passwordCategory=["password","pass_word","pwd","kennwort","kenn_wort"]
    emailCategory=[]
    birthdayCategory=[]
    ageCategory=[]
    addressCategory=[]
    phoneNumber=[]
    country=[]
    #python3 final.py xxx/xxx/xxx.apk
    source = sys.argv[1]
    print(source)
    #step 1: apktool decompile the .apk file
    #generated output folder in current folder
    subprocess.run(['apktool', 'd',source, '-o', 'apktool_output'])

    #step 2:enter into hermes_dec foler and hermes_dec decompile index_android_bundle file 
    root_path = os.getcwd()
    print("root path" ,root_path)
    newpath = root_path+'/Parse_Output'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    root_path = newpath

    os.chdir('hermes-dec')
    hermes_dec_path = os.getcwd()
    print("hermes path",hermes_dec_path)

    os.chdir('../apktool_output/assets')
    bundle_path = os.getcwd()
    print("bundle path",bundle_path) 
    subprocess.run(['file', bundle_path +'/index.android.bundle' ])
   
    subprocess.run(['python3', hermes_dec_path+'/hbc_decompiler.py', bundle_path +'/index.android.bundle', root_path +'/bundle_output.js' ])

    #step 3: change bundle output file to .txt file
    thisFile = root_path +'/bundle_output.js'
    

    base = os.path.splitext(thisFile)[0]
    os.rename(thisFile, base + ".txt")

    #step 4: find username and password in bundle file
    renamed_bundlefile = root_path +'/bundle_output.txt'
    print("****************** Result ****************** " )
    print("")
    print("current file : ", bundle_path +'/index.android.bundle' )
    print("")
    #find App.js snippet from source code js file, where the real implementation was done
    findAppContext(renamed_bundlefile,root_path)
    #only find useful information in App.js
    appContextFile = root_path+"/AppContext.txt"
    findTextInput(appContextFile,"/TextInputContext.txt","// Original name: onChangeText,",".TextInput",root_path)
    findModal(appContextFile,"/ModalContext.txt",root_path)
    parser(root_path)
    
    
    
   