#coding=utf-8




def rule1():
    #参数
    num = 3

    #出现次数
    times = 3
    #规则，最大178个值
    rule = [0,0,1,1] * 4
    #每一列的开奖号码
    # target = [0,0,0,1,1,0, 1,1,1,1,0,0, 1,0,1,0,1,0,0,0]
    # target = [0,0,1,1,1,1, 0,0,1,1,0,0, 1,0,0,0,1,0,0,0]
    target = [0,0,1,0,0,0,1,1,1,1, 0,0,1,1,0,0, 1,0,0,0,1,1,0,0]
    # target = [0,0,1,1]
    # target = [0,0,0,0,-1,0, 0,0,0,0,1,1, 1,-1,0,0,0,0,1,1]
    #开奖号码对应的中奖值
    prob_value = [0] * len(target)
    # print prob_value
    # print rule


    # print target

    count = 0
    index = 0
    max = len(target)- num
    while(count < max):
        if(target[count:count+num] == rule[index:index+num]):
            print target[count:count+num]
            #进一步判断target下一位与rule的下一位是否相等
            count = count + num
            index = index + num
            print count,'   ',target[count],'   ',index,'   ',rule[index]
            while(target[count] == rule[index]):
                prob_value[count] = 1
                count = count + 1
                index = index + 1
                #如果到最后一个，跳出循环
                if (count >= len(target)):
                    break

            #循环结束即target下一位与rule的下一位不相等，记为-1
            #下一位开始计数
            if (count >= len(target)):
                break
            else:
                prob_value[count] = -1
                count = count + 1
                index = 0
        else:
            print "no match ",count
            count = count + 1

    print prob_value


#
def rule2():
    #参数
    num = 3
    #出现次数
    times = 3
    #规则，最大178个值
    rule = [0,0,1,1] * 4
    #每一列的开奖号码
    # target = [0,0,0,1,1,0, 1,1,1,1,0,0, 1,0,1,0,1,0,0,0]
    # target = [0,0,1,1,1,1, 0,0,1,1,0,0, 1,0,0,0,1,0,0,0]
    # target = [0,0,1,0,0,0,1,1,1,1, 0,0,1,1,0,0, 1,0,0,0,1,1,0,0]
    target = [1,1,1,0,0, 1,1,1,1,1, 1,0,0,1,1, 0,0,0,0,0, 0,0,0,1,1,0,1,0]
    # target = [0,0,1,1]
    # target = [0,0,0,0,-1,0, 0,0,0,0,1,1, 1,-1,0,0,0,0,1,1]
    #开奖号码对应的中奖值
    prob_value = [0] * len(target)
    # print prob_value
    # print rule
    # print target
    count = 0
    index = 0
    max = len(target)- num
    while(count < max):
        #是否匹配规则
        if(target[count:count+num] == rule[index:index+num] and count>=times ):
            #处理location位置
            try:
                location = len(prob_value) - prob_value[::-1].index(-1) - 1
            except:
                location = -1
            print "location is ",location
            print "count is ",count
            print sum(target[count-times:count])
            #获取最后一个-1的位置，当前匹配到的位置与-1位置间隔大于3，再次判断是否三个相同
            if ((count - location > times) and (sum(target[count-times:count]) == 0 or sum(target[count-times:count]) == times)):
            #判断规则前是否出现过times次
            # if(count>=times):
                print target[count:count+num]
                #进一步判断target下一位与rule的下一位是否相等
                count = count + num
                index = index + num
                print count,'   ',target[count],'   ',index,'   ',rule[index]
                while(target[count] == rule[index]):
                    prob_value[count] = 1
                    count = count + 1
                    index = index + 1
                    #如果到最后一个，跳出循环
                    if (count >= len(target)):
                        break

                #循环结束即target下一位与rule的下一位不相等，记为-1
                #下一位开始计数
                if (count >= len(target)):
                    break
                else:
                    prob_value[count] = -1
                    count = count + 1
                    index = 0
            else:
                print "no match ",count
                count = count + 1
        else:
            print "no match ",count
            count = count + 1

    print prob_value


def test_v8():
    #参数
    num = 3

    #规则，最大178个值
    rule = [0,0,1,1] * 4
    #每一列的开奖号码
    # target = [0,0,0,1,1,0, 1,1,1,1,0,0, 1,0,1,0,1,0,0,0]
    # target = [0,0,1,1,1,1, 0,0,1,1,0,0, 1,0,0,0,1,0,0,0]
    # target = [0,0,1,0,0,0,1,1,1,1, 0,0,1,1,0,0, 1,0,0,0,1,1,0,0]
    target = [1,1,1,0,0, 1,1,1,1,1, 1,0,0,1,1, 0,0,0,0,0, 0,0,0,1,0,0,1,0]
    # target = [0,0,1,1]
    # target = [0,0,0,0,-1,0, 0,0,0,0,1,1, 1,-1,0,0,0,0,1,1]
    #开奖号码对应的中奖值
    prob_value = [0] * len(target)
    compute_rule(num, rule, target, prob_value)

#v8新规则,原始数据处理
def test_v9():
    #传入数据
    data = 5
    #参数固定
    num = 2

    #规则，最大178个值
    rule = [data] * (num + 1)
    #每一列的开奖号码
    # target = [0,0,0,1,1,0, 1,1,1,1,0,0, 1,0,1,0,1,0,0,0]
    # target = [0,0,1,1,1,1, 0,0,1,1,0,0, 1,0,0,0,1,0,0,0]
    # target = [0,0,1,0,0,0,1,1,1,1, 0,0,1,1,0,0, 1,0,0,0,1,1,0,0]
    # target = [1,1,1,0,0, 1,1,1,1,1, 1,0,0,1,1, 0,0,0,0,0, 0,0,0,1,0,0,1,0]
    target = [1,3,2,5,5, 5,5,5,1,5]
    # target = [0,0,1,1]
    # target = [0,0,0,0,-1,0, 0,0,0,0,1,1, 1,-1,0,0,0,0,1,1]
    #开奖号码对应的中奖值
    prob_value = [0] * len(target)
    compute_rule(num, rule, target, prob_value)

def compute_rule(num, rule, target, prob_value):
    count = 0
    index = 0
    max = len(target)- num
    while(count < max):
        if(target[count:count+num] == rule[index:index+num]):
            # print target[count:count+num]
            #进一步判断target下一位与rule的下一位是否相等
            count = count + num
            index = index + num
            # print count,'   ',target[count],'   ',index,'   ',rule[index]
            if(target[count] == rule[index]):
                prob_value[count] = 1
                count = count + 1
                index = 0
                #如果到最后一个，跳出循环
                if (count >= len(target)):
                    break
            else:
                #循环结束即target下一位与rule的下一位不相等，记为-1
                #下一位开始计数
                if (count >= len(target)):
                    break
                else:
                    prob_value[count] = -1
                    count = count + 1
                    index = 0
        else:
            # print "不满足",count
            count = count + 1
    print prob_value
    return prob_value

def rule3():
    print "rule3"




def test():
    a= [1,2,3,0,1,3,2,2,333,3,2,4]
    print a[0:3]
    print len(a) - a[::-1].index(2) - 1
    # print reverse(a)
    # print a.find(2,1)
if __name__ == '__main__':
    # rule1()
    # rule2()
    test_v9()
    # compute_rule(num, rule, target, prob_value)

    # rule3()
    # test()
