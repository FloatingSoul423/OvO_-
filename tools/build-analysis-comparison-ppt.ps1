param(
  [Parameter(Mandatory=$true)][string]$Source,
  [Parameter(Mandatory=$true)][string]$Output,
  [Parameter(Mandatory=$true)][string]$Repo
)
$ErrorActionPreference = 'Stop'
$app = New-Object -ComObject PowerPoint.Application
$deck = $null
function Color([int]$r,[int]$g,[int]$b) { return ($r + 256*$g + 65536*$b) }
$cream = Color 247 245 238
$ink = Color 34 42 39
$green = Color 36 100 77
$muted = Color 101 110 106
$orange = Color 174 94 22
function AddText($slide,[string]$value,[single]$x,[single]$y,[single]$w,[single]$h,[single]$size=20,[int]$color=$ink,[bool]$bold=$false) {
  $s = $slide.Shapes.AddTextbox(1,$x,$y,$w,$h)
  $s.TextFrame.TextRange.Text = $value
  $s.TextFrame.MarginLeft = 0; $s.TextFrame.MarginRight = 0
  $s.TextFrame.MarginTop = 0; $s.TextFrame.MarginBottom = 0
  $s.TextFrame.WordWrap = -1
  $s.TextFrame.TextRange.Font.Name = 'Microsoft YaHei'
  $s.TextFrame.TextRange.Font.Size = $size
  $s.TextFrame.TextRange.Font.Color.RGB = $color
  $s.TextFrame.TextRange.Font.Bold = $(if($bold){-1}else{0})
  return $s
}
function ClearSlide($slide) { for($i=$slide.Shapes.Count;$i -ge 1;$i--) { $slide.Shapes.Item($i).Delete() } }
function AddBase($slide,[string]$section,[string]$title,[string]$owner) {
  $bg=$slide.Shapes.AddShape(1,0,0,1152,648)
  $bg.Fill.ForeColor.RGB=$cream; $bg.Line.Visible=0; $bg.ZOrder(1) | Out-Null
  AddText $slide $section 48 18 790 24 12 $green $false | Out-Null
  AddText $slide $title 48 72 1050 50 31 $ink $false | Out-Null
  AddText $slide "$owner  |  学术成果分享平台  ·  需求分析汇报" 48 610 900 18 10 $muted $false | Out-Null
}
function SetNotes($slide,[string]$value) {
  foreach($s in $slide.NotesPage.Shapes) {
    if($s.HasTextFrame -and $s.Name -notmatch 'Slide Number|Slide Image') {
      $s.TextFrame.TextRange.Text=$value
      break
    }
  }
}
function AddPictureContain($slide,[string]$file,[single]$x,[single]$y,[single]$maxW,[single]$maxH) {
  if(!(Test-Path -LiteralPath $file)) { throw "Missing image: $file" }
  $pic = $slide.Shapes.AddPicture($file,0,-1,$x,$y,-1,-1)
  $scale = [Math]::Min($maxW/$pic.Width,$maxH/$pic.Height)
  $pic.Width = $pic.Width*$scale; $pic.Height = $pic.Height*$scale
  $pic.Left = $x + ($maxW-$pic.Width)/2; $pic.Top = $y + ($maxH-$pic.Height)/2
  return $pic
}
function AddRule($slide,[single]$x,[single]$y,[single]$w) {
  $line=$slide.Shapes.AddLine($x,$y,$x+$w,$y)
  $line.Line.ForeColor.RGB=$green; $line.Line.Weight=1.2
}
function AddPanel($slide,[string]$head,[string]$body,[single]$x,[single]$y,[single]$w,[single]$h) {
  $box=$slide.Shapes.AddShape(1,$x,$y,$w,$h)
  $box.Fill.ForeColor.RGB= (Color 255 255 252)
  $box.Line.ForeColor.RGB=(Color 214 222 216)
  AddText $slide $head ($x+14) ($y+12) ($w-28) 30 18 $green $true | Out-Null
  AddText $slide $body ($x+14) ($y+51) ($w-28) ($h-58) 15 $ink $false | Out-Null
}
try {
  $deck = $app.Presentations.Open($Source,$false,$false,$false)
  # Latest deck contains three zoom pages cut from one class diagram. Keep one zoom and the overview.
  $deck.Slides.Item(6).Delete(); $deck.Slides.Item(5).Delete()

  # Cover: fill known five-person OvO assignments and identify the partner group honestly.
  $cover=$deck.Slides.Item(1)
  foreach($s in $cover.Shapes) {
    if($s.HasTextFrame -and $s.TextFrame.HasText) {
      $t=$s.TextFrame.TextRange.Text
      if($t -match 'CognitaNexus' -and $s.Top -gt 140 -and $s.Top -lt 300) { $s.TextFrame.TextRange.Text="学术成果分享平台`rCognitaNexus × OvO" }
      elseif($t -match '成员及实际分工|主讲代表') {
        $s.TextFrame.TextRange.Text="第 03 组  ·  可御风雪可燃冰`rOvO：高昕宇（对象识别与报告）  王昊涵（类图）  宋显涵（采集时序）`r　　 李昊阳（认领时序）  孙子涵（检索时序与展示）`rCognitaNexus：业务规则细化与模型交叉验证（成员分工见该组材料）"
        $s.TextFrame.TextRange.Font.Size=13
      }
    }
  }
  foreach($s in $cover.Shapes) {if($s.HasTextFrame -and $s.TextFrame.HasText -and $s.Top -gt 590 -and $s.TextFrame.TextRange.Text -match 'CognitaNexus') {$s.TextFrame.TextRange.Text='联合项目  |  学术成果分享平台  ·  需求分析汇报'}}
  SetNotes $cover '开场约 25 秒：第 03 组“可御风雪可燃冰”由 CognitaNexus 与 OvO 两组共同完成。说明五名 OvO 成员的实际建模分工；CognitaNexus 成员名单与个人分工以该组材料为准。本次依次比较业务对象、核心类图与采集、认领、检索三条时序图，最后说明一致性和 AI 使用。'
  # Ownership of pre-existing content from the latest submitted deck.
  $headers=@{2='01  /  业务对象 · 联合';3='02  /  核心业务类图 · CognitaNexus';4='02  /  类图局部 · CognitaNexus';5='02  /  类间关系 · CognitaNexus';6='02  /  成果继承 · CognitaNexus';7='03  /  数据采集 · CognitaNexus';8='03  /  采集规则 · CognitaNexus';9='04  /  认领审核 · CognitaNexus';10='04  /  审核规则 · CognitaNexus';11='05  /  检索请求 · CognitaNexus';12='05  /  检索规则 · CognitaNexus';13='06  /  结论 · 联合'}
  foreach($i in 2..13) {
    $sl=$deck.Slides.Item($i)
    foreach($s in $sl.Shapes) {
      if($s.HasTextFrame -and $s.TextFrame.HasText) {
        $t=$s.TextFrame.TextRange.Text
        if($s.Top -lt 55 -and $t -match '^\d\d\s*/') {$s.TextFrame.TextRange.Text=$headers[$i]}
        if($s.Top -gt 590 -and $t -match '学术成果分享平台.*需求分析汇报') {
          $label=if($i -eq 2 -or $i -eq 13){'联合项目'}else{'CognitaNexus'}
          $s.TextFrame.TextRange.Text="$label  |  学术成果分享平台  ·  需求分析汇报"
        }
      }
    }
  }
  AddText $deck.Slides.Item(4) '身份与认领授权（类图局部放大）' 48 71 970 48 28 $ink $false | Out-Null
  foreach($s in $deck.Slides.Item(4).Shapes) {if($s.Type -eq 13) {$s.Top=130; $s.Height=392}}

  # Replace the three former rule-detail pages with OvO model pages. They remain speaker friendly.
  $class=Join-Path $Repo 'docs\analysis\uml\codearts\generated\DGA-CLASS-01-core-business.png'
  $collection=Join-Path $Repo 'docs\uml\sequence-collection-ingestion\generated\DGA-SEQUENCE-01-collection-ingestion.png'
  $claimA=Join-Path $Repo 'docs\analysis\uml\codearts\generated\DGA-SEQUENCE-02A-claim-submission-tracking.png'
  $claimB=Join-Path $Repo 'docs\analysis\uml\codearts\generated\DGA-SEQUENCE-02B-claim-review-supplement.png'
  $search=Join-Path $Repo 'docs\analysis\uml\codearts\generated\DGA-SEQUENCE-03-search-request.png'
  $slide=$deck.Slides.Add(5,12); AddBase $slide '02  /  核心业务类图 · OvO' 'OvO 类图：相同业务边界，不同关系表达' 'OvO'
  AddPictureContain $slide $class 40 152 590 420 | Out-Null
  AddPanel $slide '对照 CognitaNexus' "共同：账号、认领、成果四子类、机构、领域、来源与采集任务。`r`rOvO：以业务实体与状态变更为主线，强调学者—成果关系和来源历史。`r`rCognitaNexus：细化主页、证据、授权与版本等约束对象。`r`r取舍：联合口径保留实体分离；权限不由[提交申请]自动获得。" 666 153 440 420
  SetNotes $slide '约 45 秒。指向 OvO 类图的业务主干：账号、申请、成果、学者关系、来源与采集。对照 CognitaNexus 类图对主页、证据、授权和版本的细分。强调两组对共同业务边界的表达互补，申请获批前不得产生门户授权。'
  
  $slide=$deck.Slides.Item(9); ClearSlide $slide; AddBase $slide '03  /  数据采集入库 · OvO' 'OvO 采集时序：从许可检查到失败恢复' 'OvO'
  AddPictureContain $slide $collection 48 165 740 405 | Out-Null
  AddPanel $slide '与 CognitaNexus 对照' "共同：来源许可先于采集；逐条核验；失败留痕；停止和重试有边界。`r`rOvO：突出任务状态、检查点、治理与人工核验入口。`r`rCognitaNexus：更细化批次、去重、结果归因与失败消息。`r`r图源：仓库 XMI 与本地预览；正式 CodeArts 导出图待复核。" 813 165 295 405
  SetNotes $slide '约 45 秒。OvO 图按许可检查、创建任务、分批采集、清洗校验、结果汇总和停止重试组织。CognitaNexus 进一步细化批次与去重。说明该图目前以仓库 XMI 和本地预览展示，正式 CodeArts 同版本导出图仍待补齐。'

  $slide=$deck.Slides.Item(11); ClearSlide $slide; AddBase $slide '04  /  门户认领审核 · OvO' 'OvO 认领时序：提交、补证、审核与授权' 'OvO'
  AddText $slide 'A  申请受理与结果跟踪' 48 145 500 26 16 $green $true | Out-Null
  AddText $slide 'B  审核决定与补充循环' 598 145 500 26 16 $green $true | Out-Null
  AddPictureContain $slide $claimA 48 181 510 310 | Out-Null
  AddPictureContain $slide $claimB 598 181 510 310 | Out-Null
  AddText $slide '共同约束：申请状态与对象级授权分离；补证不等于通过；冲突不覆盖既有授权。' 48 515 1040 30 18 $green $true | Out-Null
  AddText $slide 'OvO 将提交跟踪与管理员审核拆成 A/B 两图；CognitaNexus 在单条端到端流程中集中呈现审核分支。' 48 555 1040 32 15 $ink $false | Out-Null
  SetNotes $slide '约 45 秒。OvO 将认领申请分为 A 申请与结果跟踪、B 审核与补证循环；CognitaNexus 用一张端到端时序图表示。共同规则是申请状态和授权分离；补证不等于批准；冲突不覆盖既有授权。完整图在随附 CodeArts 源文件中可放大。'

  $slide=$deck.Slides.Item(13); ClearSlide $slide; AddBase $slide '05  /  检索请求处理 · OvO' 'OvO 检索时序：条件校验与四类返回' 'OvO'
  AddPictureContain $slide $search 48 159 720 415 | Out-Null
  AddPanel $slide '与 CognitaNexus 对照' "共同：公开权限过滤先于返回；条件非法、依赖失败、无匹配、有匹配分别处理。`r`rOvO：将查询参数、范围校验和返回分支集中在一张图。`r`rCognitaNexus：细化来源摘要、上下文与稳定分页。`r`r一致性判断：空结果不能伪装为系统失败。" 793 159 315 415
  SetNotes $slide '约 40 秒。指出条件非法、依赖失败、无匹配和有匹配四类返回语义不能混淆。两组都强调公开权限过滤。OvO 聚焦参数与结果分支，CognitaNexus 展开来源摘要和稳定分页。完整时序图保留在 CodeArts 导出文件。'

  # Add the explicit course-required comparison, traceability and AI statement before the conclusion.
  $index=$deck.Slides.Count
  $slide=$deck.Slides.Add($index,12); AddBase $slide '06  /  双组建模对照 · 联合' '同一需求的两组建模取舍' '联合项目'
  AddPanel $slide 'CognitaNexus' "侧重规则、状态和审计证据。`r`r类图将主页、档案、申请、证据、授权和版本显式拆分。`r`r时序图深入批次、补证、权限与稳定分页的条件分支。" 48 170 500 360
  AddPanel $slide 'OvO' "侧重参与者、业务对象和可观察结果。`r`r类图覆盖四种成果类型、学者关系、采集与更新。`r`r时序图按采集、认领、检索三条主流程组织，并显示失败出口。" 604 170 500 360
  AddText $slide '联合结论：保留两组相互补充的表达；统一名称、状态和权限含义，以 SRS／用例／活动图／状态图为判据。' 52 551 1040 42 17 $green $true | Out-Null
  SetNotes $slide '约 40 秒。直接比较两组建模侧重，不比较篇幅。CognitaNexus 强在规则证据和细分边界，OvO 强在参与者和三条可观察主流程。两组共同使用 SRS 和先前需求模型来判定对象、状态、权限含义是否一致。'

  $index=$deck.Slides.Count
  $slide=$deck.Slides.Add($index,12); AddBase $slide '07  /  一致性与 AI · 联合' '模型追踪与 AI 使用说明' '联合项目'
  AddPanel $slide '一致性检查' "对象—类：核心业务对象应落入类图，成果四子类继承一致。`r`r规则—时序：采集许可、认领授权、检索公开过滤须出现在消息和分支中。`r`r状态—流程：申请、任务、成果状态与 SRS／状态图同义。`r`r图源—展示：CodeArts 源文件、导出图与 PPT 同版本。" 48 164 500 385
  AddPanel $slide 'AI：声明、理解、责任' "CognitaNexus：使用 AI 辅助规则细化、文档组织和跨文件检查。`r`rOvO：使用 ChatGPT／Codex 辅助对象清单、图源草拟和一致性排查。`r`r人工验证：两组成员按需求、关系多重度、状态与异常出口逐项复核；最终取舍与提交责任由成员承担。`r`r个人模型与效果记录以各组签认材料为准。" 604 164 500 385
  SetNotes $slide '约 40 秒。按课程要求说明声明、理解和责任。AI 参与对象梳理、图源初稿、文档和一致性检查；成员必须解释关系、多重度和异常分支，最终提交由人负责。两组各自的具体模型使用与效果对照以本人签认记录为准，不把未确认的个人使用情况写成事实。'

  # Update conclusion so counts are specific to CN rather than falsely presented as a joint total.
  $last=$deck.Slides.Item($deck.Slides.Count)
  foreach($s in $last.Shapes) {
    if($s.HasTextFrame -and $s.TextFrame.HasText) {
      $t=$s.TextFrame.TextRange.Text
      if($t -match '18 类业务对象') { $s.TextFrame.TextRange.Text='CognitaNexus：18 类业务对象、约 20 条关系；OvO：同域核心类图与三条时序图' }
      elseif($t -match '^06\s*/') {$s.TextFrame.TextRange.Text='08  /  结论与后续 · 联合'}
      elseif($s.Top -gt 590 -and $t -match 'CognitaNexus') {$s.TextFrame.TextRange.Text='联合项目  |  学术成果分享平台  ·  需求分析汇报'}
    }
  }
  SetNotes $last '约 30 秒。联合建模已明确核心对象、类图和三条时序图的业务边界。CognitaNexus 的 18 类对象与约 20 条关系是该组统计，不代表 OvO 的数量。后续仍需核对类图、流程图与 SRS 一致，并完成采集时序图的同版本 CodeArts 正式导出。'
  # Reset duplicated/stale page numbers in the imported source and fit ownership labels.
  for($i=1;$i -le $deck.Slides.Count;$i++) {
    $sl=$deck.Slides.Item($i)
    $footerSeen=$false; $numberSeen=$false
    for($j=$sl.Shapes.Count;$j -ge 1;$j--) {
      $sh=$sl.Shapes.Item($j)
      if($sh.HasTextFrame -and $sh.TextFrame.HasText -and $sh.Top -gt 590) {
        $tx=$sh.TextFrame.TextRange.Text
        if($sh.Left -lt 1000 -and $tx -match '学术成果分享平台.*需求分析汇报') {if($footerSeen){$sh.Delete()}else{$footerSeen=$true}}
        elseif($sh.Left -gt 1030 -and $tx -match '^\d{2}$') {if($numberSeen){$sh.Delete()}else{$numberSeen=$true}}
      }
    }
    foreach($s in $sl.Shapes) {
      if($s.HasTextFrame -and $s.TextFrame.HasText -and $s.Left -gt 1030 -and $s.Top -gt 585 -and $s.TextFrame.TextRange.Text -match '^\d{2}$') {
        $s.TextFrame.TextRange.Text=('{0:d2}' -f $i)
      }
    }
    # Page number for rebuilt/new pages.
    $hasNumber=$false
    foreach($s in $sl.Shapes) { if($s.HasTextFrame -and $s.TextFrame.HasText -and $s.Left -gt 1030 -and $s.Top -gt 585 -and $s.TextFrame.TextRange.Text -match '^\d{2}$') {$hasNumber=$true} }
    if(!$hasNumber) { AddText $sl ('{0:d2}' -f $i) 1091 608 42 22 12 $orange $false | Out-Null }
  }
  if(Test-Path -LiteralPath $Output) {Remove-Item -LiteralPath $Output -Force}
  $deck.SaveAs($Output,24)
  Write-Output "Saved $Output ($($deck.Slides.Count) slides)"
} finally {
  if($null -ne $deck) {$deck.Close()}
  $app.Quit()
}
