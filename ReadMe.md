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