# coding=utf-8
import os
import sys
import zipfile
import shutil
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


unzipDir = "python_extracted"
fileName1 = unzipDir + "/simulink/blockdiagram.xml"
fileName2 = unzipDir + "/simulink/stateflow.xml"
# 第1个参数是文件名，第2个参数是目标Chart，后面是要删除的chart
fn = sys.argv[1]
NameList = []
for i in sys.argv[3:]:
    NameList.append(i)

def removeRedundancy():
    global NameList
    # 处理blockDiagram.xml
    tree = ET.parse(fileName1)
    root = tree.getroot()
    # 查找记录Chart的父结点
    System = root.find(
        "Model/System/Block[@BlockType='SubSystem']/System")
    # 删除Chart
    for i in NameList:
        System.remove(System.find("./Block[@Name='" + i + "']"))
    # 删除连线
    lineList = System.findall("./Line")
    for i in lineList:
        System.remove(i)
    tree.write(fileName1)

    # 处理stateflow.xml
    tree = ET.parse(fileName2)
    root = tree.getroot()
    # 删除instance
    instanceList = root.findall("instance")
    for i in instanceList:
        instanceName = i.find("P[@Name='name']").text
        instanceName = instanceName[instanceName.find('/')+1:]
        if instanceName in NameList:
            root.remove(i)
    # 删除machine/Children/Chart
    childrenNode = root.find("machine/Children")
    chartList =childrenNode.findall("./chart")
    for i in chartList:
        chartName = i.find("P[@Name='name']").text
        chartName = chartName[chartName.find('/')+1:]
        if chartName in NameList:
            childrenNode.remove(i)

    tree.write(fileName2)


if __name__ == '__main__':
    # debug=True
    debug = False
    # 解压缩
    zipFileName=fn[: fn.find('.')] + '.zip'
    os.rename(fn, zipFileName)
    z=zipfile.ZipFile(zipFileName, 'a', zipfile.ZIP_DEFLATED)
    z.extractall(unzipDir)
    z.close()
    os.rename(zipFileName, fn)
    # 处理xml文件
    removeRedundancy()
    # 创建压缩文件
    if debug == False:
        zipFileNameAfter=fn[: fn.find('.')] + '_after.zip'
        f=zipfile.ZipFile(zipFileNameAfter, 'w', zipfile.ZIP_DEFLATED)
        for root, dirnames, filenames in os.walk(unzipDir + '/'):
            for filename in filenames:
                filePath=os.path.join(root, filename)
                zippath=filePath[len(unzipDir):]
                f.write(filePath, zippath)
        f.close()
        os.remove(fn)
        os.rename(zipFileNameAfter, fn)
        # 删除残留文件
        shutil.rmtree(unzipDir)
        print 'done'
