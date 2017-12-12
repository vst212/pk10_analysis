#coding=utf-8
__author__ = 'shifeixiang'

def tran_croos_data(base_data,column_num, calc_num):

    for i in range(int(column_num-calc_num)):
        base_data.append([0]*column_num)
        base_data.insert(0,[0]*column_num)
    # base_data.append([0]*5)
    # print base_data
    # tran_base_data = map(list, zip(*base_data))
    print len(base_data)
    #定义最终的数组list
    cross_data_list = [[0 for i in range(column_num)] for i in range(len(base_data) - (column_num-calc_num) - (calc_num - 1))]

    for row_data in base_data:
        print row_data
    print '---------------'
    # print cross_data_list
    row_num = 0
    max = len(base_data) - (column_num-calc_num) - (calc_num - 1)
    while(row_num<max):
    # for row_data in base_data:
        for cloumn_num in range(len(base_data[row_num])):
            # print cloumn_num
            cross_data_list[row_num][cloumn_num] = base_data[row_num+cloumn_num][cloumn_num]
        # print row_num
        row_num = row_num + 1
    return cross_data_list
if __name__ == '__main__':
    #原始数据
    base_data = [[1,2,3,4,5],[4,5,6,7,8],[7,8,9,2,1],[2,1,2,3,4],[2,1,4,5,6],[3,4,5,6,7],[4,5,6,7,8]]
    #列的长度
    column_num = 5
    #cross上存在几个数据开始计数
    calc_num = 1
    cross_data_list = tran_croos_data(base_data,column_num, calc_num)
    for i in cross_data_list:
        print i










    # larsma_lottery_list = [[0 for i in range(10)] for i in range(3)]
    # print larsma_lottery_list[1]




