import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select

from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException, NoSuchElementException
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
        self.appendant_id = ''
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
                    alert.accept()
                    return 2
        except NoAlertPresentException:
            pass

        try:
            if driver.find_element_by_class_name('errorMessage'):
                logging.info('登录失败,请检查学好和姓名')
                return 0
        except NoSuchElementException:
            logging.info('登录成功！')
            for cookie in driver.get_cookies():
                requests.utils.add_dict_to_cookiejar(self.session.cookies, {cookie['name']: cookie['value']})
            return 1

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

    def get_test_page_id(self):
        if len(self.appendant_id) == 0:
            soup = BeautifulSoup(self.session.get(TestUrl).text, 'lxml')
            self.appendant_id = soup.find(id='id')['value']
        return "id", self.appendant_id

    def get_ids_answers(self):
        return self.get_ids(), self.get_answers()

    def get_post_body(self, ids, answers, appendant=None):
        if not answers:
            answers = ["" for i in range(len(ids))]
        dic = []
        j = 0
        print("题目数量:" + str(len(ids)) + "------答案数量:" + str(len(answers)))
        if len(ids) < len(answers):
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
            elif length == 0:
                dic.append(self.con('answer' + ids[j], answer))
            else:
                dic.append(self.con('answer', answer))
            dic.append(self.con('uanswer', answer))
            dic.append(self.con('qid', ids[j]))
            j += 1
        if appendant:
            dic.append(appendant)
        print(dic)
        return tuple(dic)

    def con(self, key, value):
        return key, value

    def solve_q(self):
        if self.already_complete == 1:
            return
        response1 = self.session.post(ActionSaveUrl,
                                      data=self.get_post_body(self.get_ids(), None, appendant=self.get_test_page_id()))
        logging.info(response1.text)
        # if '已通过' in response1.text:
        #     logging.info("已通过")
        #     return
        response = self.session.post(ActionSaveUrl, data=self.get_post_body(self.get_ids(), self.get_answers(),
                                                                            appendant=self.get_test_page_id()))
        if '重新答题' in response.text:
            logging.info('答题失败！')
            return
        logging.info('答题成功!')
        pass

    def start(self):
        print('项目地址:https://github.com/Jntmkk/JNUAssistent')
        option = input('免责声明：用户在使用工具时造成对用户自己或他人任何形式的损失和伤害，由用户自己承担。（y/n)')
        if option == 'n':
            return
        while (1):
            self.require_user_message()
            r = self.login()
            if r == 1:
                break
            if r == 0:
                continue
            if r == 2:
                return
        self.solve_q()

    def end(self):
        try:
            driver.switch_to.alert.accept()
        except NoAlertPresentException:
            pass
        finally:
            driver.close()


if __name__ == '__main__':
    jun = JNUAssistant()
    jun.start()
    jun.end()
