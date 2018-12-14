from flask import Flask, render_template, redirect, request, jsonify
#from datetime import date, time, timedelta, datetime
import requests

import json

app = Flask(__name__)
APIBaseURL = "https://kylesfinalproject.ddns.net"

@app.route('/', methods=['GET'])
def default():

    url = APIBaseURL + "/learn/api/public/v1/oauth2/authorizationcode?response_type=code&client_id=bea78fb6-42ff-467f-8d3f-b8585410a28a&scope=read offline&state=125434256346345634653452&redirect_uri=https://Kymeleon.pythonanywhere.com/Authorized"
    #url = "http://learn.wsu.edu/learn/api/public/v1/oauth2/authorizationcode?response_type=code&client_id=4e6ccfd5-799d-4ca6-a186-abb40d965fe9&redirect_uri=http://Kymeleon.pythonanywhere.com/Authorized"



    return redirect(url)




@app.route('/Authorized', methods=['GET'])
def Authorized():
    SendData = dict()

    SendData['code'] = request.args.get('code')
    SendData['grant_type'] = "authorization_code"
    SendData['redirect_uri'] = "https://Kymeleon.pythonanywhere.com/Authorized"

    #url = APIBaseURL + "/learn/api/public/v1/oauth2/token?code=" + SendData['code'] + "&grant_type=" + SendData['grant_type'] + "&redirect_uri=https://Kymeleon.pythonanywhere.com/Homeworks"


    #returns = requests.get(url)

    headers = {'Accept': 'application/json', 'Authorization': 'Bearer YmVhNzhmYjYtNDJmZi00NjdmLThkM2YtYjg1ODU0MTBhMjhhOk9lQjdWZFl6VmdpbjhYQ1JVczl5dnJrNkxJblVkU2E4'}
    params = {'jsonRequest': json.dumps(SendData)}
    url = APIBaseURL + "/learn/api/public/v1/oauth2/token"


    returns = requests.post(url=APIBaseURL + "/learn/api/public/v1/oauth2/token", data=SendData, headers=headers)

    ReturnData = json.loads(returns.text)


    UserCoursesURL = APIBaseURL + "/learn/api/public/v1/users/uuid:" + ReturnData['user_id'] + "/courses?limit=200"

    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + ReturnData['access_token']}

    UserCoursesReturnData = requests.get(url=UserCoursesURL, headers=headers)

    LoadedCourses = json.loads(UserCoursesReturnData.text)


    CourseResults = [(x["userId"],x["courseId"],) for x in LoadedCourses["results"]]

    CourseContentList = dict()

    for Course in CourseResults:
        CourseContentsURL = APIBaseURL + "/learn/api/public/v1/courses/" + Course[1] + "/contents?limit=200"

        CourseContentsReturnData = requests.get(url=CourseContentsURL, headers=headers)

        CourseContentsJson = json.loads(CourseContentsReturnData.text)

        CourseContentList[Course[1]] = list()

        #print(CourseContentsJson)

        i = 0
        for Content in CourseContentsJson["results"]:
            NewUrl = APIBaseURL + "/learn/api/public/v1/courses/" + Course[1] + "/contents/" + Content['id'] + "/children"

            Content = requests.get(url=NewUrl, headers=headers)

            ContentJson = json.loads(Content.text)

            #print(Content.text + "\n")

            for assignment in ContentJson["results"]:
                if not assignment["hasGradebookColumns"]:
                    continue

                CourseContentList[Course[1]].append(dict())

                CourseContentList[Course[1]][i]["Name"] = assignment["title"]
                CourseContentList[Course[1]][i]["DueDate"] = assignment["availability"]["adaptiveRelease"]["end"]

                i = i + 1

    AdjustedeListDataSorted = ConvertListToUseableList(CourseContentList)


    html = InjectIntoHTML(AdjustedeListDataSorted)

    return html



#input: { classID1 : [{DueDate:"", Name:""},..],...}
#output: [[classID1, Name, FormattedDueDate(string), DueDate(formatted as datetime)],...] (Sorted)
def ConvertListToUseableList(DataToConvert):
    AssignmentList = list()
    n = 0
    for i in DataToConvert.keys():
        for j in DataToConvert[i]:
            AssignmentList.append(list())

            AssignmentList[n].append(i)
            AssignmentList[n].append(j["Name"])
            AssignmentList[n].append(FormatStringToLookNice(j["DueDate"]))
            AssignmentList[n].append(FormatStringToComparableInt(j["DueDate"]))


            n = n + 1

    for i in range(len(AssignmentList)):
        for j in range(len(AssignmentList)):
            if AssignmentList[i][3] < AssignmentList[j][3]:
                temp = AssignmentList[i]
                AssignmentList[i] = AssignmentList[j]
                AssignmentList[j] = temp

    return AssignmentList

def FormatStringToLookNice(TheString):
    year = TheString[:4]
    month = TheString[5:7]
    day = TheString[8:10]
    clocktime = TheString[11:16]

    return year + "/" + month + "/" + day + "    at " + clocktime

def FormatStringToComparableInt(TheString):
    year = TheString[:4]
    month = TheString[5:7]
    day = TheString[8:10]

    return int(year + month + day)


def InjectIntoHTML(DataToInject):
    FirstHalfString = """
    </head>
<body>

<h2>Assignment List</h2>

<table>
  <tr>
    <th>CourseID</th>
    <th>Assignment</th>
    <th>DueDate</th>
  </tr>"""

    for i in DataToInject:
        FirstHalfString = FirstHalfString + "<tr>"
        for j in range(3):
            FirstHalfString = FirstHalfString + "<td>" + i[j] + "</td>"

        FirstHalfString = FirstHalfString + "</tr>"

    FirstHalfString = FirstHalfString + """
</table>

</body>
</html>"""

    return FirstHalfString


if __name__ == "__main__":
    app.run(debug=True)
