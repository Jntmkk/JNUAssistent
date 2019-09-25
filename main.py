import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select

from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
import logging

from bs4 import BeautifulSoup

LoginUrl = 'https://libtrain.jnu.edu.cn/login.jsp'
TestUrl = 'https://libtrain.jnu.edu.cn/testing/testing.action'
ActionSaveUrl = 'https://libtrain.jnu.edu.cn/testing/testsave.action'
Score = 'https://libtrain.jnu.edu.cn/libtrain/score.action'
# 设置Google浏览器无头模式
chrome_options = Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.maximize_window()


class JNUAssistant(object):

    def __init__(self):
        # 设置Google浏览器无头模式
        # chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # self.driver = webdriver.Chrome(chrome_options=chrome_options)
        # driver.maximize_window()
        self.ID = '1934271036'
        self.UserName = '岳文波'
        self.Xiao_Qu = '1'
        self.session = requests.session()
        self.already_complete = 0
        logging.basicConfig(level=logging.INFO)

    def require_user_message(self):
        self.ID = input('输入学号：')
        self.UserName = input('输入姓名：')
        self.Xiao_Qu = int(input('输入校区(1-校本部 2-番禺 3-珠海 5-华文):'))

    def login(self):
        driver.get(LoginUrl)
        input_id = driver.find_element_by_id('account')
        input_id.send_keys(self.ID)
        input_username = driver.find_element_by_id('username')
        input_username.send_keys(self.UserName)
        select = Select(driver.find_element_by_id('xiaoqu'))
        select.select_by_index(self.Xiao_Qu)
        # 提交表单，表单内任意元素提交表单，selenium 寻找最近的 submit
        input_username.submit()
        try:
            alert = driver.switch_to.alert
            if alert:
                if '已通过' in alert.text:
                    logging.info('已通过')
                    self.already_complete = 1
                    return
                logging.info('登录成功')
                alert.accept()
                for cookie in driver.get_cookies():
                    requests.utils.add_dict_to_cookiejar(self.session.cookies, {cookie['name']: cookie['value']})
                return 1
            else:
                logging.info('登录失败')
                return 0
        except NoAlertPresentException:
            pass

    def get_ids(self):
        # 获取题目ID
        test_page = self.session.get(TestUrl).text
        soup = BeautifulSoup(test_page, 'lxml')
        a_id = soup.find_all(id='doPaperForm_qid')
        ids = []
        for i in a_id:
            ids.append(i['value'])
        return ids

    def get_answers(self):
        # 获取答案
        score_page = self.session.get(Score).text
        score_soup = BeautifulSoup(score_page, 'lxml')
        h_answers = score_soup.find_all('span', class_='rightAnswer')
        answers = []
        for ans in h_answers:
            answers.append(str(ans.text)[str(ans.text).index(':') + 1:])
        return answers

    def get_ids_answers(self):
        return self.get_ids(), self.get_answers()

    def get_post_body(self, ids, answers):
        if not answers:
            answers = ["" for i in range(len(ids))]
        dic = []
        j = 0
        print("题目数量:" + str(len(ids)) + "------答案数量:" + str(len(answers)))
        if len(ids) > len(answers):
            logging.info('第一题错误')
            dic.append(self.con('answer' + ids[0], 'A'))
            dic.append(self.con('uanswer', 'A'))
            dic.append(self.con('qid', ids[0]))
            j += 1
            pass
        for answer in answers:
            length = len(answer)
            if length > 1:
                for k in range(length):
                    dic.append(self.con('answer' + ids[j], answer[k]))
                    # dic['answer' + ids[j]] = str(answer[k])
            elif length == 0:
                dic.append(self.con('answer' + ids[j], answer))
            else:
                dic.append(self.con('answer', answer))
                # dic['answer' + ids[j]] = answer
            dic.append(self.con('uanswer', answer))
            dic.append(self.con('qid', ids[j]))
            j += 1
            # dic['uanswer'] = answer
            # dic['qid'] = ids[j]
        dic.append(('id', '13'))
        print(dic)
        return tuple(dic)

    def con(self, key, value):
        return key, value

    def solve_q(self):
        if self.already_complete == 1:
            return
        response1 = self.session.post(ActionSaveUrl, data=self.get_post_body(self.get_ids(), None))
        logging.info(response1.text)
        # if '已通过' in response1.text:
        #     logging.info("已通过")
        #     return
        response = self.session.post(ActionSaveUrl, data=self.get_post_body(self.get_ids(), self.get_answers()))
        if '重新答题' in response.text:
            logging.info('答题失败！')
            return
        logging.info('答题成功!')
        pass

    def start(self):
        while (1):
            # self.require_user_message()
            if self.login():
                break
            return
        self.solve_q()


if __name__ == '__main__':
    jun = JNUAssistant()
    jun.start()


# ID = '1934271033'
# UserName = '岳文波'
# 1-校本部 2-番禺 3-珠海 5-华文
# Xiao_Qu = '1'


# ID = input('输入学号：')
# UserName = input('输入姓名：')
# Xiao_Qu = int(input('输入校区(1-校本部 2-番禺 3-珠海 5-华文):'))


# def get_data(ids, answers):
#     if not answers:
#         answers = ["" for i in range(len(ids))]
#     dic = []
#     j = 0
#     print("题目数量:" + str(len(ids)) + "------答案数量:" + str(len(answers)))
#     if len(ids) > len(answers):
#         logging.info('第一题错误')
#         dic.append(con('answer' + ids[0], 'A'))
#         dic.append(con('uanswer', 'A'))
#         dic.append(con('qid', ids[0]))
#         j += 1
#         pass
#     for answer in answers:
#         length = len(answer)
#         if length > 1:
#             for k in range(length):
#                 dic.append(con('answer' + ids[j], answer[k]))
#                 # dic['answer' + ids[j]] = str(answer[k])
#         elif length == 0:
#             dic.append(con('answer' + ids[j], answer))
#         else:
#             dic.append(con('answer', answer))
#             # dic['answer' + ids[j]] = answer
#         dic.append(con('uanswer', answer))
#         dic.append(con('qid', ids[j]))
#         j += 1
#         # dic['uanswer'] = answer
#         # dic['qid'] = ids[j]
#     dic.append(('id', '13'))
#     print(dic)
#     return tuple(dic)
#     pass
#
#
# def con(key, value):
#     return key, value


def pre():
    logging.basicConfig(level=logging.INFO)

# def get_data():
#     ans = ''
#     with open('answer.txt', 'r', encoding='utf-8') as f:
#         line = f.readline()
#         while line:
#             ans += line
#             line = f.readline()
#     lists = ans.split('&')
#     dic = {}
#     for temp in lists:
#         index = temp.index('=')
#         key = temp[0:index]
#         value = temp[index + 1:]
#         dic[key] = value
#     return dic


# def check(session):
#     if '重新答题' in session.get(TestUrl).text:
#         return 0
#     logging.info("已通过！")
#     return 1
#
#
# def start():
#     driver.get(TestUrl)
#     assert '暨南大学' in driver.title
#
#     # WebDriverWait(driver, 20, ignored_exceptions=UnexpectedAlertPresentException).until(
#     #     lambda x: '暨南大学新生借阅权限开通系统' in driver.title)
#     try:
#         alert = driver.switch_to.alert
#         alert.accept()
#         logging.info("已通过！")
#         return
#     except NoAlertPresentException:
#         pass
#     session = requests.Session()
#     for cookie in driver.get_cookies():
#         requests.utils.add_dict_to_cookiejar(session.cookies, {cookie['name']: cookie['value']})
#
#     # 使用requests库
#     test_page = session.get(TestUrl).text
#     soup = BeautifulSoup(test_page, 'lxml')
#     a_id = soup.find_all(id='doPaperForm_qid')
#     ids = []
#     for i in a_id:
#         ids.append(i['value'])
#     # q_title = soup.find_all('p', class_='qtitle')
#     # for temp in q_title:
#     #     print(temp.text)
#     session.post(ActionSaveUrl, data=get_data(ids, None))
#     score_page = session.get(Score).text
#     score_soup = BeautifulSoup(score_page, 'lxml')
#     h_answers = score_soup.find_all('span', class_='rightAnswer')
#     answers = []
#     for ans in h_answers:
#         answers.append(str(ans.text)[str(ans.text).index(':') + 1:])
#     r = session.post(ActionSaveUrl,
#                      data=get_data(ids, answers))
#     if '重新答题' in r.text:
#         logging.info('答题失败！')
#         return
#     driver.get(Score)
#     logging.info('答题成功！')
#     try:
#         driver.switch_to.alert.accept()
#     except NoAlertPresentException:
#         pass
#     # with open('action.htm', 'w', encoding='utf-8') as f:
#     #     f.write(r.text)
#     #
#     # print(session.get(URL))
#     pass
