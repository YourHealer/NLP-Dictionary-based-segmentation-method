import csv
import time

# 加载词典
def get_dict(document):
    dt = set()
    # 按行读取字典文件，每行第一个空格之前的字符串提取出来。
    for line in open(document, "r",encoding='utf-8'):
        dt.add(line[0:line.find('	')])
    return dt

# 正向最长匹配算法
def forward_segment(text, dict):
    word_list = []
    i = 0
    while i < len(text):
        longest_word = text[i]                      # 记录当前扫描位置的单字
        for j in range(i + 1, len(text) + 1):       # 对于所有可能的结尾
            word = text[i:j]                        # 记录从当前位置到结尾的连续字符串
            if word in dict:                         # 判断单词是否在词典中
                if len(word) > len(longest_word):   # 判断是否该串更长，若是则优先输出
                    longest_word = word
        word_list.append(longest_word)              # 输出最长词，并进行正向扫描
        i += len(longest_word)
    return word_list

# 逆向最长匹配算法
def backward_segment(text, dict):
    word_list = []
    i = len(text) - 1
    while i >= 0:                                   # 扫描位置作为终点
        longest_word = text[i]                      # 扫描位置的单字
        for j in range(0, i):                       # 遍历[0, i]区间作为待查询词语的起点
            word = text[j: i + 1]                   # 取出[j, i]区间作为待查询单词
            if word in dict:
                if len(word) > len(longest_word):   # 越长优先级越高
                    longest_word = word
                    break
        word_list.insert(0, longest_word)           # 逆向扫描，所以越先查出的单词在位置上越靠后
        i -= len(longest_word)
    return word_list

# 双向最长匹配
def bidirectional_segment(text, dict):
    forward = forward_segment(text, dict)
    backward = backward_segment(text, dict)
    # 词数更少更优先
    if len(forward) < len(backward):
        return forward
    elif len(forward) > len(backward):
        return backward
    else:
        # 单字更少更优先
        if sum(1 for word in forward if len(word) == 1) < sum(1 for word in backward if len(word) == 1):
            return forward
        else:
            return backward

# 使用正向最长匹配对文本分词
def get_txt_forward(text):
    ls = []
    # 按行读取字典文件，每行第一个空格之前的字符串提取出来。
    for line in open(text, "r",encoding='utf-8'):
        if(line != '\n'):
            ls.append(forward_segment(line.strip(), dt))
    return ls

# 使用正向最长匹配对文本分词
def get_txt_backward(text):
    ls = []
    # 按行读取字典文件，每行第一个空格之前的字符串提取出来。
    for line in open(text, "r",encoding='utf-8'):
        if(line != '\n'):
            ls.append(backward_segment(line.strip(), dt))
    return ls

# 使用正向最长匹配对文本分词
def get_txt_bidirectional(text):
    ls = []
    # 按行读取字典文件，每行第一个空格之前的字符串提取出来。
    for line in open(text, "r",encoding='utf-8'):
        if(line != '\n'):
            ls.append(bidirectional_segment(line.strip(), dt))
    return ls

# 将分词结果转换为其在语句中的起始位置
def convert(text: list):
    ans = []
    i = 1
    for word in text:
        ans.append([i, i + len(word) - 1])
        i += len(word)
    return ans

def wordcut(file):
    if(file.split('.')[1] == 'txt'):
        ####################################################################
        # 根据暂无分词结果的.txt文件进行分词
        ####################################################################
        print("请输入分词方法，其中1为正向最长分词，2为逆向最长分词，3为双向最长分词：")
        type = input()
        if(type == '1'):
            # 正向最长
            # 输入待分词文本进行正向分词
            wordcut_forward = get_txt_forward(file)
            # 正向最长匹配算法结果：
            print("正向最长匹配算法结果：")
            for i in wordcut_forward:
                print(i)
            return wordcut_forward
        elif(type == '2'):
            # 逆向最长
            # 输入待分词文本进行逆向分词
            wordcut_backward = get_txt_backward(file)
            # 逆向最长匹配算法结果：
            print("逆向最长匹配算法结果：")
            for i in wordcut_backward:
                print(i)
            return wordcut_backward
        elif(type == '3'):
            # 双向最长
            # 输入待分词文本进行双向分词
            wordcut_bidirectional = get_txt_bidirectional(file)
            # 双向最长匹配算法结果：
            print("双向最长匹配算法结果：")
            for i in wordcut_bidirectional:
                print(i)
            return wordcut_bidirectional
    elif(file.split('.')[1] == 'csv'):
        ####################################################################
        # 根据已有分词结果的.csv文件进行分词
        ####################################################################
        reader = csv.reader(open(file, "r", encoding='utf-8'))
        test_sents = []
        ans_sents = []
        for item in reader:
            #    print(item)              item是每条语句分词后的词列表
            test_sent = ""
            ans_sent = []
            for word in item:
                #    print(word)          word是每个词列表中的每个词
                test_sent += word.strip()
                #    print(test_sent)     test_sent最终是一条完整的语句
                ans_sent.append(word)
                #    print(ans_sent)      ans_sent最终是分词列表(item)
            test_sents.append(test_sent)
            #   test_sents是所有完整语句构成的列表
            ans_sents.append(ans_sent)
            #   ans_sents是所有分词列表构成的列表

        # test_sents_num是test_sents的长度
        test_sents_num = len(test_sents)

        # 分别指代精度、召回率、F-measure值
        p_sum = 0
        r_sum = 0
        ans = []
        print("请输入分词方法，其中1为正向最长分词，2为逆向最长分词，3为双向最长分词：")
        type = input()
        if (type == '1'):
            for i in range(test_sents_num):
                # 指定“正向最长匹配”方法对每一条语句进行训练
                train = forward_segment(test_sents[i], dt)
                ans.append(train)
                train_list = convert(train)
                ans_list = convert(ans_sents[i])

                train_set = set()
                for ele in train_list:
                    train_set.add(tuple(ele))  # train_set中元素为经过训练得到的不计位置的元组

                ans_list_set = set()
                for ele in ans_list:
                    ans_list_set.add(tuple(ele))  # ans_set中元素为已有的不计位置的元组

                # TP为两个集合中共有的元组
                TP = ans_list_set & train_set

                # 对每一条语句计算精度和召回率并加和
                p = len(TP) / len(train_list)
                r = len(TP) / len(ans_list)
                p_sum += p
                r_sum += r
        elif (type == '2'):
            for i in range(test_sents_num):
                # 指定“逆向最长匹配”方法对每一条语句进行训练
                train = backward_segment(test_sents[i], dt)
                ans.append(train)
                train_list = convert(train)
                ans_list = convert(ans_sents[i])

                train_set = set()
                for ele in train_list:
                    train_set.add(tuple(ele))  # train_set中元素为经过训练得到的不计位置的元组

                ans_list_set = set()
                for ele in ans_list:
                    ans_list_set.add(tuple(ele))  # ans_set中元素为已有的不计位置的元组

                # TP为两个集合中共有的元组
                TP = ans_list_set & train_set

                # 对每一条语句计算精度和召回率并加和
                p = len(TP) / len(train_list)
                r = len(TP) / len(ans_list)
                p_sum += p
                r_sum += r
        elif (type == '3'):
            for i in range(test_sents_num):
                # 指定“双向最长匹配”方法对每一条语句进行训练
                train = bidirectional_segment(test_sents[i], dt)
                ans.append(train)
                train_list = convert(train)
                ans_list = convert(ans_sents[i])

                train_set = set()
                for ele in train_list:
                    train_set.add(tuple(ele))  # train_set中元素为经过训练得到的不计位置的元组

                ans_list_set = set()
                for ele in ans_list:
                    ans_list_set.add(tuple(ele))  # ans_set中元素为已有的不计位置的元组

                # TP为两个集合中共有的元组
                TP = ans_list_set & train_set

                # 对每一条语句计算精度和召回率并加和
                p = len(TP) / len(train_list)
                r = len(TP) / len(ans_list)
                p_sum += p
                r_sum += r

        # 计算均值
        P = p_sum / test_sents_num
        R = r_sum / test_sents_num
        F = 2 * P * R / (P + R)
        print("该方法的分词精度为：", P)
        print("该方法的分词召回率为：", R)
        print("该方法的分词F值为：", F)
        return ans

def text_save(filename, data):#filename为写入CSV文件的路径，data为要写入数据列表.
    file = open(filename,"w+",encoding='utf-8')
    for i in range(len(data)):
        s = str(data[i])
        file.writelines(s+"\n")
    file.close()
    print("保存文件成功")

# 导入字典
dt = get_dict("CoreNatureDictionary.txt")
# 输入待分词文本
file = input()
starter = time.time()
res = wordcut(file)
# text_save('fortrain_forward.txt',res)
# text_save('fortrain_backward.txt',res)
# text_save('fortrain_bidirectional.txt',res)
ender = time.time()
print("用时：",ender - starter,"s")