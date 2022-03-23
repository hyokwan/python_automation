#!/usr/bin/env python
# coding: utf-8

# In[47]:


import os
from glob import glob

######### 파일 검색 및 제외대상 구동파일 확인 #########
searchPattern = "*.py"
# root = '/home/hkhdp/sengpjt/apiScrapy/codeset'
root = './'
targetPattern = os.path.join(root,searchPattern)
fileList = glob(targetPattern)

# 구동 시 제외대상 번호 리스트 내 기입
exceptList = ["02","codeControl"]
exceptListLen = len(exceptList)

try:
    for item in fileList:
        for ex in exceptList:
            if item.count(ex) == 1 :
                fileList.remove(item)
except:
    pass


# In[48]:


fileList


# In[1]:


######### 구동파일 구동 #########
fileLen = len(fileList)

for i in range(0, fileLen ):
    exec(open( fileList[i], encoding='utf-8').read(), globals() )


# In[ ]:




