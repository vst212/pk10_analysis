# -*- coding: utf-8 -*-
__author__ = 'shifeixiang'

#格式转换
def parase_lotterys(lottery):
    # print lottery
    #定义行列矩阵,179行，10列，基础数组，原始数据
    base_lottery_list = [[0 for i in range(10)] for i in range(len(lottery))]
    #定义行列矩阵,179行，10列，奇偶数组，1表示奇，0表示偶
    parity_lottery_list = [[0 for i in range(10)] for i in range(len(lottery))]
    #定义行列矩阵,179行，10列，大小数组,1表示大，0表示小
    larsma_lottery_list = [[0 for i in range(10)] for i in range(len(lottery))]
    count = 0
    for loty in lottery:
        # print loty.lottery_number
        temp_lotys = loty.lottery_number.split(',')
        # print temp_lotys
        # print count,len(lottery)
        for i in range(len(temp_lotys)):
            sub_num = int(temp_lotys[i])
            base_lottery_list[len(lottery) - count - 1][i] = sub_num
            if (sub_num%2 == 1):
                parity_lottery_list[len(lottery) -1 - count][i] = 1
            if (sub_num > 5):
                larsma_lottery_list[len(lottery) -1 - count][i] = 1
        count = count + 1
    tran_base_lottery_list = map(list, zip(*base_lottery_list))
    # map(list, zip(*parity_lottery_list))
    # print base_lottery_list[0]
    # print base_lottery_list[1]
    # print tran_base_lottery_list[0]
    # print tran_base_lottery_list[1]
    #行列转置
    tran_parity_lottery_list = map(list, zip(*parity_lottery_list))
    tran_base_lottery_list = map(list, zip(*base_lottery_list))
    return tran_base_lottery_list,tran_parity_lottery_list,larsma_lottery_list

    # for i in range(5):
    #     print base_lottery_list[i]
    #     print parity_lottery_list[i]
    #     print larsma_list[i]
    #     print '-----'


#格式转换
#首行和末行已转换，已转换成正式查询数组,order未做任何转换
def parase_lotterys_cross(lottery):

    #定义行列矩阵,179列，10行，基础数组，原始数据，前后互换
    base_lottery_list = [[0 for i in range(10)] for i in range(len(lottery))]

    #标准数据
    order_lottery_list = [[0 for i in range(10)] for i in range(len(lottery))]

    #定义数据10行，179列，第一列与最后一列互换,左右互换
    base_lottery_list_left_right_change = [[0 for i in range(10)] for i in range(len(lottery))]

    count = 0
    for loty in lottery:
        # print loty.lottery_number
        temp_lotys = loty.lottery_number.split(',')
        #数组宽度
        wid_length = len(temp_lotys)
        for i in range(wid_length):
            sub_num = int(temp_lotys[i])
            #第一行与最后一样转换
            base_lottery_list[len(lottery) - count - 1][i] = sub_num
            order_lottery_list[count][i] = sub_num
            base_lottery_list_left_right_change[len(lottery) - count - 1][wid_length - i - 1] = sub_num

        count = count + 1

    #base_lottery_list首行和末行已转换，已转换成正式查询数组;  base_lottery_list_left_right_change  首行和末行转换后再左右转换，便于逆向查询
    return order_lottery_list

#补全后数组右上角向左下角开始
def tran_croos_data_auto(base_data,column_num, calc_num):

    for i in range(int(column_num-calc_num)):
        base_data.append([0]*column_num)
        base_data.insert(0,[0]*column_num)

    #定义最终的数组list
    cross_data_list = [[0 for i in range(column_num)] for i in range(len(base_data) - (column_num-calc_num) - (calc_num - 1))]

    row_num = 0
    max = len(base_data) - (column_num-calc_num) - (calc_num - 1)
    while(row_num<max):
        for cloumn_num in range(len(base_data[row_num])):
            cross_data_list[row_num][cloumn_num] = base_data[row_num+cloumn_num][len(base_data[row_num]) - cloumn_num -1]
        row_num = row_num + 1
    return cross_data_list

#左右交换
def change_r_l(base_data_single):
    if len(base_data_single) != 0:
        row_data_left_change_right = [[0 for i in range(len(base_data_single[0]))] for i in range(len(base_data_single))]
        count = 0
        for row_data in base_data_single:
            wid_length = len(row_data)
            for i in range(wid_length):
                #前后倒置，左右交换
                # row_data_left_change_right[len(base_data) - count - 1][wid_length-i-1] = row_data[i]
                # 前后倒置
                # row_data_left_change_right[len(base_data) - count - 1][i] = row_data[i]
                #左右交换
                row_data_left_change_right[count][wid_length-i-1] = row_data[i]
            count = count + 1
    return row_data_left_change_right
#规则
#单单单双
#双双双单
#单单单单
#双双双双
def get_rule(p_rule):
    #奇偶规则
    rule_parity_list = []
    rule_value = int(p_rule)
    if(rule_value == 1):
        rule_parity_list = [1, 1, 1, 0]
    elif (rule_value == 2):
        rule_parity_list = [0, 0, 0, 1]
    elif (rule_value == 3):
        rule_parity_list = [1, 1, 1, 1]
    elif (rule_value == 4):
        rule_parity_list = [0, 0, 0, 0]
    else:
        rule_parity_list = [2, 2, 2]
    return rule_parity_list

#基于target 和rule, 判断是否成立,成立则购买，否则跳过   ---规则为单双
def check_single_match(target,rule):
    rule_len = len(rule)
    target_len = len(target)
    # print rule[0:rule_len - 1]
    # print target[1 - rule_len:]
    if (rule[0:rule_len-1] == target[1-rule_len:]):
        count = 0
        while(target[-count-1] == target[-1]):
            count = count + 1
            if(count == len(target)):
                break
        if (count%rule_len == (rule_len -1)):
            return rule[-1]
        else:
            return -1
    else:
        return -1

#基于target 和rule, 判断是否成立,成立则购买，否则跳过  --规则为数字,rule_len=规则的长度，比如对子[5,5,5]，则长度为3
def check_double_match(target,rule_len):
    target_len = len(target)
    # print target[-1]
    # print target[-2]
    if (target[-1] == target[-2]):
        count = 0
        while(target[-count-1] == target[-1]):
            count = count + 1
            if(count == len(target)):
                break
        # print "count:",count
        if (count%(rule_len) == (rule_len-1)):
            return target[-1]
        else:
            return -1
    else:
        return -1


#交叉规则判断
def check_cross_match(target_arr,rule_len):
    target = target_arr[:]
    if len(target) < 2:
        return -1
    else:
        target.remove(0)
        while(len(target)>0 and (target[-1]==0)):
            target.pop()
        if len(target) < 2:
            return -1
        # print target
        target_len = len(target)
        # print target[-1]
        # print target[-2]
        if (target[-1] == target[-2]):
            count = 0
            while(target[-count-1] == target[-1]):
                count = count + 1
                if(count == len(target)):
                    break
            # print "count:",count
            if (count%(rule_len) == (rule_len-1)):
                return target[-1]
            else:
                return -1
        else:
            return -1

#考虑长度
def check_double_match_old(target,rule_len):
    target_len = len(target)
    print target[1 - rule_len:]
    print target[ - rule_len: -rule_len + 1]
    if (target[-rule_len:-rule_len + 1] == target[1-rule_len:]):
        count = 0
        while(target[-count-1] == target[-1]):
            count = count + 1
            if(count == len(target)):
                break
        print count
        if (count%(rule_len+1) == (rule_len)):
            return target[-1]
        else:
            return -1
    else:
        return -1