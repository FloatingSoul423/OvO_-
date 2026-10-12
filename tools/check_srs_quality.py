"""Document checks: coverage, unique definitions, trace edges and known regressions.

This verifies documents, not the future product. Semantic review remains explicit.
"""
import json
import re
from pathlib import Path
from collections import Counter
from build_srs_review import ROOT,SRS,MODULES,DETAILS,INPUTS,CRITICAL,LINKS,parse_rows,associations
from srs_cases import load_cases

def main():
    cases=load_cases()
    detail_paths=[DETAILS/dest for _,dest,_ in INPUTS]
    normative=[SRS/'OvO-SRS-Draft.md',SRS/'business-rules.md',SRS/'data-and-rules.md',SRS/'use-case-specifications.md',SRS/'cross-cutting-matrices.md',SRS/'traceability-matrix.md',SRS/'subrequirement-traceability.md',*detail_paths]
    definitions={}
    whole=''
    fields=['需求描述','前置条件','触发条件','主成功流程','备选流程','异常流程','输入/业务数据','输出/可观察结果','状态变化','权限规则','业务规则','验收条件','关联项']
    for path in detail_paths:
        text=path.read_text(encoding='utf-8');whole+=text
        for block in re.split(r'(?=^## (?:FR\d{2}|IN01|NF\d{2})-S\d{2} )',text,flags=re.M)[1:]:
            req=re.match(r'## (\S+)',block).group(1)
            assert req not in definitions,f'duplicate requirement {req}'
            definitions[req]=block
            for field in fields: assert f'### {field}\n\n' in block,(req,field)
            assert re.search(r'^1\. .+\n2\. .+\n3\. ',block,re.M),(req,'missing concrete steps')
            ac=re.findall(r'^- (AC-[\w-]+)：Given (.+)，When (.+)，Then (.+)',block,re.M)
            assert len(ac)==(3 if req in CRITICAL else 2),(req,'AC count')
            assert all(a.startswith('AC-'+req+'-') for a,*_ in ac),(req,'foreign AC')
            assert all(v.strip() for a,g,w,t in ac for v in (g,w,t)),(req,'empty GWT')
            assert cases[req]['given'] in block and cases[req]['then'] in block,(req,'fixture missing')
    expected={r for src,_,_ in INPUTS for r,_ in parse_rows(MODULES/src)}
    assert set(definitions)==expected==set(cases)
    assert len(expected)==124 and sum(r.startswith('NF') for r in expected)==17
    assert {r.split('-')[0] for r in expected}==set(LINKS)
    acs=re.findall(r'^- (AC-[\w-]+)：',whole,re.M)
    assert len(acs)==len(set(acs))==287
    # Indexes must not carry duplicate normative acceptance definitions.
    for src,_,_ in INPUTS:
        assert not re.search(r'^- (?:\*\*)?AC-',(MODULES/src).read_text(encoding='utf-8'),re.M)
    uc=(SRS/'use-case-specifications.md').read_text(encoding='utf-8')
    blocks=re.split(r'(?=^## UC-\d{2} )',uc,flags=re.M)[1:]
    assert len(blocks)==15
    for i,block in enumerate(blocks,1):
        assert block.startswith(f'## UC-{i:02d} ')
        for label in ['目标','对应需求','主要参与者','次要参与者','前置条件','触发事件']:
            assert f'**{label}：**' in block,(i,label)
        for label in ['主成功场景','备选与异常场景','后置条件','业务规则','关联状态']:
            assert f'### {label}' in block,(i,label)
        steps=set(re.findall(r'^\d+\. (M\d+)：',block,re.M))
        anchors=re.findall(r'^- B\d+（(M\d+)）：',block,re.M)
        assert len(anchors)>=2 and set(anchors)<=steps,(i,'bad branch anchor')
    trace=(SRS/'subrequirement-traceability.md').read_text(encoding='utf-8')
    for req in expected:
        row=[r for r in trace.splitlines() if f'[{req}](' in r]
        assert len(row)==1,(req,'trace missing')
        for ac in re.findall(r'^- (AC-[\w-]+)：',definitions[req],re.M): assert ac in row[0]
        for linked in associations(req)[0]: assert linked in row[0]
    # Known V0.2 semantic regressions.
    assert '注册不依赖登录' in definitions['FR04-S01']
    assert '无需先选择两名学者' in definitions['IN01-S01']
    assert '不返回A' in definitions['FR01-S01']
    assert '9999' in definitions['FR16-S06']
    assert '已通过但无授权' in definitions['FR05-S05']
    for phrase in ['系统应完成该可观察能力','与本条相关的结果','且本条能力被调用','必要时更新业务状态']:
        assert phrase not in whole,phrase
    # Verify local links and explicit anchors, including all 124 item-level edges.
    for path in normative:
        text=path.read_text(encoding='utf-8')
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',text):
            if re.match(r'(https?://|#)',target):continue
            link,_,anchor=target.partition('#'); dest=(path.parent/link).resolve()
            assert dest.exists(),(str(path),target)
            if anchor: assert f'id="{anchor}"' in dest.read_text(encoding='utf-8'),target
    stats=dict(normative_files=len(normative),physical_lines=0,nonblank_lines=0,nonspace_chars=0,han_chars=0,requirements=124,function_innovation=107,nf=17,ac=287,use_cases=15,diagrams='deferred by user')
    for path in normative:
        text=path.read_text(encoding='utf-8'); lines=text.splitlines()
        stats['physical_lines']+=len(lines);stats['nonblank_lines']+=sum(bool(x.strip()) for x in lines)
        stats['nonspace_chars']+=len(re.sub(r'\s','',text));stats['han_chars']+=len(re.findall(r'[\u3400-\u9fff]',text))
    print('PASS: document structural checks; not a product acceptance result')
    print(json.dumps(stats,ensure_ascii=False,indent=2))
    return stats

if __name__=='__main__':main()
