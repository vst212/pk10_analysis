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
    return base_lottery_list,parity_lottery_list,larsma_lottery_list

    # for i in range(5):
    #     print base_lottery_list[i]
    #     print parity_lottery_list[i]
    #     print larsma_list[i]
    #     print '-----'

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
        rule_parity_list.append([1, 1, 1, 0])
    if (rule_value == 2):
        rule_parity_list.append([0, 0, 0, 1])
    if (rule_value == 3):
        rule_parity_list.append([1, 1, 1, 1])
    if (rule_value == 4):
        rule_parity_list.append([0, 0, 0, 0])
    return rule_parity_list