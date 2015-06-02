# coding=utf-8
import os
import zipfile
import shutil
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
fn = "Model.slx"
unzipDir = "python_extracted"


class XMLProcess:
    # 主控函数
    def mainProcess(self, fileName):
        NameList = ['Chart1']
        tree = ET.parse(fileName)
        root = tree.getroot()
        System = root.findall(
            "Model/System/Block[@BlockType='SubSystem']")
        for i in NameList:
            System.remove(/Block[@Name=" + Name + "]


if __name__ == '__main__':
    # debug = True
    debug = False
    if debug == False:
        # 解压缩
        zipFileName = fn[:fn.find('.')] + '.zip'
        os.rename(fn, zipFileName)
        z = zipfile.ZipFile(zipFileName, 'a', zipfile.ZIP_DEFLATED)
        z.extractall(unzipDir)
        z.close()
        os.rename(zipFileName, fn)
    # 处理xml文件
    XMLPro = XMLProcess()
    XMLPro.mainProcess(unzipDir + "/simulink/blockdiagram.xml")
    # 创建压缩文件
    if debug == False:
        zipFileNameAfter = fn[:fn.find('.')] + '_after.zip'
        f = zipfile.ZipFile(zipFileNameAfter, 'w', zipfile.ZIP_DEFLATED)
        for root, dirnames, filenames in os.walk(unzipDir + '/'):
            for filename in filenames:
                filePath = os.path.join(root, filename)
                zippath = filePath[len(unzipDir):]
                f.write(filePath, zippath)
        f.close()
        slxFileNameAfter = zipFileNameAfter[:-4] + '.slx'
        os.rename(zipFileNameAfter, slxFileNameAfter)
        # 删除残留文件
        shutil.rmtree(unzipDir)
