# -*- coding: utf-8 -*-
"""后端全接口冒烟测试（幂等：使用唯一业务名，可重复执行）。"""
import datetime as _dt
import json
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import quote

BASE = "http://127.0.0.1:8000"
PASS = 0
FAIL = 0
FAILS = []
SUFFIX = str(int(time.time()))[-6:]  # 唯一后缀，保证幂等


def req(method, path, body=None, raw_body=None, headers=None):
    url = BASE + path
    data = None
    hdrs = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
    if raw_body is not None:
        data = raw_body
    if headers:
        hdrs.update(headers)
    r = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(r, timeout=15) as resp:
            content = resp.read()
            if "application/json" in (resp.headers.get("Content-Type") or ""):
                return resp.status, json.loads(content.decode("utf-8"))
            return resp.status, content
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        try:
            return e.code, json.loads(content)
        except Exception:
            return e.code, content


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        FAILS.append(name)
        print(f"  FAIL  {name}  {detail}")


def multipart(fields, file_field, filename, file_bytes, content_type):
    boundary = "----smoketestboundary"
    lines = []
    for k, v in fields.items():
        lines.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    lines.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"{file_field}\"; filename=\"{filename}\"\r\n"
        f"Content-Type: {content_type}\r\n\r\n".encode()
    )
    lines.append(file_bytes)
    lines.append(f"\r\n--{boundary}--\r\n".encode())
    return b"".join(lines), f"multipart/form-data; boundary={boundary}"


print("== 系统接口 ==")
st, d = req("GET", "/api/health")
check("health code=0", st == 200 and d["code"] == 0, d)
check("app name utf-8", d["data"]["app"] == "秋招辅助管理后端", repr(d["data"]["app"]))

print("== 模块一 ==")
st, d = req("GET", "/api/job-types")
jt = d["data"]
check("seed job types present", len(jt) >= 4 and jt[0]["name"] == "算法岗", jt)

jt_name = "前端岗_" + SUFFIX
st, d = req("POST", "/api/job-types", {"name": jt_name, "color": "#0000FF", "sort_order": 9})
check("create job-type", st == 200 and d["code"] == 0, d)
frontend_jt_id = d["data"]["id"]
st, d = req("POST", "/api/job-types", {"name": jt_name})
check("dup job-type 409", st == 409 and d["code"] == 40900, d)
st, d = req("PUT", f"/api/job-types/{frontend_jt_id}", {"color": "#00FF00"})
check("update job-type", d["data"]["color"] == "#00FF00", d)

st, d = req("POST", "/api/resumes", {
    "job_type_id": jt[1]["id"], "version_name": f"开发岗 v1_{SUFFIX}", "target_position": "后端开发工程师",
})
check("create resume", st == 200, d)
resume_id = d["data"]["id"]
pdf_bytes = b"%PDF-1.4 fake resume content for smoke test"
body, ctype = multipart({}, "file", "resume.pdf", pdf_bytes, "application/pdf")
st, d = req("POST", f"/api/resumes/{resume_id}/upload", raw_body=body, headers={"Content-Type": ctype})
check("upload resume file", d["code"] == 0 and d["data"]["file_type"] == "pdf", d)
check("upload auto log", d["data"]["file_name"] == "resume.pdf", d)

st, d = req("GET", f"/api/resumes/{resume_id}")
check("resume detail has logs", len(d["data"]["logs"]) >= 1, d)

st, d = req("POST", "/api/resume-logs", {"resume_version_id": resume_id, "change_desc": f"手工日志_{SUFFIX}"})
check("create resume log", d["code"] == 0, d)
st, d = req("GET", f"/api/resumes/{resume_id}/logs")
log_titles = [x["change_desc"] for x in d["data"]]
check("resume logs desc order", log_titles[0] == f"手工日志_{SUFFIX}", log_titles)

st, d = req("POST", f"/api/resumes/{resume_id}/set-default")
check("set default resume", d["data"]["is_default"] is True, d)

st, content = req("GET", f"/api/resumes/{resume_id}/file?disposition=inline")
check("download resume file", content == pdf_bytes, content[:30])
st, content = req("GET", f"/api/resumes/{resume_id}/preview")
check("preview pdf inline", content == pdf_bytes, content[:30])

st, d = req("DELETE", f"/api/job-types/{jt[1]['id']}")
check("delete job-type with resume -> 409", st == 409 and d["code"] == 40900, d)

st, d = req("POST", "/api/materials", {
    "category": "project", "title": f"订单系统_{SUFFIX}", "organization": "个人",
    "role": "后端开发", "description": "背景/任务/行动/结果", "highlights": "性能提升40%",
    "tech_stack": ["FastAPI", "Vue"], "tags": ["秋招"],
})
check("create material", d["code"] == 0, d)
st, d = req("GET", "/api/materials/categories")
check("material categories merged", "project" in d["data"], d)
st, d = req("GET", "/api/materials?category=project&keyword=" + quote(f"订单系统_{SUFFIX}"))
check("material filter", len(d["data"]) == 1, d)

st, d = req("POST", "/api/assets", {"category": "blog", "title": f"掘金文章_{SUFFIX}", "url": "https://juejin.cn"})
check("create link asset", d["code"] == 0, d)
file_bytes = b"fake certificate file"
body, ctype = multipart({"category": "certificate", "title": f"证书_{SUFFIX}"}, "file", "cet6.pdf", file_bytes, "application/pdf")
st, d = req("POST", "/api/assets/upload", raw_body=body, headers={"Content-Type": ctype})
check("upload asset file", d["code"] == 0 and bool(d["data"]["file_path"]), d)

print("== 模块二 ==")
company = "字节跳动_" + SUFFIX
st, d = req("POST", "/api/applications", {
    "company": company, "position": "后端开发工程师", "city": "北京",
    "channel": "boss", "job_type_id": jt[1]["id"], "resume_version_id": resume_id,
})
check("create application", d["code"] == 0, d)
app_id = d["data"]["id"]

st, d = req("PUT", f"/api/applications/{app_id}/status", {"to_status": "applied"})
check("status pending->applied", d["data"]["status"] == "applied", d)
st, d = req("GET", f"/api/applications/{app_id}/timeline")
check("timeline recorded", len(d["data"]) == 1 and d["data"][0]["from_status"] == "pending", d)
st, d = req("PUT", f"/api/applications/{app_id}/status", {"to_status": "resume_rejected"})
check("status applied->resume_rejected", d["data"]["status"] == "resume_rejected", d)
st, d = req("PUT", f"/api/applications/{app_id}/status", {"to_status": "ended"})
check("status resume_rejected->ended", d["data"]["status"] == "ended", d)
st, d = req("PUT", f"/api/applications/{app_id}/status", {"to_status": "exam"})
check("illegal transition ended->exam -> 409", st == 409 and d["code"] == 40900, d)

st, d = req("GET", f"/api/applications/{app_id}")
check("application detail timeline>=3", len(d["data"]["timeline"]) >= 3, d)
check("application detail blacklist_hits int", isinstance(d["data"]["blacklist_hits"], int), d)

st, d = req("POST", "/api/applications", {"company": "阿里_" + SUFFIX, "position": "开发工程师"})
app2_id = d["data"]["id"]

st, d = req("PUT", f"/api/applications/{app2_id}/status", {"to_status": "applied"})
st, d = req("PUT", f"/api/applications/{app2_id}/status", {"to_status": "exam"})
st, d = req("PUT", f"/api/applications/{app2_id}/status", {"to_status": "interview"})
st, d = req("PUT", f"/api/applications/{app2_id}/status", {"to_status": "offered", "note": "含 16 薪"})
check("full transition to offered", d["data"]["status"] == "offered", d)

st, d = req("GET", "/api/applications?company=" + quote(company) + "&page=1&page_size=10")
check("application list filter+page", d["data"]["total"] >= 1 and d["data"]["items"], d)

st, d = req("POST", "/api/offers", {
    "application_id": app_id, "company": company, "position": "后端开发",
    "city": "北京", "salary_base": 35, "salary_months": 16, "bonus_performance": 50,
    "work_intensity": 3, "industry_prospect": 4, "company_scale": "10000+人",
    "position_development": 4,
})
offer1_id = d["data"]["id"]
st, d = req("POST", "/api/offers", {
    "application_id": app2_id, "company": "阿里_" + SUFFIX, "position": "开发工程师",
    "city": "杭州", "salary_base": 28, "salary_months": 15,
    "work_intensity": 4, "industry_prospect": 5, "company_scale": "10000+人",
    "position_development": 3,
})
offer2_id = d["data"]["id"]

st, d = req("POST", "/api/offers/compare", {"offer_ids": [offer1_id, offer2_id]})
check("offer compare returns 2 results", d["code"] == 0 and len(d["data"]["results"]) == 2, d)
r1 = d["data"]["results"][0]
check("compare has scores+total+rank",
      "salary" in r1["scores"] and r1["total"] > 0 and all(x["rank"] for x in d["data"]["results"]), r1)
check("compare marks recommended", any(x["recommended"] for x in d["data"]["results"]), d)
st, d = req("GET", "/api/offer-weight-config")
check("weight config seeded", len(d["data"]) == 6, d)
st, d = req("PUT", "/api/offer-weight-config", [
    {"dimension_key": "salary", "dimension_name": "薪资", "weight": 0.4, "enabled": True, "sort_order": 0},
    {"dimension_key": "city", "dimension_name": "城市", "weight": 0.2, "enabled": True, "sort_order": 1},
])
check("weight config replace", len(d["data"]) == 2, d)
# 恢复默认权重（6 维等权），避免影响后续比对
st, d = req("PUT", "/api/offer-weight-config", [
    {"dimension_key": k, "dimension_name": n, "weight": round(1 / 6, 4), "enabled": True, "sort_order": i}
    for i, (k, n) in enumerate([
        ("salary", "薪资"), ("city", "城市"), ("work_intensity", "加班强度"),
        ("industry", "行业前景"), ("company_scale", "公司规模"), ("position_dev", "岗位发展"),
    ])
])
check("restore weight config", len(d["data"]) == 6, d)

st, d = req("GET", "/api/settings")
check("settings default range", d["data"].get("salary_ideal_range") == [240, 800], d)
st, d = req("PUT", "/api/settings", {"salary_ideal_range": [300, 900], "preferred_cities": ["北京"]})
check("settings update", d["data"]["salary_ideal_range"] == [300, 900], d)
req("PUT", "/api/settings", {"salary_ideal_range": [240, 800], "preferred_cities": []})

print("== 模块三 ==")
st, d = req("POST", "/api/exams", {"application_id": app2_id, "platform": "nowcoder", "status": "done", "duration_minutes": 120})
exam_id = d["data"]["id"]
st, d = req("GET", f"/api/exams?application_id={app2_id}&status=done")
check("exams list scoped", len(d["data"]) == 1, d)
st, d = req("PUT", f"/api/exams/{exam_id}/review", {"passed": True, "score": "通过率 60%", "key_points": ["动态规划"]})
check("exam review upsert", d["data"]["passed"] is True, d)
st, d = req("GET", f"/api/exams/{exam_id}/review")
check("exam review read", d["data"]["key_points"] == ["动态规划"], d)

st, d = req("POST", "/api/interviews", {"application_id": app_id, "round": "first", "status": "done"})
interview_id = d["data"]["id"]
st, d = req("POST", f"/api/interviews/{interview_id}/qa", {"question": f"讲一下项目难点_{SUFFIX}", "my_answer": "xxx", "category": "project"})
qa_id = d["data"]["id"]
st, d = req("GET", f"/api/interviews/{interview_id}/qa")
check("interview qa list", len(d["data"]) == 1, d)
st, d = req("PUT", "/api/interview-qa/%d" % qa_id, {"feedback": "补充量化指标"})
check("qa update", d["data"]["feedback"] == "补充量化指标", d)
st, d = req("PUT", f"/api/interviews/{interview_id}/result", {"result": "passed", "summary": "整体不错"})
check("interview result upsert", d["data"]["result"] == "passed", d)
audio = b"fake audio bytes"
body, ctype = multipart({}, "file", "record.m4a", audio, "audio/mp4")
st, d = req("POST", f"/api/interviews/{interview_id}/audio", raw_body=body, headers={"Content-Type": ctype})
check("interview audio upload", d["code"] == 0 and d["data"]["audio_path"], d)

q_title = "两数之和_" + SUFFIX
st, d = req("POST", "/api/questions", {"category": "code", "title": q_title, "difficulty": "easy", "content": "....", "answer": "hashmap", "tags": ["数组"]})
qid = d["data"]["id"]
st, d = req("PUT", f"/api/questions/{qid}/review-status", {"review_status": "todo"})
check("question review status", d["data"]["review_status"] == "todo", d)
st, d = req("GET", "/api/questions?category=code&review_status=todo")
check("question filter contains new", any(x["id"] == qid for x in d["data"]), d)

print("== 模块四 ==")
st, d = req("GET", "/api/stats/overview")
check("stats overview", d["code"] == 0 and d["data"]["total_applications"] >= 2, d)
st, d = req("GET", "/api/stats/by-job-type")
check("stats by-job-type", isinstance(d["data"], list) and len(d["data"]) >= 1, d)
st, d = req("GET", "/api/stats/by-time?granularity=week")
check("stats by-time week", d["data"]["granularity"] == "week", d)

print("== 模块五 ==")
st, d = req("POST", "/api/scripts", {"category": "tech", "title": f"项目亮点_{SUFFIX}", "content": "使用 X 技术解决了 Y 问题，提升 Z"})
sid = d["data"]["id"]
st, d = req("PUT", f"/api/scripts/{sid}/favorite", {"favorite": True})
check("script favorite", d["data"]["is_favorite"] is True, d)
st, d = req("POST", f"/api/scripts/{sid}/use")
check("script usage count", d["data"]["usage_count"] == 1, d)
st, d = req("GET", "/api/scripts?favorite=1")
check("script favorite filter", any(x["id"] == sid for x in d["data"]), d)

st, d = req("POST", "/api/blacklist", {"company": "避雷公司_" + SUFFIX, "issue_type": "overtime", "detail": "996 严重"})
st, d = req("GET", "/api/blacklist/check?company=" + quote("避雷公司_" + SUFFIX))
check("blacklist check count", d["data"]["count"] >= 1, d)

today = _dt.date.today().isoformat()
st, d = req("POST", "/api/tasks", {"task_type": "apply", "title": f"投递任务_{SUFFIX}", "due_date": today})
task_id = d["data"]["id"]
st, d = req("PUT", f"/api/tasks/{task_id}/done", {"done": True})
check("task done", d["data"]["done"] is True and d["data"]["done_at"] is not None, d)
st, d = req("GET", "/api/dashboard/today")
check("dashboard today", d["code"] == 0 and d["data"]["streak"] >= 1, d)
st, d = req("GET", "/api/dashboard/streak")
check("dashboard streak", d["data"]["streak"] >= 1, d)

print("== 导出/导入 ==")
st, d = req("GET", "/api/export")
check("export all tables", d["code"] == 0 and "applications" in d["data"]["tables"], d)
exported = d["data"]["tables"]
st, d = req("POST", "/api/import", {"tables": exported})
check("import all tables", d["code"] == 0, d)
st, d = req("GET", "/api/export")
check("re-export after import", len(d["data"]["tables"]["applications"]) >= 2, d)

print()
print(f"RESULT: {PASS} passed, {FAIL} failed")
if FAILS:
    print("FAILED:", FAILS)
    sys.exit(1)
print("ALL OK")