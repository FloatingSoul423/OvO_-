"""Render individually authored scenarios, public rules, and item-level trace links."""
from pathlib import Path
import re
from srs_cases import load_cases

ROOT = Path(__file__).resolve().parents[1]
SRS = ROOT / 'docs/srs'
MODULES = SRS / 'modules'
DETAILS = MODULES / 'detailed'
INPUTS = [
 ('01-search-and-portal.md','01-search-and-portal-detailed.md','检索 成果详情与学者门户'),
 ('02-account-claim-maintenance.md','02-account-claim-maintenance-detailed.md','账号 认领与维护'),
 ('03-collection-governance.md','03-collection-governance-detailed.md','采集 治理 更新与追踪'),
 ('04-analytics-admin-innovation.md','04-analytics-admin-innovation-detailed.md','统计 管理与合作探索'),
 ('nonfunctional.md','nonfunctional-detailed.md','非功能需求'),
]
LINKS = {
 'FR01':('01','01,12,14,17','01,02,04','查询上下文、成果、学者'),
 'FR02':('02','01,05,07,17,19','01,03,04,06','成果、来源记录、版本关系'),
 'FR03':('03','01,02,03,05,09,19','01,03,05,06','学者、门户、学者成果关系'),
 'FR04':('04','02,03,18','01,03,06','账号、会话、门户授权、安全事件'),
 'FR05':('05,06','01,03,04,18,19','01,03,05,06','认领申请、证明材料、门户授权、审计'),
 'FR06':('07','03,05,18','01,03,05,06','门户、变更申请、公开版本、审计'),
 'FR07':('08','03,05,06,07,08,09,10,18,19','01,03,04,05,06','成果、关系、变更申请、来源、审计'),
 'FR08':('09','07,11,18','03,04,07','来源登记、采集任务、检查点、来源记录'),
 'FR09':('10','07,08,10,12,18','04,05,07,08','成果、来源、候选、版本关系、审计'),
 'FR10':('09','05,07,10,18','04,05,07,08','更新批次、源版本、公开版本、检查点'),
 'FR11':('11','12,13,14,16,17','01,02,04,05','成果、历史机构、领域、统计版本'),
 'FR12':('12','09,12,15,16,17','01,02,04,05','学者、论文、作者关系、合作边'),
 'FR13':('13','12,14,16,17','01,02,04,05','成果、领域、关键词、热点版本'),
 'FR14':('06,10,14','01,03,04,05,18,19','01,03,04,05,06,07,08','队列、账号、分类、来源、审计'),
 'FR15':('08,10','02,03,04,05,06,09,18,19','03,04,05,06,07,08','学者、身份候选、成果关系、审计'),
 'FR16':('02,09,10','07,12,17','01,04,05,06,07,08','四类成果、来源记录、数量清单'),
 'IN01':('15','13,15,16,17,20','01,02,04,05','合作子图、论文证据、路径结果'),
 'NF01':('01,02,03,04,05,07,08,11,12,13,15','01,03','01','界面状态、表单、查询上下文'),
 'NF02':('01,11,12,13,14,15','','02','性能记录、查询集、环境清单'),
 'NF03':('04,05,06,07,08,09,10,14','01,03,18','03','身份、授权、受控材料、安全事件'),
 'NF04':('02,09','07,10,11','04','历史成果、任务、备份、恢复报告'),
 'NF05':('07,08,09,10,11,12,13,14,15','05,10,18','05','公开版本、视图版本、审计'),
 'NF06':('02,03,05,06,07,08,09,14','01,17','06','字段许可、证明材料、数据性质'),
 'NF07':('09,14','07,10','07','来源、维护文档、运行版本'),
 'NF08':('01,02,03,04,05,06,07,08,09,10,11,12,13,14,15','','08','追踪项、覆盖率、工程证据'),
}
CRITICAL = set('FR01-S01 FR01-S02 FR02-S03 FR03-S04 FR04-S03 FR05-S04 FR05-S05 FR05-S06 FR07-S05 FR07-S06 FR08-S04 FR08-S06 FR09-S03 FR09-S04 FR09-S08 FR10-S04 FR10-S05 FR10-S06 FR11-S03 FR11-S05 FR12-S02 FR12-S03 FR13-S05 FR14-S05 FR14-S06 FR15-S02 FR15-S07 FR15-S08 FR16-S04 FR16-S05 IN01-S03 IN01-S04 IN01-S05 NF02-S01 NF03-S02 NF04-S01 NF05-S01 NF06-S01 NF08-S01'.split())

# A second, concrete boundary fixture for each critical item. Non-critical
# requirements retain one authored, unique acceptance fixture rather than
# padding their AC count with template references to E1/A1.
EXTRA_AC = {
 'FR01-S01':'Given 关键词为空但筛选类型为专利，When 访客检索成果，Then 执行筛选浏览；关键词和筛选都空时提示补充条件且不查询',
 'FR01-S02':'Given 起年为2026、止年为2024且机构为甲，When 提交筛选，Then 指出年份范围错误并保留机构甲',
 'FR02-S03':'Given 成果P有来源A和B且审核证明M为内部材料，When 访客查看来源，Then 显示A、B及公开差异，不返回M',
 'FR03-S04':'Given 门户甲有待审核认领申请和证明材料M，When 访客查看门户，Then 只看到待审摘要，不看到申请人或M',
 'FR04-S03':'Given 用户甲无门户乙授权，When 甲通过直接请求修改乙资料，Then 请求被拒绝，乙资料与审计对象不发生业务修改',
 'FR05-S04':'Given 申请A处于待补充且补充期限已过，When 申请人补交材料，Then 拒绝过期补交并保留原状态及处理说明',
 'FR05-S05':'Given 审核通过的申请A授予门户权限时发生失败，When 管理员查看结果，Then 不出现已通过却无授权的成功状态，A保留待审核并记失败',
 'FR05-S06':'Given 门户甲已有有效管理人且新申请人与其身份冲突，When 管理员未完成核验便点击通过，Then 拒绝通过且原授权不转移',
 'FR07-S05':'Given 成果P变更已批准但统计视图刷新失败，When 访客查看统计，Then 显示旧版本时间和未同步提示，不宣称四视图全部完成',
 'FR07-S06':'Given 论文P关联甲和乙且甲解除申请获批，When 更新关系，Then 仅甲关系被排除，乙关系、P实体与来源仍在',
 'FR08-S04':'Given 采集任务已成功，When 管理员对原任务再次发出启动指令，Then 拒绝非法迁移并保留成功历史',
 'FR08-S06':'Given 来源A的记录R已产生实体P，When 同一记录R在新任务再次输入，Then 不创建第二个实体，两个任务历史均可查询',
 'FR09-S03':'Given 论文P与专利Q具有相同文本标识，When 执行去重，Then 不跨类型合并，分别保留两条来源链',
 'FR09-S04':'Given 两篇论文标题和年份相同但作者不同且均无DOI，When 执行候选生成，Then 可生成待核验候选，不自动合并',
 'FR09-S08':'Given 管理员拒绝候选P与Q，When 原批次再次处理，Then P与Q保持独立，拒绝理由及来源不丢失',
 'FR10-S04':'Given 成果P的人工确认标题为甲而新来源标题为乙，When 执行增量更新，Then 甲不被覆盖，差异进入核验',
 'FR10-S05':'Given 100条记录处理中第61条失败且检查点为第60条，When 从检查点恢复，Then 前60条不重复入库且61条失败原因仍可查',
 'FR10-S06':'Given 成果P修改已生效但检索索引尚未更新，When 查看详情与检索，Then 旧检索结果显示版本时间和未同步状态，不能报告全部一致',
 'FR11-S03':'Given 一项成果有来源A和B且归属机构甲，When 计算甲的成果数，Then 甲只计该成果实体一次',
 'FR11-S05':'Given 数据集中只有两条明确标识的模拟成果，When 查看默认现实排名，Then 不纳入两条成果且不输出真实机构名次',
 'FR12-S02':'Given 论文P支持甲乙合作且另有专利Q也由甲乙参与，When 查看合作边证据，Then 只将P作为论文合作证据',
 'FR12-S03':'Given 论文P由两个来源收录且甲乙共同署名，When 计算合作强度，Then 强度为1，不因两个来源变为2',
 'FR13-S05':'Given 热点样本全是模拟成果，When 查看默认现实热点，Then 不输出真实研究趋势结论并明确数据范围',
 'FR14-S05':'Given 操作日志关联受控证明M，When 普通管理员查询审计列表，Then 只返回获准摘要，不返回M原文',
 'FR14-S06':'Given 门户管理者甲直接请求后台审核接口，When 服务端鉴权，Then 拒绝操作并记录越权事件',
 'FR15-S02':'Given 两名学者同名且机构不同、无共同外部标识，When 归一姓名，Then 只得到同名候选，不自动合并身份',
 'FR15-S07':'Given 门户甲认领已通过且有成果P、Q待核验，When 查看关系，Then P和Q仍待核验，不能批量标为本人确认',
 'FR15-S08':'Given 关系P改归属已生效而合作网络刷新失败，When 查看网络，Then 保留旧版本时间并标未同步，不展示为最新',
 'FR16-S04':'Given 成果P一条真实来源和一条模拟来源，When 判定数据性质，Then P标混合且从默认现实统计排除',
 'FR16-S05':'Given 来源A暂时无法访问但其已收录成果P仍允许公开，When 访客打开P，Then P可浏览并显示最后更新时间',
 'IN01-S03':'Given 甲乙间存在两条等长两跳路径且均有论文证据，When 请求最短路径，Then 返回按规则选出的其中一条并说明不唯一',
 'IN01-S04':'Given 路径甲到乙的第二跳论文证据已撤回，When 重新核验路径，Then 原路径不再作为有效结果',
 'IN01-S05':'Given 机构筛选后端点甲无符合范围的合作边，When 查询甲到乙，Then 说明范围内无路径，不泄露被排除学者',
 'NF02-S01':'Given 固定环境中存在一笔超过候选2秒目标的普通检索，When 按约定样本计算P95，Then 如P95超限则判失败，不用平均值替代',
 'NF03-S02':'Given 用户甲无门户乙授权且前端隐藏入口，When 甲直接提交乙的受保护操作，Then 服务端拒绝并记录越权，不依赖前端隐藏',
 'NF04-S01':'Given 来源A断连前已收录成果P，When 采集任务失败，Then P及来源历史保留且失败原因可查',
 'NF05-S01':'Given 审核通过后统计视图仍显示旧版本且超过候选60秒，When 核对传播日志，Then 记录超时并判不一致，不把刷新请求成功视为数据已一致',
 'NF06-S01':'Given 来源记录含公开标题和私人邮箱，When 生成公开详情，Then 仅标题可见，邮箱不进入页面或公开响应',
 'NF08-S01':'Given 核心规则测试仅达到79%候选覆盖阈值，When 生成测试报告，Then 标未达标，并列出未覆盖分支而非四舍五入为通过',
}
assert set(EXTRA_AC)==CRITICAL

def expand(prefix, values):
    return [prefix + value for value in values.split(',') if value]

def parse_rows(path):
    rows=[]
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('|'):
            cells=[s.strip() for s in line.strip('|').split('|')]
            if re.fullmatch(r'(?:FR\d{2}|IN01|NF\d{2})-S\d{2}',cells[0]):
                rows.append((cells[0],cells[1].rstrip('。')))
    return rows

def associations(req):
    parent=req.split('-')[0]
    uc,br,nf,objects=LINKS[parent]
    diagrams=['DGM-USECASE-01'] if not parent.startswith('NF') else []
    if parent=='FR05': diagrams+=['DGM-ACTIVITY-01','DGM-STATE-02']
    if parent in {'FR08','FR10'} or req=='NF04-S01': diagrams+=['DGM-STATE-01']
    return expand('UC-',uc),expand('BR-',br),expand('NF',nf),objects,diagrams

def acs(req,c):
    items=[(f'AC-{req}-01',f"Given {c['given']}，When {c['when']}，Then {c['then']}。")]
    if req in CRITICAL:
        items.append((f'AC-{req}-02',EXTRA_AC[req]+'。'))
    return items

def permission(req,c):
    actor=c['actor']
    if req=='FR04-S01': return '访客可注册；注册不依赖登录或门户管理权限。'
    if req=='FR04-S02': return '登录允许未登录访问；退出仅影响当前用户的当前会话。'
    if '门户管理者' in actor: return '有效账号且有目标门户授权；共享字段审核另须管理员能力。其他门户和其他作者关系不可擅改。'
    if actor.startswith('访客'): return '公开读取无需登录；仅返回当前可公开对象，不返回受控材料。'
    if actor=='申请人': return '仅本人可补充本人申请；材料限申请人及有审核能力管理员访问。'
    if actor=='登录用户': return '须有效登录且限本人操作；认领提交不要求已获目标门户权限。'
    if '管理员' in actor: return '人工操作须具对应管理能力；自动处理受登记规则限制，不代替冲突人工核验。'
    if actor=='系统': return '只处理登记来源和获准范围；人工干预限对应治理管理员。'
    return '按权限矩阵验证允许与拒绝场景；测试人员身份不赋予生产业务权限。'

def render(req,title,c):
    parent=req.split('-')[0]
    uc,br,nf,objects,diagrams=associations(req)
    priority='Innovation' if parent=='IN01' else 'Must（非功能约束）' if parent.startswith('NF') else 'Must'
    related = '无'
    if parent in {'FR05','FR06','FR07'}: related = '申请人或门户管理者、对应审核管理员（排除本条已列主要参与者）'
    if parent in {'FR08','FR10','FR16'}: related = '外部数据来源；查看历史数据的访客'
    if parent in {'FR09','FR15'}: related = '治理管理员、受影响门户管理者'
    if parent.startswith('NF'): related = '实施验证的测试人员及对应业务用例参与者'
    lines=[f'<a id="{req.lower()}"></a>','',f'## {req} {title}','',f'- **父需求：** {parent}（V1.9）',f'- **优先级：** {priority}',f"- **主要参与者：** {c['actor']}",f'- **相关参与者：** {related}','']
    fields=[('需求描述',f'系统应满足：{title}。'),('前置条件',c['pre']+'。'),('触发条件',c['steps'][0]+'。'),('主成功流程','\n'.join(f'{i}. {s}。' for i,s in enumerate(c['steps'],1))),('备选流程','- A1：'+c['alt']+'。'),('异常流程','- E1：'+c['error']+'。'),('输入/业务数据',c['inputs']+'。'),('输出/可观察结果',c['output']+'。'),('状态变化',c['state']+'。'),('权限规则',permission(req,c)),('业务规则',('、'.join(br) if br else '无新增跨模块BR；采用本条NF测试协议')+'；字段与口径引用 [公共数据与细化规则](../../data-and-rules.md)。'),('验收条件','\n'.join(f'- {a}：{text}' for a,text in acs(req,c))),('关联项',f"- 关联用例：{'、'.join(uc)}\n- 关联非功能需求：{'、'.join(nf)}\n- 关联数据对象：{objects}\n- 关联图：{'、'.join(diagrams)}（图状态见UML清单）" if diagrams else '本条不单独建图；通过所关联用例约束业务')]
    for heading,body in fields: lines += [f'### {heading}','',body,'']
    return '\n'.join(lines)

def main():
    cases=load_cases()
    expected={r for src,_,_ in INPUTS for r,_ in parse_rows(MODULES/src)}
    assert set(cases)==expected,(set(cases)-expected,expected-set(cases))
    DETAILS.mkdir(exist_ok=True)
    trace=['# 子需求逐条追踪矩阵','','每行链接规范定义及本条全部验收条件。核心规则SPEC初稿已形成，实际测试未执行；图的完成状态见UML清单。','','| V1.9基线 | 子需求 | 用例 | 规则 | 验收条件 | NF | 图 | SPEC与测试状态 |','|---|---|---|---|---|---|---|---|']
    for src,dest,title in INPUTS:
        out=[f'# {title}','', '> 版本：V0.4 提交评审稿｜日期：2026-10-12｜编写：OvO组 AI辅助｜成员复核：待签认','', '行为来源为逐条编写的场景。字段与策略见 [数据与规则](../../data-and-rules.md)，权限和状态见 [横切矩阵](../../cross-cutting-matrices.md)。验收条件为未来系统的判据，不表示系统已实现。','']
        for req,title in parse_rows(MODULES/src):
            out.append(render(req,title,cases[req]))
            uc,br,nf,objects,diagrams=associations(req)
            ac='、'.join(a for a,_ in acs(req,cases[req]))
            spec='SPEC V0.1初稿；测试未执行' if req.split('-')[0] in {'FR01','FR08','FR09','FR10','FR15','FR16'} else '本版SPEC不单列；测试未执行'
            trace.append(f"| {req.split('-')[0]} | [{req}](modules/detailed/{dest}#{req.lower()}) | {'、'.join(uc)} | {'、'.join(br) or '本条NF协议'} | {ac} | {'、'.join(nf)} | {'、'.join(diagrams) or '不单独建图'} | {spec} |")
        (DETAILS/dest).write_text('\n'.join(out).rstrip()+'\n',encoding='utf-8',newline='\n')
    (SRS/'subrequirement-traceability.md').write_text('\n'.join(trace)+'\n',encoding='utf-8',newline='\n')
    print(f'Authored requirements: {len(cases)}; ACs: {sum(len(acs(r,c)) for r,c in cases.items())}')

if __name__=='__main__': main()
