from os import getcwd, listdir
from sys import path
from  cv2 import imread, resize, imshow, waitKey

path.append(getcwd())
from foo.pictureR import pictureFind

class Booty:
    def __init__(self, cwd):
        self.cwd = cwd
        self.bootyPicPath = cwd + '/res/booty/pics'
        self.bootyList = {'RMA70-12':pictureFind.picRead(self.bootyPicPath + '/RMA70-12.png'),
                        'RMA70-24':pictureFind.picRead(self.bootyPicPath + '/RMA70-24.png' ),
                        '白马醇':pictureFind.picRead(self.bootyPicPath + '/白马醇.png'),
                        '炽合金':pictureFind.picRead(self.bootyPicPath + '/炽合金.png'),
                        '炽合金块':pictureFind.picRead(self.bootyPicPath + '/炽合金块.png'),
                        '代糖':pictureFind.picRead(self.bootyPicPath + '/代糖.png'),
                        '改量装置':pictureFind.picRead(self.bootyPicPath + '/改量装置.png'),
                        '固源岩':pictureFind.picRead(self.bootyPicPath + '/固源岩.png'),
                        '固源岩组':pictureFind.picRead(self.bootyPicPath + '/固源岩组.png'),
                        '聚合凝胶':pictureFind.picRead(self.bootyPicPath + '/聚合凝胶.png'),
                        '聚酸酯':pictureFind.picRead(self.bootyPicPath + '/聚酸酯.png'),
                        '聚酸酯块':pictureFind.picRead(self.bootyPicPath + '/聚酸酯块.png'),
                        '聚酸酯组':pictureFind.picRead(self.bootyPicPath + '/聚酸酯组.png'),
                        '凝胶':pictureFind.picRead(self.bootyPicPath + '/凝胶.png'),
                        '扭转醇':pictureFind.picRead(self.bootyPicPath + '/扭转醇.png'),
                        '破损装置':pictureFind.picRead(self.bootyPicPath + '/破损装置.png'),
                        '轻锰矿':pictureFind.picRead(self.bootyPicPath + '/轻锰矿.png'),
                        '全新装置':pictureFind.picRead(self.bootyPicPath + '/全新装置.png'),
                        '三水锰矿':pictureFind.picRead(self.bootyPicPath + '/三水锰矿.png'),
                        '双酮':pictureFind.picRead(self.bootyPicPath + '/双酮.png'),
                        '糖':pictureFind.picRead(self.bootyPicPath + '/糖.png'),
                        '糖聚块':pictureFind.picRead(self.bootyPicPath + '/糖聚块.png'),
                        '糖组':pictureFind.picRead(self.bootyPicPath + '/糖组.png'),
                        '提纯源岩':pictureFind.picRead(self.bootyPicPath + '/提纯源岩.png'),
                        '酮凝集':pictureFind.picRead(self.bootyPicPath + '/酮凝集.png'),
                        '酮凝集组':pictureFind.picRead(self.bootyPicPath + '/酮凝集组.png'),
                        '酮阵列':pictureFind.picRead(self.bootyPicPath + '/酮阵列.png'),
                        '五水研磨石':pictureFind.picRead(self.bootyPicPath + '/五水研磨石.png'),
                        '研磨石':pictureFind.picRead(self.bootyPicPath + '/研磨石.png'),
                        '异铁':pictureFind.picRead(self.bootyPicPath + '/异铁.png'),
                        '异铁块':pictureFind.picRead(self.bootyPicPath + '/异铁块.png'),
                        '异铁碎片':pictureFind.picRead(self.bootyPicPath + '/异铁碎片.png'),
                        '异铁组':pictureFind.picRead(self.bootyPicPath + '/异铁组.png'),
                        '源岩':pictureFind.picRead(self.bootyPicPath + '/源岩.png'),
                        '酯原料':pictureFind.picRead(self.bootyPicPath + '/酯原料.png'),
                        '装置':pictureFind.picRead(self.bootyPicPath + '/装置.png'),
                        '辅助芯片':pictureFind.picRead(self.bootyPicPath + '/辅助芯片.png'),
                        '近卫芯片':pictureFind.picRead(self.bootyPicPath + '/近卫芯片.png'),
                        '狙击芯片':pictureFind.picRead(self.bootyPicPath + '/狙击芯片.png'),
                        '术师芯片':pictureFind.picRead(self.bootyPicPath + '/术师芯片.png'),
                        '特种芯片':pictureFind.picRead(self.bootyPicPath + '/特种芯片.png'),
                        '先锋芯片':pictureFind.picRead(self.bootyPicPath + '/先锋芯片.png'),
                        '医疗芯片':pictureFind.picRead(self.bootyPicPath + '/医疗芯片.png'),
                        '重装芯片':pictureFind.picRead(self.bootyPicPath + '/重装芯片.png'),
                        '辅助双芯片':pictureFind.picRead(self.bootyPicPath + '/辅助双芯片.png'),
                        '近卫双芯片':pictureFind.picRead(self.bootyPicPath + '/近卫双芯片.png'),
                        '狙击双芯片':pictureFind.picRead(self.bootyPicPath + '/狙击双芯片.png'),
                        '术师双芯片':pictureFind.picRead(self.bootyPicPath + '/术师双芯片.png'),
                        '特种双芯片':pictureFind.picRead(self.bootyPicPath + '/特种双芯片.png'),
                        '先锋双芯片':pictureFind.picRead(self.bootyPicPath + '/先锋双芯片.png'),
                        '医疗双芯片':pictureFind.picRead(self.bootyPicPath + '/医疗双芯片.png'),
                        '重装双芯片':pictureFind.picRead(self.bootyPicPath + '/重装双芯片.png')}
        self.one = pictureFind.picRead(self.cwd + '/res/booty/num/1.png')
        self.two = pictureFind.picRead(self.cwd + '/res/booty/num/2.png')

    def bootyCheck(self, bootyName, screenshot):
        scs = imread(screenshot)
        scs = resize(scs, (1920, 1080))
        scs = scs[770:1080, 710:1920]
        #imshow('test', scs)
        #waitKey(0)
        bootyInfo = pictureFind.matchImg(scs, self.bootyList[bootyName], confidencevalue=0.5, targetSize=(0,0))
        if bootyInfo == None:
            return 0
        else:
            rdPos = bootyInfo['rectangle'][3]
            if '双芯片' in bootyName:
                corpX1 = rdPos[0] - 20
                corpX2 = rdPos[0] + 25
                corpY1 = rdPos[1] + 15
                corpY2 = rdPos[1] + 60
            elif '芯片' in bootyName:
                corpX1 = rdPos[0] - 15
                corpX2 = rdPos[0] + 25
                corpY1 = rdPos[1] + 15
                corpY2 = rdPos[1] + 60
            else:
                corpX1 = rdPos[0] - 30
                corpX2 = rdPos[0] + 10
                corpY1 = rdPos[1] + 5
                corpY2 = rdPos[1] + 50
            if corpX1 < 0 or corpX2 > 1210 or corpY1 < 0 or corpY2 > 310:
                return 0
            bootyNumPic = scs[corpY1:corpY2, corpX1:corpX2]
            
            #imshow('test', bootyNumPic)
            #waitKey(0)

            oneCheck = pictureFind.matchImg(bootyNumPic, self.one)
            #print(oneCheck)
            twoCheck = pictureFind.matchImg(bootyNumPic, self.two)
            #print(twoCheck)
            if oneCheck != None:
                return 1
            elif twoCheck != None:
                return 2
            else:
                return 0
