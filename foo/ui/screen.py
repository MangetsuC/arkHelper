class Screen:
    def __init__(self, screens):
        self.vertexes = []
        self.screenHLine = []
        self.screenVLine = []
        self.HBorder = None
        self.VBorder = None
        for eachScreen in screens:
            self.addPoint(eachScreen.x(), eachScreen.y())
            self.addPoint(eachScreen.x() + eachScreen.width(), eachScreen.y())
            self.addPoint(eachScreen.x(), eachScreen.y() + eachScreen.height(),)
            self.addPoint(eachScreen.x() + eachScreen.width(), eachScreen.y() + eachScreen.height())

        self.vertexes.sort(key = lambda y:y[1])
        tempPointGroup = []
        for eachVertexNum in range(len(self.vertexes)):
            if eachVertexNum == 0:
                nowGroup = []
                nowGroup.append(self.vertexes[eachVertexNum])
            elif eachVertexNum == len(self.vertexes) - 1:
                nowGroup.append(self.vertexes[eachVertexNum])
                tempPointGroup.append(nowGroup.copy())
            else:
                if self.vertexes[eachVertexNum][1] != self.vertexes[eachVertexNum - 1][1]:
                    #y坐标不相等
                    tempPointGroup.append(nowGroup.copy())
                    nowGroup.clear()
                    nowGroup.append(self.vertexes[eachVertexNum])
                else:
                    nowGroup.append(self.vertexes[eachVertexNum])
        for eachGroup in tempPointGroup:
            eachGroup.sort(key = lambda x:x[0])
            self.screenHLine.append([eachGroup[0], eachGroup[-1]])

        self.vertexes.sort(key = lambda x:x[0])
        tempPointGroup = []
        for eachVertexNum in range(len(self.vertexes)):
            if eachVertexNum == 0:
                nowGroup = []
                nowGroup.append(self.vertexes[eachVertexNum])
            elif eachVertexNum == len(self.vertexes) - 1:
                nowGroup.append(self.vertexes[eachVertexNum])
                tempPointGroup.append(nowGroup.copy())
            else:
                if self.vertexes[eachVertexNum][0] != self.vertexes[eachVertexNum - 1][0]:
                    #x坐标不相等
                    tempPointGroup.append(nowGroup.copy())
                    nowGroup.clear()
                    nowGroup.append(self.vertexes[eachVertexNum])
                else:
                    nowGroup.append(self.vertexes[eachVertexNum])
        for eachGroup in tempPointGroup:
            eachGroup.sort(key = lambda y:y[1])
            self.screenVLine.append([eachGroup[0], eachGroup[-1]])

        print(self.screenHLine)
        print(self.screenVLine)


    def addPoint(self, pointX, pointY):
        self.vertexes.append((pointX, pointY))
        self.vertexes = list(set(self.vertexes))

    def relativePosPointLine(self, pointX, pointY, line):
        if line[0][0] == line[1][0]:
            #竖直线
            if line[0][1] <= pointY <= line[1][1]:
                if pointX <= line[0][0]:
                    if self.VBorder == None:
                        self.VBorder = line[0][0]
                    elif self.VBorder > line[0][0]:
                        self.VBorder = line[0][0]
                    return 1 #在线左侧
                else:
                    if self.VBorder == None:
                        self.VBorder = line[0][0]
                    elif self.VBorder < line[0][0]:
                        self.VBorder = line[0][0]
                    return 2 #在线右侧
            else:
                return 0 #不在线的范围内
        else:
            #水平线
            if line[0][0] <= pointX <= line[1][0]:
                if pointY <= line[0][1]:
                    if self.HBorder == None:
                        self.HBorder = line[0][1]
                    elif self.HBorder > line[0][1]:
                        self.HBorder = line[0][1]
                    return 1 #在线上方
                else:
                    if self.HBorder == None:
                        self.HBorder = line[0][1]
                    elif self.HBorder < line[0][1]:
                        self.HBorder = line[0][1]
                    return 2 #在线下方
            else:
                return 0 #不在线的范围内

    def checkPos(self, pointX, pointY):
        ans = [3, 3] #[1]上下，[0]左右
        temp = 0
        for eachVline in self.screenVLine:
            temp |= self.relativePosPointLine(pointX, pointY, eachVline)
        ans[0] = temp

        temp = 0
        for eachHline in self.screenHLine:
            temp |= self.relativePosPointLine(pointX, pointY, eachHline)
        ans[1] = temp
        
        return ans

    def getNewPos(self, relativePos, mousePosX, mousePosY, widgetW, widgetH):
        newPos = [mousePosX, mousePosY]
        if relativePos != [3, 3]:
            if relativePos[0] != 3:
                if relativePos[0] == 1: #在所有线左侧
                    newPos[0] = self.VBorder
                elif relativePos[0] == 2: #在所有线右侧
                    newPos[0] = self.VBorder - widgetW
            if relativePos[1] != 3:
                if relativePos[1] == 1: #在所有线上方
                    newPos[1] = self.HBorder
                elif relativePos[1] == 2: #在所有线下方
                    newPos[1] = self.HBorder - widgetH
        return newPos

    def checkWidget(self, mousePosX, mousePosY, widgetW, widgetH):
        newPos = [mousePosX, mousePosY]
        leftTopPos = [mousePosX, mousePosY]
        rightTopPos = [mousePosX + widgetW, mousePosY]
        leftBottomPos = [mousePosX, mousePosY + widgetH]
        rightBottomPos = [mousePosX + widgetW, mousePosY + widgetH]
        ansLeftTop = self.checkPos(leftTopPos[0], leftTopPos[1])
        ansRightTop = self.checkPos(rightTopPos[0], rightTopPos[1])
        ansLeftBottom = self.checkPos(leftBottomPos[0], leftBottomPos[1])
        ansRightBottom = self.checkPos(rightBottomPos[0], rightBottomPos[1])

        if ansLeftTop != [3, 3]:
            ans = ansLeftTop.copy()
            if ansLeftTop == ansLeftBottom and ansLeftTop != ansRightTop:
                ans[1] = 3
            elif ansLeftTop != ansLeftBottom and ansLeftTop == ansRightTop:
                ans[0] = 3
            tempNewPos = self.getNewPos(ans, mousePosX, mousePosY, widgetW, widgetH)
            if tempNewPos[0] != mousePosX:
                newPos[0] = tempNewPos[0]
            if tempNewPos[1] != mousePosY:
                newPos[1] = tempNewPos[1]

        if ansRightTop != [3, 3]:
            ans = ansRightTop.copy()
            if ansRightTop == ansRightBottom and ansRightTop != ansLeftTop:
                ans[1] = 3
            elif ansRightTop != ansRightBottom and ansRightTop == ansLeftTop:
                ans[0] = 3
            tempNewPos = self.getNewPos(ans, mousePosX, mousePosY, widgetW, widgetH)
            if tempNewPos[0] != mousePosX:
                newPos[0] = tempNewPos[0]
            if tempNewPos[1] != mousePosY:
                newPos[1] = tempNewPos[1]

        if ansLeftBottom != [3, 3]:
            ans = ansLeftBottom.copy()
            if ansLeftBottom == ansLeftTop and ansLeftBottom != ansRightBottom:
                ans[1] = 3
            elif ansLeftBottom != ansLeftTop and ansLeftBottom == ansRightBottom:
                ans[0] = 3
            tempNewPos = self.getNewPos(ans, mousePosX, mousePosY, widgetW, widgetH)
            if tempNewPos[0] != mousePosX:
                newPos[0] = tempNewPos[0]
            if tempNewPos[1] != mousePosY:
                newPos[1] = tempNewPos[1]

        if ansRightBottom != [3, 3]:
            ans = ansRightBottom.copy()
            if ansRightBottom == ansRightTop and ansRightBottom != ansLeftBottom:
                ans[1] = 3
            elif ansRightBottom != ansRightTop and ansRightBottom == ansLeftBottom:
                ans[0] = 3
            tempNewPos = self.getNewPos(ans, mousePosX, mousePosY, widgetW, widgetH)
            if tempNewPos[0] != mousePosX:
                newPos[0] = tempNewPos[0]
            if tempNewPos[1] != mousePosY:
                newPos[1] = tempNewPos[1]

        return newPos
