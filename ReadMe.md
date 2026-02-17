# 0. 项目目的
经常需要在本地归档或引用 GitHub 上的 Issue 和 Pull Request。手动复制粘贴太麻烦了，我想做一个命令行工具，给它一个 URL，它就能自动帮我把那个 Issue 或 PR 的所有内容（标题、正文、评论等），转换成一个格式漂亮的 Markdown 文件保存下来。

## prompt1:
你好！现在的任务是：我们要从零开始设计并实现 `issue2md` 工具。

你现在不仅是资深的python工程师，更是一位经验丰富的产品经理。我有一个初步的想法，需要你通过向我提问，帮助我澄清需求、挖掘边缘场景，最终目标是共创一份高质量的 `spec.md`。

我的初步想法是：**做一个命令行工具，输入一个GitHub Issue/PR/Discussion的URL，它就能自动将其转换为Markdown文件。**

请开始你的提问。



# 1. 创建AI能力引擎室
mkdir -p ./.claude/{commands,skills,agents,hooks}

# 2. 创建SDD作战室
mkdir -p ./specs

# 3. 创建.gitignore文件，并写入核心忽略规则
echo ".claude/settings.local.json" > .gitignore
echo ".vscode/" >> .gitignore
echo ".idea/" >> .gitignore
echo "*.DS_Store" >> .gitignore
echo "/my-issue2md-project" >> .gitignore # 忽略构建产物（假设与目录同名）

# 4. 创建项目宪法文件 constitution.md
# 5. 创建CLAUDE.md文件，导入宪法并设定AI角色
# 6. 初始化Git仓库并提交初始版本
```
git init

git add .

git commit -m "feat(ai): initialize AI-native development framework" -m "Set up the foundational layout for Claude Code collaboration, including constitution, CLAUDE.md, shared settings, and directory structure for SDD and AI capabilities."

# 网站创建GitHub仓库并推送
git remote add origin git@github.com:shunchaoyin/my-issue2md.git
git branch -M main
git push -u origin main

```


