"""Build the reviewable OpenAPI 3.0 contract from a compact Python source."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
O = {"openapi": "3.0.3", "info": {"title": "学术成果分享平台核心接口", "version": "0.1.0", "description": "作业5构件设计初稿；合成示例，未实现。"}, "servers": [{"url": "https://example.invalid/api/v1", "description": "设计占位地址，不是线上服务"}], "tags": [{"name": x} for x in ["搜索", "公开详情", "认领", "采集管理", "统计"]], "paths": {}, "components": {"securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "opaque"}}, "schemas": {}}}
S = O["components"]["schemas"]

def obj(props, required=()):
    x = {"type": "object", "properties": props}
    if required: x["required"] = list(required)
    return x
def st(description=None, enum=None):
    x = {"type": "string"}
    if description: x["description"] = description
    if enum: x["enum"] = enum
    return x
def ref(name): return {"$ref": f"#/components/schemas/{name}"}
def arr(item): return {"type": "array", "items": item}
def query(name, schema, desc): return {"name": name, "in": "query", "required": False, "description": desc, "schema": schema}
def pathparam(name): return {"name": name, "in": "path", "required": True, "schema": st()}
def response(code, description, schema=None):
    x = {"description": description}
    if schema: x["content"] = {"application/json": {"schema": schema}}
    return x
def request(schema): return {"required": True, "content": {"application/json": {"schema": schema}}}
def op(path, method, tag, summary, responses, parameters=None, body=None, security=None, desc=None):
    x = {"tags": [tag], "summary": summary, "operationId": method + path.title().replace("/", "").replace("-", "").replace("{", "").replace("}", ""), "responses": responses}
    if parameters: x["parameters"] = parameters
    if body: x["requestBody"] = request(body)
    if security: x["security"] = [{"bearerAuth": []}]
    if desc: x["description"] = desc
    O["paths"].setdefault(path, {})[method] = x

S["Error"] = obj({"error": obj({"code": st(), "message": st(), "details": obj({}, ()), "requestId": st()}, ["code", "message", "requestId"])}, ["error"])
S["WorkSummary"] = obj({"workId": st(), "workType": st(enum=["paper", "patent", "project", "award"]), "title": st(), "publicationYear": {"type": "integer", "nullable": True}, "dataNature": st(enum=["real", "simulated", "mixed"]), "version": {"type": "integer", "format": "int64"}}, ["workId", "workType", "title", "dataNature", "version"])
S["SearchPage"] = obj({"items": arr(ref("WorkSummary")), "nextCursor": {"type": "string", "nullable": True}, "total": {"type": "integer", "format": "int64", "nullable": True}, "totalRelation": st(enum=["exact", "estimated"]), "facets": obj({"workTypes": arr(obj({"key": st(), "count": {"type": "integer"}}, ["key", "count"])), "years": arr(obj({"key": st(), "count": {"type": "integer"}}, ["key", "count"]))}), "emptyReason": {"type": "string", "nullable": True}}, ["items", "nextCursor", "totalRelation"])
S["WorkDetail"] = obj({**S["WorkSummary"]["properties"], "abstract": {"type": "string", "nullable": True}, "typeDetails": obj({}, ()), "participants": arr(obj({"scholarId": st(), "name": st(), "role": st(), "confirmationStatus": st()}, ["scholarId", "name", "role", "confirmationStatus"])), "sources": arr(obj({"name": st(), "externalId": st(), "collectedAt": st()}, ["name", "externalId", "collectedAt"])), "updatedAt": st()}, ["workId", "workType", "title", "dataNature", "version", "typeDetails", "participants", "sources", "updatedAt"])
S["ScholarPortal"] = obj({"scholarId": st(), "displayName": st(), "organization": {"type": "string", "nullable": True}, "biography": {"type": "string", "nullable": True}, "claimStatus": st(enum=["unclaimed", "claimed", "under_review"]), "works": arr(ref("WorkSummary")), "updatedAt": st()}, ["scholarId", "displayName", "claimStatus", "works", "updatedAt"])
S["ClaimCreate"] = obj({"targetScholarId": st(), "declaration": st(), "evidenceObjectKeys": arr(st())}, ["targetScholarId", "declaration", "evidenceObjectKeys"])
S["Claim"] = obj({"claimId": st(), "targetScholarId": st(), "state": st(enum=["pending_review", "needs_more", "approved", "rejected"]), "version": {"type": "integer", "format": "int64"}, "submittedAt": st(), "applicantVisibleReason": {"type": "string", "nullable": True}}, ["claimId", "targetScholarId", "state", "version", "submittedAt"])
S["ClaimList"] = obj({"items": arr(ref("Claim")), "nextCursor": {"type": "string", "nullable": True}}, ["items", "nextCursor"])
S["ClaimDecision"] = obj({"action": st(enum=["request_more", "approve", "reject"]), "reason": st(), "expectedVersion": {"type": "integer", "format": "int64", "minimum": 1}}, ["action", "reason", "expectedVersion"])
S["TaskCreate"] = obj({"sourceId": st(), "mode": st(enum=["incremental", "full"]), "scope": st()}, ["sourceId", "mode", "scope"])
S["Task"] = obj({"taskId": st(), "sourceId": st(), "state": st(enum=["pending", "running", "succeeded", "failed", "stopped", "retrying"]), "version": {"type": "integer", "format": "int64"}, "processedCount": {"type": "integer", "format": "int64"}, "successCount": {"type": "integer", "format": "int64"}, "failureCount": {"type": "integer", "format": "int64"}, "totalCount": {"type": "integer", "format": "int64", "nullable": True}, "progressPercent": {"type": "number", "nullable": True}, "failureReason": {"type": "string", "nullable": True}}, ["taskId", "sourceId", "state", "version", "processedCount", "successCount", "failureCount"])
S["TaskAction"] = obj({"action": st(enum=["start", "stop", "retry"]), "expectedVersion": {"type": "integer", "format": "int64", "minimum": 1}}, ["action", "expectedVersion"])
S["Statistics"] = obj({"scope": st(), "dataNature": st(), "updatedAt": st(), "distinctWorkCount": {"type": "integer", "format": "int64"}, "byType": arr(obj({"type": st(), "count": {"type": "integer", "format": "int64"}}, ["type", "count"]))}, ["scope", "dataNature", "updatedAt", "distinctWorkCount", "byType"])
S["CollaborationEdge"] = obj({"fromScholarId": st(), "toScholarId": st(), "paperIds": arr(st()), "strength": {"type": "integer", "minimum": 1}}, ["fromScholarId", "toScholarId", "paperIds", "strength"])
S["CollaborationNetwork"] = obj({"scholarIds": arr(st()), "edges": arr(ref("CollaborationEdge")), "scope": st(), "updatedAt": st()}, ["scholarIds", "edges", "scope", "updatedAt"])
S["CollaborationPath"] = obj({"status": st(enum=["found", "no_path", "incomplete"]), "scholarIds": arr(st()), "paperEvidence": arr(arr(st())), "hopCount": {"type": "integer", "nullable": True}, "scope": st()}, ["status", "scholarIds", "paperEvidence", "scope"])
errors = {str(c): response(str(c), "统一错误响应", ref("Error")) for c in [400, 401, 403, 404, 409, 422, 429, 500, 503]}
def errs(*codes): return {c: errors[str(c)] for c in codes}
idem = {"name": "Idempotency-Key", "in": "header", "required": True, "schema": {"type": "string", "minLength": 8, "maxLength": 128}, "description": "同一账号和路径下重复请求返回原结果"}

op("/search/works", "get", "搜索", "检索公开成果", {"200": response(200, "公开候选经 RDS 复核", ref("SearchPage")), **errs(400, 503)}, [query("q", st(), "关键词，空值允许浏览"), query("type", st(enum=["paper", "patent", "project", "award"]), "成果类型"), query("yearFrom", {"type": "integer", "minimum": 1000, "maximum": 9999}, "起始年份含边界"), query("yearTo", {"type": "integer", "minimum": 1000, "maximum": 9999}, "结束年份含边界"), query("domainId", st(), "父领域包含子领域"), query("organizationId", st(), "机构"), query("dataNature", st(enum=["real", "all"]), "默认 real"), query("sort", st(enum=["relevance", "time"]), "排序"), query("limit", {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}, "每页数量"), query("cursor", st(), "绑定筛选条件的续页游标")])
op("/works/{workId}", "get", "公开详情", "查询公开成果详情", {"200": response(200, "成果", ref("WorkDetail")), **errs(404, 503)}, [pathparam("workId")])
op("/scholars/{scholarId}", "get", "公开详情", "查询学者门户", {"200": response(200, "门户", ref("ScholarPortal")), **errs(404, 503)}, [pathparam("scholarId")])
op("/claims", "post", "认领", "提交认领申请", {"201": response(201, "已创建申请", ref("Claim")), **errs(400, 401, 409, 422)}, [idem], ref("ClaimCreate"), True, "证明引用必须由受控上传流程签发；不得传任意 OBS 地址。")
op("/claims/{claimId}", "get", "认领", "查询本人申请进度", {"200": response(200, "仅本人可见", ref("Claim")), **errs(401, 403, 404)}, [pathparam("claimId")], security=True)
op("/admin/claims", "get", "认领", "查询待审申请", {"200": response(200, "审核队列", ref("ClaimList")), **errs(401, 403)}, [query("state", st(), "审核状态"), query("cursor", st(), "续页游标")], security=True)
op("/admin/claims/{claimId}/decision", "post", "认领", "处理认领申请", {"200": response(200, "决定已提交", ref("Claim")), **errs(400, 401, 403, 404, 409, 422)}, [pathparam("claimId"), idem], ref("ClaimDecision"), True, "批准、门户授权、审计及 Outbox 在同一 RDS 事务提交。")
op("/admin/collection-tasks", "post", "采集管理", "创建异步采集任务", {"202": response(202, "已受理，轮询任务状态", ref("Task")), **errs(400, 401, 403, 409, 422)}, [idem], ref("TaskCreate"), True, "仅保存任务，不在请求中执行采集。")
op("/admin/collection-tasks/{taskId}", "get", "采集管理", "查询采集任务进度", {"200": response(200, "任务进度", ref("Task")), **errs(401, 403, 404)}, [pathparam("taskId")], security=True)
op("/admin/collection-tasks/{taskId}/actions", "post", "采集管理", "启动停止或重试任务", {"202": response(202, "动作已受理", ref("Task")), **errs(400, 401, 403, 404, 409, 422)}, [pathparam("taskId"), idem], ref("TaskAction"), True)
op("/statistics/works", "get", "统计", "查询公开成果分布", {"200": response(200, "成果实体去重计数", ref("Statistics")), **errs(400, 503)}, [query("type", st(enum=["paper", "patent", "project", "award"]), "可选成果类型"), query("domainId", st(), "领域"), query("yearFrom", {"type": "integer"}, "起始年份"), query("yearTo", {"type": "integer"}, "结束年份"), query("dataNature", st(enum=["real", "all"]), "默认 real")])
op("/scholars/{scholarId}/collaboration-network", "get", "统计", "查询公开论文合作网络", {"200": response(200, "有证据的无向网络", ref("CollaborationNetwork")), **errs(400, 404, 422, 503)}, [pathparam("scholarId"), query("domainId", st(), "支撑论文领域"), query("organizationId", st(), "论文发生时双方机构"), query("yearFrom", {"type": "integer"}, "起始年份"), query("yearTo", {"type": "integer"}, "结束年份")])
op("/collaboration-path", "get", "统计", "查询两学者最短合作路径", {"200": response(200, "按跳数的路径与逐跳论文证据", ref("CollaborationPath")), **errs(400, 404, 422, 503)}, [{"name": "fromScholarId", "in": "query", "required": True, "schema": st()}, {"name": "toScholarId", "in": "query", "required": True, "schema": st()}, query("domainId", st(), "支撑论文领域"), query("organizationId", st(), "论文发生时双方机构")], desc="超限或中断时 status=incomplete，不宣称最短。")
for path, method, code in [("/claims", "post", "201"), ("/admin/collection-tasks", "post", "202")]:
    O["paths"][path][method]["responses"][code]["headers"] = {"Location": {"description": "新资源的状态查询地址", "schema": st()}}

out = ROOT / "07-OpenAPI文档-可御风雪可燃冰.json"
out.write_text(json.dumps(O, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {out} ({len(O['paths'])} paths, {sum(len(v) for v in O['paths'].values())} operations)")
