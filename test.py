ans = ''
with open('answer.txt', 'r', encoding='utf-8') as f:
    line = f.readline()
    while line:
        ans += line
        line = f.readline()
lists = ans.split('&')
dic = {}
for temp in lists:
    index = temp.index('=')
    key = temp[0:index]
    value = temp[index + 1:]
    dic[key] = value
print(dic)