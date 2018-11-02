# coding=utf-8
import xml.dom.minidom as xmldom
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d


def readTimeFile(file_path):
    """
    自定义函数，用于读取行时文件

    :param file_path: 行时文件的文件路径
    :return: 以list方式返回行时文件中的FrameNum和UTC属性值
    """
    FrameNums = []
    UTCs = []

    # 新建xml解析对象
    domobj = xmldom.parse(file_path)
    # 获取根节点ClockInfo
    ClockInfo = domobj.documentElement
    # 找到根节点下的叫做TimeParams的子节点
    TimeParams = ClockInfo.getElementsByTagName("TimeParams")[0]
    # 找到TimeParams节点下的所有LineParam节点
    LineParam = TimeParams.getElementsByTagName("LineParam")

    # 对每一个LineParam获取相关属性信息
    for item in LineParam:
        # 获取FrameNum、UTC节点并且返回它们的属性值
        FrameNum = item.getElementsByTagName("FrameNum")[0].firstChild.data
        UTC = item.getElementsByTagName("UTC")[0].firstChild.data

        # 将获取到的一帧的属性值添加到list中
        FrameNums.append(int(FrameNum))
        UTCs.append(float(UTC))

    return FrameNums, UTCs


def readAttFile(file_path):
    """
    自定义函数用于读取姿态文件

    :param file_path: 姿态文件的文件路径
    :return: 以list方式返回UTC、Roll、Pitch、Yaw属性值
    """
    UTCs = []
    Rolls = []
    Pitchs = []
    Yaws = []

    domobj = xmldom.parse(file_path)
    AttMeasurement = domobj.documentElement
    AttitudeParameter = AttMeasurement.getElementsByTagName("AttitudeParameter")[0]
    AttData = AttitudeParameter.getElementsByTagName("AttData")

    for item in AttData:
        UTC = item.getElementsByTagName("UTC")[0].firstChild.data
        roll = item.getElementsByTagName("Roll")[0].firstChild.data
        pitch = item.getElementsByTagName("Pitch")[0].firstChild.data
        yaw = item.getElementsByTagName("Yaw")[0].firstChild.data

        UTCs.append(float(UTC))
        Rolls.append(float(roll))
        Pitchs.append(float(pitch))
        Yaws.append(float(yaw))

    return UTCs, Rolls, Pitchs, Yaws


# main函数
if __name__ == '__main__':
    # 第一步
    # 分别读取姿态与行时文件
    UTCs, Rolls, Pitchs, Yaws = readAttFile("VAZ1_201707010006_001.att")
    FrameNum, UTC = readTimeFile("VAZ1_201707010006_001.time")

    # 第二步
    # 直接调用函数对Roll、Pitch、Yaw分别进行数据内插，得到内插函数
    # 内插即是寻找自变量(UTC)与因变量(Roll、Pitch、Yaw)的关系
    f_Roll = interp1d(UTCs, Rolls, kind='cubic')
    f_Pitch = interp1d(UTCs, Pitchs, kind='cubic')
    f_Yaw = interp1d(UTCs, Yaws, kind='cubic')

    # 由于是内插，所以不能“外推”(如果是拟合就没这个问题了)
    # 也就是说行时文件的开始与结束时间不能超过姿态文件中时间的范围
    # 所以需要对行时文件中的数据进行筛选
    # 对于超过的那些帧，直接丢弃，暂不做处理
    good_UTC = []
    good_FrameNum = []
    for num, utc in zip(FrameNum, UTC):
        if UTCs[0] <= utc <= UTCs[-1]:
            good_FrameNum.append(num)
            good_UTC.append(utc)

    # 第三步
    # 调用内插函数对行时文件中的数据进行内插，得到结果
    pred_Roll = f_Roll(good_UTC)
    pred_Pitch = f_Pitch(good_UTC)
    pred_Yaw = f_Yaw(good_UTC)

    # 第四步
    # 新建一个文本文件名字叫att.txt用于存放内插出的数据
    save_file = file("att.txt", 'w')
    save_file.write("FrameNum\tUTC\tRoll\tPitch\tYaw\n")
    # 对于每一帧的数据都逐行输出到控制台以及写入文本文件
    for i in range(good_UTC.__len__()):
        print good_FrameNum[i], good_UTC[i], pred_Roll[i], pred_Pitch[i], pred_Yaw[i]
        save_file.write(good_FrameNum[i].__str__() + "\t" +
                        good_UTC[i].__str__() + "\t" +
                        pred_Roll[i].__str__() + "\t" +
                        pred_Pitch[i].__str__() + "\t" +
                        pred_Yaw[i].__str__() + "\n")

    # 写入完成后，别忘关闭文件输出流
    save_file.close()

    # 至此，内插完成。可以将内插的数据与真实数据进行比较
    plt.figure(1)  # 图像编号
    plt.title("interpolation for Roll")  # 图像标题
    plt.plot(UTCs, Rolls, label='real data')
    plt.plot(good_UTC, pred_Roll, label='interpolate data')
    plt.legend()  # 显示图例
    plt.grid()  # 显示格网

    plt.figure(2)
    plt.title("interpolation for Pitch")
    plt.plot(UTCs, Pitchs, label='real data')
    plt.plot(good_UTC, pred_Pitch, label='interpolate data')
    plt.legend()
    plt.grid()

    plt.figure(3)
    plt.title("interpolation for Yaw")
    plt.plot(UTCs, Yaws, label='real data')
    plt.plot(good_UTC, pred_Yaw, label='interpolate data')
    plt.legend()
    plt.grid()

    plt.show()
