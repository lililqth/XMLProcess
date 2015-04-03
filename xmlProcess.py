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

    inputList = []
    outputList = []

    # 主控函数
    def mainProcess(self, fileName):
        tree = ET.parse(fileName)
        root = tree.getroot()
        # 确定总输入输出
        self.getInputOutput(root)
        # 为chart添加顶层state
        self.addRootState(root)
        # 重新映射SSID
        self.resetSSID(root)
        # 重置总输入输出为顶层
        self.replaceInputOutput(root)
        # 合并多个chart
        self.mergeChart(root)
        # 重置输入输出后续工作
        # 重置Model->System->SubSystem->Chart（mainChart）的输入输出连接
        # 重置Model->System->SubSyetem(SubSystem)的连线
        self.resetIOLines(root)
        tree.write(fileName)

    # 重置输入输出后续工作
    # 重置Model->System->SubSystem->Chart（mainChart）的输入输出连接
    # 重置Model->System->SubSyetem(SubSystem)的连线
    def resetIOLines(self, root):
        mainChart = root.find(
            "Model/System/Block[@BlockType='SubSystem']/System/Block[@BlockType='SubSystem']/System")
        tmpInput = mainChart.findall("Block[@BlockType='Inport']")
        tmpOutput = mainChart.findall("Block[@BlockType='Outport']")
        # 删除所有的输入输出结点和连线
        if tmpInput != None:
            for i in tmpInput:
                mainChart.remove(i)
        if tmpOutput != None:
            for i in tmpOutput:
                mainChart.remove(i)
        for i in mainChart.findall("Line"):
            mainChart.remove(i)

        # 根据输入输出列表添加输入输出结点
        if not XMLProcess.inputList == []:
            for i in XMLProcess.inputList:
                template = ET.parse("template.xml")
                templateRoot = template.getroot()
                tempInput = templateRoot.find(
                    "Inport/Block[@BlockType='Inport']")
                tempInput.set('Name', i[2])
                mainChart.append(tempInput)
        else:
            print "模型没有输入"

        if not XMLProcess.outputList == []:
            for i in XMLProcess.outputList:
                template = ET.parse("template.xml")
                templateRoot = template.getroot()
                tempOutput = templateRoot.find(
                    "Outport/Block[@BlockType='Outport']")
                tempOutput.set('Name', i[2])
                mainChart.append(tempOutput)
        else:
            print "模型没有输出"

        # 重设SID
        mainChartRoot = root.find(
            "Model/System/Block[@BlockType='SubSystem']/System/Block[@BlockType='SubSystem']")
        SIDList = []
        sList = mainChart.findall("Block")
        SIDStart = 1
        for j in sList:
            j.set("SID", mainChartRoot.get("SID") + "::" + str(SIDStart))
            SIDStart += 1
        mainChart.find("P[@Name='SIDHighWatermark']").text = str(SIDStart - 1)

        # 重新连线
        SFunc = mainChart.find("Block[@BlockType='S-Function']")
        Termin = mainChart.find("Block[@BlockType='Terminator']")
        Demux = mainChart.find("Block[@BlockType='Demux']")

        def getLine(src, dst):
            template = ET.parse("template.xml")
            templateRoot = template.getroot()
            Line = templateRoot.find("Line")
            Line.find("P[@Name='Src']").text = src
            Line.find("P[@Name='Dst']").text = dst
            return Line

        # 连接输入输出
        num = 1
        for i in mainChart.findall("Block[@BlockType='Inport']"):
            Line = getLine(i.get("SID") + "#out:1", SFunc.get("SID") + "#in:" + str(num))
            num += 1
            mainChart.append(Line)

        portNumList = [i.text for i in SFunc.findall("Port/P[@Name='PortNumber']")]
        num = 0
        for i in mainChart.findall("Block[@BlockType='Outport']"):
            Line = getLine(
                SFunc.get("SID") + "#out:" + portNumList[num], i.get("SID") + "#in:1")
            num += 1
            mainChart.append(Line)

        # 连接额外的线
        SFunc_Demux = getLine(
            SFunc.get("SID") + "#out:" + "1", Demux.get("SID") + "#in:1")
        mainChart.append(SFunc_Demux)
        Demux_Termin = getLine(
            Demux.get("SID") + "#out:1", Termin.get("SID") + "#in:1")
        mainChart.append(Demux_Termin)

    def getChartName(self, chart):
        name = chart.find(".//P[@Name='name']").text
        if '/' in name:
            name = name.replace('/', '_')
        return name

    # 添加外层的state SSID为0
    def addRootState(self, root):
        chart = root.findall("Stateflow/machine/Children/chart")
        for i in chart:
            # CLUSTER_CHART 转 SET_CHART
            i.find("P[@Name='decomposition']").text = "SET_CHART"
            # 决定位置
            minLeftX = 0x3f3f3f3f
            minLeftY = 0x3f3f3f3f
            maxRightX = -1
            maxRightY = -1
            items = i.findall(".//P[@Name='position']")
            for j in items:
                posList = [float(num) for num in j.text[1:-1].split(' ')]
                minLeftX = (posList[0] < minLeftX) and posList[0] or minLeftX
                minLeftY = (posList[1] < minLeftY) and posList[1] or minLeftY
                if posList[0] + posList[2] > maxRightX:
                    maxRightX = posList[0] + posList[2]
                if posList[1] + posList[3] > maxRightY:
                    maxRightY = posList[1] + posList[3]
            positionText = '[' + str(minLeftX - 50) + ' ' + str(minLeftY - 50) + ' ' + str(
                maxRightX - minLeftX + 100) + ' ' + str(maxRightY - minLeftY + 100) + ']'
            # 获取模板
            template = ET.parse("template.xml")
            templateRoot = template.getroot()
            templateAdd = templateRoot.find("state/Children")
            templateState = templateAdd.find("state")
            childrenNode = i.find("Children")
            i.remove(childrenNode)
            templateState.append(childrenNode)
            # 设置state位置
            templateState.find("P[@Name='position']").text = positionText
            # 重置state名称
            templateState.find(
                "P[@Name='labelString']").text = self.getChartName(i)
            i.append(templateAdd)

    # 重新映射SSID
    # 1. Model中删除多余的subsystem/chart
    # 2. StateFlow instance 中删除多余的instance
    # 3. StateFlow/machine中合并内容
    def resetSSID(self, root):
        # 获取外层chart的名称和SSID
        chart = root.findall("Stateflow/machine/Children/chart")
        SSIDList = []
        for i in range(len(chart)):
            # 获取所有的SSID
            sList = chart[i].findall(".//*[@SSID]")
            for j in sList:
                SSID = j.get("SSID")
                SSIDList.append(str(i) + ':' + str(SSID))
        maxID = max([int(id.get("id"))
                     for id in root.findall(".//*[@id]")]) + 1
        SSIDDict = dict(
            zip(SSIDList, [i for i in range(maxID, maxID + len(SSIDList) + 1)]))

        for i in range(len(chart)):
            items = chart[i].findall(".//*[@SSID]")
            # 重新映射SSID
            for j in range(len(items)):
                if items[j].tag == "transition":
                    try:
                        items[j].find("src/P[@Name='SSID']").text = str(
                            SSIDDict[str(i) + ':' + items[j].find("src/P[@Name='SSID']").text])
                    except:
                        print "默认连线起点"
                    try:
                        items[j].find("dst/P[@Name='SSID']").text = str(
                            SSIDDict[str(i) + ':' + items[j].find("dst/P[@Name='SSID']").text])
                    except:
                        print "连线终点为空"

                items[j].set(
                    "SSID", str(SSIDDict[str(i) + ':' + items[j].get("SSID")]))

    # 寻找输入输出列表
    def getInputOutput(self, root):
        SubSystem = root.find("Model/System/Block[@BlockType='SubSystem']")
        lines = SubSystem.findall("System/Line")
        Blocks = SubSystem.findall("System/Block")

        for i in lines:
            srcText = i.find("P[@Name='Src']").text
            srcSID = srcText[:srcText.find('#')]
            srcPort = srcText[srcText.find(':') + 1:]
            srcBlock = SubSystem.find("System/Block[@SID='" + srcSID + "']")

            dstText = i.find("P[@Name='Dst']").text
            dstSID = dstText[:dstText.find('#')]
            dstPort = dstText[dstText.find(':') + 1:]
            dstBlock = SubSystem.find(
                "System/Block[@SID='" + dstSID + "']")

            # 如果某条线的src是inport 则dst端是总模型的输入
            if srcBlock.get("BlockType") == "Inport":
                # subSystem/Chart/name
                inputInfo = []
                inputInfo.append(SubSystem.get("Name"))
                inputInfo.append(dstBlock.get("Name"))
                # 寻找Model/System/Block[Inport]
                for j in dstBlock.findall("System/Block[@BlockType='Inport']"):
                    tmp = j.find("P[@Name='Port']")
                    if (tmp == None and dstPort == "1") or (tmp != None and tmp.text == dstPort):
                        inputInfo.append(j.get("Name"))
                        break
                XMLProcess.inputList.append(inputInfo)
            # 如果某条线的dst是outport，则src端是模型的总输出
            if dstBlock.get("BlockType") == "Outport":
                outputInfo = []
                outputInfo.append(SubSystem.get("Name"))
                outputInfo.append(srcBlock.get("Name"))
                for j in srcBlock.findall("System/Block[@BlockType='Outport']"):
                    tmp = j.find("P[@Name='Port']")
                    if (tmp == None and srcPort == '1') or (tmp != None and tmp.text == srcPort):
                        outputInfo.append(j.get("Name"))
                        break
                XMLProcess.outputList.append(outputInfo)
        # 重置第一个chart的输出名称（待完善）
        try:
            SubSystem.find("System/Block[@BlockType='SubSystem']/System/Block[@BlockType='Outport']").set(
                "Name", XMLProcess.outputList[0][2])
        except:
            print "第一个chart没有输出结点"

    # 合并chart
    def mergeChart(self, root):
        chart = root.findall("Stateflow/machine/Children/chart")
        Children = root.find("Stateflow/machine/Children")
        # 将chart合并
        nameList = []
        # 先不考虑1.输入输出数据 2.连线 3.外层chart
        mainChart = chart[0]
        maxWidthPre = 0
        height = 100
        for i in range(len(chart)):
            # 获取nameList
            name = chart[i].find("P[@Name='name']").text
            if '/' in name:
                name = name.replace('/', '_')
            nameList.append(name)
            # 修改位置
            positionPre = chart[i].find(
                "Children/state").find("P[@Name='position']").text
            posList = [float(num) for num in positionPre[1:-1].split(' ')]
            shiftX = maxWidthPre + 100 - posList[0]  # 获取偏移量
            shiftY = height - posList[1]
            maxWidthPre += 100 + posList[2]
            for item in chart[i].findall(".//Children/*"):
                # state
                if item.tag == "state":
                    positionPre = item.find("P[@Name='position']").text
                    posList = [float(num)
                               for num in positionPre[1:-1].split(' ')]
                    posList[0] += shiftX
                    posList[1] += shiftY
                    item.find("P[@Name='position']").text = '[' + str(posList[0]) + ' ' + str(
                        posList[1]) + ' ' + str(posList[2]) + ' ' + str(posList[3]) + ']'

                # transition
                if item.tag == "transition":
                    # labelPosition
                    positionPre = item.find("P[@Name='labelPosition']").text
                    posList = [float(num)
                               for num in positionPre[1:-1].split(' ')]
                    posList[0] += shiftX
                    posList[1] += shiftY
                    item.find("P[@Name='labelPosition']").text = '[' + str(posList[0]) + ' ' +\
                        str(posList[1]) + ' ' + str(posList[2]) +\
                        ' ' + str(posList[3]) + ']'

                    # src
                    positionPre = item.find("src/P[@Name='intersection']").text
                    posList = [float(num)
                               for num in positionPre[1:-1].split(' ')]
                    posList[4] += shiftX
                    posList[5] += shiftY
                    item.find("src/P[@Name='intersection']").text = '[' + str(posList[0]) + ' ' +\
                        str(posList[1]) + ' ' + str(posList[2]) + ' ' + str(posList[3]) + ' ' +\
                        str(posList[4]) + ' ' + str(posList[5]) + ' ' +\
                        str(posList[6]) + ' ' + str(posList[7]) + ']'

                    # dst
                    positionPre = item.find("dst/P[@Name='intersection']").text
                    posList = [float(num)
                               for num in positionPre[1:-1].split(' ')]
                    posList[4] += shiftX
                    posList[5] += shiftY
                    item.find("dst/P[@Name='intersection']").text = '[' + str(posList[0]) + ' ' +\
                        str(posList[1]) + ' ' + str(posList[2]) + ' ' + str(posList[3]) + ' ' +\
                        str(posList[4]) + ' ' + str(posList[5]) + ' ' +\
                        str(posList[6]) + ' ' + str(posList[7]) + ']'

                    # midPoint
                    positionPre = item.find("P[@Name='midPoint']").text
                    posList = [float(num)
                               for num in positionPre[1:-1].split(' ')]
                    posList[0] += shiftX
                    posList[1] += shiftY
                    item.find("P[@Name='midPoint']").text = '[' +\
                        str(posList[0]) + ' ' + str(posList[1]) + ']'

            # 将其他chart的内容(rootChart和输入输出)放到第一个chart中
            if i > 0:
                mainChart.find("Children").extend(
                    chart[i].findall("Children/*"))
                # 删除多余的StateFlow->Children->chart
                Children.remove(chart[i])

        # 删除多余的Stateflow->instance, 仅保留第一个
        for i in root.findall("Stateflow/instance")[1:]:
            root.find("Stateflow").remove(i)
        # 删除多余的Model->System->Block[subsystem]->Block[Chart]
        ChartNameList = []
        for i in nameList[1:]:  # 第一个Chart是mainchart
            ChartNameList.append(i[i.find('_') + 1:])
        for i in root.findall("Model/System/Block[@BlockType='SubSystem']/System/Block[@BlockType='SubSystem']"):
            if i.get("Name") in ChartNameList:
                root.find(
                    "Model/System/Block[@BlockType='SubSystem']/System").remove(i)

    # 重置总输入输出，和中间的输出设置为顶层,将其余的输入删除
    def replaceInputOutput(self, root):
        # 已经添加了顶层state，只有一个chart
        charts = root.findall("Stateflow/machine/Children/chart")
        for i in charts:
            children = i.find("Children")
            rootState =children.find("state/Children")
            datas =rootState.findall("data")
            inputData = []
            outputData = []
            chartName = i.find("P[@Name='name']").text[i.find("P[@Name='name']").text.find('/')+1:]
            for j in XMLProcess.inputList:
                if j[1] == chartName:
                    inputData.append(j[2])
            for j in XMLProcess.outputList:
                if j[1] == chartName:
                    outputData.append(j[2])
            # 重置总输入输出为顶层并重命名
            for j in datas:
                if j.find("P[@Name='scope']").text == "INPUT_DATA" and j.get("name") in inputData or \
                        j.find("P[@Name='scope']").text == "OUTPUT_DATA" and j.get("name") in outputData:
                    rootState.remove(j)
                    children.append(j)
                    #j.set("name", i.find("P[@Name='name']").text+"/"+j.get("name"))
            # 重置其余的输出为顶层并重命名


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
