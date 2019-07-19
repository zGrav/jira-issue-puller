boardUrl = ""

boardId = 6 # you can get the id after selection a project and during board seletion. e.g RapidBoard.jspa?rapidView=6

fullBoardUrl = boardUrl + "/rest/agile/1.0/board/" + str(boardId)

activeSprintUrl = fullBoardUrl + "/sprint?state=active"

userName = ""
apiToken = "" # you can generate your API token here: https://id.atlassian.com/manage/api-tokens

import urllib.request, json, base64

data_string = userName + ":" + apiToken
data_bytes = data_string.encode("ASCII")
base64string = base64.b64encode(data_bytes)

authHeader = {'Authorization': 'Basic ' + base64string.decode("ASCII")}

todoIssues = []
inProgressOrReviewIssues = []
doneOrResolvedIssues = []

def tryUrl(req: urllib.request.Request):
    try: urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        print(e.reason)
        exit()

def getSprint():
    activeSprintReq = urllib.request.Request(activeSprintUrl, None, authHeader)

    tryUrl(activeSprintReq)

    with urllib.request.urlopen(activeSprintReq) as response:
       data = json.loads(response.read().decode())

       activeSprint = data['values'][0]

       return activeSprint

def getBoard():
    boardReq = urllib.request.Request(fullBoardUrl, None, authHeader)

    tryUrl(boardReq)

    with urllib.request.urlopen(boardReq) as response:
       data = json.loads(response.read().decode())

       board = data

       return board

board = getBoard()
sprint = getSprint()

if(not board):
    print("no board found :(")
    exit()

if(not sprint):
    print("no active sprint found :(")
    exit()
else:
    sprintName = sprint['name']
    sprintUrl = sprint['self']

    boardName = board['name']
    projectName = board['location']['name']

    sprintTasksReq = urllib.request.Request(sprintUrl + '/issue?fields=name,subtasks,issuetype,summary,status,assignee&maxResults=200', None, authHeader) # bump up if needed, iirc max is 500

    tryUrl(sprintTasksReq)

    with urllib.request.urlopen(sprintTasksReq) as response:
        data = json.loads(response.read().decode())

        issues = data['issues']

        print("Fetched " + str(len(issues)) + " issues for active sprint: " + sprintName + " in board: " + boardName + " for project: " + projectName)

        for issue in issues:
            isSubTask = issue['fields']['issuetype']['subtask']

            if isSubTask:
                continue
            else:
                issueSubtasks = issue['fields']['subtasks']

                if issue['fields']['issuetype']['name'] == 'Story' and not len(issueSubtasks) == 0:
                    issueKey = issue['fields']['issuetype']['name'].upper() + ' - ' + issue['key']
                else:
                    issueKey = issue['key']

                issueStatus = issue['fields']['status']['name']

                issueName = issue['fields']['summary']

                issueTag = issueKey + ': ' + issueName

                if issueStatus == 'To Do':
                    todoIssues.append(issueTag)
                elif issueStatus == 'In Progress' or issueStatus == 'In Review':
                    inProgressOrReviewIssues.append(issueTag)
                elif issueStatus == 'Done' or issueStatus == 'Resolved' or issueStatus == 'Closed':
                    doneOrResolvedIssues.append(issueTag)

print()
print("Grand total of:")
print(str(len(todoIssues)) + " issues in To Do")
print(str(len(inProgressOrReviewIssues)) + " issues in In Progress/Review")
print(str(len(doneOrResolvedIssues)) + " issues in Done/Resolved")

print()
print("Displaying output so you can port it to slides!")

print()
print("To Do:")
if(len(todoIssues) == 0):
    print("Nothing! :)")
else:
    print(*todoIssues, sep = "\n")

print()
print("In Progress/Review")
if(len(inProgressOrReviewIssues) == 0):
    print("Nothing! :)")
else:
    print(*inProgressOrReviewIssues, sep = "\n")

print()
print("Done/Resolved")
if(len(doneOrResolvedIssues) == 0):
    print("Nothing! :)")
else:
    print(*doneOrResolvedIssues, sep = "\n")
