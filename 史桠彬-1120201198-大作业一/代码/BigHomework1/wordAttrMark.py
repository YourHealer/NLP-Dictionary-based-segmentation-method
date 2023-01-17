import csv
import time

# 加载语料库
def load_corpus(document):
    file = open(document, "r", encoding='utf-8')
    reader = csv.reader(file)
    sents = []
    for item in reader:
        sent = []
        for i in item:
            sent.append(i.strip())
        sents.append(sent)
    return sents

# 获得词性标注字典
def get_dict_wordattr(sents):
    dt_wordattr = dict()
    # 统计所有词性个数
    for sent in sents:
        for word in sent:
            word_part = word.split('/')[-1].split(']')[0].split('!')[0]
            if word_part in dt_wordattr:
                dt_wordattr[word_part] += 1
            else:
                dt_wordattr[word_part] = 1
    return dt_wordattr

# 计算马尔科夫链的转移矩阵
# 获得转移矩阵
def get_transMatrix(sents):
    trans = dict()
    for sent in sents:
        for i in range(len(sent) - 1):
            one = sent[i].split('/')[-1].split(']')[0].split('!')[0]
            two = sent[i + 1].split('/')[-1].split(']')[0].split('!')[0]
            if one in trans:
                if two in trans[one]:
                    trans[one][two] += 1
                else:
                    trans[one][two] = 1
            else:
                trans[one] = dict()
                trans[one][two] = 1
    return trans

# 每个词的词性概率
def get_percent(sents):
    percent = dict()
    for sent in sents:
        for word in sent:
            word_word = word.split('/')[0].split('{')[0].strip('[')
            word_part = word.split('/')[-1].split(']')[0].split('!')[0]
            if word_word in percent:
                if word_part in percent[word_word]:
                    percent[word_word][word_part] += 1
                else:
                    percent[word_word][word_part] = 1
            else:
                percent[word_word] = dict()
                percent[word_word][word_part] = 1
    return percent

def Viterbi(text,text_percent,trans,dic):
    dict_len = len(dic)
    dis = [dict() for _ in range(len(text))]
    node = [dict() for _ in range(len(text))]
    for first in text_percent[0].keys():
        dis[0][first] = 1
    for i in range(len(text) - 1):
        word_one = text[i]
        word_two = text[i + 1]
        word_one_percent_dict = text_percent[i]
        word_two_percent_dict = text_percent[i + 1]

        word_one_percent_key = list(word_one_percent_dict.keys())
        word_one_percent_value = list(word_one_percent_dict.values())
        word_two_percent_key = list(word_two_percent_dict.keys())
        word_two_percent_value = list(word_two_percent_dict.values())
        for word_two_per in word_two_percent_key:
            tmp_dis = []
            for word_one_per in word_one_percent_key:
                if word_two_per in trans[word_one_per]:
                    tmp_num = dis[i][word_one_per] * (
                            (trans[word_one_per][word_two_per] + 1) / (dic[word_one_per] + dict_len)) * (
                                      text_percent[i + 1][word_two_per] / dic[word_two_per])
                    tmp_dis.append(tmp_num)
                else:
                    tmp_num = dis[i][word_one_per] * (1 / (dic[word_one_per] + dict_len)) * (
                            text_percent[i + 1][word_two_per] / dic[word_two_per])
                    tmp_dis.append(tmp_num)

            max_tmp_dis = max(tmp_dis)
            max_tmp_dis_loc = tmp_dis.index(max_tmp_dis)
            dis[i + 1][word_two_per] = max_tmp_dis
            node[i + 1][word_two_per] = word_one_percent_key[max_tmp_dis_loc]

    path = []
    f_value = list(dis[len(dis) - 1].values())
    f_key = list(dis[len(dis) - 1].keys())
    f = f_key[f_value.index(max(f_value))]
    path.append(f)
    for i in range(len(dis) - 1, 0, -1):
        f = node[i][f]
        path.append(f)
    path.reverse()
    return path

def get_text_percent(text,percent):
    text_percent = []
    for word in text:
        # 对于语料库中不存在的词性标注，我们统一认为是名词
        try:
            word_percent = percent[word]
        except KeyError as e:
            word_percent = {'n': 1}
        text_percent.append(word_percent)
    return text_percent

def get_ans(mytxt,percent_wordattr,trans_wordattr,dt_wordattr,sents_part):
    counter = 0
    p_sum = 0
    r_sum = 0
    for line in open(mytxt, "r", encoding='utf-8'):
        text = eval(line)
        print("第", counter + 1, "行:", text)
        text_percent = get_text_percent(text, percent_wordattr)
        print(text_percent)
        ans = Viterbi(text, text_percent, trans_wordattr, dt_wordattr)
        # print(ans)
        myList = []
        for i in range(len(text)):
            myList.append(text[i] + '/' + ans[i])
        print("算法词性标注结果：", myList)
        print("人工词性标注结果", sents_part[counter])

        dict_train = {}
        dict_check = {}
        for i in myList:
            try:
                tmp = dict_train[i]
            except:
                dict_train[i] = 1
            else:
                dict_train[i] += 1

        for i in sents_part[counter]:
            try:
                tmp = dict_check[i]
            except:
                dict_check[i] = 1
            else:
                dict_check[i] += 1

        # 求精度
        p = 0
        for i in dict_train.keys():
            try:
                tmp = dict_check[i]
            except:
                p += 0
            else:
                p += min(dict_check[i], dict_train[i])
        print("预测成功数：", p)
        p_percent = p / sum(j for j in dict_train.values())
        print("预测成功率：", p_percent)
        p_sum += p_percent

        # 求召回率
        r = 0
        for i in dict_check.keys():
            try:
                tmp = dict_train[i]
            except:
                r += 0
            else:
                r += min(dict_check[i], dict_train[i])
        print("召回成功数：", r)
        r_percent = r / sum(j for j in dict_check.values())
        print("召回成功率：", r_percent)
        r_sum += r_percent

        counter += 1
        print()

    # 计算均值
    P = p_sum / counter
    R = r_sum / counter
    F = 2 * P * R / (P + R)
    print("该方法的分词精度为：", P)
    print("该方法的分词召回率为：", R)
    print("该方法的分词F值为：", F)


# 加载语料库
sents = load_corpus("train.csv")
sents_part = load_corpus("corpus_wordattr.csv")
print("输入需要词性标注的文件：")
mytxt = input()
starter = time.time()
# 获得语料字典
dt_wordattr = get_dict_wordattr(sents)
dt_len = len(dt_wordattr)
# 获得语料转移矩阵
trans_wordattr = get_transMatrix(sents)
# 获得每个词的词性频度列表
percent_wordattr = get_percent(sents)
# print(percent_wordattr)
get_ans(mytxt,percent_wordattr,trans_wordattr,dt_wordattr,sents_part)
ender = time.time()
print("用时：",ender - starter,"s")