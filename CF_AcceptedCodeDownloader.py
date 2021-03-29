# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

# %%

import urllib
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as BS
import http.client
from file_type import file_type
import json
import time
import datetime
import random
import re


# %%
def make_remark(title, author, timeStamp, language):
    remark = "//# Author : " + author + " " + "=" * (34-len(author)) + "#\n"
    remark += "//# Problem Title : " + title + " " + "=" * (23-len(title)) + "#\n"
    remark += "//# Time Stamp : " + timeStamp + " " + "=" * (30-len(timeStamp)) + "#\n"
    remark += "//# Language : " + language + " " + "=" * (32-len(language)) + "#\n\n"
    return remark


# %%
def get_response(url, query=None, header=None, data=None):
    if query == None:
        req = Request(url, data)
    else:
        req = Request(url+query, data)
    try:
        response = urlopen(req)
        return response
    except urllib.error.HTTPError:
        print(urllib.error.HTTPError)
        sys.exit(1)


# %%
def main(handle, code_list_file, code_path):
    with open(code_list_file, "r", encoding="utf-8") as f:
        codeList = json.load(f)

    num = 1
    count = 100
    while(True):
        conn = get_response("https://codeforces.com/api/user.status?", f"handle={handle}&from={num}&count={count}")
        data = conn.read()
        conn.close()
        
        res = json.loads(data.decode("utf-8"))
        print(num)

        if res["status"] == "OK":
            results = res["result"]

            if results == []:
                break
            
            for result in results:
                if result['verdict'] != "OK":
                    continue
                contestId = result['problem']['contestId']
                contestIdx = result['problem']['index']
                solutionId = result['id']
                language = result['programmingLanguage']
                
                fName = str(contestId) + str(contestIdx)
                if fName not in codeList:
                    codeList[fName] = [solutionId]
                else:
                    if solutionId in codeList[fName]:
                        continue
                    else:
                        codeList[fName].append(solutionId)
                        fName += "_" + str(len(codeList[fName]))
                
                solutionApi = f'https://codeforces.com/contest/{contestId}/submission/{solutionId}'
                
                conn = get_response(solutionApi)
                bs_res = BS(conn, 'html.parser')
                conn.close()

                code = bs_res.find('pre').text.strip()
                code = re.sub("\r\n", "\n", code)

                
                
                fName += file_type[language]
                remark = make_remark(result['problem']['name'], handle, datetime.datetime.fromtimestamp(result['creationTimeSeconds']).isoformat(), language)
                code = remark + code

                try:
                    with open(code_path + fName, "w", encoding="utf-8") as f:
                            f.write(code)
                except:
                    print(code_path + "가 존재하지 않거나 파일이 열려있는 상태입니다.")
                    sys.exit(1)

                time.sleep(random.uniform(1,2))
        num += count

    try:
        with open(code_list_file, "w", encoding="utf-8") as f:
            json.dump(codeList, f)
    except:
        print(code_list_file + "를 다시 작성중 오류가 발생했습니다.")
        sys.exit(1)


# %%
if __name__ == "__main__":
    with open("./personal_info.json", "r", encoding="utf-8") as f:
        pData = json.load(f)
        handle = pData["handle"]
        code_list_file = pData["code_list_file"]
        code_path = pData["code_path"]
    main(handle, code_list_file, code_path)


