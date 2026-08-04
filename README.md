# Obsidian Aesthetic Library Skill

[English](README.en.md)

一个帮助 Codex 在 Obsidian 中建立设计审美库的 Skill。它把优秀设计工作室订阅、项目基线、每周更新、阅读状态、标签筛选和编辑精选整合成一套轻量的本地工作流。

## 它能建立什么

- 设计工作室画廊：集中浏览和筛选关注的工作室。
- 设计内容画廊：按品牌、字体、视觉识别、概念等维度查找项目。
- 52 家工作室的起始目录，以及可扩展的订阅源配置。
- 老项目基线与每周新增同步，避免把历史内容误判为本周更新。
- 未读/已读管理、受控标签、AI 编辑评语和“本周精选”。
- 不依赖审美库文件夹名称的检查、修复和同步脚本。

## 自动订阅与每周更新

初始化后，Skill 会为工作室建立订阅源配置和永久项目基线。它可以读取官网项目页、Feed、Sitemap 或经过验证的页面监控入口，并用基线识别真正新增的项目。

要让系统每周自动运行，可以让 Codex 创建一个每周任务：

```text
为我的审美库创建一个每周自动任务：同步所有工作室的新项目，整理候选内容，并生成本周精选。
```

每周流程包括：

1. 检查订阅源是否仍然有效。
2. 同步各工作室的新项目，并与永久基线去重。
3. 生成新增候选池，由 AI 编辑补充中文导读、标签、观察重点和编辑短评。
4. 从候选中整理“本周精选”：第一期最多 15 个，之后每期最多 10 个，实际数量由当周内容质量决定。

定时任务需要用户明确授权和创建。安装 Skill 本身不会静默添加后台任务。

## 内置工作室目录

目录收录 52 家工作室，覆盖品牌、平面、字体、出版、动态、数字体验、空间与实验设计。它是一份可修改的起始名单，来源状态以仓库内目录的核查日期为准。

### 北美

- [Pentagram](https://www.pentagram.com/)：由合伙人共同拥有和运营的独立设计机构，覆盖品牌战略、视觉识别、出版、数字体验、动态影像与空间设计。

- [PORTO ROCHA](https://www.portorocha.com/)：纽约与伦敦的策略设计机构，以严谨策略和情感表达处理大型品牌更新及独立文化项目。
- [Actual Source](https://actualsource.work/)：把策略、创意指导和视觉识别延伸到出版、网站、包装、服装与实体空间的设计工作室。
- [DIA Studio](https://www.dia.studio/)：设计、研究与创新工作室，专注动态身份系统、字体系统和生成式设计工具。
- [Order](https://order.design/)：专注品牌识别的设计事务所，强调每个决定都有理由，重视标准、档案和系统化执行。
- [Center](https://center.design/)：布鲁克林品牌团队，为消费品牌提供识别、包装、策略、动态、3D 和网站。
- [Other Means](https://othermeans.us/)：服务文化机构与组织的布鲁克林平面设计工作室，以字体身份、出版、展览、导视和网站回应当代文化。
- [Sunday Afternoon](https://sundayafternoon.us/)：纽约品牌与艺术家管理机构，把品牌策略和识别与广告、字体、摄影、动态及影片制作结合。
- [Wedge](https://www.wedge.work/)：蒙特利尔与洛杉矶的品牌设计机构，强调鲜明品牌性格，项目常落在餐饮、消费品和生活方式领域。
- [Caserne](https://www.caserne.com/)：蒙特利尔设计工作室，以故事和使命组织品牌，从定位、命名和叙事发展到完整视觉系统。
- [Mouthwash Studio](https://mouthwash.studio/)：面向艺术、建筑、时尚、科技与可持续领域，通过策略、视觉、动态和数字体验影响文化。
- [&Walsh](https://andwalsh.com/)：纽约品牌与广告机构，从品牌策略、设计和艺术指导一直负责到广告、社交与最终影像制作。
- [Special Offer](https://www.specialoffer.inc/)：以数字体验推动亚文化生长的创意科技公司，工作重点是技术、交互和网络文化之间的连接。
- [Gander](https://takeagander.com/)：纽约品牌与平面设计工作室，通过策略、包装、网站和艺术指导塑造具有个性与内容的品牌。
- [Polymode](https://www.polymode.studio/)：服务文化与社会正义项目的少数族裔和酷儿设计工作室，结合研究、出版、身份、展览与教育。
- [Landscape](https://thisislandscape.com/)：服务社会、环境、科学、科技与文化领域，以品牌策略、设计系统和传播推动改变。

### 欧洲

- [Studio Feixen](https://www.studiofeixen.ch/)：瑞士多学科设计工作室，以视觉概念为起点，覆盖图形、字体、动画、产品与空间设计。
- [Studio Yukiko](https://y-u-k-i-k-o.com/)：柏林创意机构，为商业与文化客户提供创意指导、视觉方向、品牌策略和概念开发。
- [Studio Nari](https://www.studionari.co.uk/)：把品牌视为人们愿意归属的文化系统，围绕身份、体验和表达建立文化导向的品牌。
- [How&How](https://how.studio/)：伦敦与洛杉矶的品牌机构，以策略、设计和数字体验帮助企业形成可识别的品牌系统。
- [Studio Kiln](https://www.studio-kiln.com/)：通过品牌、叙事和数字体验塑造具有生命感的品牌，客户集中在文化、娱乐和科技领域。
- [OMSE](https://www.omse.co/)：伦敦独立设计工作室，通过清晰而有意义的品牌帮助企业和用户形成连接。
- [Studio Airport](https://www.studioairport.nl/)：跨学科设计工作室，把策略和创意放在同一过程中，通过原型、叙事和影像实验发展品牌体验。
- [Barkas](https://barkas.com/)：哥本哈根独立创意公司，以清晰的策略和协作式创意建立跨身份、传播与数字触点的品牌。
- [Bielke&Yang](https://bielkeyang.com/)：奥斯陆设计机构，专注身份与长期品牌建设，也参与网站、故事表达和场所营造。
- [Studio Mut](https://www.studiomut.com/)：意大利平面设计工作室，长期合作建立视觉识别、数字平台和出版物，也持续探索动态与展览。
- [The Rodina](https://www.therodina.com/)：在文化与科技之间工作的实验设计工作室，以表演、游戏和研究发展视觉、线上平台与参与式装置。
- [Offshore Studio](https://www.offshorestudio.ch/)：苏黎世与维也纳的合作型设计工作室，研究编辑设计、字体、图像制作和视觉叙事。
- [Badesaison](https://www.badesaison.ch/)：苏黎世平面设计工作室，制作书籍、出版物、海报和视觉识别，也延伸至网页应用和空间装置。
- [Marcus Kraft](https://www.marcuskraft.com/)：苏黎世视觉传达工作室，以强叙事和字体质量发展品牌、出版、展览、包装、导视与数字项目。
- [Ohlman Consorti](https://www.ohlmanconsorti.com/)：巴黎的广告与数字媒体咨询机构，专长包括艺术指导、图像、字体、出版和网站。
- [Koto](https://koto.com/)：跨地区品牌设计工作室，通过策略、共同创作和细致执行，建立覆盖不同触点的品牌系统。

### 中国

- [ABCD](https://ablackcover.com/)：以品牌视觉为核心的国际设计机构，为新品牌与新零售项目提供策略、识别、包装和传播形象。
- [Studio NA.EO](https://www.studionaeo.com/)：独立视觉设计工作室，项目多围绕品牌视觉、文化活动、展览传播和消费类项目展开。
- [RELATED](https://www.related.design/)：围绕艺术与文化语境工作的视觉设计实践，项目常见出版物、海报、展览视觉、唱片和网站。
- [Pocca](https://pocca.design/)：研究驱动的设计工作室，在品牌策略与视觉叙事之间工作，强调信息、事实和情绪的共同组织。
- [Same Paper](https://samepaper.com/)：上海创意工作室，同时运营自主产品线，实践集中在摄影图像、出版内容和独立产品。
- [Workbyworks](https://workbyworks.studio/)：纽约与上海的多学科设计工作室，提供创意指导、品牌识别、包装、网站与书籍设计。
- [KAUKAU](https://www.kaukau.design/)：以品牌识别和视觉系统为核心，常通过字体、版式、包装和动态图形建立品牌表达。
- [Qingyu Wu](https://qingyuwu.com/)：服务独立艺术家、音乐人、品牌、学校和博物馆的设计实践，重点是印刷物与图形识别。
- [HDU²³ Lab](https://hdu23lab.com/)：无锡的小型平面设计工作室，为零售、轻餐饮和互联网项目提供品牌、视觉形象、海报与包装。
- [Guawa Design](https://www.guawadesign.com/)：上海与纽约的品牌设计工作室，为商业和文化客户提供品牌战略、识别、推广以及视觉咨询。
- [Mint Design](https://mintdesign.cn/)：关注人文、艺术与功能关系的多元创新工作室，常从日常生活和场域观察中发展视觉观点。

### 日本

- [GOO CHOKI PAR](https://gcp.design/)：由三位平面设计师组成的东京设计与艺术组合，以跨语言的视觉沟通和实验性图形表达为核心。
- [Yuta Takahashi Design Studio](https://yutatakahashi.jp/)：通过策略、概念开发和精细视觉解决品牌问题，项目常见品牌识别与包装系统。
- [TAKAIYAMA](https://takaiyama.jp/)：东京的艺术指导与平面设计工作室，作品覆盖印刷品、书籍、标志、导视和其他视觉项目。
- [STUDIO DETAILS](https://www.details.co.jp/)：从品牌价值衡量和战略出发，贯通创意开发、网站、产品与传播落地的品牌咨询型工作室。
- [Semitransparent Design](https://www.semitransparentdesign.com/)：由设计师、设备开发者和程序员组成的团队，长期探索网络与现实空间联动的数字设计和装置。
- [Whatever](https://whatever.co/)：横跨广告、娱乐与科技的创意团队，从品牌、电视广告和节目延伸到产品及新业务开发。
- [UMA / design farm](https://beta.umamu.jp/)：关注文化、福祉和地域议题，通过平面、空间、展览与企划开发，把理念转化为公共体验。
- [LABORATORIES](https://www.labor-atories.com/)：以艺术指导和视觉传达为核心，持续从事图形、书籍、网站与导视设计的东京工作室。
- [we+](https://weplus.jp/)：以研究和实验为方法的当代设计工作室，关注自然、社会环境以及被效率逻辑忽略的多元价值。

## 使用条件

- Codex
- Obsidian（启用 Bases 核心插件）
- Python 3

## 安装

将仓库克隆到 Codex 的 Skills 目录：

```bash
git clone https://github.com/shawpeng8815/obsidian-aesthetic-library-skill.git ~/.codex/skills/obsidian-aesthetic-library-skill
```

重新打开 Codex 后，可以这样使用：

```text
使用 $obsidian-aesthetic-library-skill，在我的 Obsidian Vault 中建立一套设计审美库。
```

Codex 会询问目标路径，并让你选择使用内置的 52 家工作室目录或从空目录开始。

## 说明

仓库只包含可复用的模板、脚本、字段规范和起始目录，不包含抓取后的项目内容与图片。工作室官网、Feed 和页面结构可能变化，正式同步前应重新验证来源。

Skill 的完整执行规则见 [`SKILL.md`](SKILL.md)。
